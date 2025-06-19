import streamlit as st
import uuid
import pandas as pd
from typing import Dict, List, Any

# Import functions from other modules
try:
    from src.database.queries import get_segment_statistics, save_segment
except ImportError:
    # Fallback if database module not available
    def get_segment_statistics(segment_definition):
        return {'visitors': 0, 'sessions': 0, 'hits': 0, 'total_visitors': 1, 'total_sessions': 1, 'total_hits': 1}


    def save_segment(segment_data):
        return True

try:
    from src.components.react_segment_builder import render_react_segment_builder

    REACT_AVAILABLE = True
except ImportError:
    REACT_AVAILABLE = False


def render_segment_builder(config):
    """Render the main segment builder interface - FIXED VERSION"""

    # Initialize segment definition
    initialize_segment_definition()

    # Apply Adobe-style CSS
    apply_adobe_styling()

    # Segment header section
    col1, col2 = st.columns([3, 1])

    with col1:
        # Title and Description - FIXED: Removed label_visibility
        st.session_state.segment_definition['name'] = st.text_input(
            "Title *",
            value=st.session_state.segment_definition['name'],
            placeholder="Enter segment name",
            help="Give your segment a descriptive name"
        )

        st.session_state.segment_definition['description'] = st.text_area(
            "Description",
            value=st.session_state.segment_definition['description'],
            placeholder="Enter a description for this segment",
            height=80,
            help="Describe what this segment captures"
        )

    with col2:
        # Segment visualization
        render_segment_visualization()

    # Tags input
    tags_value = st.text_input(
        "Tags",
        placeholder="Search tags",
        help="Add tags to organize your segment",
        value=""
    )

    # Main builder section
    st.markdown("### Definition *")

    # UI Mode Selection
    ui_modes = ["Standard Builder"]
    ui_descriptions = {"Standard Builder": "Simple and reliable form-based interface"}

    # Check for React availability
    if REACT_AVAILABLE:
        ui_modes.insert(0, "Drag & Drop Builder")
        ui_descriptions["Drag & Drop Builder"] = "Adobe Analytics style drag-and-drop interface"

    # UI Mode selector
    if len(ui_modes) > 1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; 
                    border-left: 4px solid #1473e6;">
            <strong>Choose Builder Interface:</strong>
        </div>
        """, unsafe_allow_html=True)

        selected_ui = st.selectbox(
            "Interface",
            options=ui_modes,
            index=0,
            format_func=lambda x: f"{x} - {ui_descriptions.get(x, '')}",
            key="ui_mode_selector"
        )

        # Render the selected UI
        if selected_ui == "Drag & Drop Builder" and REACT_AVAILABLE:
            try:
                render_react_segment_builder(config, st.session_state.segment_definition)
            except Exception as e:
                st.error(f"Error loading drag-and-drop builder: {str(e)}")
                st.info("Falling back to standard builder...")
                render_standard_builder(config)
        else:
            render_standard_builder(config)
    else:
        # Only standard builder available
        render_standard_builder(config)

    # Save/Cancel buttons
    st.markdown("---")
    st.markdown(
        '<p style="color: #6e6e6e; font-size: 12px;">* All fields with an asterisk are required in order to save.</p>',
        unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3, 1.2, 1.2])

    with col2:
        if st.button("❌ Cancel", key="cancel_segment_btn", help="Discard changes and reset"):
            reset_segment()

    with col3:
        if st.button("💾 Save Segment", key="save_segment_btn", type="primary", help="Save segment to library"):
            with st.spinner("Saving..."):
                if validate_and_save_segment():
                    st.success("✅ Segment saved successfully!")
                    st.balloons()


def initialize_segment_definition():
    """Initialize segment definition if it doesn't exist"""
    if 'segment_definition' not in st.session_state:
        st.session_state.segment_definition = {
            'name': '',
            'description': '',
            'container_type': 'hit',
            'logic': 'and',
            'containers': []
        }


def apply_adobe_styling():
    """Apply Adobe Analytics-style CSS"""
    st.markdown("""
    <style>
    /* Adobe Analytics Theme */
    .main .block-container {
        max-width: 100%;
        padding: 1rem 2rem;
    }

    /* Container styles */
    .segment-container {
        background: white;
        border: 1px solid #e1e1e1;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .segment-container:hover {
        border-color: #1473e6;
        box-shadow: 0 2px 8px rgba(20, 115, 230, 0.15);
    }

    /* Condition styles */
    .condition-item {
        background: white;
        border: 1px solid #e1e1e1;
        border-radius: 4px;
        padding: 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.2s ease;
    }

    .condition-item:hover {
        border-color: #1473e6;
        box-shadow: 0 2px 8px rgba(20, 115, 230, 0.1);
    }

    /* Nested container styles */
    .nested-container {
        margin-left: 24px;
        padding-left: 16px;
        border-left: 3px solid #1473e6;
        margin-top: 12px;
        position: relative;
    }

    .nested-container::before {
        content: '';
        position: absolute;
        left: -12px;
        top: 20px;
        width: 12px;
        height: 2px;
        background: #1473e6;
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #6e6e6e;
        border: 2px dashed #d3d3d3;
        border-radius: 12px;
        background: #fafafa;
        margin: 20px 0;
    }

    .empty-state-icon {
        font-size: 64px;
        margin-bottom: 20px;
        opacity: 0.7;
    }

    .empty-state-text {
        font-size: 16px;
        line-height: 1.5;
        color: #6e6e6e;
    }
    </style>
    """, unsafe_allow_html=True)


def render_standard_builder(config):
    """Render the standard Streamlit builder - FIXED VERSION"""

    # Container type selector
    container_type = st.selectbox(
        "Container Type",
        options=['hit', 'visit', 'visitor'],
        format_func=lambda x: {
            'hit': 'Hit (Page View)',
            'visit': 'Visit (Session)',
            'visitor': 'Visitor'
        }.get(x, x),
        index=['hit', 'visit', 'visitor'].index(
            st.session_state.segment_definition.get('container_type', 'hit')
        ),
        key="main_container_type"
    )
    st.session_state.segment_definition['container_type'] = container_type

    # Display existing containers
    containers = st.session_state.segment_definition.get('containers', [])

    if not containers:
        # Empty state
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🎯</div>
            <div class="empty-state-text">
                <strong>No conditions defined</strong><br>
                Click the + button next to components in the left panel to add conditions<br>
                or click "Add Container" below to start building
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕ Add Container", key="add_first_container", type="primary"):
            add_new_container()
            st.rerun()
    else:
        # Render existing containers with nesting support
        for idx, container in enumerate(containers):
            render_container(container, idx, config, containers, level=0)

        # Add container button
        if st.button("➕ Add Container", key="add_another_container"):
            add_new_container()
            st.rerun()


def render_container(container: Dict, idx: int, config: Dict, container_list: List, level: int = 0):
    """Render container with nested support - FIXED VERSION"""

    container_id = container.get('id', f"container_{idx}")

    # Apply nesting style
    if level > 0:
        st.markdown(f'<div class="nested-container">', unsafe_allow_html=True)

    st.markdown('<div class="segment-container">', unsafe_allow_html=True)

    # Container header
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    with col1:
        # Include/Exclude radio - FIXED: No label_visibility
        include_mode = st.radio(
            "Mode",
            options=["Include", "Exclude"],
            key=f"{container_id}_mode_{level}",
            index=0 if container.get('include', True) else 1,
            horizontal=True
        )
        container['include'] = (include_mode == "Include")

    with col2:
        # Container type - FIXED: No label_visibility
        container['type'] = st.selectbox(
            "Type",
            options=['hit', 'visit', 'visitor'],
            format_func=lambda x: {
                'hit': 'Hit',
                'visit': 'Visit',
                'visitor': 'Visitor'
            }.get(x, x),
            key=f"{container_id}_type_{level}",
            index=['hit', 'visit', 'visitor'].index(container.get('type', 'hit'))
        )

    with col3:
        # Logic operator for multiple containers
        if level == 0 and len(st.session_state.segment_definition['containers']) > 1 and idx > 0:
            st.session_state.segment_definition['logic'] = st.selectbox(
                "Logic",
                options=['and', 'or'],
                key=f"segment_logic_{idx}_{level}",
                format_func=lambda x: x.upper()
            )

    with col4:
        # Remove container button
        if st.button("✕", key=f"{container_id}_remove_{level}", help="Remove container"):
            container_list.pop(idx)
            if 'preview_data' in st.session_state:
                st.session_state.preview_data = None
            st.rerun()

    # Container content
    conditions = container.get('conditions', [])
    children = container.get('children', [])

    if conditions:
        # Render conditions
        for cond_idx, condition in enumerate(conditions):
            if cond_idx > 0:
                # Logic operator between conditions
                container['logic'] = st.selectbox(
                    "Condition Logic",
                    options=['and', 'or', 'then'],
                    key=f"{container_id}_logic_{cond_idx}_{level}",
                    format_func=lambda x: x.upper(),
                    index=['and', 'or', 'then'].index(container.get('logic', 'and'))
                )

            render_condition(condition, container_id, cond_idx, config, level)

    # Render nested containers
    if children:
        st.markdown("**Nested Containers:**")
        for child_idx, child_container in enumerate(children):
            render_container(child_container, child_idx, config, children, level + 1)

    # Add nested container button
    if st.button(f"➕ Add Nested Container", key=f"{container_id}_add_nested_{level}"):
        add_nested_container(container)
        st.rerun()

    # Show info if no conditions
    if not conditions and not children:
        st.info("No conditions. Add items from the left panel using the + buttons.")

    st.markdown('</div>', unsafe_allow_html=True)

    if level > 0:
        st.markdown('</div>', unsafe_allow_html=True)


def render_condition(condition: Dict, container_id: str, cond_idx: int, config: Dict, level: int):
    """Render a condition - FIXED VERSION"""

    st.markdown('<div class="condition-item">', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([3, 2, 2, 0.5])

    with col1:
        # Field display with icon
        field_display = condition.get('name', 'Select field')
        field_type = "📊" if condition.get('type') == 'dimension' else "📈"
        st.markdown(f"**{field_type} {field_display}**")

    with col2:
        # Operator selector - FIXED: No label_visibility
        data_type = condition.get('data_type', 'string')
        operators = config.get('operators', {}).get(data_type, ['equals'])

        condition['operator'] = st.selectbox(
            "Operator",
            options=operators,
            key=f"{container_id}_operator_{cond_idx}_{level}",
            index=operators.index(condition.get('operator', 'equals')) if condition.get('operator',
                                                                                        'equals') in operators else 0
        )

    with col3:
        # Value input - FIXED: No label_visibility
        if condition['operator'] not in ['exists', 'does not exist']:
            if data_type == 'number':
                condition['value'] = st.number_input(
                    "Value",
                    key=f"{container_id}_value_{cond_idx}_{level}",
                    value=float(condition.get('value', 0)) if condition.get('value') else 0.0
                )
            else:
                condition['value'] = st.text_input(
                    "Value",
                    value=str(condition.get('value', '')),
                    placeholder="Enter value",
                    key=f"{container_id}_value_{cond_idx}_{level}"
                )

    with col4:
        # Remove condition button
        if st.button("✕", key=f"{container_id}_remove_cond_{cond_idx}_{level}", help="Remove condition"):
            # Find and remove condition
            containers = st.session_state.segment_definition.get('containers', [])
            remove_condition_from_containers(containers, container_id, cond_idx)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_segment_visualization():
    """Render the segment match visualization"""

    # Get segment statistics
    try:
        stats = get_segment_statistics(st.session_state.segment_definition)
    except Exception:
        # Fallback stats if database is not available
        stats = {
            'visitors': 0,
            'sessions': 0,
            'hits': 0,
            'total_visitors': 1,
            'total_sessions': 1,
            'total_hits': 1
        }

    # Calculate percentages
    total_visitors = stats.get('total_visitors', 1)
    total_sessions = stats.get('total_sessions', 1)
    total_hits = stats.get('total_hits', 1)

    matched_visitors = stats.get('visitors', 0)
    matched_sessions = stats.get('sessions', 0)
    matched_hits = stats.get('hits', 0)

    # Calculate percentages
    visitor_percentage = round((matched_visitors / total_visitors) * 100, 1) if total_visitors > 0 else 0
    session_percentage = round((matched_sessions / total_sessions) * 100, 1) if total_sessions > 0 else 0
    hit_percentage = round((matched_hits / total_hits) * 100, 1) if total_hits > 0 else 0

    # Create a simple donut chart representation
    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <div style="font-size: 48px; margin-bottom: 10px;">⭕</div>
        <div style="font-size: 24px; font-weight: bold; color: #1473e6;">
            {visitor_percentage}%
        </div>
        <div style="font-size: 14px; color: #6e6e6e;">
            Visitors
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Show metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Hits", f"{matched_hits:,}", f"{hit_percentage}%")
    with col2:
        st.metric("🔄 Visits", f"{matched_sessions:,}", f"{session_percentage}%")
    with col3:
        st.metric("👥 Visitors", f"{matched_visitors:,}", f"{visitor_percentage}%")


def add_new_container():
    """Add a new container to the segment"""
    new_container = {
        'id': f'container_{uuid.uuid4().hex[:8]}',
        'type': 'hit',
        'include': True,
        'conditions': [],
        'children': [],
        'logic': 'and'
    }

    if 'containers' not in st.session_state.segment_definition:
        st.session_state.segment_definition['containers'] = []

    st.session_state.segment_definition['containers'].append(new_container)


def add_nested_container(parent_container: Dict):
    """Add a nested container to a parent container"""
    nested_container = {
        'id': f'container_{uuid.uuid4().hex[:8]}',
        'type': 'hit',
        'include': True,
        'conditions': [],
        'children': [],
        'logic': 'and'
    }

    if 'children' not in parent_container:
        parent_container['children'] = []

    parent_container['children'].append(nested_container)


def remove_condition_from_containers(containers: List[Dict], container_id: str, condition_idx: int):
    """Remove a condition from containers recursively"""

    for container in containers:
        if container.get('id') == container_id:
            if 0 <= condition_idx < len(container.get('conditions', [])):
                container['conditions'].pop(condition_idx)
                return True

        # Check children
        children = container.get('children', [])
        if children and remove_condition_from_containers(children, container_id, condition_idx):
            return True

    return False


def reset_segment():
    """Reset the segment definition"""
    st.session_state.segment_definition = {
        'name': '',
        'description': '',
        'container_type': 'hit',
        'logic': 'and',
        'containers': []
    }
    if 'preview_data' in st.session_state:
        st.session_state.preview_data = None
    st.rerun()


def validate_and_save_segment():
    """Validate and save the segment"""

    # Validation
    if not st.session_state.segment_definition.get('name'):
        st.error("Segment name is required")
        return False

    if not st.session_state.segment_definition.get('containers'):
        st.error("Segment must have at least one container with conditions")
        return False

    # Check if containers have conditions
    has_conditions = check_containers_have_conditions(st.session_state.segment_definition['containers'])

    if not has_conditions:
        st.error("Segment must have at least one condition")
        return False

    # Save segment
    try:
        # Add metadata
        segment_data = {
            **st.session_state.segment_definition,
            'created_date': pd.Timestamp.now().strftime('%Y-%m-%d'),
            'created_by': 'User',
            'usage_count': 0
        }

        # Save to session state (you can implement database saving here)
        if 'saved_segments' not in st.session_state:
            st.session_state.saved_segments = []

        st.session_state.saved_segments.append(segment_data)

        return True

    except Exception as e:
        st.error(f"Error saving segment: {str(e)}")
        return False


def check_containers_have_conditions(containers: List[Dict]) -> bool:
    """Check if containers have conditions recursively"""

    for container in containers:
        if container.get('conditions'):
            return True

        # Check nested containers
        children = container.get('children', [])
        if children and check_containers_have_conditions(children):
            return True

    return False


# Utility functions for sidebar integration
def add_item_to_segment(item: Dict, item_type: str):
    """Add an item to the segment (called from sidebar)"""

    # Create condition
    condition = {
        'id': f"{item_type}_{item.get('field', uuid.uuid4().hex[:8])}_{uuid.uuid4().hex[:8]}",
        'field': item.get('field', ''),
        'name': item.get('name', 'Unknown'),
        'type': item_type,
        'operator': 'equals',
        'value': '',
        'data_type': item.get('dataType', 'string')
    }

    # Add to segment
    containers = st.session_state.segment_definition.get('containers', [])

    if not containers:
        # Create first container
        add_new_container()
        containers = st.session_state.segment_definition['containers']

    # Add to first container
    containers[0]['conditions'].append(condition)

    # Clear preview data
    if 'preview_data' in st.session_state:
        st.session_state.preview_data = None


def add_segment_to_builder(segment: Dict):
    """Add a pre-built segment to the builder (called from sidebar)"""

    # Check if segment has a complete definition
    if 'definition' in segment and segment['definition']:
        # Load the complete segment definition
        st.session_state.segment_definition = segment['definition'].copy()
    elif 'containers' in segment:
        # Use the segment structure directly
        st.session_state.segment_definition = {
            'name': segment.get('name', 'Imported Segment'),
            'description': segment.get('description', ''),
            'container_type': segment.get('container_type', 'hit'),
            'logic': segment.get('logic', 'and'),
            'containers': segment.get('containers', [])
        }
    else:
        # Create a basic container with the segment as a condition
        new_condition = {
            'id': f"segment_{segment.get('id', uuid.uuid4().hex[:8])}",
            'field': 'segment',
            'name': segment.get('name', 'Unknown Segment'),
            'type': 'segment',
            'operator': 'matches',
            'value': segment.get('id', ''),
            'data_type': 'segment'
        }

        if not st.session_state.segment_definition.get('containers'):
            add_new_container()

        st.session_state.segment_definition['containers'][0]['conditions'].append(new_condition)

    # Clear preview data
    if 'preview_data' in st.session_state:
        st.session_state.preview_data = None