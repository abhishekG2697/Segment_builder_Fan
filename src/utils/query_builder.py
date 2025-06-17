import streamlit as st
import json
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.yaml"
try:
    with open(CONFIG_PATH, "r") as f:
        _CONFIG = yaml.safe_load(f)
except Exception:
    _CONFIG = {}


def _build_field_table_map(cfg):
    mapping = {}
    for section in ["dimensions", "metrics"]:
        for cat in cfg.get(section, []):
            for item in cat.get("items", []):
                mapping[item.get("field")] = item.get("table", "hits")
    return mapping


FIELD_TABLE_MAP = _build_field_table_map(_CONFIG)
FIELD_TABLE_MAP.setdefault("total_hits", "sessions")
FIELD_TABLE_MAP.setdefault("total_revenue", "sessions")
FIELD_TABLE_MAP.setdefault("session_duration", "sessions")
FIELD_TABLE_MAP.setdefault("pages_viewed", "sessions")
FIELD_TABLE_MAP.setdefault("total_orders", "users")
FIELD_TABLE_MAP.setdefault("total_sessions", "users")


def iter_all_containers(cont_list):
    """Yield containers recursively"""
    for c in cont_list:
        yield c
        if c.get('children'):
            yield from iter_all_containers(c['children'])

def build_sql_from_segment(segment_definition):
    """Build SQL query from segment definition - FIXED VERSION"""
    
    if not segment_definition or not segment_definition.get('containers'):
        # Return a basic query if no containers
        return "SELECT * FROM hits LIMIT 0"
    
    containers = segment_definition.get('containers', [])
    container_type = segment_definition.get('container_type', 'hit')
    segment_logic = segment_definition.get('logic', 'and').upper()
    
    # Build container queries
    container_queries = []
    required_joins = set()
    
    for container in containers:
        container_sql, joins = build_container_sql(container, container_type, 0)
        if container_sql:
            container_queries.append(container_sql)
            required_joins.update(joins)
    
    if not container_queries:
        return "SELECT * FROM hits LIMIT 0"
    
    # Combine container queries
    if len(container_queries) == 1:
        final_query = container_queries[0]
    else:
        # Join multiple containers with segment logic
        final_query = f"({f') {segment_logic} ('.join(container_queries)})"
    
    # Wrap in main query
    join_clauses = ""
    if "sessions" in required_joins:
        join_clauses += " LEFT JOIN sessions s ON h.session_id = s.session_id"
    if "users" in required_joins:
        join_clauses += " LEFT JOIN users u ON h.user_id = u.user_id"

    main_query = f"""
    SELECT DISTINCT h.*
    FROM hits h{join_clauses}
    WHERE {final_query}
    ORDER BY h.timestamp DESC
    """
    
    return main_query

def build_container_sql(container, main_container_type, level=0):
    """Build SQL for a single container, supporting nested children"""
    
    conditions = container.get('conditions', [])
    children = container.get('children', [])
    if not conditions and not children:
        return None, set()
    
    container_type = container.get('type', main_container_type)
    include = container.get('include', True)
    container_logic = container.get('logic', 'and').upper()
    
    # Build condition SQL
    condition_sqls = []
    used_tables = set()

    if container_type == 'hit':
        aliases = {"hits": "h", "sessions": "s", "users": "u"}
    else:
        aliases = {"hits": "h2", "sessions": "s2", "users": "u2"}

    for condition in conditions:
        condition_sql, table = build_condition_sql(condition, aliases)
        if condition_sql:
            condition_sqls.append(condition_sql)
            used_tables.add(table)

    for child in children:
        child_sql, child_tables = build_container_sql(child, container_type, level + 1)
        if child_sql:
            condition_sqls.append(child_sql)
            used_tables.update(child_tables)
    
    if not condition_sqls:
        return None, set()
    
    # Combine conditions
    if len(condition_sqls) == 1:
        combined_conditions = condition_sqls[0]
    else:
        combined_conditions = f"({f' {container_logic} '.join(condition_sqls)})"
    
    # Handle different container types
    if container_type == 'hit':
        # Hit level - direct conditions
        base_query = combined_conditions
        join_tables = used_tables - {"hits"}
    elif container_type == 'visit':
        # Visit level - exists in session
        joins = ""
        if "sessions" in used_tables:
            joins += " LEFT JOIN sessions s2 ON h2.session_id = s2.session_id"
        if "users" in used_tables:
            joins += " LEFT JOIN users u2 ON h2.user_id = u2.user_id"
        base_query = f"""
        h.session_id IN (
            SELECT DISTINCT h2.session_id
            FROM hits h2{joins}
            WHERE {combined_conditions}
        )
        """
        join_tables = set()
    elif container_type == 'visitor':
        # Visitor level - exists for user
        joins = ""
        if "sessions" in used_tables:
            joins += " LEFT JOIN sessions s2 ON h2.session_id = s2.session_id"
        if "users" in used_tables:
            joins += " LEFT JOIN users u2 ON h2.user_id = u2.user_id"
        base_query = f"""
        h.user_id IN (
            SELECT DISTINCT h2.user_id
            FROM hits h2{joins}
            WHERE {combined_conditions}
        )
        """
        join_tables = set()
    else:
        base_query = combined_conditions
        join_tables = used_tables - {"hits"}
    
    # Handle include/exclude
    if not include:
        base_query = f"NOT ({base_query})"

    return base_query, join_tables

def build_condition_sql(condition, aliases):
    """Build SQL for a single condition and return used table."""

    field = condition.get('field')
    operator = condition.get('operator', 'equals')
    value = condition.get('value')
    data_type = condition.get('data_type', 'string')
    
    if not field:
        return None, 'hits'

    table = FIELD_TABLE_MAP.get(field, 'hits')
    alias = aliases.get(table, '')
    
    # Handle exists/does not exist operators
    field_ref = f"{alias}.{field}" if alias else field

    if operator == 'exists':
        return f"{field_ref} IS NOT NULL", table
    elif operator == 'does not exist':
        return f"{field_ref} IS NULL", table
    
    # For other operators, value is required
    if value is None or str(value).strip() == '':
        return None, table
    
    # Clean and format value
    clean_value = str(value).strip()
    
    # Build condition based on operator and data type
    if data_type == 'number':
        try:
            numeric_value = float(clean_value)
            if operator == 'equals':
                return f"{field_ref} = {numeric_value}", table
            elif operator == 'does not equal':
                return f"{field_ref} != {numeric_value}"
            elif operator == 'is greater than':
                return f"{field_ref} > {numeric_value}"
            elif operator == 'is greater than or equal to':
                return f"{field_ref} >= {numeric_value}"
            elif operator == 'is less than':
                return f"{field_ref} < {numeric_value}"
            elif operator == 'is less than or equal to':
                return f"{field_ref} <= {numeric_value}"
            elif operator == 'is between':
                value2 = condition.get('value2')
                if value2 is not None:
                    numeric_value2 = float(value2)
                    return f"{field_ref} BETWEEN {numeric_value} AND {numeric_value2}", table
                else:
                    return f"{field_ref} = {numeric_value}", table
        except (ValueError, TypeError):
            # If not a valid number, treat as string
            data_type = 'string'
    
    # String operations
    if data_type == 'string':
        # Escape single quotes in value
        escaped_value = clean_value.replace("'", "''")

        if operator == 'equals':
            return f"{field_ref} = '{escaped_value}'", table
        elif operator == 'does not equal':
            return f"{field_ref} != '{escaped_value}'", table
        elif operator == 'contains':
            return f"{field_ref} LIKE '%{escaped_value}%'", table
        elif operator == 'does not contain':
            return f"{field_ref} NOT LIKE '%{escaped_value}%'", table
        elif operator == 'starts with':
            return f"{field_ref} LIKE '{escaped_value}%'", table
        elif operator == 'ends with':
            return f"{field_ref} LIKE '%{escaped_value}'", table
        else:
            # Default to equals for unknown operators
            return f"{field_ref} = '{escaped_value}'", table
    
    return None, table

def render_query_builder(config):
    """Render a simple query builder interface"""
    
    st.markdown("### SQL Query Builder")
    
    # Show current segment
    if st.session_state.get('segment_definition'):
        with st.expander("Current Segment Definition", expanded=False):
            st.json(st.session_state.segment_definition)
        
        # Generate and show SQL
        try:
            sql_query = build_sql_from_segment(st.session_state.segment_definition)
            
            st.markdown("### Generated SQL Query")
            st.code(sql_query, language='sql')
            
            # Test query button
            if st.button("Test Query"):
                try:
                    from src.database.queries import execute_segment_query
                    result_df = execute_segment_query(sql_query, limit=10)
                    
                    if not result_df.empty:
                        st.success(f"Query executed successfully! Found {len(result_df)} records.")
                        st.dataframe(result_df.head(10))
                    else:
                        st.warning("Query executed successfully but returned no results.")
                        
                except Exception as e:
                    st.error(f"Query execution failed: {str(e)}")
            
        except Exception as e:
            st.error(f"Error generating SQL: {str(e)}")
    
    else:
        st.info("No segment defined. Please create a segment first.")

def convert_to_query_builder_format(segment_definition):
    """Convert segment definition to query builder format"""
    
    if not segment_definition:
        return {}
    
    # Extract basic info
    result = {
        'name': segment_definition.get('name', 'Unnamed Segment'),
        'description': segment_definition.get('description', ''),
        'container_type': segment_definition.get('container_type', 'hit'),
        'logic': segment_definition.get('logic', 'and'),
        'containers': []
    }
    
    def process_container(cont):
        c_data = {
            'id': cont.get('id', ''),
            'type': cont.get('type', 'hit'),
            'include': cont.get('include', True),
            'logic': cont.get('logic', 'and'),
            'conditions': [],
            'children': []
        }

        for condition in cont.get('conditions', []):
            c_data['conditions'].append({
                'id': condition.get('id', ''),
                'field': condition.get('field', ''),
                'name': condition.get('name', ''),
                'type': condition.get('type', 'dimension'),
                'operator': condition.get('operator', 'equals'),
                'value': condition.get('value', ''),
                'data_type': condition.get('data_type', 'string')
            })

        for child in cont.get('children', []):
            c_data['children'].append(process_container(child))

        return c_data

    for container in segment_definition.get('containers', []):
        result['containers'].append(process_container(container))
    
    return result

def validate_sql_query(query):
    """Validate SQL query for basic safety"""
    
    # Convert to lowercase for checking
    query_lower = query.lower().strip()
    
    # Check for dangerous keywords
    dangerous_keywords = [
        'drop', 'delete', 'truncate', 'alter', 'create', 'insert', 'update',
        'grant', 'revoke', 'exec', 'execute', 'xp_', 'sp_'
    ]
    
    for keyword in dangerous_keywords:
        if keyword in query_lower:
            return False, f"Dangerous keyword detected: {keyword}"
    
    # Must start with SELECT
    if not query_lower.startswith('select'):
        return False, "Query must start with SELECT"
    
    # Basic structure validation
    if 'from' not in query_lower:
        return False, "Query must contain FROM clause"
    
    return True, "Query appears safe"

def optimize_query(query):
    """Apply basic query optimizations"""
    
    # Remove extra whitespace
    optimized = ' '.join(query.split())
    
    # Add LIMIT if not present (for safety)
    if 'limit' not in optimized.lower():
        optimized += ' LIMIT 10000'
    
    return optimized

def explain_query_structure(segment_definition):
    """Explain the structure of the generated query"""
    
    if not segment_definition or not segment_definition.get('containers'):
        return "No segment containers defined."
    
    explanation = []
    explanation.append("**Query Structure:**")
    
    containers = segment_definition.get('containers', [])
    container_type = segment_definition.get('container_type', 'hit')

    flat_containers = list(iter_all_containers(containers))

    explanation.append(f"- Main container type: **{container_type.title()}**")
    explanation.append(f"- Number of containers: **{len(flat_containers)}**")

    for i, container in enumerate(flat_containers):
        mode = "Include" if container.get('include', True) else "Exclude"
        cond_count = len(container.get('conditions', []))
        explanation.append(f"- Container {i+1}: **{mode}** {container.get('type', 'hit')} with {cond_count} condition(s)")
    
    if len(containers) > 1:
        logic = segment_definition.get('logic', 'and').upper()
        explanation.append(f"- Containers combined with: **{logic}**")
    
    return "\n".join(explanation)

# Additional utility functions for debugging and analysis

def analyze_segment_complexity(segment_definition):
    """Analyze the complexity of a segment definition"""
    
    if not segment_definition:
        return {"complexity": "none", "score": 0, "details": "No segment defined"}
    
    score = 0
    details = []
    
    # Count containers
    containers = segment_definition.get('containers', [])
    flat_containers = list(iter_all_containers(containers))
    container_count = len(flat_containers)
    score += container_count * 2
    details.append(f"{container_count} container(s)")
    
    # Count total conditions
    total_conditions = sum(len(c.get('conditions', [])) for c in flat_containers)
    score += total_conditions
    details.append(f"{total_conditions} total condition(s)")
    
    # Check for exclude containers
    exclude_containers = sum(1 for c in flat_containers if not c.get('include', True))
    if exclude_containers > 0:
        score += exclude_containers * 3
        details.append(f"{exclude_containers} exclude container(s)")
    
    # Check for different container types
    container_types = set(c.get('type', 'hit') for c in flat_containers)
    if len(container_types) > 1:
        score += 2
        details.append("Mixed container types")
    
    # Determine complexity level
    if score == 0:
        complexity = "none"
    elif score <= 3:
        complexity = "simple"
    elif score <= 8:
        complexity = "moderate"
    elif score <= 15:
        complexity = "complex"
    else:
        complexity = "very complex"
    
    return {
        "complexity": complexity,
        "score": score,
        "details": ", ".join(details)
    }

def get_field_suggestions(partial_field, config):
    """Get field suggestions based on partial input"""
    
    suggestions = []
    partial_lower = partial_field.lower()
    
    # Search dimensions
    for category in config.get('dimensions', []):
        for item in category['items']:
            if partial_lower in item['name'].lower() or partial_lower in item['field'].lower():
                suggestions.append({
                    'name': item['name'],
                    'field': item['field'],
                    'type': 'dimension',
                    'category': category['category']
                })
    
    # Search metrics
    for category in config.get('metrics', []):
        for item in category['items']:
            if partial_lower in item['name'].lower() or partial_lower in item['field'].lower():
                suggestions.append({
                    'name': item['name'],
                    'field': item['field'],
                    'type': 'metric',
                    'category': category['category']
                })
    
    return suggestions[:10]  # Limit to 10 suggestions