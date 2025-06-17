"""
API endpoint for saving segments to database
Place this file in the project root or src/api/
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
import streamlit as st

def save_segment_to_db(segment_data):
    """Save segment to the segments table in database"""
    try:
        # Database path
        db_path = Path("data/analytics.db")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create segments table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS segments (
            segment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            definition TEXT NOT NULL,
            sql_query TEXT,
            container_type TEXT,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT DEFAULT 'User',
            usage_count INTEGER DEFAULT 0,
            tags TEXT
        )
        """)
        
        # Generate SQL from segment definition
        from src.utils.query_builder import build_sql_from_segment
        sql_query = build_sql_from_segment(segment_data)
        
        # Prepare data for insertion
        name = segment_data.get('name')
        description = segment_data.get('description', '')
        definition = json.dumps(segment_data)
        container_type = segment_data.get('container_type', 'hit')
        tags = json.dumps(segment_data.get('tags', []))
        
        # Check if segment with same name exists
        cursor.execute("SELECT segment_id FROM segments WHERE name = ?", (name,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing segment
            cursor.execute("""
                UPDATE segments 
                SET description = ?, 
                    definition = ?, 
                    sql_query = ?,
                    container_type = ?,
                    modified_date = CURRENT_TIMESTAMP,
                    tags = ?
                WHERE name = ?
            """, (description, definition, sql_query, container_type, tags, name))
        else:
            # Insert new segment
            cursor.execute("""
                INSERT INTO segments 
                (name, description, definition, sql_query, container_type, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, description, definition, sql_query, container_type, tags))
        
        conn.commit()
        conn.close()
        
        return True, "Segment saved successfully"
        
    except Exception as e:
        return False, f"Error saving segment: {str(e)}"

def load_all_segments():
    """Load all segments from database"""
    try:
        db_path = Path("data/analytics.db")
        if not db_path.exists():
            return []
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if segments table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='segments'
        """)
        if not cursor.fetchone():
            conn.close()
            return []
        
        # Load all segments
        cursor.execute("""
            SELECT name, description, definition, container_type, 
                   created_date, created_by, usage_count, tags
            FROM segments
            ORDER BY created_date DESC
        """)
        
        segments = []
        for row in cursor.fetchall():
            segment = {
                'name': row[0],
                'description': row[1],
                'container_type': row[3],
                'created_date': row[4],
                'created_by': row[5],
                'usage_count': row[6],
                'tags': json.loads(row[7]) if row[7] else []
            }
            
            # Parse definition
            if row[2]:
                try:
                    segment['definition'] = json.loads(row[2])
                except:
                    segment['definition'] = {}
            
            segments.append(segment)
        
        conn.close()
        return segments
        
    except Exception as e:
        st.error(f"Error loading segments: {str(e)}")
        return []