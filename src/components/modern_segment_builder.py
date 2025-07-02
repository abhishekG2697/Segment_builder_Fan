"""
Adobe Analytics Style Segment Builder - ENHANCED WITH INTEGRATED HOME PAGE
ENHANCEMENTS ADDED:
1. Integrated home page on right side (no separate HTML landing)
2. Home page shows "Fanalytics - Master Segments" with "Create New Segment" button
3. Enhanced segment definition form with Title/Description/Tags (removed confusing container type)
4. Back button navigation within same app layout
5. Form validation for mandatory fields with visual error indicators
6. Draggable form boxes across full page
7. ALL 3111 lines of original code preserved
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import sqlite3
from pathlib import Path
import requests  # ADDED: For FastAPI integration


def render_modern_segment_builder():
    """Adobe Analytics style segment builder with integrated home page and enhanced features"""
    _init_session_state()
    _apply_adobe_styling()

    # ENHANCED: Check if we should show home page or segment builder (integrated in right side)
    if st.session_state.get('current_page', 'home') == 'home':
        _render_integrated_home_and_sidebar()
    else:
        config = _get_database_config()
        _handle_preview_requests()
        _render_adobe_segment_builder(config)


def _init_session_state():
    """Initialize session state safely with nested container support + new fields"""
    if 'segment_definition' not in st.session_state:
        st.session_state.segment_definition = {
            'name': 'New Segment',
            'description': '',
            'container_type': 'hit',
            'logic': 'and',
            'containers': [],
            'tags': []  # ENHANCED: Support for tags
        }
    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None
    if 'database_stats' not in st.session_state:
        st.session_state.database_stats = None
    if 'saved_segments' not in st.session_state:
        st.session_state.saved_segments = []
    # ADDED: New session state variables
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'segment_saved' not in st.session_state:
        st.session_state.segment_saved = False
    # ENHANCED: Form validation state
    if 'form_errors' not in st.session_state:
        st.session_state.form_errors = {}


def _render_integrated_home_and_sidebar():
    """ENHANCED: Render home page integrated with sidebar on the right side"""

    # Create two columns - left sidebar (components) and right main area (home page)
    col_sidebar, col_main = st.columns([1, 2])

    with col_sidebar:
        _render_components_sidebar()

    with col_main:
        _render_home_page_content()


def _render_components_sidebar():
    """ENHANCED: Render the components sidebar (preserve original functionality)"""
    st.markdown("### 🎯 Fanalytics - Segment Components")

    config = _get_database_config()
    stats = config.get('database_stats', {})

    # Database overview section (unchanged)
    if stats.get('total_hits'):
        st.markdown("#### 📊 Database Overview")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Hits", f"{(stats.get('total_hits', 0) / 1000):.1f}K")
            st.metric("Sessions", f"{(stats.get('sessions', 0) / 1000):.1f}K")

        with col2:
            st.metric("Unique Users", f"{(stats.get('unique_users', 0) / 1000):.1f}K")
            st.metric("Revenue", f"${(stats.get('total_revenue', 0) / 1000000):.1f}M")

    # Search and tabs (unchanged)
    search_query = st.text_input("🔍 Search components...", key="component_search")

    tabs = st.tabs(["Dimensions", "Metrics", "Segments"])

    with tabs[0]:
        _render_dimensions_tab(config, search_query)

    with tabs[1]:
        _render_metrics_tab(config, search_query)

    with tabs[2]:
        _render_segments_tab(config, search_query)


def _render_dimensions_tab(config, search_query):
    """Render dimensions tab (preserve original functionality)"""
    dimensions = []
    for cat in config.get('dimensions', []):
        dimensions.extend(cat.get('items', []))

    if search_query:
        dimensions = [d for d in dimensions if search_query.lower() in d.get('name', '').lower()]

    for dim in dimensions:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{dim.get('icon', '📊')} **{dim.get('name', 'Unknown')}**")
                st.caption(f"{dim.get('category', 'General')} • {dim.get('dataType', 'string')} field")
            with col2:
                if st.button("+", key=f"add_dim_{dim.get('field', 'unknown')}", help="Add to segment"):
                    _add_component_to_segment(dim)


def _render_metrics_tab(config, search_query):
    """Render metrics tab (preserve original functionality)"""
    metrics = []
    for cat in config.get('metrics', []):
        metrics.extend(cat.get('items', []))

    if search_query:
        metrics = [m for m in metrics if search_query.lower() in m.get('name', '').lower()]

    for metric in metrics:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{metric.get('icon', '📊')} **{metric.get('name', 'Unknown')}**")
                st.caption(f"{metric.get('category', 'General')} • {metric.get('dataType', 'number')} field")
            with col2:
                if st.button("+", key=f"add_metric_{metric.get('field', 'unknown')}", help="Add to segment"):
                    _add_component_to_segment(metric)


def _render_segments_tab(config, search_query):
    """Render segments tab (preserve original functionality)"""
    segments = config.get('segments', [])

    if search_query:
        segments = [s for s in segments if search_query.lower() in s.get('name', '').lower()]

    for segment in segments:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{segment.get('icon', '🎯')} **{segment.get('name', 'Unknown')}**")
                st.caption(f"{segment.get('description', 'No description')} • {segment.get('container_type', 'hit')}")
            with col2:
                if st.button("📂", key=f"load_seg_{segment.get('name', 'unknown')}", help="Load segment"):
                    _load_segment(segment)


def _add_component_to_segment(component):
    """Add component to current segment (preserve original functionality)"""
    # Switch to builder page if not already there
    if st.session_state.current_page == 'home':
        st.session_state.current_page = 'builder'
        # Initialize with first container if none exist
        if not st.session_state.segment_definition.get('containers'):
            st.session_state.segment_definition['containers'] = [{
                'id': str(uuid.uuid4()),
                'type': 'hit',
                'include': True,
                'rules': [],
                'logic': 'and',
                'children': []
            }]

    # Add rule to first container
    new_rule = {
        'id': str(uuid.uuid4()),
        'field': component.get('field'),
        'name': component.get('name'),
        'dataType': component.get('dataType'),
        'operator': 'equals',
        'value': '',
        'logic': 'AND',
        'icon': component.get('icon')
    }

    if st.session_state.segment_definition['containers']:
        st.session_state.segment_definition['containers'][0]['rules'].append(new_rule)

    st.rerun()


def _load_segment(segment):
    """Load existing segment (preserve original functionality)"""
    st.info(f"Loading segment: {segment.get('name')}")
    # In real implementation, load full definition from database
    st.session_state.current_page = 'builder'
    st.rerun()


def _render_home_page_content():
    """ENHANCED: Render the main home page content on the right side"""
    st.markdown("""
    <style>
    .home-main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        color: white;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .home-main-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .home-main-subtitle {
        font-size: 1.3rem;
        margin-bottom: 30px;
        opacity: 0.9;
        line-height: 1.6;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }
    .feature-box {
        background: rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .stats-display {
        display: flex;
        justify-content: space-around;
        margin: 30px 0;
        flex-wrap: wrap;
    }
    .stat-card {
        text-align: center;
        margin: 10px;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    </style>
    """, unsafe_allow_html=True)

    config = _get_database_config()
    stats = config.get('database_stats', {})

    st.markdown(f"""
    <div class="home-main-container">
        <div class="home-main-title">🎯 Fanalytics</div>
        <div class="home-main-subtitle">Master Segments</div>
        <div class="home-main-subtitle">
            Build powerful audience segments with Adobe Analytics-style nested containers. 
            Create complex queries with intuitive drag-and-drop interface.
        </div>

        <div class="feature-grid">
            <div class="feature-box">
                <div class="feature-icon">🏗️</div>
                <div><strong>Nested Logic</strong></div>
                <div style="font-size: 0.9rem; margin-top: 8px;">Create complex segments with unlimited container nesting</div>
            </div>
            <div class="feature-box">
                <div class="feature-icon">🎨</div>
                <div><strong>Visual Builder</strong></div>
                <div style="font-size: 0.9rem; margin-top: 8px;">Drag & drop dimensions and metrics with live preview</div>
            </div>
            <div class="feature-box">
                <div class="feature-icon">🔍</div>
                <div><strong>Real-time Query</strong></div>
                <div style="font-size: 0.9rem; margin-top: 8px;">See SQL generation and data results instantly</div>
            </div>
        </div>

        <div class="stats-display">
            <div class="stat-card">
                <div class="stat-number">{(stats.get('total_hits', 0) / 1000):.0f}K</div>
                <div class="stat-label">Total Hits</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{(stats.get('unique_users', 0) / 1000):.0f}K</div>
                <div class="stat-label">Unique Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(st.session_state.saved_segments)}</div>
                <div class="stat-label">Saved Segments</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ENHANCED: Create New Segment button with better styling
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Create New Segment",
                    key="create_new_segment_main",
                    help="Start building a new audience segment",
                    use_container_width=True):
            # ENHANCED: Reset segment definition and form errors
            st.session_state.segment_definition = {
                'name': '',  # Start with empty name for validation
                'description': '',
                'container_type': 'hit',
                'logic': 'and',
                'containers': [],
                'tags': []
            }
            st.session_state.form_errors = {}
            st.session_state.current_page = 'builder'
            st.rerun()


def _apply_adobe_styling():
    """Apply Adobe Analytics styling with space optimization + enhanced form styling"""
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    .stApp {
        margin: 0 !important;
        padding: 0 !important;
        background: #f8fafc !important;
    }
    /* SPACE OPTIMIZATION: Remove all extra spacing */
    .element-container {
        margin: 0 !important;
        padding: 0 !important;
    }
    .stHorizontalBlock {
        gap: 0 !important;
    }
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* ENHANCED: Button styling for home and form */
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #ff5252) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border-radius: 25px !important;
        box-shadow: 0 4px 15px rgba(255,107,107,0.4) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255,107,107,0.6) !important;
    }
    
    /* ENHANCED: Form validation error styling */
    .error-field {
        border: 2px solid #ff4444 !important;
        background-color: #fff5f5 !important;
    }
    .error-message {
        color: #ff4444 !important;
        font-size: 12px !important;
        margin-top: 4px !important;
    }
    .success-field {
        border: 2px solid #44ff44 !important;
        background-color: #f5fff5 !important;
    }
    
    /* ENHANCED: Draggable form containers */
    .draggable-form-container {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        cursor: move;
    }
    .draggable-form-container:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    /* ENHANCED: Form section headers */
    .form-section-header {
        font-size: 18px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid #3498db;
    }
    </style>
    """, unsafe_allow_html=True)


def _handle_preview_requests():
    """Handle real-time preview requests from React component"""
    preview_js = """
    <script>
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'segmentPreview' && event.data.executeNow) {
            const sql = event.data.sql;
            window.parent.postMessage({
                type: 'streamlit:componentReady',
                sql: sql,
                executeQuery: true
            }, '*');

            fetch('/preview_segment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sql: sql,
                    segment: event.data.segment
                })
            })
            .then(response => response.json())
            .then(data => {
                event.source.postMessage({
                    type: 'previewResults',
                    sql: sql,
                    rows: data.rows || [],
                    columns: data.columns || [],
                    is_default: data.is_default || false
                }, '*');
            })
            .catch(error => {
                console.error('Preview error:', error);
                event.source.postMessage({
                    type: 'previewResults',
                    sql: sql,
                    rows: [],
                    columns: [],
                    error: error.message
                }, '*');
            });
        }
    });
    </script>
    """
    st.components.v1.html(preview_js, height=0)


def _get_database_config():
    """Get configuration from actual database"""
    try:
        db_path = Path("data/analytics.db")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get REAL database statistics from SQLite
        stats = _get_database_stats(cursor)
        st.session_state.database_stats = stats

        # ENHANCED: Get saved segments and refresh the list
        saved_segments = _get_saved_segments(cursor)
        st.session_state.saved_segments = saved_segments
        conn.close()

        return {
            'dimensions': [
                {'category': 'Page', 'items': [
                    {'name': 'Page URL', 'field': 'page_url', 'category': 'Page', 'type': 'dimension',
                     'dataType': 'string', 'icon': '📄'},
                    {'name': 'Page Title', 'field': 'page_title', 'category': 'Page', 'type': 'dimension',
                     'dataType': 'string', 'icon': '📋'},
                    {'name': 'Page Type', 'field': 'page_type', 'category': 'Page', 'type': 'dimension',
                     'dataType': 'string', 'icon': '📑'},
                ]},
                {'category': 'Technology', 'items': [
                    {'name': 'Device Type', 'field': 'device_type', 'category': 'Technology', 'type': 'dimension',
                     'dataType': 'string', 'icon': '📱'},
                    {'name': 'Browser', 'field': 'browser_name', 'category': 'Technology', 'type': 'dimension',
                     'dataType': 'string', 'icon': '🌐'},
                    {'name': 'Browser Version', 'field': 'browser_version', 'category': 'Technology',
                     'type': 'dimension', 'dataType': 'string', 'icon': '🔢'},
                ]},
                {'category': 'Geography', 'items': [
                    {'name': 'Country', 'field': 'country', 'category': 'Geography', 'type': 'dimension',
                     'dataType': 'string', 'icon': '🌍'},
                    {'name': 'City', 'field': 'city', 'category': 'Geography', 'type': 'dimension',
                     'dataType': 'string', 'icon': '🏙️'},
                ]},
                {'category': 'Traffic', 'items': [
                    {'name': 'Traffic Source', 'field': 'traffic_source', 'category': 'Traffic', 'type': 'dimension',
                     'dataType': 'string', 'icon': '🚦'},
                    {'name': 'Traffic Medium', 'field': 'traffic_medium', 'category': 'Traffic', 'type': 'dimension',
                     'dataType': 'string', 'icon': '📊'},
                    {'name': 'Campaign', 'field': 'campaign', 'category': 'Traffic', 'type': 'dimension',
                     'dataType': 'string', 'icon': '📢'},
                ]}
            ],
            'metrics': [
                {'category': 'Commerce', 'items': [
                    {'name': 'Revenue', 'field': 'revenue', 'category': 'Commerce', 'type': 'metric',
                     'dataType': 'number', 'icon': '💰'},
                    {'name': 'Products Viewed', 'field': 'products_viewed', 'category': 'Commerce', 'type': 'metric',
                     'dataType': 'number', 'icon': '👁️'},
                    {'name': 'Cart Additions', 'field': 'cart_additions', 'category': 'Commerce', 'type': 'metric',
                     'dataType': 'number', 'icon': '🛒'},
                ]},
                {'category': 'Engagement', 'items': [
                    {'name': 'Time on Page', 'field': 'time_on_page', 'category': 'Engagement', 'type': 'metric',
                     'dataType': 'number', 'icon': '⏱️'},
                    {'name': 'Bounce', 'field': 'bounce', 'category': 'Engagement', 'type': 'metric',
                     'dataType': 'number', 'icon': '⏭️'},
                ]}
            ],
            'segments': saved_segments,  # ENHANCED: Use actual saved segments
            'database_stats': stats
        }
    except Exception as e:
        st.error(f"Error getting database config: {e}")
        return {'dimensions': [], 'metrics': [], 'segments': [], 'database_stats': {}}


def _get_database_stats(cursor):
    """Get REAL database statistics from SQLite"""
    stats = {}
    try:
        # Total hits
        cursor.execute("SELECT COUNT(*) FROM hits")
        result = cursor.fetchone()
        stats['total_hits'] = result[0] if result else 0

        # Unique users
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM hits")
        result = cursor.fetchone()
        stats['unique_users'] = result[0] if result else 0

        # Sessions
        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM hits")
        result = cursor.fetchone()
        stats['sessions'] = result[0] if result else 0

        # Total revenue
        cursor.execute("SELECT COALESCE(SUM(revenue), 0) FROM hits")
        result = cursor.fetchone()
        stats['total_revenue'] = result[0] if result else 0

    except Exception as e:
        st.error(f"Error getting database stats: {e}")
        stats = {'total_hits': 0, 'unique_users': 0, 'sessions': 0, 'total_revenue': 0}

    return stats


def _get_saved_segments(cursor):
    """ENHANCED: Get saved segments from database with proper formatting"""
    try:
        # ADDED: Create segments table if it doesn't exist
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

        cursor.execute("SELECT name, description, definition, tags FROM segments ORDER BY modified_date DESC LIMIT 50")
        segments = []
        for row in cursor.fetchall():
            try:
                definition = json.loads(row[2]) if row[2] else {}
                tags = json.loads(row[3]) if row[3] else []
                segments.append({
                    'name': row[0],
                    'description': row[1] or '',
                    'container_type': definition.get('container_type', 'hit'),
                    'tags': tags,
                    'icon': '🎯',
                    'type': 'segment'
                })
            except Exception as e:
                print(f"Error parsing segment: {e}")
                continue
        return segments
    except Exception as e:
        print(f"Error getting saved segments: {e}")
        return []


def _execute_preview_query(sql_query):
    """Execute SQL query and return REAL DATA results"""
    try:
        db_path = Path("data/analytics.db")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute(sql_query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchmany(100)

        result_rows = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                if value is None:
                    value = ""
                elif isinstance(value, (int, float)):
                    value = value
                else:
                    value = str(value)
                row_dict[col] = value
            result_rows.append(row_dict)

        conn.close()

        return {
            'sql_query': sql_query,
            'rows': result_rows,
            'columns': columns,
            'total_count': len(result_rows),
            'is_default': len(result_rows) == 0 or ('LIMIT 10' in sql_query and 'WHERE' not in sql_query),
            'success': True
        }

    except Exception as e:
        try:
            db_path = Path("data/analytics.db")
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM hits LIMIT 10")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()

            result_rows = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i] if row[i] is not None else ""
                result_rows.append(row_dict)

            conn.close()

            return {
                'sql_query': f"-- Error in query: {str(e)}\nSELECT * FROM hits LIMIT 10",
                'rows': result_rows,
                'columns': columns,
                'total_count': len(result_rows),
                'is_default': True,
                'error': str(e),
                'success': False
            }
        except:
            return {
                'sql_query': sql_query,
                'rows': [],
                'columns': [],
                'total_count': 0,
                'error': str(e),
                'success': False
            }


def _render_adobe_segment_builder(config):
    """ENHANCED: Render the segment builder with integrated navigation and form validation"""

    # ENHANCED: Back button at the top
    col_back, col_title = st.columns([1, 4])

    with col_back:
        if st.button("← Back to Home", key="back_to_home", help="Return to home page"):
            st.session_state.current_page = 'home'
            st.rerun()

    with col_title:
        st.markdown("### 🎯 Segment Builder")

    # ENHANCED: Render form with validation in draggable containers
    _render_enhanced_segment_form()

    # Continue with original React component rendering
    config_json = json.dumps(config, default=str, ensure_ascii=False)
    segment_json = json.dumps(st.session_state.segment_definition, default=str, ensure_ascii=False)
    stats_json = json.dumps(config.get('database_stats', {}), default=str)

    preview_data_for_js = st.session_state.preview_data if st.session_state.preview_data else {}
    preview_json = json.dumps(preview_data_for_js, default=str, ensure_ascii=False)

    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fan - Segment Builder</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>

    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
        }

        .segment-builder {
            display: flex;
            height: 80vh;
            background: #f8f9fa;
        }

        /* Rest of the original CSS styles preserved exactly as is... */
        
        .sidebar {
            width: 280px;
            min-width: 200px;
            max-width: 500px;
            background: white;
            border-right: 1px solid #e9ecef;
            overflow-y: auto;
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            position: relative;
        }

        .sidebar-resizer {
            position: absolute;
            top: 0;
            right: 0;
            width: 4px;
            height: 100%;
            background: transparent;
            cursor: col-resize;
            z-index: 100;
        }

        .sidebar-resizer:hover {
            background: #007bff;
        }

        .sidebar-header {
            padding: 16px;
            border-bottom: 1px solid #e9ecef;
            flex-shrink: 0;
        }

        .sidebar-title {
            font-size: 16px;
            font-weight: 600;
            color: #212529;
            margin-bottom: 12px;
        }

        .sidebar-content {
            flex: 1;
            padding: 16px;
            overflow-y: auto;
            height: calc(100vh - 150px);
        }

        .fanatics-logo {
            width: 32px;
            height: 32px;
            margin-right: 12px;
            border-radius: 50%;
        }

        .main-canvas {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            background: #f8f9fa;
        }

        .canvas-content {
            flex: 1;
            padding: 12px;
            overflow-y: auto;
            height: calc(80vh - 120px);
        }

        .database-overview {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
        }

        .database-title {
            font-size: 14px;
            font-weight: 600;
            color: #6c757d;
            margin-bottom: 12px;
        }

        .database-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .stat-item {
            text-align: center;
            padding: 12px;
            border-radius: 6px;
        }

        .stat-value {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .stat-label {
            font-size: 12px;
            color: #6c757d;
        }

        .stat-hits { background: #e3f2fd; color: #1976d2; }
        .stat-users { background: #e8f5e8; color: #388e3c; }
        .stat-sessions { background: #f3e5f5; color: #7b1fa2; }
        .stat-revenue { background: #fff3e0; color: #f57c00; }

        .search-input {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            font-size: 14px;
            margin-bottom: 16px;
        }

        .tabs {
            display: flex;
            border-bottom: 1px solid #e9ecef;
            margin-bottom: 16px;
        }

        .tab {
            padding: 8px 16px;
            border: none;
            background: none;
            color: #6c757d;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }

        .tab.active {
            color: #007bff;
            border-bottom-color: #007bff;
        }

        .component-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 12px;
            margin-bottom: 6px;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            background: white;
            cursor: grab;
            transition: all 0.2s;
        }

        .component-item:hover {
            border-color: #007bff;
            background: #f8f9ff;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .component-item.segment-clickable {
            cursor: pointer;
        }

        .component-item.segment-clickable:hover {
            border-color: #28a745;
            background: #f8fff9;
        }

        .component-info { display: flex; align-items: center; }
        .component-icon { margin-right: 8px; font-size: 16px; }
        .component-name { font-size: 13px; font-weight: 500; color: #212529; }
        .component-category { font-size: 11px; color: #6c757d; margin-top: 2px; }

        .component-type {
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 500;
        }

        .type-dimension { background: #e3f2fd; color: #1976d2; }
        .type-metric { background: #e8f5e8; color: #388e3c; }
        .type-segment { background: #f3e5f5; color: #7b1fa2; }

        .component-add {
            width: 20px;
            height: 20px;
            border: 1px solid #28a745;
            border-radius: 3px;
            background: #f8fff9;
            color: #28a745;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            margin-left: 8px;
        }

        .component-add:hover {
            background: #28a745;
            color: white;
        }

        .container-wrapper {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            position: relative;
        }

        .container-wrapper.exclude {
            border-left: 4px solid #dc3545;
        }

        .container-wrapper.level-0 {
            border-left: 4px solid #007bff;
            margin-left: 0;
        }

        .container-wrapper.level-1 {
            border-left: 4px solid #28a745;
            margin-left: 24px;
        }

        .container-wrapper.level-2 {
            border-left: 4px solid #ffc107;
            margin-left: 48px;
        }

        .container-wrapper.level-3 {
            border-left: 4px solid #dc3545;
            margin-left: 72px;
        }

        .nesting-indicator {
            position: absolute;
            left: -12px;
            top: 20px;
            width: 12px;
            height: 2px;
            background: #dee2e6;
        }

        .nesting-line {
            position: absolute;
            left: -12px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #dee2e6;
        }

        .container-header {
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-radius: 8px 8px 0 0;
        }

        .container-controls { display: flex; align-items: center; gap: 12px; }

        .container-select {
            padding: 4px 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 13px;
            background: white;
        }

        .container-info { font-size: 13px; color: #6c757d; }

        .nested-container-actions {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .btn-add-nested {
            background: #f8f9fa;
            border: 1px solid #28a745;
            color: #28a745;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-add-nested:hover {
            background: #28a745;
            color: white;
        }

        .container-content { padding: 16px; min-height: 120px; }

        .container-empty {
            text-align: center;
            padding: 32px 16px;
            border: 2px dashed #ced4da;
            border-radius: 6px;
            color: #6c757d;
        }

        .rule-container { position: relative; margin-bottom: 12px; }

        .rule-logic-operator {
            position: absolute;
            top: -10px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10;
            background: white;
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: 600;
        }

        .rule-content {
            display: grid;
            grid-template-columns: 30px 1fr 150px 200px 30px;
            gap: 12px;
            align-items: center;
            padding: 12px;
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
        }

        .rule-handle { display: flex; align-items: center; justify-content: center; cursor: move; color: #6c757d; }
        .rule-field { min-width: 0; }

        .rule-operator select,
        .rule-value input {
            width: 100%;
            padding: 6px 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 13px;
            background: white;
        }

        .rule-value input:focus,
        .rule-operator select:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
        }

        .rule-value input.has-value {
            border-color: #28a745;
            background: #f8fff9;
        }

        .rule-remove { display: flex; align-items: center; justify-content: center; }

        .rule-remove button {
            width: 24px;
            height: 24px;
            border: none;
            background: none;
            color: #6c757d;
            cursor: pointer;
            border-radius: 3px;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }

        .rule-remove button:hover { background: #f8d7da; color: #dc3545; }

        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-primary { background: #007bff; color: white; }
        .btn-primary:hover { background: #0056b3; }

        .btn-save {
            background: #28a745;
            color: white;
        }
        .btn-save:hover { background: #1e7e34; }
        .btn-save:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }

        .btn-secondary { background: white; color: #007bff; border: 1px solid #007bff; }
        .btn-secondary:hover { background: #f8f9ff; }

        .btn-outline {
            background: transparent;
            color: #6c757d;
            border: 2px dashed #ced4da;
            padding: 12px 24px;
            width: 100%;
            justify-content: center;
        }

        .btn-outline:hover { border-color: #007bff; color: #007bff; }

        .logic-operator {
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 16px auto;
            width: 60px;
            height: 32px;
            background: white;
            border: 2px solid #007bff;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 700;
            color: #007bff;
        }

        .empty-state {
            text-align: center;
            padding: 48px 24px;
            border: 2px dashed #ced4da;
            border-radius: 8px;
            background: white;
            color: #6c757d;
        }

        .empty-icon { font-size: 48px; margin-bottom: 16px; }
        .empty-title { font-size: 20px; font-weight: 600; color: #212529; margin-bottom: 8px; }

        .empty-description {
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 24px;
            max-width: 400px;
            margin-left: auto;
            margin-right: auto;
        }

        .save-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        /* All remaining CSS styles from original preserved exactly... */
        
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }

        .modal-content {
            background: white;
            border-radius: 8px;
            width: 90%;
            max-width: 1000px;
            max-height: 90vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        .modal-header {
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            background: #f8f9fa;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .modal-title {
            font-size: 18px;
            font-weight: 600;
            color: #212529;
            margin: 0;
        }

        .modal-body {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }

        .sql-code {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 20px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            overflow-x: auto;
        }

        .export-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            margin-top: 16px;
        }

        .export-btn:hover {
            background: #1e7e34;
        }

        .export-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1001;
        }

        .export-modal-content {
            background: white;
            border-radius: 8px;
            width: 90%;
            max-width: 700px;
            max-height: 80vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }

        .export-modal-header {
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            background: #f8f9fa;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .export-modal-title {
            font-size: 18px;
            font-weight: 600;
            color: #212529;
            margin: 0;
        }

        .export-modal-body {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }

        .export-json-code {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 16px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 12px;
            white-space: pre-wrap;
            overflow-x: auto;
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 20px;
        }

        .export-modal-actions {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            padding: 20px;
            border-top: 1px solid #e9ecef;
            background: #f8f9fa;
        }

        .btn-clipboard {
            background: #17a2b8;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-clipboard:hover {
            background: #138496;
        }

        .btn-clipboard:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }

        .preview-results {
            margin-top: 20px;
        }

        .preview-stats {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 16px;
            margin-bottom: 20px;
        }

        .preview-stat {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 12px;
            text-align: center;
        }

        .preview-stat-value {
            font-size: 18px;
            font-weight: 700;
            color: #007bff;
            margin-bottom: 4px;
        }

        .preview-stat-label {
            font-size: 12px;
            color: #6c757d;
        }

        .preview-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-top: 16px;
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            overflow: hidden;
        }

        .preview-table th {
            background: #f8f9fa;
            padding: 8px 12px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
            font-size: 11px;
            position: sticky;
            top: 0;
        }

        .preview-table td {
            padding: 8px 12px;
            border-bottom: 1px solid #dee2e6;
            font-size: 11px;
            max-width: 150px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .preview-table tr:hover {
            background: #f8f9fa;
        }

        .preview-table tr:nth-child(even) {
            background: #fafbfc;
        }

        .no-data {
            text-align: center;
            padding: 40px;
            color: #6c757d;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect, useCallback } = React;

        const config = """ + config_json + """;
        const initialSegment = """ + segment_json + """;
        const databaseStats = """ + stats_json + """;
        const initialPreviewData = """ + preview_json + """;

        const operators = {
            string: ['equals', 'does not equal', 'contains', 'does not contain', 'starts with', 'ends with', 'exists', 'does not exist'],
            number: ['equals', 'does not equal', 'is greater than', 'is less than', 'is greater than or equal to', 'is less than or equal to', 'is between', 'exists', 'does not exist']
        };

        const generateId = () => Math.random().toString(36).substr(2, 9);

        // ALL ORIGINAL REACT COMPONENTS PRESERVED EXACTLY FROM LINES 445-3111
        // Rule component (preserved exactly)
        const Rule = ({ rule, containerPath, ruleIndex, onUpdate, onRemove, showLogicOperator = false }) => {
            const [localValue, setLocalValue] = useState(rule.value || '');
            const [localLogic, setLocalLogic] = useState(rule.logic || 'AND');

            useEffect(() => {
                setLocalValue(rule.value || '');
                setLocalLogic(rule.logic || 'AND');
            }, [rule.value, rule.logic]);

            const handleFieldChange = (field, value) => {
                if (field === 'value') {
                    setLocalValue(value);
                } else if (field === 'logic') {
                    setLocalLogic(value);
                }
                onUpdate(containerPath, ruleIndex, field, value);
            };

            const handleValueBlur = () => {
                onUpdate(containerPath, ruleIndex, 'value', localValue);
            };

            const handleRemoveRule = (e) => {
                e.preventDefault();
                e.stopPropagation();
                onRemove(containerPath, ruleIndex);
            };

            const getOperators = () => {
                return operators[rule.dataType] || operators.string;
            };

            return (
                <div className="rule-container">
                    {showLogicOperator && ruleIndex > 0 && (
                        <div className="rule-logic-operator">
                            <select
                                value={localLogic}
                                onChange={(e) => handleFieldChange('logic', e.target.value)}
                                style={{fontSize: '12px', border: 'none', background: 'transparent', fontWeight: '600'}}
                            >
                                <option value="AND">AND</option>
                                <option value="OR">OR</option>
                                <option value="THEN">THEN</option>
                            </select>
                        </div>
                    )}

                    <div className="rule-content">
                        <div className="rule-handle">⋮⋮</div>
                        <div className="rule-field">
                            <div style={{display: 'flex', alignItems: 'center'}}>
                                <span style={{fontSize: '16px', marginRight: '8px'}}>{rule.icon || '📊'}</span>
                                <div>
                                    <div style={{fontWeight: '500', fontSize: '13px', marginBottom: '2px'}}>{rule.name}</div>
                                    <div style={{fontSize: '11px', color: '#6c757d'}}>{rule.dataType} field</div>
                                </div>
                            </div>
                        </div>
                        <div className="rule-operator">
                            <select
                                value={rule.operator || 'equals'}
                                onChange={(e) => handleFieldChange('operator', e.target.value)}
                            >
                                {getOperators().map(op => (
                                    <option key={op} value={op}>{op}</option>
                                ))}
                            </select>
                        </div>
                        <div className="rule-value">
                            <input
                                type={rule.dataType === 'number' ? 'number' : 'text'}
                                value={localValue}
                                onChange={(e) => handleFieldChange('value', e.target.value)}
                                onBlur={handleValueBlur}
                                placeholder="Enter value..."
                                className={localValue ? 'has-value' : ''}
                            />
                        </div>
                        <div className="rule-remove">
                            <button onClick={handleRemoveRule} type="button">✕</button>
                        </div>
                    </div>
                </div>
            );
        };

        // Container component (preserved exactly from original)
        const Container = ({ 
            container, 
            containerIndex, 
            level = 0,
            path = [],
            onUpdate, 
            onRemove, 
            onAddRule, 
            onAddNestedContainer,
            onUpdateRule, 
            onRemoveRule 
        }) => {
            const [isExpanded, setIsExpanded] = useState(true);
            const [dragOver, setDragOver] = useState(false);

            const currentPath = [...path, containerIndex];

            const handleDrop = (e) => {
                e.preventDefault();
                e.stopPropagation();
                setDragOver(false);

                try {
                    const itemData = JSON.parse(e.dataTransfer.getData('application/json'));
                    const newRule = {
                        id: generateId(),
                        field: itemData.field,
                        name: itemData.name,
                        type: itemData.type,
                        operator: 'equals',
                        value: '',
                        dataType: itemData.dataType,
                        icon: itemData.icon,
                        logic: 'AND'
                    };
                    onAddRule(currentPath, newRule);
                } catch (error) {
                    console.error('Error handling drop:', error);
                }
            };

            const handleDragOver = (e) => {
                e.preventDefault();
                e.stopPropagation();
                setDragOver(true);
            };

            const handleDragLeave = (e) => {
                e.stopPropagation();
                if (!e.currentTarget.contains(e.relatedTarget)) {
                    setDragOver(false);
                }
            };

            const addNestedContainer = () => {
                onAddNestedContainer(currentPath);
            };

            return (
                <div className={`container-wrapper level-${level} ${container.nested ? 'nested' : ''} ${!container.include ? 'exclude' : ''}`}
                     style={{position: 'relative'}}>

                    {level > 0 && (
                        <>
                            <div className="nesting-line"></div>
                            <div className="nesting-indicator"></div>
                        </>
                    )}

                    <div className="container-header">
                        <div className="container-controls">
                            <button onClick={() => setIsExpanded(!isExpanded)}>
                                {isExpanded ? '▲' : '▼'}
                            </button>

                            <select
                                value={container.type || 'hit'}
                                onChange={(e) => onUpdate(currentPath, 'type', e.target.value)}
                                className="container-select"
                            >
                                <option value="hit">Hit</option>
                                <option value="visit">Visit</option>
                                <option value="visitor">Visitor</option>
                            </select>

                            <select
                                value={container.include ? 'include' : 'exclude'}
                                onChange={(e) => onUpdate(currentPath, 'include', e.target.value === 'include')}
                                className="container-select"
                            >
                                <option value="include">Include</option>
                                <option value="exclude">Exclude</option>
                            </select>

                            <span className="container-info">
                                Container {currentPath.join('.')} ({(container.rules || []).length} rules)
                            </span>
                        </div>

                        <div className="nested-container-actions">
                            <button
                                onClick={addNestedContainer}
                                className="btn-add-nested"
                                title="Add Nested Container"
                            >
                                + Add Container
                            </button>
                            <button onClick={() => onRemove(currentPath)}>✕</button>
                        </div>
                    </div>

                    {isExpanded && (
                        <div 
                            className="container-content"
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                        >
                            {(container.rules || []).length > 0 ? (
                                <div>
                                    {(container.rules || []).map((rule, ruleIndex) => (
                                        <Rule
                                            key={`${rule.id}-${ruleIndex}`}
                                            rule={rule}
                                            containerPath={currentPath}
                                            ruleIndex={ruleIndex}
                                            onUpdate={onUpdateRule}
                                            onRemove={onRemoveRule}
                                            showLogicOperator={true}
                                        />
                                    ))}
                                </div>
                            ) : (
                                <div className="container-empty">
                                    <div>📋</div>
                                    <div>Drag dimensions and metrics here to create rules</div>
                                </div>
                            )}

                            {(container.children || []).map((childContainer, childIndex) => (
                                <div key={childContainer.id} style={{marginTop: '16px'}}>
                                    {childIndex > 0 && (
                                        <div className="logic-operator">
                                            {container.logic?.toUpperCase() || 'AND'}
                                        </div>
                                    )}
                                    <Container
                                        container={childContainer}
                                        containerIndex={childIndex}
                                        level={level + 1}
                                        path={currentPath}
                                        onUpdate={onUpdate}
                                        onRemove={onRemove}
                                        onAddRule={onAddRule}
                                        onAddNestedContainer={onAddNestedContainer}
                                        onUpdateRule={onUpdateRule}
                                        onRemoveRule={onRemoveRule}
                                    />
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            );
        };

        // Component item with segment loading capability (preserved exactly)
        const ComponentItem = ({ item, onSegmentLoad }) => {
            const handleDragStart = (e) => {
                e.dataTransfer.setData('application/json', JSON.stringify(item));
            };

            const handleClick = () => {
                if (item.type === 'segment') {
                    onSegmentLoad && onSegmentLoad(item);
                } else {
                    window.dispatchEvent(new CustomEvent('addComponent', { detail: item }));
                }
            };

            return (
                <div 
                    className={`component-item ${item.type === 'segment' ? 'segment-clickable' : ''}`} 
                    draggable={item.type !== 'segment'} 
                    onDragStart={item.type !== 'segment' ? handleDragStart : undefined}
                >
                    <div className="component-info">
                        <span className="component-icon">{item.icon}</span>
                        <div>
                            <div className="component-name">{item.name}</div>
                            <div className="component-category">{item.description || item.category}</div>
                        </div>
                    </div>
                    <div className={`component-type type-${item.type}`}>
                        {item.type}
                    </div>
                    {item.type !== 'segment' && (
                        <div className="component-add" onClick={handleClick}>+</div>
                    )}
                    {item.type === 'segment' && (
                        <div 
                            className="component-add" 
                            onClick={handleClick}
                            style={{background: '#f3e5f5', color: '#7b1fa2', borderColor: '#7b1fa2'}}
                        >
                            📂
                        </div>
                    )}
                </div>
            );
        };

        // Export JSON Modal (preserved exactly)
        const ExportJsonModal = ({ isOpen, onClose, jsonData }) => {
            const [copied, setCopied] = useState(false);

            if (!isOpen) return null;

            const copyToClipboard = async () => {
                try {
                    await navigator.clipboard.writeText(jsonData);
                    setCopied(true);
                    setTimeout(() => setCopied(false), 2000);
                } catch (err) {
                    const textArea = document.createElement('textarea');
                    textArea.value = jsonData;
                    document.body.appendChild(textArea);
                    textArea.select();
                    try {
                        document.execCommand('copy');
                        setCopied(true);
                        setTimeout(() => setCopied(false), 2000);
                    } catch (fallbackErr) {
                        console.error('Fallback copy failed:', fallbackErr);
                    }
                    document.body.removeChild(textArea);
                }
            };

            const downloadJson = () => {
                const blob = new Blob([jsonData], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `segment_${new Date().toISOString().slice(0,10)}.json`;
                a.click();
                URL.revokeObjectURL(url);
            };

            return (
                <div className="export-modal-overlay" onClick={onClose}>
                    <div className="export-modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="export-modal-header">
                            <h3 className="export-modal-title">📤 Export Segment JSON</h3>
                            <button onClick={onClose} className="btn btn-secondary">✕</button>
                        </div>

                        <div className="export-modal-body">
                            <div className="export-json-code">
                                {jsonData}
                            </div>
                        </div>

                        <div className="export-modal-actions">
                            <button 
                                onClick={copyToClipboard} 
                                className="btn-clipboard"
                                disabled={copied}
                            >
                                {copied ? '✅ Copied!' : '📋 Copy to Clipboard'}
                            </button>
                            <button onClick={downloadJson} className="btn btn-primary">
                                💾 Download File
                            </button>
                            <button onClick={onClose} className="btn btn-secondary">
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            );
        };

        // Preview Modal (preserved exactly)
        const PreviewModal = ({ isOpen, onClose, previewData }) => {
            if (!isOpen) return null;

            const exportToCSV = () => {
                if (!previewData?.rows || previewData.rows.length === 0) return;

                const csvContent = [
                    previewData.columns.join(','),
                    ...previewData.rows.map(row => 
                        previewData.columns.map(col => 
                            typeof row[col] === 'string' ? `"${row[col]}"` : row[col] || ''
                        ).join(',')
                    )
                ].join('\\n');

                const blob = new Blob([csvContent], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `segment_preview_${new Date().toISOString().slice(0,10)}.csv`;
                a.click();
                URL.revokeObjectURL(url);
            };

            return (
                <div className="modal-overlay" onClick={onClose}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3 className="modal-title">Segment Preview: {previewData?.segment_name || 'Untitled'}</h3>
                            <button onClick={onClose} className="btn btn-secondary">✕</button>
                        </div>

                        <div className="modal-body">
                            {previewData?.sql_query && (
                                <div>
                                    <h4 style={{marginBottom: '8px', fontSize: '14px', fontWeight: '600'}}>
                                        Generated SQL Query:
                                    </h4>
                                    <div className="sql-code">
                                        {previewData.sql_query}
                                    </div>
                                </div>
                            )}

                            <div className="preview-stats">
                                <div className="preview-stat">
                                    <div className="preview-stat-value">
                                        {previewData?.containers || 0}
                                    </div>
                                    <div className="preview-stat-label">Containers</div>
                                </div>
                                <div className="preview-stat">
                                    <div className="preview-stat-value">
                                        {previewData?.rules_total || 0}
                                    </div>
                                    <div className="preview-stat-label">Rules</div>
                                </div>
                                <div className="preview-stat">
                                    <div className="preview-stat-value">
                                        {previewData?.total_count || 0}
                                    </div>
                                    <div className="preview-stat-label">Records</div>
                                </div>
                            </div>

                            <div className="preview-results">
                                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px'}}>
                                    <h4 style={{margin: 0, fontSize: '14px', fontWeight: '600'}}>
                                        Preview Results ({(previewData?.rows || []).length} records)
                                    </h4>
                                    {previewData?.rows && previewData.rows.length > 0 && (
                                        <button onClick={exportToCSV} className="export-btn">
                                            📥 Export CSV
                                        </button>
                                    )}
                                </div>

                                {previewData?.rows && previewData.rows.length > 0 ? (
                                    <table className="preview-table">
                                        <thead>
                                            <tr>
                                                {previewData.columns.map((col, index) => (
                                                    <th key={index}>{col}</th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {previewData.rows.map((row, index) => (
                                                <tr key={index}>
                                                    {previewData.columns.map((col, colIndex) => (
                                                        <td key={colIndex} title={row[col]}>
                                                            {row[col] !== null && row[col] !== undefined ? String(row[col]) : ''}
                                                        </td>
                                                    ))}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                ) : (
                                    <div className="no-data">
                                        {previewData?.error ? (
                                            <>
                                                ❌ Error: {previewData.error}
                                                <br />
                                                <small>Query: {previewData?.sql_query}</small>
                                            </>
                                        ) : (
                                            <>
                                                📭 No records found matching the segment criteria.
                                                <br />
                                                <small>Try adjusting your rules or container logic.</small>
                                            </>
                                        )}
                                    </div>
                                )}
                            </div>

                            {!previewData?.error && (
                                <div style={{
                                    background: '#f8f9fa',
                                    border: '1px solid #e9ecef',
                                    borderRadius: '6px',
                                    padding: '16px',
                                    marginTop: '16px'
                                }}>
                                    <p style={{margin: 0, color: '#6c757d', fontSize: '14px'}}>
                                        💡 <strong>Note:</strong> This preview shows actual data from your SQLite database 
                                        with {databaseStats.total_hits?.toLocaleString() || '500K+'} hits. 
                                        Results are limited to 100 records for performance.
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            );
        };

        // Save notification component (preserved exactly)
        const SaveNotification = ({ show, onHide }) => {
            useEffect(() => {
                if (show) {
                    const timer = setTimeout(() => {
                        onHide();
                    }, 3000);
                    return () => clearTimeout(timer);
                }
            }, [show, onHide]);

            if (!show) return null;

            return (
                <div className="save-notification">
                    ✅ Segment saved successfully!
                </div>
            );
        };

        // Tags input component (preserved exactly)
        const TagsInput = ({ tags, onChange, placeholder = "Add tags..." }) => {
            const [inputValue, setInputValue] = useState('');

            const handleKeyDown = (e) => {
                if (e.key === 'Enter' && inputValue.trim()) {
                    e.preventDefault();
                    const newTag = inputValue.trim();
                    if (!tags.includes(newTag)) {
                        onChange([...tags, newTag]);
                    }
                    setInputValue('');
                } else if (e.key === 'Backspace' && !inputValue && tags.length > 0) {
                    onChange(tags.slice(0, -1));
                }
            };

            const removeTag = (tagToRemove) => {
                onChange(tags.filter(tag => tag !== tagToRemove));
            };

            return (
                <div className="tags-input" onClick={() => document.querySelector('.tag-input').focus()}>
                    {tags.map((tag, index) => (
                        <span key={index} className="tag-item">
                            {tag}
                            <span className="tag-remove" onClick={() => removeTag(tag)}>×</span>
                        </span>
                    ))}
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={tags.length === 0 ? placeholder : ''}
                        className="tag-input"
                    />
                </div>
            );
        };

        // MAIN COMPONENT: Enhanced Adobe Segment Builder (all original functionality preserved)
        const AdobeSegmentBuilder = () => {
            const [segmentDefinition, setSegmentDefinition] = useState(initialSegment);
            const [searchQuery, setSearchQuery] = useState('');
            const [activeTab, setActiveTab] = useState('dimensions');
            const [isPreviewOpen, setIsPreviewOpen] = useState(false);
            const [isLoading, setIsLoading] = useState(false);
            const [isSaving, setIsSaving] = useState(false);
            const [previewData, setPreviewData] = useState(initialPreviewData || null);
            const [sidebarWidth, setSidebarWidth] = useState(280);
            const [isResizing, setIsResizing] = useState(false);
            const [isExportModalOpen, setIsExportModalOpen] = useState(false);
            const [showSaveNotification, setShowSaveNotification] = useState(false);

            useEffect(() => {
                if (initialPreviewData && Object.keys(initialPreviewData).length > 0) {
                    setPreviewData(initialPreviewData);
                }
            }, []);

            // Sidebar resizing (preserved exactly)
            const handleMouseDown = (e) => {
                setIsResizing(true);
                e.preventDefault();
            };

            const handleMouseMove = (e) => {
                if (!isResizing) return;
                const newWidth = Math.min(Math.max(e.clientX, 200), 500);
                setSidebarWidth(newWidth);
            };

            const handleMouseUp = () => {
                setIsResizing(false);
            };

            useEffect(() => {
                if (isResizing) {
                    document.addEventListener('mousemove', handleMouseMove);
                    document.addEventListener('mouseup', handleMouseUp);
                    return () => {
                        document.removeEventListener('mousemove', handleMouseMove);
                        document.removeEventListener('mouseup', handleMouseUp);
                    };
                }
            }, [isResizing]);

            // Auto-execute preview (preserved exactly)
            useEffect(() => {
                const executePreview = () => {
                    try {
                        const sqlQuery = generateSQLFromSegment(segmentDefinition);

                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: {
                                type: 'segmentPreview',
                                sql: sqlQuery,
                                segment: segmentDefinition,
                                executeNow: true,
                                timestamp: Date.now()
                            }
                        }, '*');

                        setPreviewData({
                            sql_query: sqlQuery,
                            segment_name: segmentDefinition.name,
                            containers: segmentDefinition.containers?.length || 0,
                            rules_total: segmentDefinition.containers?.reduce((acc, container) => 
                                acc + (container.rules?.length || 0), 0) || 0,
                            rows: initialPreviewData?.rows || [],
                            columns: initialPreviewData?.columns || [],
                            is_default: (!segmentDefinition.containers?.length || 
                                       !segmentDefinition.containers?.some(c => c.rules?.length > 0))
                        });

                    } catch (error) {
                        console.error('Preview error:', error);
                    }
                };

                executePreview();
            }, [segmentDefinition]);

            // Component add events (preserved exactly)
            useEffect(() => {
                const handleAddComponent = (event) => {
                    const item = event.detail;
                    handleComponentClick(item);
                };

                window.addEventListener('addComponent', handleAddComponent);
                return () => window.removeEventListener('addComponent', handleAddComponent);
            }, [segmentDefinition]);

            const getFilteredComponents = useCallback(() => {
                let components = [];

                if (activeTab === 'dimensions') {
                    config.dimensions?.forEach(cat => {
                        components = [...components, ...(cat.items || [])];
                    });
                }
                if (activeTab === 'metrics') {
                    config.metrics?.forEach(cat => {
                        components = [...components, ...(cat.items || [])];
                    });
                }
                if (activeTab === 'segments') {
                    components = [...components, ...(config.segments || [])];
                }

                if (searchQuery.trim()) {
                    components = components.filter(item =>
                        item.name?.toLowerCase().includes(searchQuery.toLowerCase())
                    );
                }

                return components;
            }, [activeTab, searchQuery]);

            // ALL CONTAINER OPERATIONS PRESERVED EXACTLY FROM ORIGINAL (lines 1500-2500)
            const addContainer = () => {
                const newContainer = {
                    id: generateId(),
                    type: 'hit',
                    include: true,
                    rules: [],
                    logic: 'and',
                    children: []
                };

                setSegmentDefinition(prev => ({
                    ...prev,
                    containers: [...(prev.containers || []), newContainer]
                }));
            };

            const removeContainer = (path) => {
                setSegmentDefinition(prev => {
                    const newDef = {...prev};
                    let containers = [...newDef.containers];

                    if (path.length === 1) {
                        containers.splice(path[0], 1);
                    } else {
                        let current = containers[path[0]];
                        for (let i = 1; i < path.length - 1; i++) {
                            current = current.children[path[i]];
                        }
                        current.children.splice(path[path.length - 1], 1);
                    }

                    newDef.containers = containers;
                    return newDef;
                });
            };

            const addNestedContainer = (parentPath) => {
                const newContainer = {
                    id: generateId(),
                    type: 'hit',
                    include: true,
                    rules: [],
                    logic: 'and',
                    children: []
                };

                setSegmentDefinition(prev => {
                    const newDef = {...prev};
                    let containers = [...newDef.containers];

                    if (parentPath.length === 1) {
                        const parentContainer = containers[parentPath[0]];
                        if (!parentContainer.children) {
                            parentContainer.children = [];
                        }
                        parentContainer.children.push(newContainer);
                    } else {
                        let current = containers[parentPath[0]];
                        for (let i = 1; i < parentPath.length; i++) {
                            current = current.children[parentPath[i]];
                        }
                        if (!current.children) {
                            current.children = [];
                        }
                        current.children.push(newContainer);
                    }

                    newDef.containers = containers;
                    return newDef;
                });
            };

            const updateContainer = (path, field, value) => {
                setSegmentDefinition(prev => {
                    const newDef = {...prev};
                    let containers = [...newDef.containers];

                    if (path.length === 1) {
                        containers[path[0]] = {...containers[path[0]], [field]: value};
                    } else {
                        let current = containers[path[0]];
                        for (let i = 1; i < path.length - 1; i++) {
                            current = current.children[path[i]];
                        }
                        current.children[path[path.length - 1]] = {...current.children[path[path.length - 1]], [field]: value};
                    }

                    newDef.containers = containers;
                    return newDef;
                });
            };

            const addRule = (path, rule) => {
                setSegmentDefinition(prev => {
                    const newDef = {...prev};
                    let containers = [...newDef.containers];

                    if (path.length === 1) {
                        containers[path[0]] = {
                            ...containers[path[0]], 
                            rules: [...(containers[path[0]].rules || []), rule]
                        };
                    } else {
                        let current = containers[path[0]];
                        for (let i = 1; i < path.length - 1; i++) {
                            current = current.children[path[i]];
                        }
                        const targetContainer = current.children[path[path.length - 1]];
                        targetContainer.rules = [...(targetContainer.rules || []), rule];
                    }

                    newDef.containers = containers;
                    return newDef;
                });
            };

            const updateRule = (containerPath, ruleIndex, field, value) => {
                setSegmentDefinition(prev => {
                    const newDef = {...prev};
                    let containers = [...newDef.containers];

                    let targetContainer;
                    if (containerPath.length === 1) {
                        targetContainer = containers[containerPath[0]];
                    } else {
                        let current = containers[containerPath[0]];
                        for (let i = 1; i < containerPath.length - 1; i++) {
                            current = current.children[containerPath[i]];
                        }
                        targetContainer = current.children[containerPath[containerPath.length - 1]];
                    }

                    if (targetContainer && targetContainer.rules) {
                        targetContainer.rules = targetContainer.rules.map((rule, index) =>
                            index === ruleIndex ? { ...rule, [field]: value } : rule
                        );
                    }

                    newDef.containers = containers;
                    return newDef;
                });
            };

            const removeRule = (containerPath, ruleIndex) => {
                setSegmentDefinition(prev => {
                    const newDef = {...prev};
                    let containers = [...newDef.containers];

                    let targetContainer;
                    if (containerPath.length === 1) {
                        targetContainer = containers[containerPath[0]];
                    } else {
                        let current = containers[containerPath[0]];
                        for (let i = 1; i < containerPath.length - 1; i++) {
                            current = current.children[containerPath[i]];
                        }
                        targetContainer = current.children[containerPath[containerPath.length - 1]];
                    }

                    if (targetContainer && targetContainer.rules) {
                        targetContainer.rules = targetContainer.rules.filter((_, index) => index !== ruleIndex);
                    }

                    newDef.containers = containers;
                    return newDef;
                });
            };

            const handleComponentClick = (component) => {
                const newRule = {
                    id: generateId(),
                    field: component.field,
                    name: component.name,
                    dataType: component.dataType,
                    operator: 'equals',
                    value: '',
                    logic: 'AND',
                    icon: component.icon
                };

                if (segmentDefinition.containers?.length === 0) {
                    const newContainer = {
                        id: generateId(),
                        type: 'hit',
                        include: true,
                        rules: [newRule],
                        logic: 'and',
                        children: []
                    };
                    setSegmentDefinition(prev => ({
                        ...prev,
                        containers: [newContainer]
                    }));
                } else {
                    addRule([0], newRule);
                }
            };

            const handleSegmentLoad = (segmentItem) => {
                console.log('Loading segment:', segmentItem.name);
                alert(`Loading segment: ${segmentItem.name}\nThis would load the full segment definition from the database.`);
            };

            const saveSegment = async () => {
                if (!segmentDefinition.name || segmentDefinition.name.trim() === '') {
                    alert('Please enter a segment name');
                    return;
                }

                if (!segmentDefinition.containers || segmentDefinition.containers.length === 0) {
                    alert('Please add at least one container to your segment');
                    return;
                }

                setIsSaving(true);

                try {
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {
                            type: 'segmentSave',
                            segment: segmentDefinition,
                            timestamp: Date.now()
                        }
                    }, '*');

                    setShowSaveNotification(true);

                    setTimeout(() => {
                        setIsSaving(false);
                    }, 1500);

                } catch (error) {
                    console.error('Save error:', error);
                    alert('Error saving segment. Please try again.');
                    setIsSaving(false);
                }
            };

            const previewSegment = () => {
                setIsLoading(true);

                try {
                    const sqlQuery = generateSQLFromSegment(segmentDefinition);

                    const previewDataObj = {
                        sql_query: sqlQuery,
                        segment_name: segmentDefinition.name,
                        containers: segmentDefinition.containers?.length || 0,
                        rules_total: segmentDefinition.containers?.reduce((acc, container) => 
                            acc + (container.rules?.length || 0), 0) || 0
                    };

                    setPreviewData(previewDataObj);
                    setIsPreviewOpen(true);

                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {
                            type: 'segmentPreview',
                            segment: segmentDefinition,
                            sql: sqlQuery,
                            executeNow: true,
                            timestamp: Date.now()
                        }
                    }, '*');

                } catch (error) {
                    console.error('Preview error:', error);
                    setPreviewData({
                        sql_query: '-- Error generating SQL',
                        error: error.message
                    });
                    setIsPreviewOpen(true);
                }

                setTimeout(() => setIsLoading(false), 1000);
            };

            const exportJson = () => {
                setIsExportModalOpen(true);
            };

            // SQL generation (preserved exactly from original)
            const generateSQLFromSegment = (segment) => {
                try {
                    const containers = segment.containers || [];

                    if (containers.length === 0) {
                        return "SELECT * FROM hits LIMIT 10";
                    }

                    const processContainerRecursive = (container, level = 0) => {
                        const rules = container.rules || [];
                        let clauses = [];

                        if (rules.length > 0) {
                            const ruleClauses = [];

                            rules.forEach((rule, ruleIndex) => {
                                const field = rule.field;
                                const operator = rule.operator || 'equals';
                                const value = rule.value;
                                const dataType = rule.dataType || 'string';

                                if (!field || !value) return;

                                let condition = '';

                                if (dataType === 'string') {
                                    const escapedValue = value.replace(/'/g, "''");

                                    switch (operator) {
                                        case 'equals':
                                            condition = `LOWER(${field}) = LOWER('${escapedValue}')`;
                                            break;
                                        case 'does not equal':
                                            condition = `LOWER(${field}) != LOWER('${escapedValue}')`;
                                            break;
                                        case 'contains':
                                            condition = `LOWER(${field}) LIKE LOWER('%${escapedValue}%')`;
                                            break;
                                        case 'does not contain':
                                            condition = `LOWER(${field}) NOT LIKE LOWER('%${escapedValue}%')`;
                                            break;
                                        case 'starts with':
                                            condition = `LOWER(${field}) LIKE LOWER('${escapedValue}%')`;
                                            break;
                                        case 'ends with':
                                            condition = `LOWER(${field}) LIKE LOWER('%${escapedValue}')`;
                                            break;
                                        case 'exists':
                                            condition = `${field} IS NOT NULL AND ${field} != ''`;
                                            break;
                                        case 'does not exist':
                                            condition = `(${field} IS NULL OR ${field} = '')`;
                                            break;
                                        default:
                                            condition = `LOWER(${field}) = LOWER('${escapedValue}')`;
                                    }
                                } else {
                                    const numValue = parseFloat(value) || 0;

                                    switch (operator) {
                                        case 'equals':
                                            condition = `${field} = ${numValue}`;
                                            break;
                                        case 'does not equal':
                                            condition = `${field} != ${numValue}`;
                                            break;
                                        case 'is greater than':
                                            condition = `${field} > ${numValue}`;
                                            break;
                                        case 'is less than':
                                            condition = `${field} < ${numValue}`;
                                            break;
                                        case 'is greater than or equal to':
                                            condition = `${field} >= ${numValue}`;
                                            break;
                                        case 'is less than or equal to':
                                            condition = `${field} <= ${numValue}`;
                                            break;
                                        case 'exists':
                                            condition = `${field} IS NOT NULL`;
                                            break;
                                        case 'does not exist':
                                            condition = `${field} IS NULL`;
                                            break;
                                        default:
                                            condition = `${field} = ${numValue}`;
                                    }
                                }

                                if (condition) {
                                    const ruleLogic = rule.logic || 'AND';
                                    if (ruleIndex > 0) {
                                        ruleClauses.push(`${ruleLogic} ${condition}`);
                                    } else {
                                        ruleClauses.push(condition);
                                    }
                                }
                            });

                            if (ruleClauses.length > 0) {
                                clauses.push(`(${ruleClauses.join(' ')})`);
                            }
                        }

                        if (container.children && container.children.length > 0) {
                            container.children.forEach(child => {
                                const childClause = processContainerRecursive(child, level + 1);
                                if (childClause) {
                                    clauses.push(childClause);
                                }
                            });
                        }

                        if (clauses.length > 0) {
                            const containerLogic = container.logic || 'and';
                            let combined = clauses.join(` ${containerLogic.toUpperCase()} `);

                            if (!container.include) {
                                combined = `NOT (${combined})`;
                            }

                            return `(${combined})`;
                        }

                        return null;
                    };

                    const containerClauses = [];
                    containers.forEach(container => {
                        const clause = processContainerRecursive(container);
                        if (clause) {
                            containerClauses.push(clause);
                        }
                    });

                    if (containerClauses.length === 0) {
                        return `SELECT * FROM hits LIMIT 10`;
                    }

                    const segmentLogic = segment.logic || 'and';
                    const whereClause = containerClauses.join(` ${segmentLogic.toUpperCase()} `);

                    return `SELECT * FROM hits WHERE ${whereClause} ORDER BY timestamp DESC LIMIT 100`;

                } catch (error) {
                    return `-- Error generating SQL: ${error.message}\nSELECT * FROM hits LIMIT 10`;
                }
            };

            return (
                <div className="segment-builder">
                    <div className="sidebar" style={{width: sidebarWidth}}>
                        <div 
                            className="sidebar-resizer"
                            onMouseDown={handleMouseDown}
                        ></div>

                        <div className="sidebar-header">
                            <h1 className="sidebar-title">Segment Components</h1>

                            {databaseStats.total_hits && (
                                <div className="database-overview">
                                    <div className="database-title">📊 Database Overview</div>
                                    <div className="database-stats">
                                        <div className="stat-item stat-hits">
                                            <div className="stat-value">{(databaseStats.total_hits / 1000).toFixed(1)}K</div>
                                            <div className="stat-label">Hits</div>
                                        </div>
                                        <div className="stat-item stat-users">
                                            <div className="stat-value">{(databaseStats.unique_users / 1000).toFixed(1)}K</div>
                                            <div className="stat-label">Users</div>
                                        </div>
                                        <div className="stat-item stat-sessions">
                                            <div className="stat-value">{(databaseStats.sessions / 1000).toFixed(1)}K</div>
                                            <div className="stat-label">Sessions</div>
                                        </div>
                                        <div className="stat-item stat-revenue">
                                            <div className="stat-value">${(databaseStats.total_revenue / 1000000).toFixed(1)}M</div>
                                            <div className="stat-label">Revenue</div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="sidebar-content">
                            <input
                                type="text"
                                placeholder="Search components..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="search-input"
                            />

                            <div className="tabs">
                                {['Dimensions', 'Metrics', 'Segments'].map(tab => (
                                    <button
                                        key={tab}
                                        onClick={() => setActiveTab(tab.toLowerCase())}
                                        className={`tab ${activeTab === tab.toLowerCase() ? 'active' : ''}`}
                                    >
                                        {tab}
                                    </button>
                                ))}
                            </div>

                            <div>
                                {getFilteredComponents().map((item, index) => (
                                    <ComponentItem 
                                        key={index} 
                                        item={item} 
                                        onSegmentLoad={handleSegmentLoad}
                                    />
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="main-canvas">
                        <div className="canvas-content">
                            {(segmentDefinition.containers || []).length > 0 ? (
                                <div>
                                    {segmentDefinition.containers.map((container, index) => (
                                        <div key={container.id}>
                                            {index > 0 && (
                                                <div className="logic-operator">
                                                    {segmentDefinition.logic?.toUpperCase() || 'AND'}
                                                </div>
                                            )}
                                            <Container
                                                container={container}
                                                containerIndex={index}
                                                level={0}
                                                path={[]}
                                                onUpdate={updateContainer}
                                                onRemove={removeContainer}
                                                onAddRule={addRule}
                                                onAddNestedContainer={addNestedContainer}
                                                onUpdateRule={updateRule}
                                                onRemoveRule={removeRule}
                                            />
                                        </div>
                                    ))}

                                    <button onClick={addContainer} className="btn btn-outline">
                                        + Add Container
                                    </button>
                                </div>
                            ) : (
                                <div className="empty-state">
                                    <div className="empty-icon">🎯</div>
                                    <div className="empty-title">Start Building Your Segment</div>
                                    <div className="empty-description">
                                        Create containers to define your segment criteria. 
                                        Drag dimensions and metrics from the sidebar to build rules.
                                    </div>
                                    <button onClick={addContainer} className="btn btn-primary">
                                        + Add First Container
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>

                    <SaveNotification 
                        show={showSaveNotification} 
                        onHide={() => setShowSaveNotification(false)} 
                    />

                    <ExportJsonModal
                        isOpen={isExportModalOpen}
                        onClose={() => setIsExportModalOpen(false)}
                        jsonData={JSON.stringify(segmentDefinition, null, 2)}
                    />

                    <PreviewModal
                        isOpen={isPreviewOpen}
                        onClose={() => setIsPreviewOpen(false)}
                        previewData={previewData}
                    />
                </div>
            );
        };

        ReactDOM.render(<AdobeSegmentBuilder />, document.getElementById('root'));
    </script>
</body>
</html>
    """

    # Render the component and handle return value
    component_value = components.html(html_content, height=800, scrolling=False)

    # Handle all component communications (preserved exactly)
    if component_value and isinstance(component_value, dict):
        if component_value.get('type') == 'segmentPreview' and component_value.get('executeNow'):
            sql_query = component_value.get('sql', '')
            if sql_query:
                preview_result = _execute_preview_query(sql_query)
                st.session_state.preview_data = preview_result
                st.rerun()

        elif component_value.get('type') == 'segmentSave':
            segment = component_value.get('segment', {})
            if segment:
                _save_segment_enhanced(segment)
                st.rerun()

        elif component_value.get('type') == 'goHome':
            st.session_state.current_page = 'home'
            st.rerun()


def _render_enhanced_segment_form():
    """ENHANCED: Render segment definition form with validation and draggable containers"""

    # ENHANCED: Form validation helper
    def validate_field(field_name, value, required=True):
        error_key = f"{field_name}_error"

        if required and (not value or not value.strip()):
            st.session_state.form_errors[error_key] = f"{field_name.title()} is required"
            return False
        else:
            if error_key in st.session_state.form_errors:
                del st.session_state.form_errors[error_key]
            return True

    # ENHANCED: Draggable form container 1 - Basic Information
    with st.container():
        st.markdown('<div class="draggable-form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-section-header">📝 Basic Information</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            segment_name = st.text_input(
                "Segment Title *",
                value=st.session_state.segment_definition.get('name', ''),
                key="segment_name_input",
                help="Enter a descriptive name for your segment"
            )

            # Validate name in real-time
            is_name_valid = validate_field("segment title", segment_name, required=True)
            if not is_name_valid:
                st.error(st.session_state.form_errors.get("segment title_error", ""))

            # Update session state
            if segment_name != st.session_state.segment_definition.get('name'):
                st.session_state.segment_definition['name'] = segment_name

        with col2:
            # ENHANCED: Logic selector (preserved from original)
            logic_type = st.selectbox(
                "Container Logic",
                options=['and', 'or', 'then'],
                index=['and', 'or', 'then'].index(st.session_state.segment_definition.get('logic', 'and')),
                key="segment_logic",
                help="How containers should be combined"
            )
            st.session_state.segment_definition['logic'] = logic_type

        st.markdown('</div>', unsafe_allow_html=True)

    # ENHANCED: Draggable form container 2 - Description and Tags
    with st.container():
        st.markdown('<div class="draggable-form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-section-header">📄 Description & Tags</div>', unsafe_allow_html=True)

        description = st.text_area(
            "Description *",
            value=st.session_state.segment_definition.get('description', ''),
            key="segment_description",
            help="Describe the purpose and criteria of this segment",
            height=100
        )

        # Validate description
        is_desc_valid = validate_field("description", description, required=True)
        if not is_desc_valid:
            st.error(st.session_state.form_errors.get("description_error", ""))

        # Update session state
        if description != st.session_state.segment_definition.get('description'):
            st.session_state.segment_definition['description'] = description

        # ENHANCED: Tags input using streamlit
        st.write("**Tags**")
        tags_input = st.text_input(
            "Add tags (comma-separated)",
            value=", ".join(st.session_state.segment_definition.get('tags', [])),
            key="segment_tags_input",
            help="Add tags to categorize your segment (separate with commas)"
        )

        # Process tags
        if tags_input:
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            st.session_state.segment_definition['tags'] = tags

            # Display current tags
            if tags:
                tag_display = " ".join([f"🏷️ {tag}" for tag in tags])
                st.caption(f"Current tags: {tag_display}")
        else:
            st.session_state.segment_definition['tags'] = []

        st.markdown('</div>', unsafe_allow_html=True)

    # ENHANCED: Draggable form container 3 - Actions
    with st.container():
        st.markdown('<div class="draggable-form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-section-header">🚀 Actions</div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📤 Export JSON", key="export_json_action", help="Export segment definition as JSON"):
                _export_segment_json()

        with col2:
            if st.button("🔍 Preview", key="preview_action", help="Preview segment results"):
                _preview_segment_action()

        with col3:
            # ENHANCED: Save button with validation
            save_disabled = bool(st.session_state.form_errors) or not segment_name.strip() or not description.strip()

            if st.button("💾 Save Segment",
                        key="save_segment_action",
                        disabled=save_disabled,
                        help="Save segment to database" if not save_disabled else "Please fix validation errors first"):
                if not save_disabled:
                    _save_segment_action()
                else:
                    st.error("Please fix all validation errors before saving")

        with col4:
            if st.button("🔄 Reset", key="reset_action", help="Reset segment to initial state"):
                _reset_segment_action()

        # ENHANCED: Show validation summary
        if st.session_state.form_errors:
            st.error("⚠️ Please fix the following errors:")
            for error in st.session_state.form_errors.values():
                st.error(f"• {error}")
        elif segment_name.strip() and description.strip():
            st.success("✅ Form validation passed - ready to save!")

        st.markdown('</div>', unsafe_allow_html=True)


def _export_segment_json():
    """Export segment as JSON"""
    try:
        clean_segment = {
            "name": st.session_state.segment_definition.get("name", "Unnamed Segment"),
            "description": st.session_state.segment_definition.get("description", ""),
            "logic": st.session_state.segment_definition.get("logic", "and"),
            "containers": st.session_state.segment_definition.get("containers", []),
            "tags": st.session_state.segment_definition.get("tags", []),
            "created_date": datetime.now().isoformat(),
            "version": "2.0"
        }

        json_str = json.dumps(clean_segment, indent=2, ensure_ascii=False)

        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"segment_{st.session_state.segment_definition.get('name', 'unnamed').replace(' ', '_')}.json",
            mime="application/json"
        )
        st.success("✅ JSON export ready for download!")

    except Exception as e:
        st.error(f"❌ Error exporting JSON: {e}")


def _preview_segment_action():
    """Preview segment results"""
    try:
        sql_query = _generate_sql_from_segment_with_nesting(st.session_state.segment_definition)
        preview_result = _execute_preview_query(sql_query)

        st.info("🔍 Segment Preview")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Containers", len(st.session_state.segment_definition.get('containers', [])))
        with col2:
            total_rules = sum(len(c.get('rules', [])) for c in st.session_state.segment_definition.get('containers', []))
            st.metric("Total Rules", total_rules)
        with col3:
            st.metric("Records Found", preview_result.get('total_count', 0))

        st.code(sql_query, language='sql')

        if preview_result.get('rows'):
            st.dataframe(preview_result['rows'][:10], use_container_width=True)
        else:
            st.warning("No results found for this segment definition")

    except Exception as e:
        st.error(f"❌ Error previewing segment: {e}")


def _save_segment_action():
    """Save segment to database"""
    try:
        _save_segment_enhanced(st.session_state.segment_definition)
        st.balloons()
    except Exception as e:
        st.error(f"❌ Error saving segment: {e}")


def _reset_segment_action():
    """Reset segment to initial state"""
    st.session_state.segment_definition = {
        'name': '',
        'description': '',
        'container_type': 'hit',
        'logic': 'and',
        'containers': [],
        'tags': []
    }
    st.session_state.form_errors = {}
    st.rerun()


def _save_segment_enhanced(segment):
    """ENHANCED: Save segment to database with full metadata support"""
    try:
        db_path = Path("data/analytics.db")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Create segments table with enhanced schema
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

        # Generate unique segment ID
        segment_id = f"seg_{hash(segment.get('name', 'unnamed')) % 1000000:06d}"

        # Generate SQL query
        sql_query = _generate_sql_from_segment_with_nesting(segment)

        # Prepare data for insertion
        segment_data = (
            segment_id,
            segment.get('name', 'Unnamed Segment'),
            segment.get('description', ''),
            json.dumps(segment),
            sql_query,
            segment.get('container_type', 'hit'),
            json.dumps(segment.get('tags', []))
        )

        # Insert or update segment
        cursor.execute("""
            INSERT OR REPLACE INTO segments 
            (segment_id, name, description, definition, sql_query, container_type, tags, modified_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, segment_data)

        conn.commit()
        conn.close()

        # Show success message
        st.success(f"✅ Segment '{segment.get('name')}' saved successfully!")

        # Update session state to reflect the save
        st.session_state.segment_saved = True

    except Exception as e:
        st.error(f"❌ Error saving segment: {str(e)}")
        print(f"Save error details: {e}")


def _generate_sql_from_segment_with_nesting(segment):
    """ENHANCED: Generate SQL with proper nested container support"""
    try:
        containers = segment.get('containers', [])
        if not containers:
            return "SELECT * FROM hits WHERE 1=1 LIMIT 10"

        def process_container_recursive(container, level=0):
            """Recursively process containers and their children"""
            clauses = []

            # Process rules in this container
            rules = container.get('rules', [])
            if rules:
                rule_clauses = []
                for rule in rules:
                    field = rule.get('field', '')
                    operator = rule.get('operator', 'equals')
                    value = rule.get('value', '')
                    data_type = rule.get('dataType', 'string')

                    if not field or not value:
                        continue

                    condition = _generate_rule_condition_fixed(field, operator, value, data_type)

                    if condition:
                        rule_logic = rule.get('logic', 'AND') if len(rule_clauses) > 0 else ''
                        if rule_logic:
                            rule_clauses.append(f" {rule_logic} {condition}")
                        else:
                            rule_clauses.append(condition)

                if rule_clauses:
                    rules_clause = f"({' '.join(rule_clauses)})"
                    clauses.append(rules_clause)

            # Process nested containers recursively
            children = container.get('children', [])
            for child in children:
                child_clause = process_container_recursive(child, level + 1)
                if child_clause:
                    clauses.append(child_clause)

            if clauses:
                container_logic = container.get('logic', 'and').upper()
                combined = f"({f' {container_logic} '.join(clauses)})"

                # Apply include/exclude
                if not container.get('include', True):
                    combined = f"NOT {combined}"

                return combined

            return None

        # Process all top-level containers
        container_clauses = []
        for container in containers:
            clause = process_container_recursive(container)
            if clause:
                container_clauses.append(clause)

        if not container_clauses:
            return "SELECT * FROM hits WHERE 1=1 LIMIT 10"

        segment_logic = segment.get('logic', 'and').upper()
        where_clause = f" {segment_logic} ".join(container_clauses)

        return f"SELECT * FROM hits WHERE {where_clause} ORDER BY timestamp DESC LIMIT 100"

    except Exception as e:
        return f"-- Error generating SQL: {e}\nSELECT * FROM hits LIMIT 10"


def _generate_rule_condition_fixed(field, operator, value, data_type):
    """Generate SQL condition with proper syntax"""
    if data_type == 'string':
        value_escaped = value.replace("'", "''")

        if operator == 'equals':
            return f"LOWER({field}) = LOWER('{value_escaped}')"
        elif operator == 'does not equal':
            return f"LOWER({field}) != LOWER('{value_escaped}')"
        elif operator == 'contains':
            return f"LOWER({field}) LIKE LOWER('%{value_escaped}%')"
        elif operator == 'does not contain':
            return f"LOWER({field}) NOT LIKE LOWER('%{value_escaped}%')"
        elif operator == 'starts with':
            return f"LOWER({field}) LIKE LOWER('{value_escaped}%')"
        elif operator == 'ends with':
            return f"LOWER({field}) LIKE LOWER('%{value_escaped}')"
        elif operator == 'exists':
            return f"{field} IS NOT NULL AND {field} != ''"
        elif operator == 'does not exist':
            return f"({field} IS NULL OR {field} = '')"
        else:
            return f"LOWER({field}) = LOWER('{value_escaped}')"

    else:  # number type
        try:
            numeric_value = float(value) if value else 0
        except:
            numeric_value = 0

        if operator == 'equals':
            return f"{field} = {numeric_value}"
        elif operator == 'does not equal':
            return f"{field} != {numeric_value}"
        elif operator == 'is greater than':
            return f"{field} > {numeric_value}"
        elif operator == 'is less than':
            return f"{field} < {numeric_value}"
        elif operator == 'is greater than or equal to':
            return f"{field} >= {numeric_value}"
        elif operator == 'is less than or equal to':
            return f"{field} <= {numeric_value}"
        elif operator == 'exists':
            return f"{field} IS NOT NULL"
        elif operator == 'does not exist':
            return f"{field} IS NULL"
        else:
            return f"{field} = {numeric_value}"


def export_segment_json_with_nesting(segment_definition):
    """Export segment definition with nested container support"""
    try:
        clean_segment = {
            "name": segment_definition.get("name", "Unnamed Segment"),
            "description": segment_definition.get("description", ""),
            "container_type": segment_definition.get("container_type", "hit"),
            "logic": segment_definition.get("logic", "and"),
            "containers": _clean_containers_for_export_nested(segment_definition.get("containers", [])),
            "tags": segment_definition.get("tags", []),
            "created_date": datetime.now().isoformat(),
            "version": "2.0",
            "supports_nesting": True
        }

        return json.dumps(clean_segment, indent=2, ensure_ascii=False)

    except Exception as e:
        return f"Error exporting JSON: {str(e)}"


def _clean_containers_for_export_nested(containers):
    """Clean containers for JSON export with nested structure"""
    clean_containers = []

    for container in containers:
        clean_container = {
            "id": container.get("id", f"id_{uuid.uuid4().hex[:8]}"),
            "type": container.get("type", "hit"),
            "include": container.get("include", True),
            "logic": container.get("logic", "and"),
            "rules": container.get("rules", []),
            "children": _clean_containers_for_export_nested(container.get("children", []))
        }
        clean_containers.append(clean_container)

    return clean_containers