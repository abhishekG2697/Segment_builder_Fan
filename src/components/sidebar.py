import streamlit as st
import uuid
from src.database.queries import load_saved_segments

def render_sidebar(config):
    """Render the sidebar with enhanced UI and better functionality"""

    st.markdown("""
    <style>
    /* Force light theme everywhere */
    :root {
        --primary-color: #1473E6 !important;
        --text-dark: #2C2C2C !important;
        --text-light: #6E6E6E !important;
        --bg-white: #FFFFFF !important;
        --bg-light: #F5F5F5 !important;
        --border-color: #E1E1E1 !important;
    }
    
    /* Compact sidebar styling */
    section[data-testid="stSidebar"] {
        width: 300px !important;
        background: #FFFFFF !important;
        border-right: 1px solid #E8E8E8;
    }
    
    section[data-testid="stSidebar"] > div {
        padding: 12px;
        background-color: #FFFFFF !important;
    }
    
    /* Remove default spacing */
    section[data-testid="stSidebar"] .block-container {
        padding: 0;
    }
    
    /* Fix ALL sidebar buttons - WHITE BACKGROUNDS ONLY */
    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] .stButton > button {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
        border: 1px solid #D3D3D3 !important;
        cursor: pointer !important;
    }
    
    section[data-testid="stSidebar"] button:hover,
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #F0F8FF !important;
        border-color: #1473E6 !important;
        color: #1473E6 !important;
    }
    
    /* Fix "+" buttons specifically - WHITE BACKGROUND, DARK SYMBOL */
    section[data-testid="stSidebar"] button[key*="add"],
    section[data-testid="stSidebar"] button[title*="Add"],
    section[data-testid="stSidebar"] button:has(➕) {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
        border: 1px solid #D3D3D3 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        padding: 4px 8px !important;
        min-width: 32px !important;
        height: 32px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
    }
    
    section[data-testid="stSidebar"] button[key*="add"]:hover {
        background-color: #E8F5FF !important;
        border-color: #1473E6 !important;
        color: #1473E6 !important;
        transform: scale(1.1);
    }
    
    /* Search box styling */
    .sidebar-search {
        position: sticky;
        top: 0;
        background: white;
        z-index: 100;
        padding-bottom: 12px;
        border-bottom: 1px solid #E8E8E8;
        margin-bottom: 12px;
    }
    
    /* Fix search input background */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
        border: 1px solid #D3D3D3 !important;
        cursor: text !important;
    }
    
    /* Component sections */
    .component-section {
        margin-bottom: 8px;
    }
    
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        background: #F8F8F8;
        cursor: pointer;
        user-select: none;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        color: #323232;
        letter-spacing: 0.5px;
        margin: 0 -12px;
    }
    
    .section-header:hover {
        background: #F0F0F0;
    }
    
    .section-count {
        color: #E34850;
        font-weight: 700;
        font-size: 14px;
    }
    
    /* Component items - ultra compact */
    .component-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 8px;
        margin: 2px 0;
        background: #FFFFFF;
        border: 1px solid #E8E8E8;
        border-radius: 3px;
        cursor: grab;
        transition: all 0.15s ease;
        font-size: 13px;
        min-height: 32px;
    }
    
    .component-item:hover {
        background: #F0F8FF;
        border-color: #1473E6;
        transform: translateX(2px);
        box-shadow: 0 1px 3px rgba(20, 115, 230, 0.15);
    }
    
    .component-item:active {
        cursor: grabbing;
    }
    
    .component-name {
        display: flex;
        align-items: center;
        gap: 6px;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        color: #2C2C2C !important;
    }
    
    .component-icon {
        font-size: 14px;
        flex-shrink: 0;
    }
    
    /* Segment items - special styling */
    .segment-item {
        padding: 8px;
        background: #FAFAFA;
        border-left: 3px solid #6B46C1;
    }
    
    .segment-item:hover {
        background: #F5F0FF;
        border-left-color: #553C9A;
    }
    
    .segment-description {
        font-size: 11px;
        color: #6E6E6E;
        margin-top: 2px;
        line-height: 1.3;
    }
    
    /* Remove Streamlit expander styling */
    .streamlit-expanderHeader {
        display: none !important;
    }
    
    /* Custom expander content */
    .streamlit-expanderContent {
        padding: 0 !important;
        border: none !important;
        margin-top: 8px !important;
    }
    
    /* Filter dropdown */
    .filter-select {
        font-size: 12px;
        padding: 4px 8px;
        border: 1px solid #E8E8E8;
        border-radius: 3px;
        margin-bottom: 8px;
    }
    
    /* Scrollbar styling */
    section[data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 6px;
    }
    
    section[data-testid="stSidebar"] ::-webkit-scrollbar-track {
        background: #F5F5F5;
    }
    
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
        background: #D3D3D3;
        border-radius: 3px;
    }
    
    /* Fix selectbox backgrounds in sidebar */
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #FFFFFF !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div > div {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
    }
    
    /* Ensure all text in sidebar is dark */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] label {
        color: #2C2C2C !important;
    }
    
    /* Override any remaining dark backgrounds */
    section[data-testid="stSidebar"] [style*="background-color: rgb(38, 39, 48)"],
    section[data-testid="stSidebar"] [style*="background-color: rgb(49, 51, 63)"],
    section[data-testid="stSidebar"] [style*="background: rgb(38, 39, 48)"],
    section[data-testid="stSidebar"] [style*="background: rgb(49, 51, 63)"] {
        background-color: #FFFFFF !important;
    }
    </style>

    """, unsafe_allow_html=True)

    # Load segments from the database so they are available in the sidebar
    try:
        st.session_state.db_segments = load_saved_segments()
    except Exception:
        st.session_state.db_segments = []
    
    # Search functionality - WORKING
    search_query = st.text_input(
        "🔍", 
        placeholder="Search components...",
        key="sidebar_search_input",
        label_visibility="collapsed"
    ).lower()  # Convert to lowercase for case-insensitive search
    
    # Filter dropdown
    filter_option = st.selectbox(
        "Filter",
        ["All Components", "Dimensions", "Metrics", "Segments"],
        key="sidebar_filter",
        label_visibility="collapsed"
    )
    
    # Pre-built segment definitions with correct field mappings
    segment_definitions = {
        'High Value Customers': {
            'name': 'High Value Customers',
            'description': 'Visitors with revenue > $500',
            'container_type': 'visitor',
            'containers': [{
                'id': 'container_high_value_1',
                'type': 'visitor',
                'include': True,
                'conditions': [{
                    'id': 'cond_revenue_1',
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
        },
        'Mobile Users': {
            'name': 'Mobile Users',
            'description': 'All mobile device traffic',
            'container_type': 'hit',
            'containers': [{
                'id': 'container_mobile_1',
                'type': 'hit',
                'include': True,
                'conditions': [{
                    'id': 'cond_device_1',
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
        },
        'Engaged Sessions': {
            'name': 'Engaged Sessions',
            'description': 'Sessions with 5+ pages viewed',
            'container_type': 'visit',
            'containers': [{
                'id': 'container_engaged_1',
                'type': 'visit',
                'include': True,
                'conditions': [{
                    'id': 'cond_pageviews_1',
                    'field': 'pages_viewed',
                    'name': 'Pages Viewed',
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
    }
    
    # Create sections based on filter
    sections = []
    
    if filter_option in ["All Components", "Dimensions"]:
        dimensions_data = []
        for category in config.get('dimensions', []):
            for item in category['items']:
                # Apply search filter
                if not search_query or search_query in item['name'].lower():
                    dimensions_data.append({
                        'item': item,
                        'category': category['category'],
                        'type': 'dimension'
                    })
        if dimensions_data:
            sections.append(('dimensions', dimensions_data))
    
    if filter_option in ["All Components", "Metrics"]:
        metrics_data = []
        for category in config.get('metrics', []):
            for item in category['items']:
                # Apply search filter
                if not search_query or search_query in item['name'].lower():
                    metrics_data.append({
                        'item': item,
                        'category': category['category'],
                        'type': 'metric'
                    })
        if metrics_data:
            sections.append(('metrics', metrics_data))
    
    if filter_option in ["All Components", "Segments"]:
        segments_data = []
        
        # Start with config segments
        all_segments = list(config.get('segments', []))
        
        # Add database segments
        if 'db_segments' in st.session_state:
            for db_seg in st.session_state.db_segments:
                # Check if not already in list
                if not any(s['name'] == db_seg['name'] for s in all_segments):
                    all_segments.append(db_seg)
        
        # Process all segments
        for segment in all_segments:
            # Apply search filter - check both name and description
            segment_name = segment.get('name', '').lower()
            segment_desc = segment.get('description', '').lower()
            
            if search_query and search_query not in segment_name and search_query not in segment_desc:
                continue
                
            segment_with_def = segment.copy()
            
            # Get definition from various sources
            if 'definition' in segment:
                # Already has definition
                pass
            elif segment['name'] in segment_definitions:
                segment_with_def['definition'] = segment_definitions[segment['name']]
            
            segments_data.append({
                'item': segment_with_def,
                'type': 'segment'
            })
        
        if segments_data:
            sections.append(('segments', segments_data))
    
    # Render sections
    for section_type, items in sections:
        if section_type == 'dimensions':
            render_section("DIMENSIONS", items, "📊", "#5B9BD5")
        elif section_type == 'metrics':
            render_section("METRICS", items, "📈", "#70AD47")
        elif section_type == 'segments':
            render_section("SEGMENTS", items, "🎯", "#7C4DFF")

def render_section(title, items, icon, color):
    """Render a collapsible section with items"""
    section_key = f"section_{title.lower()}"
    
    # Create custom expander
    with st.container():
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div class="section-header">
                <span>{icon} {title}</span>
                <span class="section-count">{len(items)}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Items container
        with st.expander("", expanded=True):
            for item_data in items:
                if item_data['type'] == 'segment':
                    render_segment_item(item_data['item'])
                else:
                    render_component_item(item_data)

def render_component_item(item_data):
    """Render a dimension or metric item"""
    item = item_data['item']
    item_type = item_data['type']
    category = item_data['category']
    
    item_id = f"{item_type}_{item['field']}_{uuid.uuid4().hex[:6]}"
    
    col1, col2 = st.columns([10, 1])
    
    with col1:
        icon = "📊" if item_type == 'dimension' else "📈"
        st.markdown(f"""
        <div class="component-item" draggable="true" data-item='{item_id}'>
            <div class="component-name">
                <span class="component-icon">{icon}</span>
                <span>{item['name']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Fixed button with unique key and proper styling
        button_key = f"add_{item_id}"
        if st.button("➕", key=button_key, help=f"Add {item['name']}", use_container_width=True):
            add_to_segment(item, item_type, category)

def render_segment_item(segment):
    """Render a segment item with description"""
    segment_id = f"seg_{segment['name'].replace(' ', '_')}_{uuid.uuid4().hex[:6]}"
    
    col1, col2 = st.columns([10, 1])
    
    with col1:
        st.markdown(f"""
        <div class="component-item segment-item" draggable="true" data-segment='{segment_id}'>
            <div>
                <div class="component-name">
                    <span class="component-icon">🎯</span>
                    <span>{segment['name']}</span>
                </div>
                <div class="segment-description">{segment['description']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Fixed button with unique key
        button_key = f"add_{segment_id}"
        if st.button("➕", key=button_key, help=f"Add {segment['name']}", use_container_width=True):
            add_segment_to_builder(segment)

def add_to_segment(item, item_type, category):
    """Add a dimension or metric to the current segment - FIXED TO WORK PROPERLY"""
    # Create a properly structured condition
    new_condition = {
        'id': f"{item_type}_{item['field']}_{uuid.uuid4().hex[:8]}",
        'field': item['field'],
        'name': item['name'],
        'type': item_type,
        'category': category,
        'operator': 'equals',
        'value': '',
        'data_type': item.get('type', 'string')
    }
    
    # Initialize containers if needed
    if 'segment_definition' not in st.session_state:
        st.session_state.segment_definition = {
            'name': 'New Segment',
            'description': '',
            'container_type': 'hit',
            'containers': [],
            'logic': 'and'
        }
    
    # Ensure containers list exists
    if not st.session_state.segment_definition.get('containers'):
        st.session_state.segment_definition['containers'] = []
    
    # If no containers exist, create the first one
    if not st.session_state.segment_definition['containers']:
        first_container = {
            'id': f'container_{uuid.uuid4().hex[:8]}',
            'type': st.session_state.segment_definition.get('container_type', 'hit'),
            'include': True,
            'conditions': [],
            'logic': 'and'
        }
        st.session_state.segment_definition['containers'].append(first_container)
    
    # Add condition to the first container
    st.session_state.segment_definition['containers'][0]['conditions'].append(new_condition)
    
    # Success message and state updates
    st.success(f"✅ Added {item['name']} to segment")
    # Clear preview to force regeneration
    st.session_state.preview_data = None
    # Trigger segment update
    st.session_state.segment_updated = True
    # Force a rerun to update the UI
    st.rerun()

def add_segment_to_builder(segment):
    """Load a pre-built segment to the builder - FIXED"""
    if 'definition' in segment and segment['definition']:
        # Deep copy the segment definition
        import copy
        new_definition = copy.deepcopy(segment['definition'])
        
        # Ensure all required fields are present
        if 'name' not in new_definition:
            new_definition['name'] = segment.get('name', 'Unnamed Segment')
        if 'description' not in new_definition:
            new_definition['description'] = segment.get('description', '')
        if 'container_type' not in new_definition:
            new_definition['container_type'] = 'hit'
        if 'logic' not in new_definition:
            new_definition['logic'] = 'and'
        if 'containers' not in new_definition:
            new_definition['containers'] = []
        
        # Update session state
        st.session_state.segment_definition = new_definition
        # Reset preview selector and clear cached data
        st.session_state.preview_segment_selector = "Current Segment"
        st.session_state.preview_data = None
        st.success(f"✅ Loaded segment: {segment['name']}")
        # Force rerun
        st.rerun()
    else:
        st.error(f"Segment {segment['name']} has no complete definition")