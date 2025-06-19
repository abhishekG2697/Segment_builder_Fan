import sqlite3
import pandas as pd
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
import json
import uuid
from datetime import datetime
import yaml
from pathlib import Path

# Load configuration for field mappings
CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.yaml"
try:
    with open(CONFIG_PATH, "r") as f:
        _CONFIG = yaml.safe_load(f)
except Exception:
    _CONFIG = {}


def _build_field_table_map(cfg):
    """Build mapping of fields to their database tables"""
    mapping = {}
    for section in ["dimensions", "metrics"]:
        for cat in cfg.get(section, []):
            for item in cat.get("items", []):
                mapping[item.get("field")] = item.get("table", "hits")
    return mapping


# Field to table mapping
FIELD_TABLE_MAP = _build_field_table_map(_CONFIG)
FIELD_TABLE_MAP.setdefault("total_hits", "sessions")
FIELD_TABLE_MAP.setdefault("total_revenue", "sessions")
FIELD_TABLE_MAP.setdefault("session_duration", "sessions")
FIELD_TABLE_MAP.setdefault("pages_viewed", "sessions")
FIELD_TABLE_MAP.setdefault("total_orders", "users")
FIELD_TABLE_MAP.setdefault("total_sessions", "users")


def build_sql_query(segment_definition: Dict) -> str:
    """
    Build SQL query from segment definition with nested container support
    """
    if not segment_definition or not segment_definition.get('containers'):
        return "-- No segment definition provided"

    # Extract basic info
    containers = segment_definition.get('containers', [])
    segment_logic = segment_definition.get('logic', 'and').upper()

    # Build WHERE clause from containers
    where_conditions = []

    for container in containers:
        container_sql = build_container_sql(container)
        if container_sql:
            where_conditions.append(f"({container_sql})")

    # Combine container conditions
    if where_conditions:
        where_clause = f" {segment_logic} ".join(where_conditions)
    else:
        where_clause = "1=1"

    # Build final query
    query = f"""
    SELECT 
        user_id,
        COUNT(*) as hit_count,
        COUNT(DISTINCT session_id) as session_count,
        MIN(timestamp) as first_hit,
        MAX(timestamp) as last_hit
    FROM hits 
    WHERE {where_clause}
    GROUP BY user_id
    ORDER BY hit_count DESC
    """

    return query.strip()


def build_sql_from_segment(segment_definition: Dict) -> str:
    """
    Build SQL query from segment definition - FIXED VERSION for backward compatibility
    """
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
        container_sql, joins = build_container_sql_with_joins(container, container_type, 0)
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
    SELECT DISTINCT h.user_id, h.session_id, h.timestamp, h.page_url, h.device_type
    FROM hits h{join_clauses}
    WHERE {final_query}
    """

    return main_query


def build_container_sql_with_joins(container: Dict, container_type: str = 'hit', level: int = 0) -> Tuple[str, set]:
    """
    Build SQL for a single container with join requirements (for backward compatibility)
    """
    container_sql = build_container_sql(container, level)
    joins = set()

    # Determine required joins based on conditions
    conditions = container.get('conditions', [])
    for condition in conditions:
        field = condition.get('field', '')
        if field in FIELD_TABLE_MAP:
            table = FIELD_TABLE_MAP[field]
            if table != 'hits':
                joins.add(table)

    # Check children for join requirements
    children = container.get('children', [])
    for child in children:
        _, child_joins = build_container_sql_with_joins(child, container_type, level + 1)
        joins.update(child_joins)

    return container_sql, joins


def build_container_sql(container: Dict, level: int = 0) -> str:
    """
    Build SQL for a single container with nested support
    """
    container_type = container.get('type', 'hit')
    include = container.get('include', True)
    logic = container.get('logic', 'and').upper()
    conditions = container.get('conditions', [])
    children = container.get('children', [])

    # Build condition SQL
    condition_sqls = []

    # Add direct conditions
    for condition in conditions:
        condition_sql = build_condition_sql(condition)
        if condition_sql:
            condition_sqls.append(condition_sql)

    # Add child container SQL
    for child in children:
        child_sql = build_container_sql(child, level + 1)
        if child_sql:
            condition_sqls.append(f"({child_sql})")

    # Combine conditions
    if condition_sqls:
        combined_sql = f" {logic} ".join(condition_sqls)
    else:
        combined_sql = "1=1"

    # Apply container-specific logic
    if container_type == 'visit':
        # Visit-level container: conditions must be met within the same session
        combined_sql = f"session_id IN (SELECT session_id FROM hits WHERE {combined_sql})"
    elif container_type == 'visitor':
        # Visitor-level container: conditions must be met by the same user
        combined_sql = f"user_id IN (SELECT user_id FROM hits WHERE {combined_sql})"

    # Handle include/exclude
    if not include:
        combined_sql = f"NOT ({combined_sql})"

    return combined_sql


def build_condition_sql(condition: Dict) -> str:
    """
    Build SQL for a single condition
    """
    field = condition.get('field', '')
    operator = condition.get('operator', 'equals')
    value = condition.get('value', '')
    data_type = condition.get('data_type', 'string')

    if not field or value == '':
        return ""

    # Escape field name
    field = field.replace("'", "''")

    # Handle different operators
    if operator == 'equals':
        if data_type == 'number':
            return f"{field} = {value}"
        else:
            return f"{field} = '{value}'"
    elif operator == 'not_equals':
        if data_type == 'number':
            return f"{field} != {value}"
        else:
            return f"{field} != '{value}'"
    elif operator == 'contains':
        return f"{field} LIKE '%{value}%'"
    elif operator == 'not_contains':
        return f"{field} NOT LIKE '%{value}%'"
    elif operator == 'starts_with':
        return f"{field} LIKE '{value}%'"
    elif operator == 'ends_with':
        return f"{field} LIKE '%{value}'"
    elif operator == 'greater_than':
        return f"{field} > {value}"
    elif operator == 'less_than':
        return f"{field} < {value}"
    elif operator == 'greater_equal':
        return f"{field} >= {value}"
    elif operator == 'less_equal':
        return f"{field} <= {value}"
    else:
        return f"{field} = '{value}'"


def iter_all_containers(containers: List[Dict], level: int = 0) -> List[Dict]:
    """
    Iterate through all containers including nested ones
    """
    all_containers = []

    for container in containers:
        # Add current container with level info
        container_with_level = {**container, 'level': level}
        all_containers.append(container_with_level)

        # Recursively add children
        children = container.get('children', [])
        if children:
            all_containers.extend(iter_all_containers(children, level + 1))

    return all_containers


def execute_segment_query(segment_definition: Dict, db_path: str = "data/analytics.db") -> pd.DataFrame:
    """
    Execute segment query and return results
    """
    try:
        query = build_sql_query(segment_definition)

        if query.startswith("--"):
            return pd.DataFrame()

        conn = sqlite3.connect(db_path)
        result_df = pd.read_sql_query(query, conn)
        conn.close()

        return result_df

    except Exception as e:
        st.error(f"Query execution failed: {str(e)}")
        return pd.DataFrame()


def render_query_preview(segment_definition: Dict):
    """
    Render SQL query preview with nested container support
    """
    if not segment_definition or not segment_definition.get('containers'):
        st.info("No segment defined. Please create a segment first.")
        return

    # Generate and display SQL
    sql_query = build_sql_query(segment_definition)

    st.subheader("Generated SQL Query")
    st.code(sql_query, language="sql")

    # Show query explanation
    explanation = explain_query_structure(segment_definition)
    st.markdown("### Query Explanation")
    st.markdown(explanation)

    # Execute query if requested
    if st.button("Execute Query", type="primary"):
        with st.spinner("Executing query..."):
            result_df = execute_segment_query(segment_definition)

            if not result_df.empty:
                st.success(f"Query executed successfully. Found {len(result_df)} records.")

                # Display summary statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Users", len(result_df))
                with col2:
                    st.metric("Avg Hits per User", f"{result_df['hit_count'].mean():.1f}")
                with col3:
                    st.metric("Avg Sessions per User", f"{result_df['session_count'].mean():.1f}")

                # Display sample results
                st.subheader("Sample Results")
                st.dataframe(result_df.head(10))

                # Download option
                csv = result_df.to_csv(index=False)
                st.download_button(
                    label="Download Results as CSV",
                    data=csv,
                    file_name=f"segment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Query executed successfully but returned no results.")


def render_query_builder(segment_definition: Dict):
    """
    Render the query builder interface for segment preview
    """
    if not segment_definition:
        st.info("No segment defined. Please create a segment first.")
        return

    st.subheader("Query Builder")

    # Show segment summary
    col1, col2, col3 = st.columns(3)

    with col1:
        containers = segment_definition.get('containers', [])
        flat_containers = iter_all_containers(containers)
        st.metric("Total Containers", len(flat_containers))

    with col2:
        total_conditions = sum(len(c.get('conditions', [])) for c in flat_containers)
        st.metric("Total Conditions", total_conditions)

    with col3:
        max_depth = get_max_nesting_depth(containers)
        st.metric("Max Nesting Level", max_depth)

    # Query preview and execution
    render_query_preview(segment_definition)


def explain_query_structure(segment_definition: Dict) -> str:
    """
    Explain the structure of the generated query with nested support
    """
    if not segment_definition or not segment_definition.get('containers'):
        return "No segment containers defined."

    explanation = []
    explanation.append("**Query Structure:**")

    containers = segment_definition.get('containers', [])
    container_type = segment_definition.get('container_type', 'hit')

    flat_containers = iter_all_containers(containers)

    explanation.append(f"- Main container type: **{container_type.title()}**")
    explanation.append(f"- Total containers (including nested): **{len(flat_containers)}**")

    # Analyze container hierarchy
    levels = {}
    for container in flat_containers:
        level = container.get('level', 0)
        if level not in levels:
            levels[level] = []
        levels[level].append(container)

    explanation.append(f"- Container hierarchy levels: **{len(levels)}**")

    for level, containers_at_level in sorted(levels.items()):
        level_name = "Root" if level == 0 else f"Level {level}"
        explanation.append(f"  - {level_name}: {len(containers_at_level)} container(s)")

        for container in containers_at_level:
            mode = "Include" if container.get('include', True) else "Exclude"
            cond_count = len(container.get('conditions', []))
            child_count = len(container.get('children', []))
            explanation.append(
                f"    - **{mode}** {container.get('type', 'hit')} with {cond_count} condition(s) and {child_count} child(ren)")

    if len(containers) > 1:
        logic = segment_definition.get('logic', 'and').upper()
        explanation.append(f"- Root containers combined with: **{logic}**")

    return "\n".join(explanation)


def analyze_segment_complexity(segment_definition: Dict) -> Dict[str, Any]:
    """
    Analyze the complexity of a segment definition with nested support
    """
    if not segment_definition:
        return {"complexity": "none", "score": 0, "details": "No segment defined"}

    score = 0
    details = []

    # Count containers at all levels
    containers = segment_definition.get('containers', [])
    flat_containers = iter_all_containers(containers)
    container_count = len(flat_containers)
    score += container_count * 2
    details.append(f"{container_count} total container(s)")

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

    # Nesting complexity
    max_level = max((c.get('level', 0) for c in flat_containers), default=0)
    if max_level > 0:
        score += max_level * 3
        details.append(f"Maximum nesting level: {max_level}")

    # Logic complexity
    complex_logic_count = sum(1 for c in flat_containers if c.get('logic') in ['or', 'then'])
    if complex_logic_count > 0:
        score += complex_logic_count * 2
        details.append(f"{complex_logic_count} container(s) with OR/THEN logic")

    # Determine complexity level
    if score == 0:
        complexity = "none"
    elif score <= 5:
        complexity = "simple"
    elif score <= 15:
        complexity = "moderate"
    elif score <= 30:
        complexity = "complex"
    else:
        complexity = "very complex"

    return {
        "complexity": complexity,
        "score": score,
        "details": "; ".join(details),
        "max_nesting_level": max_level,
        "total_containers": container_count,
        "total_conditions": total_conditions
    }


def validate_sql_query(query: str) -> Tuple[bool, str]:
    """
    Validate SQL query for basic safety
    """
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


def optimize_query(query: str) -> str:
    """
    Apply basic query optimizations
    """
    # Remove extra whitespace
    optimized = ' '.join(query.split())

    # Add LIMIT if not present (for safety)
    if 'limit' not in optimized.lower():
        optimized += ' LIMIT 10000'

    return optimized


def convert_to_query_builder_format(segment_definition: Dict) -> Dict:
    """
    Convert segment definition to query builder format with nested support
    """
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


def export_segment_json(segment_definition: Dict, filename: str = None) -> str:
    """
    Export segment definition to JSON format
    """
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        segment_name = segment_definition.get('name', 'segment').lower().replace(' ', '_')
        filename = f"{segment_name}_{timestamp}.json"

    # Add metadata
    export_data = {
        **segment_definition,
        'exported_at': datetime.now().isoformat(),
        'exported_by': 'segment_builder',
        'version': '2.0'
    }

    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
    return json_str


def import_segment_json(json_str: str) -> Dict:
    """
    Import segment definition from JSON string
    """
    try:
        data = json.loads(json_str)

        # Validate required fields
        if 'name' not in data:
            raise ValueError("Segment must have a name")

        if 'containers' not in data:
            data['containers'] = []

        # Ensure all containers have required fields
        def validate_container(container):
            if 'id' not in container:
                container['id'] = str(uuid.uuid4())
            if 'type' not in container:
                container['type'] = 'hit'
            if 'include' not in container:
                container['include'] = True
            if 'logic' not in container:
                container['logic'] = 'and'
            if 'conditions' not in container:
                container['conditions'] = []
            if 'children' not in container:
                container['children'] = []

            # Validate children recursively
            for child in container['children']:
                validate_container(child)

        for container in data['containers']:
            validate_container(container)

        return data

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error importing segment: {str(e)}")


def get_segment_statistics(segment_definition: Dict) -> Dict[str, Any]:
    """
    Get comprehensive statistics about a segment
    """
    if not segment_definition:
        return {}

    stats = {
        'basic_info': {
            'name': segment_definition.get('name', 'Unnamed'),
            'description': segment_definition.get('description', ''),
            'container_type': segment_definition.get('container_type', 'hit'),
            'logic': segment_definition.get('logic', 'and')
        },
        'structure': {},
        'complexity': {},
        'containers': []
    }

    # Get all containers
    containers = segment_definition.get('containers', [])
    flat_containers = iter_all_containers(containers)

    # Structure statistics
    stats['structure'] = {
        'total_containers': len(flat_containers),
        'root_containers': len(containers),
        'max_nesting_level': max((c.get('level', 0) for c in flat_containers), default=0),
        'total_conditions': sum(len(c.get('conditions', [])) for c in flat_containers),
        'container_types': list(set(c.get('type', 'hit') for c in flat_containers))
    }

    # Complexity analysis
    complexity_info = analyze_segment_complexity(segment_definition)
    stats['complexity'] = complexity_info

    # Container details
    for container in flat_containers:
        container_stats = {
            'id': container.get('id'),
            'type': container.get('type', 'hit'),
            'include': container.get('include', True),
            'level': container.get('level', 0),
            'conditions_count': len(container.get('conditions', [])),
            'children_count': len(container.get('children', [])),
            'logic': container.get('logic', 'and')
        }
        stats['containers'].append(container_stats)

    return stats


def render_segment_statistics(segment_definition: Dict):
    """
    Render segment statistics in Streamlit
    """
    if not segment_definition:
        st.info("No segment defined")
        return

    stats = get_segment_statistics(segment_definition)

    # Basic info
    st.subheader("Segment Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Containers", stats['structure']['total_containers'])
        st.metric("Root Containers", stats['structure']['root_containers'])
    with col2:
        st.metric("Max Nesting Level", stats['structure']['max_nesting_level'])
        st.metric("Total Conditions", stats['structure']['total_conditions'])

    # Complexity
    st.subheader("Complexity Analysis")
    complexity = stats['complexity']

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Complexity Level", complexity['complexity'].title())
    with col2:
        st.metric("Complexity Score", complexity['score'])
    with col3:
        st.metric("Nesting Levels", complexity['max_nesting_level'])

    st.write(f"**Details:** {complexity['details']}")

    # Container breakdown
    if stats['containers']:
        st.subheader("Container Breakdown")

        container_df = pd.DataFrame(stats['containers'])
        container_df['Mode'] = container_df['include'].map({True: 'Include', False: 'Exclude'})

        # Show container table
        display_df = container_df[['type', 'Mode', 'level', 'conditions_count', 'children_count', 'logic']].copy()
        display_df.columns = ['Type', 'Mode', 'Level', 'Conditions', 'Children', 'Logic']

        st.dataframe(display_df, use_container_width=True)

        # Container type distribution
        type_counts = container_df['type'].value_counts()
        if len(type_counts) > 1:
            st.bar_chart(type_counts)


def generate_segment_documentation(segment_definition: Dict) -> str:
    """
    Generate comprehensive documentation for a segment
    """
    if not segment_definition:
        return "No segment definition provided"

    doc = []

    # Header
    doc.append(f"# Segment Documentation: {segment_definition.get('name', 'Unnamed')}")
    doc.append("")

    # Basic info
    doc.append("## Basic Information")
    doc.append(f"- **Name:** {segment_definition.get('name', 'Unnamed')}")
    doc.append(f"- **Description:** {segment_definition.get('description', 'No description')}")
    doc.append(f"- **Container Type:** {segment_definition.get('container_type', 'hit').title()}")
    doc.append(f"- **Logic:** {segment_definition.get('logic', 'and').upper()}")
    doc.append("")

    # Statistics
    stats = get_segment_statistics(segment_definition)
    doc.append("## Statistics")
    doc.append(f"- **Total Containers:** {stats['structure']['total_containers']}")
    doc.append(f"- **Root Containers:** {stats['structure']['root_containers']}")
    doc.append(f"- **Maximum Nesting Level:** {stats['structure']['max_nesting_level']}")
    doc.append(f"- **Total Conditions:** {stats['structure']['total_conditions']}")
    doc.append(f"- **Complexity Level:** {stats['complexity']['complexity'].title()}")
    doc.append(f"- **Complexity Score:** {stats['complexity']['score']}")
    doc.append("")

    # Container details
    doc.append("## Container Structure")

    def document_container(container, level=0):
        indent = "  " * level
        mode = "Include" if container.get('include', True) else "Exclude"
        container_type = container.get('type', 'hit').title()
        logic = container.get('logic', 'and').upper()

        doc.append(f"{indent}- **{mode} {container_type} Container** (Logic: {logic})")

        # Conditions
        conditions = container.get('conditions', [])
        if conditions:
            doc.append(f"{indent}  - **Conditions:**")
            for i, condition in enumerate(conditions):
                if i > 0:
                    doc.append(f"{indent}    - *{logic}*")
                doc.append(
                    f"{indent}    - {condition.get('name', 'Unknown')} {condition.get('operator', 'equals')} '{condition.get('value', '')}'")

        # Children
        children = container.get('children', [])
        if children:
            doc.append(f"{indent}  - **Child Containers:**")
            for child in children:
                document_container(child, level + 2)

        doc.append("")

    containers = segment_definition.get('containers', [])
    for i, container in enumerate(containers):
        if i > 0:
            segment_logic = segment_definition.get('logic', 'and').upper()
            doc.append(f"*{segment_logic}*")
            doc.append("")
        document_container(container)

    # SQL Query
    doc.append("## Generated SQL Query")
    doc.append("```sql")
    doc.append(build_sql_query(segment_definition))
    doc.append("```")
    doc.append("")

    # Export info
    doc.append("## Export Information")
    doc.append(f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.append(f"- **Tool:** Adobe Analytics Segment Builder")
    doc.append(f"- **Version:** 2.0")

    return "\n".join(doc)


def create_segment_backup(segment_definition: Dict) -> str:
    """
    Create a backup of the segment definition
    """
    if not segment_definition:
        return ""

    backup_data = {
        'segment': segment_definition,
        'backup_timestamp': datetime.now().isoformat(),
        'backup_type': 'manual',
        'version': '2.0'
    }

    return json.dumps(backup_data, indent=2)


def restore_segment_from_backup(backup_json: str) -> Dict:
    """
    Restore segment from backup JSON
    """
    try:
        backup_data = json.loads(backup_json)

        if 'segment' not in backup_data:
            raise ValueError("Invalid backup format: missing segment data")

        segment = backup_data['segment']

        # Validate restored segment
        if 'name' not in segment:
            raise ValueError("Invalid segment: missing name")

        return segment

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid backup JSON: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error restoring backup: {str(e)}")


# Helper functions for container operations
def find_container_by_id(containers: List[Dict], container_id: str) -> Optional[Dict]:
    """
    Find a container by its ID in nested structure
    """
    for container in containers:
        if container.get('id') == container_id:
            return container

        # Search in children
        children = container.get('children', [])
        if children:
            found = find_container_by_id(children, container_id)
            if found:
                return found

    return None


def get_container_path(containers: List[Dict], container_id: str, current_path: List[int] = None) -> Optional[
    List[int]]:
    """
    Get the path to a container by its ID
    """
    if current_path is None:
        current_path = []

    for i, container in enumerate(containers):
        path = current_path + [i]

        if container.get('id') == container_id:
            return path

        # Search in children
        children = container.get('children', [])
        if children:
            child_path = get_container_path(children, container_id, path)
            if child_path:
                return child_path

    return None


def count_containers_by_type(containers: List[Dict]) -> Dict[str, int]:
    """
    Count containers by type across all nesting levels
    """
    counts = {'hit': 0, 'visit': 0, 'visitor': 0}

    flat_containers = iter_all_containers(containers)

    for container in flat_containers:
        container_type = container.get('type', 'hit')
        if container_type in counts:
            counts[container_type] += 1

    return counts


def get_max_nesting_depth(containers: List[Dict]) -> int:
    """
    Get maximum nesting depth of containers
    """
    if not containers:
        return 0

    max_depth = 0

    def get_depth(container_list, current_depth=0):
        nonlocal max_depth
        max_depth = max(max_depth, current_depth)

        for container in container_list:
            children = container.get('children', [])
            if children:
                get_depth(children, current_depth + 1)

    get_depth(containers)
    return max_depth


def build_sql_query(segment_definition: Dict) -> str:
    """
    Build SQL query from segment definition with nested container support
    """
    if not segment_definition or not segment_definition.get('containers'):
        return "-- No segment definition provided"

    # Extract basic info
    containers = segment_definition.get('containers', [])
    segment_logic = segment_definition.get('logic', 'and').upper()

    # Build WHERE clause from containers
    where_conditions = []

    for container in containers:
        container_sql = build_container_sql(container)
        if container_sql:
            where_conditions.append(f"({container_sql})")

    # Combine container conditions
    if where_conditions:
        where_clause = f" {segment_logic} ".join(where_conditions)
    else:
        where_clause = "1=1"

    # Build final query
    query = f"""
    SELECT 
        user_id,
        COUNT(*) as hit_count,
        COUNT(DISTINCT session_id) as session_count,
        MIN(timestamp) as first_hit,
        MAX(timestamp) as last_hit
    FROM hits 
    WHERE {where_clause}
    GROUP BY user_id
    ORDER BY hit_count DESC
    """

    return query.strip()


def build_container_sql(container: Dict, level: int = 0) -> str:
    """
    Build SQL for a single container with nested support
    """
    container_type = container.get('type', 'hit')
    include = container.get('include', True)
    logic = container.get('logic', 'and').upper()
    conditions = container.get('conditions', [])
    children = container.get('children', [])

    # Build condition SQL
    condition_sqls = []

    # Add direct conditions
    for condition in conditions:
        condition_sql = build_condition_sql(condition)
        if condition_sql:
            condition_sqls.append(condition_sql)

    # Add child container SQL
    for child in children:
        child_sql = build_container_sql(child, level + 1)
        if child_sql:
            condition_sqls.append(f"({child_sql})")

    # Combine conditions
    if condition_sqls:
        combined_sql = f" {logic} ".join(condition_sqls)
    else:
        combined_sql = "1=1"

    # Apply container-specific logic
    if container_type == 'visit':
        # Visit-level container: conditions must be met within the same session
        combined_sql = f"session_id IN (SELECT session_id FROM hits WHERE {combined_sql})"
    elif container_type == 'visitor':
        # Visitor-level container: conditions must be met by the same user
        combined_sql = f"user_id IN (SELECT user_id FROM hits WHERE {combined_sql})"

    # Handle include/exclude
    if not include:
        combined_sql = f"NOT ({combined_sql})"

    return combined_sql


def build_condition_sql(condition: Dict) -> str:
    """
    Build SQL for a single condition
    """
    field = condition.get('field', '')
    operator = condition.get('operator', 'equals')
    value = condition.get('value', '')
    data_type = condition.get('data_type', 'string')

    if not field or value == '':
        return ""

    # Escape field name
    field = field.replace("'", "''")

    # Handle different operators
    if operator == 'equals':
        if data_type == 'number':
            return f"{field} = {value}"
        else:
            return f"{field} = '{value}'"
    elif operator == 'not_equals':
        if data_type == 'number':
            return f"{field} != {value}"
        else:
            return f"{field} != '{value}'"
    elif operator == 'contains':
        return f"{field} LIKE '%{value}%'"
    elif operator == 'not_contains':
        return f"{field} NOT LIKE '%{value}%'"
    elif operator == 'starts_with':
        return f"{field} LIKE '{value}%'"
    elif operator == 'ends_with':
        return f"{field} LIKE '%{value}'"
    elif operator == 'greater_than':
        return f"{field} > {value}"
    elif operator == 'less_than':
        return f"{field} < {value}"
    elif operator == 'greater_equal':
        return f"{field} >= {value}"
    elif operator == 'less_equal':
        return f"{field} <= {value}"
    else:
        return f"{field} = '{value}'"


def iter_all_containers(containers: List[Dict], level: int = 0) -> List[Dict]:
    """
    Iterate through all containers including nested ones
    """
    all_containers = []

    for container in containers:
        # Add current container with level info
        container_with_level = {**container, 'level': level}
        all_containers.append(container_with_level)

        # Recursively add children
        children = container.get('children', [])
        if children:
            all_containers.extend(iter_all_containers(children, level + 1))

    return all_containers


def execute_segment_query(segment_definition: Dict, db_path: str = "data/analytics.db") -> pd.DataFrame:
    """
    Execute segment query and return results
    """
    try:
        query = build_sql_query(segment_definition)

        if query.startswith("--"):
            return pd.DataFrame()

        conn = sqlite3.connect(db_path)
        result_df = pd.read_sql_query(query, conn)
        conn.close()

        return result_df

    except Exception as e:
        st.error(f"Query execution failed: {str(e)}")
        return pd.DataFrame()


def render_query_preview(segment_definition: Dict):
    """
    Render SQL query preview with nested container support
    """
    if not segment_definition or not segment_definition.get('containers'):
        st.info("No segment defined. Please create a segment first.")
        return

    # Generate and display SQL
    sql_query = build_sql_query(segment_definition)

    st.subheader("Generated SQL Query")
    st.code(sql_query, language="sql")

    # Show query explanation
    explanation = explain_query_structure(segment_definition)
    st.markdown("### Query Explanation")
    st.markdown(explanation)

    # Execute query if requested
    if st.button("Execute Query", type="primary"):
        with st.spinner("Executing query..."):
            result_df = execute_segment_query(segment_definition)

            if not result_df.empty:
                st.success(f"Query executed successfully. Found {len(result_df)} records.")

                # Display summary statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Users", len(result_df))
                with col2:
                    st.metric("Avg Hits per User", f"{result_df['hit_count'].mean():.1f}")
                with col3:
                    st.metric("Avg Sessions per User", f"{result_df['session_count'].mean():.1f}")

                # Display sample results
                st.subheader("Sample Results")
                st.dataframe(result_df.head(10))

                # Download option
                csv = result_df.to_csv(index=False)
                st.download_button(
                    label="Download Results as CSV",
                    data=csv,
                    file_name=f"segment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Query executed successfully but returned no results.")


def explain_query_structure(segment_definition: Dict) -> str:
    """
    Explain the structure of the generated query with nested support
    """
    if not segment_definition or not segment_definition.get('containers'):
        return "No segment containers defined."

    explanation = []
    explanation.append("**Query Structure:**")

    containers = segment_definition.get('containers', [])
    container_type = segment_definition.get('container_type', 'hit')

    flat_containers = iter_all_containers(containers)

    explanation.append(f"- Main container type: **{container_type.title()}**")
    explanation.append(f"- Total containers (including nested): **{len(flat_containers)}**")

    # Analyze container hierarchy
    levels = {}
    for container in flat_containers:
        level = container.get('level', 0)
        if level not in levels:
            levels[level] = []
        levels[level].append(container)

    explanation.append(f"- Container hierarchy levels: **{len(levels)}**")

    for level, containers_at_level in sorted(levels.items()):
        level_name = "Root" if level == 0 else f"Level {level}"
        explanation.append(f"  - {level_name}: {len(containers_at_level)} container(s)")

        for container in containers_at_level:
            mode = "Include" if container.get('include', True) else "Exclude"
            cond_count = len(container.get('conditions', []))
            child_count = len(container.get('children', []))
            explanation.append(
                f"    - **{mode}** {container.get('type', 'hit')} with {cond_count} condition(s) and {child_count} child(ren)")

    if len(containers) > 1:
        logic = segment_definition.get('logic', 'and').upper()
        explanation.append(f"- Root containers combined with: **{logic}**")

    return "\n".join(explanation)


def analyze_segment_complexity(segment_definition: Dict) -> Dict[str, Any]:
    """
    Analyze the complexity of a segment definition with nested support
    """
    if not segment_definition:
        return {"complexity": "none", "score": 0, "details": "No segment defined"}

    score = 0
    details = []

    # Count containers at all levels
    containers = segment_definition.get('containers', [])
    flat_containers = iter_all_containers(containers)
    container_count = len(flat_containers)
    score += container_count * 2
    details.append(f"{container_count} total container(s)")

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

    # Nesting complexity
    max_level = max((c.get('level', 0) for c in flat_containers), default=0)
    if max_level > 0:
        score += max_level * 3
        details.append(f"Maximum nesting level: {max_level}")

    # Logic complexity
    complex_logic_count = sum(1 for c in flat_containers if c.get('logic') in ['or', 'then'])
    if complex_logic_count > 0:
        score += complex_logic_count * 2
        details.append(f"{complex_logic_count} container(s) with OR/THEN logic")

    # Determine complexity level
    if score == 0:
        complexity = "none"
    elif score <= 5:
        complexity = "simple"
    elif score <= 15:
        complexity = "moderate"
    elif score <= 30:
        complexity = "complex"
    else:
        complexity = "very complex"

    return {
        "complexity": complexity,
        "score": score,
        "details": "; ".join(details),
        "max_nesting_level": max_level,
        "total_containers": container_count,
        "total_conditions": total_conditions
    }


def validate_sql_query(query: str) -> Tuple[bool, str]:
    """
    Validate SQL query for basic safety
    """
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


def optimize_query(query: str) -> str:
    """
    Apply basic query optimizations
    """
    # Remove extra whitespace
    optimized = ' '.join(query.split())

    # Add LIMIT if not present (for safety)
    if 'limit' not in optimized.lower():
        optimized += ' LIMIT 10000'

    return optimized


def convert_to_query_builder_format(segment_definition: Dict) -> Dict:
    """
    Convert segment definition to query builder format with nested support
    """
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


def export_segment_json(segment_definition: Dict, filename: str = None) -> str:
    """
    Export segment definition to JSON format
    """
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        segment_name = segment_definition.get('name', 'segment').lower().replace(' ', '_')
        filename = f"{segment_name}_{timestamp}.json"

    # Add metadata
    export_data = {
        **segment_definition,
        'exported_at': datetime.now().isoformat(),
        'exported_by': 'segment_builder',
        'version': '2.0'
    }

    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
    return json_str


def import_segment_json(json_str: str) -> Dict:
    """
    Import segment definition from JSON string
    """
    try:
        data = json.loads(json_str)

        # Validate required fields
        if 'name' not in data:
            raise ValueError("Segment must have a name")

        if 'containers' not in data:
            data['containers'] = []

        # Ensure all containers have required fields
        def validate_container(container):
            if 'id' not in container:
                container['id'] = str(uuid.uuid4())
            if 'type' not in container:
                container['type'] = 'hit'
            if 'include' not in container:
                container['include'] = True
            if 'logic' not in container:
                container['logic'] = 'and'
            if 'conditions' not in container:
                container['conditions'] = []
            if 'children' not in container:
                container['children'] = []

            # Validate children recursively
            for child in container['children']:
                validate_container(child)

        for container in data['containers']:
            validate_container(container)

        return data

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error importing segment: {str(e)}")


def get_segment_statistics(segment_definition: Dict) -> Dict[str, Any]:
    """
    Get comprehensive statistics about a segment
    """
    if not segment_definition:
        return {}

    stats = {
        'basic_info': {
            'name': segment_definition.get('name', 'Unnamed'),
            'description': segment_definition.get('description', ''),
            'container_type': segment_definition.get('container_type', 'hit'),
            'logic': segment_definition.get('logic', 'and')
        },
        'structure': {},
        'complexity': {},
        'containers': []
    }

    # Get all containers
    containers = segment_definition.get('containers', [])
    flat_containers = iter_all_containers(containers)

    # Structure statistics
    stats['structure'] = {
        'total_containers': len(flat_containers),
        'root_containers': len(containers),
        'max_nesting_level': max((c.get('level', 0) for c in flat_containers), default=0),
        'total_conditions': sum(len(c.get('conditions', [])) for c in flat_containers),
        'container_types': list(set(c.get('type', 'hit') for c in flat_containers))
    }

    # Complexity analysis
    complexity_info = analyze_segment_complexity(segment_definition)
    stats['complexity'] = complexity_info

    # Container details
    for container in flat_containers:
        container_stats = {
            'id': container.get('id'),
            'type': container.get('type', 'hit'),
            'include': container.get('include', True),
            'level': container.get('level', 0),
            'conditions_count': len(container.get('conditions', [])),
            'children_count': len(container.get('children', [])),
            'logic': container.get('logic', 'and')
        }
        stats['containers'].append(container_stats)

    return stats


def render_segment_statistics(segment_definition: Dict):
    """
    Render segment statistics in Streamlit
    """
    if not segment_definition:
        st.info("No segment defined")
        return

    stats = get_segment_statistics(segment_definition)

    # Basic info
    st.subheader("Segment Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Containers", stats['structure']['total_containers'])
        st.metric("Root Containers", stats['structure']['root_containers'])
    with col2:
        st.metric("Max Nesting Level", stats['structure']['max_nesting_level'])
        st.metric("Total Conditions", stats['structure']['total_conditions'])

    # Complexity
    st.subheader("Complexity Analysis")
    complexity = stats['complexity']

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Complexity Level", complexity['complexity'].title())
    with col2:
        st.metric("Complexity Score", complexity['score'])
    with col3:
        st.metric("Nesting Levels", complexity['max_nesting_level'])

    st.write(f"**Details:** {complexity['details']}")

    # Container breakdown
    if stats['containers']:
        st.subheader("Container Breakdown")

        container_df = pd.DataFrame(stats['containers'])
        container_df['Mode'] = container_df['include'].map({True: 'Include', False: 'Exclude'})

        # Show container table
        display_df = container_df[['type', 'Mode', 'level', 'conditions_count', 'children_count', 'logic']].copy()
        display_df.columns = ['Type', 'Mode', 'Level', 'Conditions', 'Children', 'Logic']

        st.dataframe(display_df, use_container_width=True)

        # Container type distribution
        type_counts = container_df['type'].value_counts()
        if len(type_counts) > 1:
            st.bar_chart(type_counts)


def generate_segment_documentation(segment_definition: Dict) -> str:
    """
    Generate comprehensive documentation for a segment
    """
    if not segment_definition:
        return "No segment definition provided"

    doc = []

    # Header
    doc.append(f"# Segment Documentation: {segment_definition.get('name', 'Unnamed')}")
    doc.append("")

    # Basic info
    doc.append("## Basic Information")
    doc.append(f"- **Name:** {segment_definition.get('name', 'Unnamed')}")
    doc.append(f"- **Description:** {segment_definition.get('description', 'No description')}")
    doc.append(f"- **Container Type:** {segment_definition.get('container_type', 'hit').title()}")
    doc.append(f"- **Logic:** {segment_definition.get('logic', 'and').upper()}")
    doc.append("")

    # Statistics
    stats = get_segment_statistics(segment_definition)
    doc.append("## Statistics")
    doc.append(f"- **Total Containers:** {stats['structure']['total_containers']}")
    doc.append(f"- **Root Containers:** {stats['structure']['root_containers']}")
    doc.append(f"- **Maximum Nesting Level:** {stats['structure']['max_nesting_level']}")
    doc.append(f"- **Total Conditions:** {stats['structure']['total_conditions']}")
    doc.append(f"- **Complexity Level:** {stats['complexity']['complexity'].title()}")
    doc.append(f"- **Complexity Score:** {stats['complexity']['score']}")
    doc.append("")

    # Container details
    doc.append("## Container Structure")

    def document_container(container, level=0):
        indent = "  " * level
        mode = "Include" if container.get('include', True) else "Exclude"
        container_type = container.get('type', 'hit').title()
        logic = container.get('logic', 'and').upper()

        doc.append(f"{indent}- **{mode} {container_type} Container** (Logic: {logic})")

        # Conditions
        conditions = container.get('conditions', [])
        if conditions:
            doc.append(f"{indent}  - **Conditions:**")
            for i, condition in enumerate(conditions):
                if i > 0:
                    doc.append(f"{indent}    - *{logic}*")
                doc.append(
                    f"{indent}    - {condition.get('name', 'Unknown')} {condition.get('operator', 'equals')} '{condition.get('value', '')}'")

        # Children
        children = container.get('children', [])
        if children:
            doc.append(f"{indent}  - **Child Containers:**")
            for child in children:
                document_container(child, level + 2)

        doc.append("")

    containers = segment_definition.get('containers', [])
    for i, container in enumerate(containers):
        if i > 0:
            segment_logic = segment_definition.get('logic', 'and').upper()
            doc.append(f"*{segment_logic}*")
            doc.append("")
        document_container(container)

    # SQL Query
    doc.append("## Generated SQL Query")
    doc.append("```sql")
    doc.append(build_sql_query(segment_definition))
    doc.append("```")
    doc.append("")

    # Export info
    doc.append("## Export Information")
    doc.append(f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.append(f"- **Tool:** Adobe Analytics Segment Builder")
    doc.append(f"- **Version:** 2.0")

    return "\n".join(doc)


def create_segment_backup(segment_definition: Dict) -> str:
    """
    Create a backup of the segment definition
    """
    if not segment_definition:
        return ""

    backup_data = {
        'segment': segment_definition,
        'backup_timestamp': datetime.now().isoformat(),
        'backup_type': 'manual',
        'version': '2.0'
    }

    return json.dumps(backup_data, indent=2)


def restore_segment_from_backup(backup_json: str) -> Dict:
    """
    Restore segment from backup JSON
    """
    try:
        backup_data = json.loads(backup_json)

        if 'segment' not in backup_data:
            raise ValueError("Invalid backup format: missing segment data")

        segment = backup_data['segment']

        # Validate restored segment
        if 'name' not in segment:
            raise ValueError("Invalid segment: missing name")

        return segment

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid backup JSON: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error restoring backup: {str(e)}")


# Helper functions for container operations
def find_container_by_id(containers: List[Dict], container_id: str) -> Optional[Dict]:
    """
    Find a container by its ID in nested structure
    """
    for container in containers:
        if container.get('id') == container_id:
            return container

        # Search in children
        children = container.get('children', [])
        if children:
            found = find_container_by_id(children, container_id)
            if found:
                return found

    return None


def get_container_path(containers: List[Dict], container_id: str, current_path: List[int] = None) -> Optional[
    List[int]]:
    """
    Get the path to a container by its ID
    """
    if current_path is None:
        current_path = []

    for i, container in enumerate(containers):
        path = current_path + [i]

        if container.get('id') == container_id:
            return path

        # Search in children
        children = container.get('children', [])
        if children:
            child_path = get_container_path(children, container_id, path)
            if child_path:
                return child_path

    return None


def count_containers_by_type(containers: List[Dict]) -> Dict[str, int]:
    """
    Count containers by type across all nesting levels
    """
    counts = {'hit': 0, 'visit': 0, 'visitor': 0}

    flat_containers = iter_all_containers(containers)

    for container in flat_containers:
        container_type = container.get('type', 'hit')
        if container_type in counts:
            counts[container_type] += 1

    return counts


def get_max_nesting_depth(containers: List[Dict]) -> int:
    """
    Get maximum nesting depth of containers
    """
    if not containers:
        return 0

    max_depth = 0

    def get_depth(container_list, current_depth=0):
        nonlocal max_depth
        max_depth = max(max_depth, current_depth)

        for container in container_list:
            children = container.get('children', [])
            if children:
                get_depth(children, current_depth + 1)

    get_depth(containers)
    return max_depth


def render_query_builder(segment_definition: Dict):
    """
    Render the query builder interface for segment preview
    """
    if not segment_definition:
        st.info("No segment defined. Please create a segment first.")
        return

    st.subheader("Query Builder")

    # Show segment summary
    col1, col2, col3 = st.columns(3)

    with col1:
        containers = segment_definition.get('containers', [])
        flat_containers = iter_all_containers(containers)
        st.metric("Total Containers", len(flat_containers))

    with col2:
        total_conditions = sum(len(c.get('conditions', [])) for c in flat_containers)
        st.metric("Total Conditions", total_conditions)

    with col3:
        max_depth = get_max_nesting_depth(containers)
        st.metric("Max Nesting Level", max_depth)

    # Query preview and execution
    render_query_preview(segment_definition)


def build_sql_from_segment(segment_definition: Dict) -> str:
    """
    Build SQL from segment definition (alias for build_sql_query for backward compatibility)
    """
    return build_sql_query(segment_definition)