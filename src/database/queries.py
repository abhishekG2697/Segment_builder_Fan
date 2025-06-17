import sqlite3
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    db_path = Path("data/analytics.db")
    return sqlite3.connect(str(db_path))

def save_segment(segment_definition):
    """Save a segment to the database"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if segments table exists, create if not
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS segments (
            segment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            definition TEXT NOT NULL,
            container_type TEXT,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            usage_count INTEGER DEFAULT 0,
            tags TEXT
        )
        """)
        
        # Convert definition to JSON string
        definition_json = json.dumps(segment_definition)
        
        # Check if segment with this name exists
        cursor.execute("SELECT segment_id FROM segments WHERE name = ?", (segment_definition.get('name', ''),))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing segment
            cursor.execute("""
            UPDATE segments 
            SET description = ?, definition = ?, container_type = ?, 
                modified_date = CURRENT_TIMESTAMP
            WHERE name = ?
            """, (
                segment_definition.get('description', ''),
                definition_json,
                segment_definition.get('container_type', 'hit'),
                segment_definition.get('name', '')
            ))
        else:
            # Insert new segment
            cursor.execute("""
            INSERT INTO segments (name, description, definition, container_type, created_by, tags)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                segment_definition.get('name', 'Unnamed Segment'),
                segment_definition.get('description', ''),
                definition_json,
                segment_definition.get('container_type', 'hit'),
                segment_definition.get('created_by', 'User'),
                json.dumps(segment_definition.get('tags', []))
            ))
        
        conn.commit()
        return True, "Segment saved successfully"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def load_saved_segments():
    """Load all saved segments from database"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if segments table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='segments'")
        if not cursor.fetchone():
            return []
        
        query = """
        SELECT segment_id, name, description, definition, container_type, 
               created_date, modified_date, created_by, usage_count, tags
        FROM segments
        ORDER BY modified_date DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        segments = []
        for row in rows:
            try:
                segment = {
                    'segment_id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'definition': json.loads(row[3]) if row[3] else {},
                    'container_type': row[4],
                    'created_date': row[5],
                    'modified_date': row[6],
                    'created_by': row[7],
                    'usage_count': row[8],
                    'tags': json.loads(row[9]) if row[9] else []
                }
                segments.append(segment)
            except Exception as e:
                print(f"Error parsing segment {row[1]}: {str(e)}")
                continue
        
        return segments
    except Exception as e:
        print(f"Error loading segments: {str(e)}")
        return []
    finally:
        conn.close()

def execute_segment_query(sql_query, limit=10000):
    """Execute a segment query and return results as DataFrame"""
    conn = get_db_connection()
    try:
        # Add limit if not present
        if 'limit' not in sql_query.lower():
            sql_query = f"{sql_query} LIMIT {limit}"
        
        df = pd.read_sql_query(sql_query, conn)
        return df
    except Exception as e:
        raise Exception(f"Query execution failed: {str(e)}")
    finally:
        conn.close()

def get_segment_statistics(segment_definition):
    """Get statistics for a segment definition"""
    from src.utils.query_builder import build_sql_from_segment
    
    try:
        # If no containers, return default stats
        if not segment_definition.get('containers'):
            conn = get_db_connection()
            # Get total counts
            total_hits = pd.read_sql_query("SELECT COUNT(*) as count FROM hits", conn).iloc[0]['count']
            total_sessions = pd.read_sql_query("SELECT COUNT(DISTINCT session_id) as count FROM hits", conn).iloc[0]['count']
            total_visitors = pd.read_sql_query("SELECT COUNT(DISTINCT user_id) as count FROM hits", conn).iloc[0]['count']
            conn.close()
            
            return {
                'hits': 0,
                'sessions': 0,
                'visitors': 0,
                'total_hits': total_hits,
                'total_sessions': total_sessions,
                'total_visitors': total_visitors
            }
        
        # Build SQL query
        sql_query = build_sql_from_segment(segment_definition)
        
        # Get counts at different levels
        conn = get_db_connection()
        
        stats = {}
        
        # Get total counts first
        total_hits = pd.read_sql_query("SELECT COUNT(*) as count FROM hits", conn).iloc[0]['count']
        total_sessions = pd.read_sql_query("SELECT COUNT(DISTINCT session_id) as count FROM hits", conn).iloc[0]['count']
        total_visitors = pd.read_sql_query("SELECT COUNT(DISTINCT user_id) as count FROM hits", conn).iloc[0]['count']
        
        # Hit level count
        hit_query = f"""
        SELECT COUNT(*) as hit_count
        FROM ({sql_query}) as segment_data
        """
        stats['hits'] = pd.read_sql_query(hit_query, conn).iloc[0]['hit_count']
        
        # Session level count
        session_query = f"""
        SELECT COUNT(DISTINCT session_id) as session_count
        FROM ({sql_query}) as segment_data
        """
        stats['sessions'] = pd.read_sql_query(session_query, conn).iloc[0]['session_count']
        
        # Visitor level count
        visitor_query = f"""
        SELECT COUNT(DISTINCT user_id) as visitor_count
        FROM ({sql_query}) as segment_data
        """
        stats['visitors'] = pd.read_sql_query(visitor_query, conn).iloc[0]['visitor_count']
        
        # Add totals
        stats['total_hits'] = total_hits
        stats['total_sessions'] = total_sessions
        stats['total_visitors'] = total_visitors
        
        conn.close()
        return stats
        
    except Exception as e:
        print(f"Error getting segment statistics: {str(e)}")
        return {
            'hits': 0,
            'sessions': 0,
            'visitors': 0,
            'total_hits': 100000,
            'total_sessions': 50000,
            'total_visitors': 10000,
            'error': str(e)
        }

def get_available_values(field_name, limit=100):
    """Get available values for a given field"""
    conn = get_db_connection()
    try:
        # Determine which table contains the field
        if field_name in ['user_id', 'user_type']:
            table = 'users'
        elif field_name in ['session_id']:
            table = 'sessions'
        else:
            table = 'hits'
        
        query = f"""
        SELECT DISTINCT {field_name} as value, COUNT(*) as count
        FROM {table}
        WHERE {field_name} IS NOT NULL
        GROUP BY {field_name}
        ORDER BY count DESC
        LIMIT {limit}
        """
        
        df = pd.read_sql_query(query, conn)
        return df['value'].tolist()
    except Exception as e:
        return []
    finally:
        conn.close()

def get_field_statistics(field_name):
    """Get statistics for a numeric field"""
    conn = get_db_connection()
    try:
        # Determine table
        if field_name in ['total_revenue', 'total_orders', 'avg_session_duration']:
            table = 'users'
        elif field_name in ['session_duration', 'pages_viewed']:
            table = 'sessions'
        else:
            table = 'hits'
        
        query = f"""
        SELECT 
            MIN({field_name}) as min_value,
            MAX({field_name}) as max_value,
            AVG({field_name}) as avg_value,
            COUNT(*) as count
        FROM {table}
        WHERE {field_name} IS NOT NULL
        """
        
        df = pd.read_sql_query(query, conn)
        return df.iloc[0].to_dict()
    except Exception as e:
        return {}
    finally:
        conn.close()

def validate_segment_sql(sql_query):
    """Validate a segment SQL query"""
    conn = get_db_connection()
    try:
        # Try to execute with LIMIT 1 to validate syntax
        test_query = f"{sql_query} LIMIT 1"
        cursor = conn.cursor()
        cursor.execute(test_query)
        return True, "Query is valid"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()