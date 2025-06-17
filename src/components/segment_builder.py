import streamlit as st
import streamlit.components.v1 as components
from src.database.queries import get_segment_statistics, save_segment, load_saved_segments
import plotly.graph_objects as go
from datetime import datetime
import uuid
import json

# Import UI builders
try:
    from src.components.react_segment_builder import render_react_segment_builder
    REACT_AVAILABLE = True
except ImportError:
    REACT_AVAILABLE = False

try:
    from src.components.blockly_segment_builder import render_blockly_segment_builder
    BLOCKLY_AVAILABLE = True
except ImportError:
    BLOCKLY_AVAILABLE = False

try:
    from src.components.visual_query_builder import render_visual_query_builder
    VISUAL_AVAILABLE = True
except ImportError:
    VISUAL_AVAILABLE = False

def render_segment_builder(config):
    """Render the main segment builder interface with enhanced UI"""
    
    # Custom CSS - COMPLETE LIGHT THEME WITH FIXED INPUTS
    st.markdown("""
    <style>
    /* Force light theme everywhere - NO DARK BACKGROUNDS */
    * {
        --primary-color: #1473E6 !important;
        --primary-hover: #0D66D0 !important;
        --text-dark: #2C2C2C !important;
        --text-light: #6E6E6E !important;
        --bg-white: #FFFFFF !important;
        --bg-light: #F5F5F5 !important;
        --bg-lighter: #FAFAFA !important;
        --border-color: #E1E1E1 !important;
        --border-dark: #D3D3D3 !important;
    }
    
    /* Global overrides - NO BLACK BACKGROUNDS */
    .stApp {
        background-color: var(--bg-light) !important;
    }
    
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* Fix ALL inputs, textareas, and selects - WHITE BACKGROUNDS ONLY */
    input, textarea, select,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    [data-baseweb="input"],
    [data-baseweb="textarea"],
    [data-baseweb="select"] {
        background-color: var(--bg-white) !important;
        color: var(--text-dark) !important;
        border: 1px solid var(--border-dark) !important;
        cursor: text !important;
    }
    
    /* Fix dark description box specifically */
    textarea[aria-label="Description"],
    textarea[placeholder*="Describe"],
    .stTextArea textarea {
        background-color: var(--bg-white) !important;
        color: var(--text-dark) !important;
        cursor: text !important;
    }
    
    /* CRITICAL: Fix disabled state */
    input:disabled,
    textarea:disabled,
    select:disabled,
    .stTextInput input:disabled,
    .stTextArea textarea:disabled {
        background-color: #F0F0F0 !important;
        color: #999999 !important;
        cursor: not-allowed !important;
        opacity: 0.6 !important;
    }
    
    /* Fix ALL buttons - NO DARK BACKGROUNDS */
    button,
    .stButton > button,
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-primary"],
    [role="button"] {
        background-color: var(--bg-white) !important;
        color: var(--text-dark) !important;
        border: 1px solid var(--border-dark) !important;
        cursor: pointer !important;
    }
    
    button:hover,
    .stButton > button:hover {
        background-color: var(--bg-lighter) !important;
        border-color: var(--primary-color) !important;
        color: var(--primary-color) !important;
    }
    
    /* Primary buttons - Light blue */
    .stButton > button[type="primary"],
    .stButton > button[kind="primary"],
    button.primary {
        background-color: #E8F5FF !important;
        color: var(--primary-color) !important;
        border: 1px solid var(--primary-color) !important;
        font-weight: 600 !important;
    }
    
    .stButton > button[type="primary"]:hover,
    .stButton > button[kind="primary"]:hover {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    
    /* Fix segment visualization */
    .segment-viz-container {
        background: var(--bg-white) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px;
        padding: 16px;
        text-align: center;
        margin-top: 0;
    }
    
    .segment-match-percentage {
        font-size: 36px !important;
        font-weight: 700 !important;
        color: var(--primary-color) !important;
        margin: 8px 0 !important;
        line-height: 1 !important;
    }
    
    .segment-match-label {
        font-size: 12px;
        color: var(--text-light);
        margin-bottom: 12px;
    }
    
    .segment-metrics {
        display: flex;
        justify-content: space-around;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid var(--border-color);
    }
    
    .metric-item {
        text-align: center;
    }
    
    .metric-value {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-dark);
    }
    
    .metric-label {
        font-size: 11px;
        color: var(--text-light);
        margin-top: 2px;
    }
    
    /* Labels */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stNumberInput > label,
    label {
        color: var(--text-dark) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        background: transparent !important;
    }
    
    /* Container styling */
    .segment-container {
        background: var(--bg-white) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        padding: 12px !important;
        margin: 8px 0 !important;
        position: relative !important;
    }
    
    .segment-container::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: #FF6B00;
        border-radius: 4px 0 0 4px;
    }
    
    /* Radio buttons */
    .stRadio > div {
        gap: 16px !important;
        background: transparent !important;
    }
    
    .stRadio > div > label {
        font-size: 13px !important;
        color: var(--text-dark) !important;
        background: transparent !important;
        cursor: pointer !important;
    }
    
    /* Include/Exclude dots */
    .include-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #12B886;
    }
    
    .exclude-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #E34850;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-dark) !important;
    }
    
    /* Required field note */
    .required-note {
        font-size: 11px;
        color: var(--text-light);
        margin-bottom: 12px;
    }
    
    /* Fix ALL dropdowns and select boxes */
    [data-baseweb="select"] > div,
    [role="listbox"],
    [role="option"],
    .stSelectbox > div > div,
    .stSelectbox > div > div > div {
        background-color: var(--bg-white) !important;
        color: var(--text-dark) !important;
        cursor: pointer !important;
    }
    
    [role="option"]:hover {
        background-color: var(--bg-lighter) !important;
    }
    
    /* Fix Cancel button - Light style */
    .stButton > button[key="cancel_segment_btn"] {
        background-color: var(--bg-white) !important;
        color: var(--text-dark) !important;
        border: 2px solid var(--border-dark) !important;
        padding: 10px 24px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button[key="cancel_segment_btn"]:hover {
        background-color: #FFF5F5 !important;
        border-color: #E34850 !important;
        color: #E34850 !important;
    }
    
    /* Fix Save button - Light blue */
    .stButton > button[key="save_segment_btn"] {
        background: #E8F5FF !important;
        color: var(--primary-color) !important;
        border: 2px solid var(--primary-color) !important;
        padding: 10px 32px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button[key="save_segment_btn"]:hover {
        background: var(--primary-color) !important;
        color: white !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 6px rgba(20, 115, 230, 0.3) !important;
    }
    
    /* Definition area */
    .definition-area {
        background-color: var(--bg-white) !important;
        border: 1px solid var(--border-color) !important;
        padding: 16px !important;
        border-radius: 4px !important;
    }
    
    /* Ensure all inputs are enabled */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select {
        pointer-events: auto !important;
        cursor: text !important;
    }
    
    /* Fix cursor for selects */
    select,
    .stSelectbox select {
        cursor: pointer !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header section with tighter layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Title input - ENSURE IT'S ENABLED
        segment_title = st.text_input(
            "Title*", 
            value=st.session_state.segment_definition.get('name', 'New Segment'),
            placeholder="Enter segment name",
            help="Give your segment a descriptive name",
            key="segment_title_input",
            disabled=False  # Explicitly set to False
        )
        # Update the session state immediately
        st.session_state.segment_definition['name'] = segment_title
        
        # Description textarea - ENSURE IT'S ENABLED
        segment_description = st.text_area(
            "Description",
            value=st.session_state.segment_definition.get('description', ''),
            placeholder="Describe what this segment captures",
            height=50,
            help="Optional: Describe the purpose of this segment",
            key="segment_description_input",
            disabled=False  # Explicitly set to False
        )
        # Update the session state immediately
        st.session_state.segment_definition['description'] = segment_description
    
    with col2:
        # Segment visualization with DYNAMIC calculation
        render_enhanced_segment_visualization()
    
    # Definition section
    st.markdown("### Definition*")
    
    # UI Mode Selector
    st.markdown('<div class="ui-mode-container">', unsafe_allow_html=True)
    st.markdown('<div class="ui-mode-label">Builder Interface</div>', unsafe_allow_html=True)
    
    # Build UI mode options
    ui_modes = []
    ui_descriptions = {}
    
    # Add all available UI modes
    if REACT_AVAILABLE:
        ui_modes.append("Drag & Drop Builder")
        ui_descriptions["Drag & Drop Builder"] = "Adobe Analytics style drag-and-drop"
    
    if VISUAL_AVAILABLE:
        ui_modes.append("Visual Query Builder")
        ui_descriptions["Visual Query Builder"] = "Clean visual interface with dropdowns"
    
    if BLOCKLY_AVAILABLE:
        ui_modes.append("Blockly Visual Builder")
        ui_descriptions["Blockly Visual Builder"] = "Visual programming with connecting blocks"
    
    # Always add Standard as fallback
    ui_modes.append("Standard Builder")
    ui_descriptions["Standard Builder"] = "Simple form-based interface"
    
    # Select UI mode
    selected_ui = st.selectbox(
        "Choose your preferred builder interface",
        options=ui_modes,
        index=0,
        format_func=lambda x: f"{x} - {ui_descriptions.get(x, '')}",
        key="ui_mode_selector",
        label_visibility="collapsed",
        disabled=False
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Store the iframe container for message handling
    iframe_placeholder = st.empty()
    
    # Render the selected UI
    if selected_ui == "Drag & Drop Builder" and REACT_AVAILABLE:
        # React Drag & Drop Builder
        with iframe_placeholder.container():
            component_value = render_react_segment_builder(config, st.session_state.segment_definition)
            handle_component_messages()
        
    elif selected_ui == "Visual Query Builder" and VISUAL_AVAILABLE:
        # Visual Query Builder
        with iframe_placeholder.container():
            component_value = render_visual_query_builder(config, st.session_state.segment_definition)
            handle_component_messages()
    
    elif selected_ui == "Blockly Visual Builder" and BLOCKLY_AVAILABLE:
        # Blockly Visual Builder
        with iframe_placeholder.container():
            component_value = render_blockly_segment_builder(config, st.session_state.segment_definition)
            handle_component_messages()
        
    else:
        # Standard Streamlit Builder
        render_standard_builder(config)
    
    # Footer section with Save/Cancel buttons
    st.markdown("---")
    st.markdown('<p class="required-note">* All fields with an asterisk are required in order to save.</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 1.2, 1.2])
    
    with col2:
        # Cancel button - Light style
        if st.button("❌ Cancel", key="cancel_segment_btn", use_container_width=True, help="Discard changes and reset"):
            reset_segment()
    
    with col3:
        # Save button - Light blue style
        if st.button("💾 Save Segment", key="save_segment_btn", type="primary", use_container_width=True, help="Save segment to library"):
            with st.spinner("Saving..."):
                if validate_and_save_segment():
                    st.success("✅ Segment saved successfully!", icon="🎉")
                    st.balloons()
                    # Force refresh to show new segment in sidebar
                    st.rerun()

def handle_component_messages():
    """Handle messages from iframe components"""
    # JavaScript to handle postMessage
    components.html("""
    <script>
    // Listen for messages from iframes
    window.addEventListener('message', function(e) {
        if (e.data && e.data.type === 'segmentUpdate') {
            // Send the segment data to Streamlit
            window.parent.postMessage({
                isStreamlitMessage: true,
                type: 'streamlit:setComponentValue',
                key: 'segment_update',
                value: JSON.stringify(e.data.segment)
            }, '*');
        }
    });
    </script>
    """, height=0)
    
    # Check for segment updates in query params
    if 'segment_update' in st.query_params:
        try:
            segment_data = json.loads(st.query_params['segment_update'])
            st.session_state.segment_definition = segment_data
            st.session_state.preview_data = None
            del st.query_params['segment_update']
            st.rerun()
        except:
            pass

def render_enhanced_segment_visualization():
    """Render an enhanced segment visualization with DYNAMIC calculation and pie chart"""
    import plotly.graph_objects as go
    
    # Check if segment was updated
    if st.session_state.get('segment_updated'):
        st.session_state.preview_data = None
        st.session_state.segment_updated = False
    
    # Get real statistics from database
    stats = get_segment_statistics(st.session_state.segment_definition)
    
    # Use actual calculated values
    total_visitors = stats.get('total_visitors', 100000)
    total_sessions = stats.get('total_sessions', 200000)
    total_hits = stats.get('total_hits', 500000)
    
    matched_visitors = stats.get('visitors', 0)
    matched_sessions = stats.get('sessions', 0)
    matched_hits = stats.get('hits', 0)
    
    # Calculate percentages dynamically
    visitor_percentage = round((matched_visitors / total_visitors * 100) if total_visitors > 0 else 0)
    session_percentage = round((matched_sessions / total_sessions * 100) if total_sessions > 0 else 0)
    hit_percentage = round((matched_hits / total_hits * 100) if total_hits > 0 else 0)
    
    # Create pie chart
    fig = go.Figure()
    
    # Add three pie charts for visitors, sessions, hits
    fig.add_trace(go.Pie(
        values=[matched_visitors, total_visitors - matched_visitors],
        labels=['Matched', 'Not Matched'],
        hole=0.7,
        marker_colors=['#1473E6', '#E8E8E8'],
        textinfo='none',
        hoverinfo='label+percent',
        domain={'x': [0, 0.3], 'y': [0, 1]},
        name='Visitors'
    ))
    
    fig.add_trace(go.Pie(
        values=[matched_sessions, total_sessions - matched_sessions],
        labels=['Matched', 'Not Matched'],
        hole=0.7,
        marker_colors=['#44B556', '#E8E8E8'],
        textinfo='none',
        hoverinfo='label+percent',
        domain={'x': [0.35, 0.65], 'y': [0, 1]},
        name='Sessions'
    ))
    
    fig.add_trace(go.Pie(
        values=[matched_hits, total_hits - matched_hits],
        labels=['Matched', 'Not Matched'],
        hole=0.7,
        marker_colors=['#FF6B00', '#E8E8E8'],
        textinfo='none',
        hoverinfo='label+percent',
        domain={'x': [0.7, 1], 'y': [0, 1]},
        name='Hits'
    ))
    
    # Add center text for each pie
    fig.add_annotation(x=0.15, y=0.5, text=f"<b>{visitor_percentage}%</b><br>Visitors", 
                      showarrow=False, font=dict(size=14, color='#1473E6'))
    fig.add_annotation(x=0.5, y=0.5, text=f"<b>{session_percentage}%</b><br>Sessions", 
                      showarrow=False, font=dict(size=14, color='#44B556'))
    fig.add_annotation(x=0.85, y=0.5, text=f"<b>{hit_percentage}%</b><br>Hits", 
                      showarrow=False, font=dict(size=14, color='#FF6B00'))
    
    fig.update_layout(
        showlegend=False,
        height=150,
        margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Render the visualization
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Show actual numbers below
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Visitors", f"{matched_visitors:,}", f"{visitor_percentage}%", label_visibility="collapsed")
    with col2:
        st.metric("Sessions", f"{matched_sessions:,}", f"{session_percentage}%", label_visibility="collapsed")
    with col3:
        st.metric("Hits", f"{matched_hits:,}", f"{hit_percentage}%", label_visibility="collapsed")

def render_standard_builder(config):
    """Render the standard Streamlit-based builder"""
    # Container type selector - MAKE SURE IT'S NOT DISABLED
    container_type = st.selectbox(
        "Container Type",
        options=['hit', 'visit', 'visitor'],
        format_func=lambda x: {
            'hit': 'Hit (Page View)',
            'visit': 'Visit (Session)',
            'visitor': 'Visitor'
        }.get(x, x),
        index=['hit', 'visit', 'visitor'].index(st.session_state.segment_definition.get('container_type', 'hit')),
        key="main_container_type",
        disabled=False
    )
    st.session_state.segment_definition['container_type'] = container_type
    
    # Definition area for adding containers - EDITABLE
    with st.container():
        # Containers area
        containers = st.session_state.segment_definition.get('containers', [])
        
        if not containers:
            # Empty state
            st.info("👆 Click the + button next to items in the left panel to add conditions, or click 'Add Container' below")
            
            if st.button("➕ Add Container", key="add_first_container_standard"):
                add_new_container()
                st.rerun()
        else:
            # Render existing containers
            for idx, container in enumerate(containers):
                render_container(container, idx, config, containers)
            
            if st.button("➕ Add Container", key="add_another_container_standard"):
                add_new_container()
                st.rerun()

def render_container(container, idx, config, container_list, level=0):
    """Render a single container with improved UI"""
    container_id = container.get('id', f"container_{idx}")

    indent = f"margin-left: {level * 20}px;" if level > 0 else ""

    with st.container():
        st.markdown(f'<div class="segment-container" style="{indent}">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            # Include/Exclude radio
            include_mode = st.radio(
                "Mode",
                options=["Include", "Exclude"],
                key=f"{container_id}_mode",
                index=0 if container.get('include', True) else 1,
                horizontal=True,
                label_visibility="collapsed"
            )
            container['include'] = (include_mode == "Include")
        
        with col2:
            # Container type
            container['type'] = st.selectbox(
                "Type",
                options=['hit', 'visit', 'visitor'],
                format_func=lambda x: {
                    'hit': 'Hit',
                    'visit': 'Visit',
                    'visitor': 'Visitor'
                }.get(x, x),
                key=f"{container_id}_type",
                index=['hit', 'visit', 'visitor'].index(container.get('type', 'hit')),
                label_visibility="collapsed",
                disabled=False
            )
        
        with col3:
            # Logic operator for top-level containers
            if level == 0 and len(st.session_state.segment_definition['containers']) > 1 and idx > 0:
                st.session_state.segment_definition['logic'] = st.selectbox(
                    "Logic",
                    options=['and', 'or'],
                    key=f"segment_logic_{idx}",
                    format_func=lambda x: x.upper(),
                    label_visibility="collapsed",
                    disabled=False
                )
        
        with col4:
            if st.button("✕", key=f"{container_id}_remove", help="Remove container"):
                container_list.pop(idx)
                st.session_state.preview_data = None
                st.rerun()
        
        # Conditions
        conditions = container.get('conditions', [])
        if conditions:
            for cond_idx, condition in enumerate(conditions):
                if cond_idx > 0:
                    # Logic operator between conditions
                    container['logic'] = st.selectbox(
                        "Logic",
                        options=['and', 'or', 'then'],
                        key=f"{container_id}_logic_{cond_idx}",
                        format_func=lambda x: x.upper(),
                        index=['and', 'or', 'then'].index(container.get('logic', 'and')),
                        label_visibility="collapsed",
                        disabled=False
                    )

                render_condition(condition, container, cond_idx, config, container_id)
        else:
            st.info("Add conditions using the + button in the left panel")

        # Child containers
        children = container.get('children', [])
        for c_idx, child in enumerate(children):
            render_container(child, c_idx, config, children, level+1)

        if st.button("➕ Add Subcontainer", key=f"{container_id}_add_child"):
            add_new_container(parent=container)
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

def render_condition(condition, container, condition_idx, config, container_id):
    """Render a single condition"""
    col1, col2, col3, col4 = st.columns([3, 2, 2, 0.5])
    
    with col1:
        # Field display
        field_display = condition.get('name', 'Select field')
        field_type = "📊" if condition.get('type') == 'dimension' else "📈"
        st.markdown(f"**{field_type} {field_display}**")
    
    with col2:
        # Operator selector
        data_type = condition.get('data_type', 'string')
        operators = config['operators'].get(data_type, ['equals'])
        
        condition['operator'] = st.selectbox(
            "Operator",
            options=operators,
            key=f"{container_id}_operator_{condition_idx}",
            index=operators.index(condition.get('operator', 'equals')) if condition.get('operator', 'equals') in operators else 0,
            label_visibility="collapsed",
            disabled=False
        )
    
    with col3:
        # Value input
        if condition['operator'] not in ['exists', 'does not exist']:
            if data_type == 'number':
                condition['value'] = st.number_input(
                    "Value",
                    key=f"{container_id}_value_{condition_idx}",
                    value=float(condition.get('value', 0)) if condition.get('value') else 0.0,
                    label_visibility="collapsed",
                    disabled=False
                )
            else:
                condition['value'] = st.text_input(
                    "Value",
                    value=str(condition.get('value', '')),
                    placeholder="Enter value",
                    key=f"{container_id}_value_{condition_idx}",
                    label_visibility="collapsed",
                    disabled=False
                )
    
    with col4:
        if st.button("✕", key=f"{container_id}_remove_cond_{condition_idx}", help="Remove"):
            container['conditions'].pop(condition_idx)
            st.session_state.preview_data = None
            st.rerun()

def add_new_container(parent=None):
    """Add a new container to the segment"""
    new_container = {
        'id': f'container_{uuid.uuid4().hex[:8]}',
        'type': st.session_state.segment_definition.get('container_type', 'hit'),
        'include': True,
        'conditions': [],
        'children': [],
        'logic': 'and'
    }

    if parent is None:
        if 'containers' not in st.session_state.segment_definition:
            st.session_state.segment_definition['containers'] = []
        st.session_state.segment_definition['containers'].append(new_container)
    else:
        parent.setdefault('children', []).append(new_container)

    st.session_state.preview_data = None

def iter_all_containers(cont_list):
    """Yield all containers recursively"""
    for c in cont_list:
        yield c
        if c.get('children'):
            yield from iter_all_containers(c['children'])

def reset_segment():
    """Reset segment to initial state"""
    st.session_state.segment_definition = {
        'name': 'New Segment',
        'description': '',
        'container_type': 'visit',
        'containers': [],
        'logic': 'and'
    }
    st.session_state.preview_data = None
    st.rerun()

def validate_and_save_segment():
    """Validate and save the segment to database - FIXED VALIDATION"""
    from src.utils.validators import validate_segment
    
    # Get current segment definition
    segment_def = st.session_state.segment_definition
    
    # Basic validation
    segment_name = segment_def.get('name', '').strip()
    if not segment_name or segment_name == 'New Segment':
        st.error("Please enter a segment name")
        return False
    
    # Check for containers
    containers = segment_def.get('containers', [])
    if not containers:
        st.error("Please add at least one container with conditions")
        return False
    
    # Check if containers have conditions
    total_conditions = 0
    for container in iter_all_containers(containers):
        conditions = container.get('conditions', [])
        total_conditions += len(conditions)
        
        # Validate each condition has required fields
        for condition in conditions:
            # Check if condition has required fields
            if not condition.get('field'):
                st.error("Each condition must have a field selected")
                return False
            
            if not condition.get('operator'):
                st.error("Each condition must have an operator selected")
                return False
                
            # Check value for operators that require it
            if condition.get('operator') not in ['exists', 'does not exist']:
                value = condition.get('value')
                if value is None or str(value).strip() == '':
                    st.error(f"Please enter a value for the condition: {condition.get('name', 'Unknown field')}")
                    return False
    
    if total_conditions == 0:
        st.error("Please add at least one condition to your containers")
        return False
    
    # Additional validation using validators
    if not validate_segment(segment_def):
        st.error("Segment validation failed. Please check all fields are complete.")
        return False
    
    try:
        # Save to database
        success, message = save_segment(segment_def)
        
        if success:
            # Force clear any cached data
            if hasattr(st, '_clear_cache'):
                st._clear_cache()

            # Add success flag to session state
            st.session_state.segment_saved = True
            st.session_state.last_saved_segment = segment_def.get('name')
            st.session_state.preview_data = None
            st.session_state.last_preview_segment = None

            # Refresh sidebar segment list from the database
            try:
                st.session_state.db_segments = load_saved_segments()
            except Exception:
                st.session_state.db_segments = []

            return True
        else:
            st.error(f"Failed to save segment: {message}")
            return False
            
    except Exception as e:
        st.error(f"Error saving segment: {str(e)}")
        return False