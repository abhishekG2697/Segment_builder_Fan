"""
Complete FastAPI Backend for Modern Segment Builder
Works with existing SQLite database (502K+ records)
Provides REST API endpoints for the React frontend
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
import pandas as pd

app = FastAPI(
    title="Adobe Analytics Segment Builder API",
    description="Modern API for building and managing segments with existing database",
    version="2.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class Condition(BaseModel):
    id: str
    field: str
    name: str
    type: str  # 'dimension' or 'metric'
    operator: str
    value: Any
    dataType: str  # 'string' or 'number'


class Container(BaseModel):
    id: str
    type: str  # 'hit', 'visit', 'visitor'
    include: bool
    conditions: List[Condition]
    logic: str  # 'and' or 'or'
    children: Optional[List['Container']] = []


class SegmentDefinition(BaseModel):
    name: str
    description: Optional[str] = ""
    container_type: str = "hit"
    logic: str = "and"
    containers: List[Container]
    tags: Optional[List[str]] = []


class SaveSegmentRequest(BaseModel):
    segment: SegmentDefinition


class SegmentResponse(BaseModel):
    segment_id: str
    name: str
    description: str
    definition: Dict[str, Any]
    container_type: str
    created_date: str
    modified_date: str
    created_by: str
    usage_count: int
    tags: List[str]


class PreviewResponse(BaseModel):
    estimated_count: int
    sample_data: List[Dict[str, Any]]
    sql_query: str
    statistics: Optional[Dict[str, Any]] = None


# Database connection
def get_db_connection():
    """Get database connection to existing SQLite database"""
    db_path = Path("data/analytics.db")
    if not db_path.exists():
        raise HTTPException(status_code=500, detail="Database not found at data/analytics.db")
    return sqlite3.connect(str(db_path))


def initialize_segments_table():
    """Initialize segments table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS segments
                   (
                       segment_id
                       TEXT
                       PRIMARY
                       KEY,
                       name
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       description
                       TEXT,
                       definition
                       TEXT
                       NOT
                       NULL,
                       sql_query
                       TEXT,
                       container_type
                       TEXT,
                       created_date
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       modified_date
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       created_by
                       TEXT
                       DEFAULT
                       'User',
                       usage_count
                       INTEGER
                       DEFAULT
                       0,
                       tags
                       TEXT
                   )
                   """)

    conn.commit()
    conn.close()


# Configuration data based on actual database schema
@app.get("/api/config")
async def get_config():
    """Get dimensions, metrics, and segments configuration based on actual database schema"""

    # Real dimensions based on your actual database schema
    dimensions = [
        {"name": "Page URL", "field": "page_url", "category": "Page", "type": "dimension", "dataType": "string"},
        {"name": "Page Title", "field": "page_title", "category": "Page", "type": "dimension", "dataType": "string"},
        {"name": "Page Type", "field": "page_type", "category": "Page", "type": "dimension", "dataType": "string"},
        {"name": "Device Type", "field": "device_type", "category": "Technology", "type": "dimension",
         "dataType": "string",
         "values": ["Desktop", "Mobile", "Tablet"]},
        {"name": "Browser Name", "field": "browser_name", "category": "Technology", "type": "dimension",
         "dataType": "string",
         "values": ["Chrome", "Firefox", "Safari", "Edge", "Other"]},
        {"name": "Browser Version", "field": "browser_version", "category": "Technology", "type": "dimension",
         "dataType": "string"},
        {"name": "Country", "field": "country", "category": "Geography", "type": "dimension", "dataType": "string"},
        {"name": "City", "field": "city", "category": "Geography", "type": "dimension", "dataType": "string"},
        {"name": "Traffic Source", "field": "traffic_source", "category": "Marketing", "type": "dimension",
         "dataType": "string"},
        {"name": "Traffic Medium", "field": "traffic_medium", "category": "Marketing", "type": "dimension",
         "dataType": "string"},
        {"name": "Campaign", "field": "campaign", "category": "Marketing", "type": "dimension", "dataType": "string"},
    ]

    # Real metrics based on your actual database schema
    metrics = [
        {"name": "Revenue", "field": "revenue", "category": "Commerce", "type": "metric", "dataType": "number"},
        {"name": "Products Viewed", "field": "products_viewed", "category": "Commerce", "type": "metric",
         "dataType": "number"},
        {"name": "Cart Additions", "field": "cart_additions", "category": "Commerce", "type": "metric",
         "dataType": "number"},
        {"name": "Time on Page", "field": "time_on_page", "category": "Engagement", "type": "metric",
         "dataType": "number"},
        {"name": "Bounce", "field": "bounce", "category": "Engagement", "type": "metric", "dataType": "number"},
        {"name": "Page Views", "field": "COUNT(*)", "category": "Traffic", "type": "metric", "dataType": "number"},
        {"name": "Unique Visitors", "field": "COUNT(DISTINCT user_id)", "category": "Traffic", "type": "metric",
         "dataType": "number"},
        {"name": "Sessions", "field": "COUNT(DISTINCT session_id)", "category": "Traffic", "type": "metric",
         "dataType": "number"},
    ]

    # Get saved segments from database
    saved_segments = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if segments table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='segments'")
        if cursor.fetchone():
            cursor.execute("""
                           SELECT segment_id, name, description, container_type, tags
                           FROM segments
                           ORDER BY modified_date DESC LIMIT 20
                           """)

            for row in cursor.fetchall():
                saved_segments.append({
                    "segment_id": row[0],
                    "name": row[1],
                    "description": row[2] or "",
                    "container_type": row[3] or "hit",
                    "tags": json.loads(row[4]) if row[4] else []
                })

        conn.close()
    except Exception as e:
        print(f"Error loading saved segments: {e}")

    return {
        "dimensions": [
            {"category": "Page", "items": [d for d in dimensions if d["category"] == "Page"]},
            {"category": "Technology", "items": [d for d in dimensions if d["category"] == "Technology"]},
            {"category": "Geography", "items": [d for d in dimensions if d["category"] == "Geography"]},
            {"category": "Marketing", "items": [d for d in dimensions if d["category"] == "Marketing"]}
        ],
        "metrics": [
            {"category": "Commerce", "items": [m for m in metrics if m["category"] == "Commerce"]},
            {"category": "Engagement", "items": [m for m in metrics if m["category"] == "Engagement"]},
            {"category": "Traffic", "items": [m for m in metrics if m["category"] == "Traffic"]}
        ],
        "segments": saved_segments
    }


@app.post("/api/segments/save")
async def save_segment(request: SaveSegmentRequest) -> Dict[str, Any]:
    """Save a segment to the database"""
    try:
        initialize_segments_table()

        segment = request.segment
        segment_id = str(uuid.uuid4())

        # Convert segment to SQL
        sql_query = build_sql_from_segment(segment.dict())

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if segment with same name exists
        cursor.execute("SELECT segment_id FROM segments WHERE name = ?", (segment.name,))
        existing = cursor.fetchone()

        if existing:
            # Update existing segment
            cursor.execute("""
                           UPDATE segments
                           SET description    = ?,
                               definition     = ?,
                               sql_query      = ?,
                               container_type = ?,
                               modified_date  = CURRENT_TIMESTAMP,
                               tags           = ?
                           WHERE name = ?
                           """, (
                               segment.description,
                               json.dumps(segment.dict()),
                               sql_query,
                               segment.container_type,
                               json.dumps(segment.tags),
                               segment.name
                           ))
            segment_id = existing[0]
        else:
            # Insert new segment
            cursor.execute("""
                           INSERT INTO segments
                           (segment_id, name, description, definition, sql_query, container_type, tags)
                           VALUES (?, ?, ?, ?, ?, ?, ?)
                           """, (
                               segment_id,
                               segment.name,
                               segment.description,
                               json.dumps(segment.dict()),
                               sql_query,
                               segment.container_type,
                               json.dumps(segment.tags)
                           ))

        conn.commit()
        conn.close()

        return {"success": True, "segment_id": segment_id, "message": "Segment saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving segment: {str(e)}")


@app.get("/api/segments", response_model=List[SegmentResponse])
async def get_segments():
    """Get all saved segments"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if segments table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='segments'")
        if not cursor.fetchone():
            conn.close()
            return []

        cursor.execute("""
                       SELECT segment_id,
                              name,
                              description,
                              definition,
                              container_type,
                              created_date,
                              modified_date,
                              created_by,
                              usage_count,
                              tags
                       FROM segments
                       ORDER BY modified_date DESC
                       """)

        segments = []
        for row in cursor.fetchall():
            segments.append(SegmentResponse(
                segment_id=row[0],
                name=row[1],
                description=row[2] or "",
                definition=json.loads(row[3]) if row[3] else {},
                container_type=row[4] or "hit",
                created_date=row[5] or "",
                modified_date=row[6] or "",
                created_by=row[7] or "User",
                usage_count=row[8] or 0,
                tags=json.loads(row[9]) if row[9] else []
            ))

        conn.close()
        return segments

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading segments: {str(e)}")


@app.get("/api/segments/{segment_id}")
async def get_segment(segment_id: str) -> SegmentResponse:
    """Get a specific segment by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT segment_id,
                              name,
                              description,
                              definition,
                              container_type,
                              created_date,
                              modified_date,
                              created_by,
                              usage_count,
                              tags
                       FROM segments
                       WHERE segment_id = ?
                       """, (segment_id,))

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Segment not found")

        conn.close()

        return SegmentResponse(
            segment_id=row[0],
            name=row[1],
            description=row[2] or "",
            definition=json.loads(row[3]) if row[3] else {},
            container_type=row[4] or "hit",
            created_date=row[5] or "",
            modified_date=row[6] or "",
            created_by=row[7] or "User",
            usage_count=row[8] or 0,
            tags=json.loads(row[9]) if row[9] else []
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading segment: {str(e)}")


@app.delete("/api/segments/{segment_id}")
async def delete_segment(segment_id: str):
    """Delete a segment"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM segments WHERE segment_id = ?", (segment_id,))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Segment not found")

        conn.commit()
        conn.close()

        return {"success": True, "message": "Segment deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting segment: {str(e)}")


@app.post("/api/segments/preview")
async def preview_segment(request: SaveSegmentRequest) -> PreviewResponse:
    """Preview a segment and get estimated results using actual database"""
    try:
        segment = request.segment

        # Build SQL query
        sql_query = build_sql_from_segment(segment.dict())

        # Execute preview query with limit
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get count estimate (limit to prevent long queries)
        count_query = f"SELECT COUNT(*) FROM ({sql_query} LIMIT 10000) as segment_result"
        cursor.execute(count_query)
        estimated_count = cursor.fetchone()[0]

        # Get sample data with relevant fields from actual schema
        sample_query = f"{sql_query} LIMIT 100"
        cursor.execute(sample_query)

        columns = [description[0] for description in cursor.description]
        sample_data = []
        for row in cursor.fetchall():
            sample_data.append(dict(zip(columns, row)))

        # Get some statistics about the segment
        stats_query = f"""
        SELECT 
            COUNT(DISTINCT user_id) as unique_users,
            COUNT(DISTINCT session_id) as unique_sessions,
            COUNT(*) as total_hits,
            SUM(revenue) as total_revenue,
            AVG(revenue) as avg_revenue,
            COUNT(DISTINCT device_type) as device_types,
            COUNT(DISTINCT browser_name) as browsers
        FROM ({sql_query} LIMIT 10000) as segment_result
        """

        cursor.execute(stats_query)
        stats_row = cursor.fetchone()

        statistics = {
            "unique_users": stats_row[0] if stats_row[0] else 0,
            "unique_sessions": stats_row[1] if stats_row[1] else 0,
            "total_hits": stats_row[2] if stats_row[2] else 0,
            "total_revenue": float(stats_row[3]) if stats_row[3] else 0.0,
            "avg_revenue": float(stats_row[4]) if stats_row[4] else 0.0,
            "device_types": stats_row[5] if stats_row[5] else 0,
            "browsers": stats_row[6] if stats_row[6] else 0
        }

        conn.close()

        return PreviewResponse(
            estimated_count=estimated_count,
            sample_data=sample_data,
            sql_query=sql_query,
            statistics=statistics
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error previewing segment: {str(e)}")


@app.get("/api/database/stats")
async def get_database_stats():
    """Get database statistics for the UI"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get total counts
        cursor.execute("SELECT COUNT(*) FROM hits")
        total_hits = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM hits")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM hits")
        total_sessions = cursor.fetchone()[0]

        # Get device type breakdown
        cursor.execute("""
                       SELECT device_type, COUNT(*) as count
                       FROM hits
                       GROUP BY device_type
                       ORDER BY count DESC
                       """)
        device_breakdown = [{"device_type": row[0], "count": row[1]} for row in cursor.fetchall()]

        # Get browser breakdown
        cursor.execute("""
                       SELECT browser_name, COUNT(*) as count
                       FROM hits
                       GROUP BY browser_name
                       ORDER BY count DESC
                           LIMIT 10
                       """)
        browser_breakdown = [{"browser_name": row[0], "count": row[1]} for row in cursor.fetchall()]

        # Get top countries
        cursor.execute("""
                       SELECT country, COUNT(*) as count
                       FROM hits
                       WHERE country IS NOT NULL AND country != ''
                       GROUP BY country
                       ORDER BY count DESC
                           LIMIT 10
                       """)
        country_breakdown = [{"country": row[0], "count": row[1]} for row in cursor.fetchall()]

        # Get revenue statistics
        cursor.execute("""
                       SELECT SUM(revenue)                            as total_revenue,
                              AVG(revenue)                            as avg_revenue,
                              COUNT(CASE WHEN revenue > 0 THEN 1 END) as revenue_hits
                       FROM hits
                       """)
        revenue_row = cursor.fetchone()
        revenue_stats = {
            "total_revenue": float(revenue_row[0]) if revenue_row[0] else 0.0,
            "avg_revenue": float(revenue_row[1]) if revenue_row[1] else 0.0,
            "revenue_hits": revenue_row[2] if revenue_row[2] else 0
        }

        conn.close()

        return {
            "total_hits": total_hits,
            "total_users": total_users,
            "total_sessions": total_sessions,
            "device_breakdown": device_breakdown,
            "browser_breakdown": browser_breakdown,
            "country_breakdown": country_breakdown,
            "revenue_stats": revenue_stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting database stats: {str(e)}")


@app.get("/api/fields/{field_name}/values")
async def get_field_values(field_name: str, limit: int = 50):
    """Get unique values for a specific field"""
    try:
        # Validate field name to prevent SQL injection
        valid_fields = [
            'device_type', 'browser_name', 'country', 'city', 'page_type',
            'traffic_source', 'traffic_medium', 'campaign', 'page_url'
        ]

        if field_name not in valid_fields:
            raise HTTPException(status_code=400, detail=f"Invalid field name: {field_name}")

        conn = get_db_connection()
        cursor = conn.cursor()

        query = f"""
            SELECT {field_name}, COUNT(*) as count 
            FROM hits 
            WHERE {field_name} IS NOT NULL AND {field_name} != ''
            GROUP BY {field_name} 
            ORDER BY count DESC
            LIMIT ?
        """

        cursor.execute(query, (limit,))
        values = [{"value": row[0], "count": row[1]} for row in cursor.fetchall()]

        conn.close()

        return {"field": field_name, "values": values}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting field values: {str(e)}")


def build_sql_from_segment(segment_definition: Dict[str, Any]) -> str:
    """Build SQL query from segment definition using actual database schema"""
    try:
        containers = segment_definition.get('containers', [])
        if not containers:
            return "SELECT * FROM hits LIMIT 0"

        container_queries = []

        for container in containers:
            container_type = container.get('type', 'hit')
            include = container.get('include', True)
            conditions = container.get('conditions', [])
            logic = container.get('logic', 'and').upper()

            if not conditions:
                continue

            # Build conditions
            condition_clauses = []
            for condition in conditions:
                field = condition.get('field', '')
                operator = condition.get('operator', 'equals')
                value = condition.get('value', '')
                data_type = condition.get('dataType', 'string')

                if not field or value == '':
                    continue

                # Handle special metric fields (aggregations)
                if field in ['COUNT(*)', 'COUNT(DISTINCT user_id)', 'COUNT(DISTINCT session_id)']:
                    # Skip aggregations in WHERE clause, handle separately
                    continue

                # Build condition based on operator
                if operator == 'equals':
                    if data_type == 'string':
                        clause = f"{field} = '{value}'"
                    else:
                        clause = f"{field} = {value}"
                elif operator == 'does not equal':
                    if data_type == 'string':
                        clause = f"{field} != '{value}'"
                    else:
                        clause = f"{field} != {value}"
                elif operator == 'contains':
                    clause = f"{field} LIKE '%{value}%'"
                elif operator == 'does not contain':
                    clause = f"{field} NOT LIKE '%{value}%'"
                elif operator == 'starts with':
                    clause = f"{field} LIKE '{value}%'"
                elif operator == 'ends with':
                    clause = f"{field} LIKE '%{value}'"
                elif operator == 'is greater than':
                    clause = f"{field} > {value}"
                elif operator == 'is less than':
                    clause = f"{field} < {value}"
                elif operator == 'is greater than or equal to':
                    clause = f"{field} >= {value}"
                elif operator == 'is less than or equal to':
                    clause = f"{field} <= {value}"
                elif operator == 'is between':
                    # For between, expect value as "min,max"
                    if ',' in str(value):
                        min_val, max_val = str(value).split(',', 1)
                        clause = f"{field} BETWEEN {min_val.strip()} AND {max_val.strip()}"
                    else:
                        clause = f"{field} = {value}"
                elif operator == 'exists':
                    clause = f"{field} IS NOT NULL AND {field} != ''"
                elif operator == 'does not exist':
                    clause = f"({field} IS NULL OR {field} = '')"
                else:
                    # Default to equals
                    if data_type == 'string':
                        clause = f"{field} = '{value}'"
                    else:
                        clause = f"{field} = {value}"

                condition_clauses.append(clause)

            if condition_clauses:
                conditions_sql = f" {logic} ".join(condition_clauses)

                # Build container query based on type using actual database schema
                if container_type == 'hit':
                    # Hit-level query using hits table
                    if include:
                        container_query = f"SELECT DISTINCT user_id FROM hits WHERE {conditions_sql}"
                    else:
                        container_query = f"SELECT DISTINCT user_id FROM hits WHERE NOT ({conditions_sql})"
                elif container_type == 'visit':
                    # Visit-level query using sessions table joined with hits
                    if include:
                        container_query = f"""
                        SELECT DISTINCT h.user_id 
                        FROM hits h 
                        INNER JOIN sessions s ON h.session_id = s.session_id 
                        WHERE {conditions_sql}
                        """
                    else:
                        container_query = f"""
                        SELECT DISTINCT h.user_id 
                        FROM hits h 
                        INNER JOIN sessions s ON h.session_id = s.session_id 
                        WHERE NOT ({conditions_sql})
                        """
                elif container_type == 'visitor':
                    # Visitor-level query using users table joined with hits
                    if include:
                        container_query = f"""
                        SELECT DISTINCT h.user_id 
                        FROM hits h 
                        INNER JOIN users u ON h.user_id = u.user_id 
                        WHERE {conditions_sql}
                        """
                    else:
                        container_query = f"""
                        SELECT DISTINCT h.user_id 
                        FROM hits h 
                        INNER JOIN users u ON h.user_id = u.user_id 
                        WHERE NOT ({conditions_sql})
                        """
                else:
                    # Default to hit-level
                    if include:
                        container_query = f"SELECT DISTINCT user_id FROM hits WHERE {conditions_sql}"
                    else:
                        container_query = f"SELECT DISTINCT user_id FROM hits WHERE NOT ({conditions_sql})"

                container_queries.append(container_query)

        if not container_queries:
            return "SELECT * FROM hits LIMIT 0"

        # Combine container queries
        segment_logic = segment_definition.get('logic', 'and').upper()

        if len(container_queries) == 1:
            final_query = f"""
            SELECT h.hit_id, h.user_id, h.session_id, h.timestamp, h.page_url, 
                   h.device_type, h.browser_name, h.country, h.revenue,
                   h.products_viewed, h.cart_additions, h.time_on_page
            FROM hits h 
            WHERE h.user_id IN ({container_queries[0]})
            ORDER BY h.timestamp DESC
            """
        else:
            if segment_logic == 'AND':
                # Users must be in all containers
                intersect_query = " INTERSECT ".join(container_queries)
                final_query = f"""
                SELECT h.hit_id, h.user_id, h.session_id, h.timestamp, h.page_url, 
                       h.device_type, h.browser_name, h.country, h.revenue,
                       h.products_viewed, h.cart_additions, h.time_on_page
                FROM hits h 
                WHERE h.user_id IN ({intersect_query})
                ORDER BY h.timestamp DESC
                """
            else:  # OR
                # Users can be in any container
                union_query = " UNION ".join(container_queries)
                final_query = f"""
                SELECT h.hit_id, h.user_id, h.session_id, h.timestamp, h.page_url, 
                       h.device_type, h.browser_name, h.country, h.revenue,
                       h.products_viewed, h.cart_additions, h.time_on_page
                FROM hits h 
                WHERE h.user_id IN ({union_query})
                ORDER BY h.timestamp DESC
                """

        return final_query

    except Exception as e:
        print(f"Error building SQL: {e}")
        return "SELECT * FROM hits LIMIT 0"


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Adobe Analytics Segment Builder API", "version": "2.0.0"}


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM hits")
        hit_count = cursor.fetchone()[0]
        conn.close()
        return {"status": "healthy", "database": "connected", "total_hits": hit_count}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    # Initialize database on startup
    try:
        initialize_segments_table()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

    print("🚀 Starting Adobe Analytics Segment Builder API...")
    print("📊 Working with existing SQLite database at data/analytics.db")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)