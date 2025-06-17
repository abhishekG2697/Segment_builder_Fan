import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from src.database.queries import load_saved_segments

def render_library():
    """Render the segment library interface"""
    
    # Custom CSS for library - FIXED WHITE BACKGROUNDS
    st.markdown("""
    <style>
    /* Library styling */
    .library-controls {
        display: flex;
        gap: 12px;
        align-items: center;
        margin-bottom: 20px;
    }
    
    /* Fix input and select backgrounds */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
        border: 1px solid #D3D3D3 !important;
    }
    
    /* Segment cards */
    .segment-card {
        background: #FFFFFF;
        border: 1px solid #E1E1E1;
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 12px;
        position: relative;
        transition: all 0.15s ease;
    }
    
    .segment-card:hover {
        border-color: #1473E6;
        box-shadow: 0 2px 8px rgba(20, 115, 230, 0.1);
    }
    
    .segment-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
    }
    
    .segment-card-header h4 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #323232;
    }
    
    .segment-type-badge {
        padding: 4px 8px;
        border-radius: 3px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .hit-badge {
        background: #E3F2FF;
        color: #1473E6;
    }
    
    .visit-badge {
        background: #E8F5E9;
        color: #2E7D32;
    }
    
    .visitor-badge {
        background: #FCE4EC;
        color: #C2185B;
    }
    
    .segment-card-description {
        color: #6E6E6E;
        font-size: 13px;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    
    .segment-card-metrics {
        display: flex;
        gap: 20px;
        font-size: 12px;
        color: #6E6E6E;
        margin-bottom: 12px;
    }
    
    .segment-card-actions {
        display: flex;
        gap: 8px;
    }
    
    /* Fix ALL buttons in library - NO DARK BACKGROUNDS */
    button,
    .stButton > button,
    [data-testid="baseButton-secondary"],
    [role="button"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D3D3D3 !important;
        color: #323232 !important;
        padding: 6px 16px !important;
        font-size: 13px !important;
        border-radius: 3px !important;
    }
    
    button:hover,
    .stButton > button:hover {
        background-color: #F0F8FF !important;
        border-color: #1473E6 !important;
        color: #1473E6 !important;
    }
    
    /* Edit button - Light blue */
    .stButton > button[key*="edit"] {
        background-color: #E8F5FF !important;
        color: #1473E6 !important;
        border: 1px solid #1473E6 !important;
    }
    
    .stButton > button[key*="edit"]:hover {
        background-color: #1473E6 !important;
        color: white !important;
    }
    
    /* Preview button - Light green */
    .stButton > button[key*="preview"] {
        background-color: #E8F5E9 !important;
        color: #2E7D32 !important;
        border: 1px solid #2E7D32 !important;
    }
    
    .stButton > button[key*="preview"]:hover {
        background-color: #2E7D32 !important;
        color: white !important;
    }
    
    /* Copy button - Light orange */
    .stButton > button[key*="copy"] {
        background-color: #FFF3E0 !important;
        color: #E65100 !important;
        border: 1px solid #E65100 !important;
    }
    
    .stButton > button[key*="copy"]:hover {
        background-color: #E65100 !important;
        color: white !important;
    }
    
    /* Delete button - Light red */
    .stButton > button[key*="delete"] {
        background-color: #FFEBEE !important;
        color: #C62828 !important;
        border: 1px solid #C62828 !important;
    }
    
    .stButton > button[key*="delete"]:hover {
        background-color: #C62828 !important;
        color: white !important;
    }
    
    /* Primary buttons */
    .stButton > button[type="primary"],
    .stButton > button[kind="primary"] {
        background-color: #E8F5FF !important;
        color: #1473E6 !important;
        border: 1px solid #1473E6 !important;
    }
    
    .stButton > button[type="primary"]:hover,
    .stButton > button[kind="primary"]:hover {
        background-color: #1473E6 !important;
        color: white !important;
    }
    
    /* Force override any dark backgrounds */
    [style*="background-color: rgb(38, 39, 48)"] button,
    [style*="background-color: rgb(49, 51, 63)"] button,
    [style*="background: rgb(38, 39, 48)"] button,
    [style*="background: rgb(49, 51, 63)"] button {
        background-color: #FFFFFF !important;
    }
    
    /* Search and filters */
    .stTextInput > div > div > input {
        font-size: 13px !important;
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
    }
    
    .stSelectbox > div > div {
        font-size: 13px !important;
        background-color: #FFFFFF !important;
    }
    
    /* Fix dropdown menus */
    [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
    }
    
    [role="listbox"] {
        background-color: #FFFFFF !important;
    }
    
    [role="option"] {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
    }
    
    [role="option"]:hover {
        background-color: #F5F5F5 !important;
    }
    
    /* Fix expander backgrounds */
    .streamlit-expanderHeader {
        background-color: #F8F8F8 !important;
        color: #2C2C2C !important;
        border: 1px solid #E1E1E1 !important;
    }
    
    .streamlit-expanderContent {
        background-color: #FFFFFF !important;
    }
    
    /* Fix file uploader */
    .stFileUploader > div {
        background-color: #FFFFFF !important;
    }
    
    .stFileUploader > div > div {
        background-color: #FFFFFF !important;
        border: 2px dashed #D3D3D3 !important;
    }
    
    .stFileUploader label {
        color: #2C2C2C !important;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: #E3F2FF !important;
        color: #2C2C2C !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background-color: #F8F8F8 !important;
    }
    
    /* JSON viewer */
    pre {
        background-color: #F8F8F8 !important;
        color: #2C2C2C !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📚 Segment Library")
    
    # Search and filter controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input(
            "Search segments",
            placeholder="Search by name, description, or tags...",
            key="library_search"
        )
    
    with col2:
        filter_type = st.selectbox(
            "Filter by type",
            options=["All", "Hit", "Visit", "Visitor"],
            key="library_filter_type"
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            options=["Name", "Created Date", "Modified Date", "Usage"],
            key="library_sort"
        )
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("📥 Import Segment", key="import_segment_btn"):
            import_segment()
    
    with col2:
        if st.button("🔄 Refresh", key="refresh_library_btn"):
            st.rerun()
    
    # Get and display segments
    render_segment_grid(search_term, filter_type, sort_by)

def render_segment_grid(search_term, filter_type, sort_by):
    """Render the grid of saved segments"""
    
    # Get saved segments
    saved_segments = get_saved_segments()
    
    # Filter segments
    filtered_segments = []
    for segment in saved_segments:
        # Apply search filter
        if search_term:
            search_lower = search_term.lower()
            if not any([
                search_lower in segment.get('name', '').lower(),
                search_lower in segment.get('description', '').lower(),
                any(search_lower in tag for tag in segment.get('tags', []))
            ]):
                continue
        
        # Apply type filter
        if filter_type != "All":
            segment_type = segment.get('container_type', segment.get('definition', {}).get('container_type', 'hit'))
            if segment_type.lower() != filter_type.lower():
                continue
        
        filtered_segments.append(segment)
    
    # Sort segments
    if sort_by == "Name":
        filtered_segments.sort(key=lambda x: x.get('name', ''))
    elif sort_by == "Created Date":
        filtered_segments.sort(key=lambda x: x.get('created_date', ''), reverse=True)
    elif sort_by == "Modified Date":
        filtered_segments.sort(key=lambda x: x.get('modified_date', x.get('created_date', '')), reverse=True)
    elif sort_by == "Usage":
        filtered_segments.sort(key=lambda x: x.get('usage_count', 0), reverse=True)
    
    # Display segments
    if filtered_segments:
        st.info(f"Found {len(filtered_segments)} segments")
        
        # Display as a list (more compact than grid)
        for idx, segment in enumerate(filtered_segments):
            render_segment_card(segment, idx)
    else:
        st.info("No segments found. Create your first segment in the Segment Builder tab!")

def render_segment_card(segment, idx):
    """Render a single segment card"""
    
    # Get segment type and definition
    segment_type = segment.get('container_type', segment.get('definition', {}).get('container_type', 'hit'))
    has_definition = 'definition' in segment or 'containers' in segment
    
    # Create a unique key for this segment
    segment_key = f"seg_{idx}_{segment.get('name', 'unnamed').replace(' ', '_')}"
    
    # Card container
    with st.container():
        st.markdown(f"""
        <div class="segment-card">
            <div class="segment-card-header">
                <h4>{segment.get('name', 'Unnamed Segment')}</h4>
                <span class="segment-type-badge {segment_type}-badge">
                    {segment_type.upper()}
                </span>
            </div>
            <div class="segment-card-description">
                {segment.get('description', 'No description available')}
            </div>
            <div class="segment-card-metrics">
                <span>📊 {segment.get('usage_count', 0)} uses</span>
                <span>📅 {segment.get('created_date', 'Unknown')}</span>
                <span>👤 {segment.get('created_by', 'Unknown')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Actions row
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 3])
        
        with col1:
            if st.button("📝 Edit", key=f"edit_{segment_key}", help="Load segment in builder", use_container_width=True):
                if has_definition:
                    load_segment_to_builder(segment)
                else:
                    st.error("This segment has no definition to load")
        
        with col2:
            if st.button("👁️ Preview", key=f"preview_{segment_key}", help="Preview segment data", use_container_width=True):
                if has_definition:
                    load_segment_and_preview(segment)
                else:
                    st.error("This segment has no definition to preview")
        
        with col3:
            if st.button("📋 Copy", key=f"copy_{segment_key}", help="Duplicate segment", use_container_width=True):
                duplicate_segment(segment)
        
        with col4:
            if st.button("🗑️ Delete", key=f"delete_{segment_key}", help="Delete segment", use_container_width=True):
                delete_segment(segment, segment_key)
        
        # Show segment details in expander
        with st.expander("View Segment Details", expanded=False):
            if has_definition:
                definition = segment.get('definition', segment)
                st.json(definition)
            else:
                st.warning("No segment definition available")

def get_saved_segments():
    """Get list of saved segments with complete definitions"""
    
    # Complete segment definitions for pre-built segments
    sample_segments = [
        {
            'name': 'High Value Customers',
            'description': 'Visitors who have made purchases over $500',
            'container_type': 'visitor',
            'created_date': '2024-01-15',
            'created_by': 'Admin',
            'usage_count': 45,
            'tags': ['revenue', 'customers', 'high-value'],
            'definition': {
                'name': 'High Value Customers',
                'description': 'Visitors who have made purchases over $500',
                'container_type': 'visitor',
                'containers': [{
                    'id': 'container_hv_1',
                    'type': 'visitor',
                    'include': True,
                    'conditions': [{
                        'id': 'cond_rev_1',
                        'field': 'revenue',
                        'name': 'Revenue',
                        'type': 'metric',
                        'category': 'Commerce',
                        'operator': 'is greater than',
                        'value': 500,
                        'data_type': 'number'
                    }],
                    'logic': 'and'
                }],
                'logic': 'and'
            }
        },
        {
            'name': 'Mobile Users',
            'description': 'All sessions from mobile devices',
            'container_type': 'hit',
            'created_date': '2024-01-20',
            'created_by': 'Marketing Team',
            'usage_count': 128,
            'tags': ['mobile', 'device', 'traffic'],
            'definition': {
                'name': 'Mobile Users',
                'description': 'All sessions from mobile devices',
                'container_type': 'hit',
                'containers': [{
                    'id': 'container_mob_1',
                    'type': 'hit',
                    'include': True,
                    'conditions': [{
                        'id': 'cond_dev_1',
                        'field': 'device_type',
                        'name': 'Device Type',
                        'type': 'dimension',
                        'category': 'Browser',
                        'operator': 'equals',
                        'value': 'Mobile',
                        'data_type': 'string'
                    }],
                    'logic': 'and'
                }],
                'logic': 'and'
            }
        },
        {
            'name': 'Cart Abandoners',
            'description': 'Users who added items to cart but did not complete purchase',
            'container_type': 'visitor',
            'created_date': '2024-02-01',
            'created_by': 'Analytics Team',
            'usage_count': 67,
            'tags': ['cart', 'conversion', 'abandonment'],
            'definition': {
                'name': 'Cart Abandoners',
                'description': 'Users who added items to cart but did not complete purchase',
                'container_type': 'visitor',
                'containers': [{
                    'id': 'container_cart_1',
                    'type': 'visitor',
                    'include': True,
                    'conditions': [
                        {
                            'id': 'cond_cart_1',
                            'field': 'cart_additions',
                            'name': 'Cart Additions',
                            'type': 'metric',
                            'category': 'Commerce',
                            'operator': 'is greater than',
                            'value': 0,
                            'data_type': 'number'
                        },
                        {
                            'id': 'cond_orders_1',
                            'field': 'revenue',
                            'name': 'Revenue',
                            'type': 'metric',
                            'category': 'Commerce',
                            'operator': 'equals',
                            'value': 0,
                            'data_type': 'number'
                        }
                    ],
                    'logic': 'and'
                }],
                'logic': 'and'
            }
        },
        {
            'name': 'Engaged Visitors',
            'description': 'Visitors who viewed 5+ pages in a session',
            'container_type': 'visit',
            'created_date': '2024-02-05',
            'created_by': 'Product Team',
            'usage_count': 89,
            'tags': ['engagement', 'behavior', 'pageviews'],
            'definition': {
                'name': 'Engaged Visitors',
                'description': 'Visitors who viewed 5+ pages in a session',
                'container_type': 'visit',
                'containers': [{
                    'id': 'container_eng_1',
                    'type': 'visit',
                    'include': True,
                    'conditions': [{
                        'id': 'cond_pv_1',
                        'field': 'total_hits',
                        'name': 'Page Views',
                        'type': 'metric',
                        'category': 'Engagement',
                        'operator': 'is greater than or equal to',
                        'value': 5,
                        'data_type': 'number'
                    }],
                    'logic': 'and'
                }],
                'logic': 'and'
            }
        },
        {
            'name': 'Chrome Users from US',
            'description': 'All visitors using Chrome browser from United States',
            'container_type': 'hit',
            'created_date': '2024-02-10',
            'created_by': 'Tech Team',
            'usage_count': 156,
            'tags': ['browser', 'geography', 'chrome'],
            'definition': {
                'name': 'Chrome Users from US',
                'description': 'All visitors using Chrome browser from United States',
                'container_type': 'hit',
                'containers': [{
                    'id': 'container_chrome_1',
                    'type': 'hit',
                    'include': True,
                    'conditions': [
                        {
                            'id': 'cond_browser_1',
                            'field': 'browser_name',
                            'name': 'Browser Name',
                            'type': 'dimension',
                            'category': 'Browser',
                            'operator': 'equals',
                            'value': 'Chrome',
                            'data_type': 'string'
                        },
                        {
                            'id': 'cond_country_1',
                            'field': 'country',
                            'name': 'Country',
                            'type': 'dimension',
                            'category': 'User',
                            'operator': 'equals',
                            'value': 'US',
                            'data_type': 'string'
                        }
                    ],
                    'logic': 'and'
                }],
                'logic': 'and'
            }
        }
    ]
    
    # Try to load from database
    try:
        db_segments = load_saved_segments()
        if db_segments:
            # Ensure db segments have proper structure
            for seg in db_segments:
                if 'definition' in seg and isinstance(seg['definition'], str):
                    try:
                        seg['definition'] = json.loads(seg['definition'])
                    except:
                        pass
            sample_segments.extend(db_segments)
    except Exception as e:
        st.warning(f"Could not load segments from database: {str(e)}")
    
    # Add session segments
    if 'saved_segments' in st.session_state:
        for seg in st.session_state.saved_segments:
            # Ensure the segment has a complete definition
            if 'containers' in seg and not 'definition' in seg:
                seg['definition'] = seg.copy()
        sample_segments.extend(st.session_state.saved_segments)
    
    return sample_segments

def load_segment_to_builder(segment):
    """Load a segment into the builder for editing"""
    try:
        # Get the complete segment definition
        if 'definition' in segment:
            definition = segment['definition']
            if isinstance(definition, str):
                definition = json.loads(definition)
        else:
            # Use the segment itself as definition
            definition = segment.copy()
        
        # Ensure all required fields are present
        if not definition.get('name'):
            definition['name'] = segment.get('name', 'Unnamed Segment')
        if not definition.get('description'):
            definition['description'] = segment.get('description', '')
        if not definition.get('container_type'):
            definition['container_type'] = segment.get('container_type', 'hit')
        if not definition.get('logic'):
            definition['logic'] = 'and'
        
        # Load into session state
        st.session_state.segment_definition = definition

        # Reset preview selector and clear preview data
        st.session_state.preview_segment_selector = "Current Segment"
        st.session_state.preview_data = None
        
        # Switch to builder tab
        st.session_state.active_tab = 0
        
        st.success(f"✅ Loaded segment: {definition.get('name', 'Unnamed')}")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error loading segment: {str(e)}")
        with st.expander("Debug Info"):
            st.json(segment)

def load_segment_and_preview(segment):
    """Load a segment and switch to preview tab"""
    try:
        # First load the segment
        if 'definition' in segment:
            definition = segment['definition']
            if isinstance(definition, str):
                definition = json.loads(definition)
        else:
            definition = segment.copy()
        
        # Load into session state
        st.session_state.segment_definition = definition

        # Reset preview selector and clear preview data
        st.session_state.preview_segment_selector = "Current Segment"
        st.session_state.preview_data = None
        
        # Switch to preview tab
        st.session_state.active_tab = 1
        
        st.success(f"✅ Loading preview for: {definition.get('name', 'Unnamed')}")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error loading segment preview: {str(e)}")

def duplicate_segment(segment):
    """Create a duplicate of the segment"""
    try:
        new_segment = json.loads(json.dumps(segment))  # Deep copy
        new_segment['name'] = f"{segment.get('name', 'Unnamed')} - Copy"
        new_segment['created_date'] = datetime.now().strftime('%Y-%m-%d')
        new_segment['usage_count'] = 0
        
        # Update the definition name too
        if 'definition' in new_segment:
            if isinstance(new_segment['definition'], dict):
                new_segment['definition']['name'] = new_segment['name']
        
        if 'saved_segments' not in st.session_state:
            st.session_state.saved_segments = []
        
        st.session_state.saved_segments.append(new_segment)
        st.success(f"✅ Created copy: {new_segment['name']}")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error duplicating segment: {str(e)}")

def delete_segment(segment, segment_key):
    """Delete a segment from the library"""
    confirm_key = f"confirm_delete_{segment_key}"
    
    if st.session_state.get(confirm_key):
        # Perform deletion
        segment_name = segment.get('name', 'Unnamed')
        
        # Remove from saved segments
        if 'saved_segments' in st.session_state:
            st.session_state.saved_segments = [
                s for s in st.session_state.saved_segments 
                if s.get('name') != segment_name
            ]
        
        st.success(f"✅ Deleted segment: {segment_name}")
        st.session_state[confirm_key] = False
        st.rerun()
    else:
        st.session_state[confirm_key] = True
        st.warning(f"⚠️ Click delete again to confirm deletion of: {segment.get('name', 'Unnamed')}")

def import_segment():
    """Import segment from JSON file"""
    uploaded_file = st.file_uploader(
        "Choose a segment JSON file",
        type=['json'],
        key="segment_uploader"
    )
    
    if uploaded_file is not None:
        try:
            segment_data = json.load(uploaded_file)
            
            # Validate segment structure
            if not segment_data.get('name'):
                st.error("Invalid segment file: missing name")
                return
            
            # Ensure it has a definition
            if 'containers' in segment_data and 'definition' not in segment_data:
                segment_data['definition'] = {
                    'name': segment_data.get('name'),
                    'description': segment_data.get('description', ''),
                    'container_type': segment_data.get('container_type', 'hit'),
                    'containers': segment_data.get('containers', []),
                    'logic': segment_data.get('logic', 'and')
                }
            
            # Add metadata
            segment_data['created_date'] = datetime.now().strftime('%Y-%m-%d')
            segment_data['created_by'] = 'Imported'
            segment_data['usage_count'] = 0
            
            if 'saved_segments' not in st.session_state:
                st.session_state.saved_segments = []
            
            st.session_state.saved_segments.append(segment_data)
            st.success(f"✅ Imported segment: {segment_data.get('name')}")
            st.rerun()
            
        except Exception as e:
            st.error(f"Error importing segment: {str(e)}")