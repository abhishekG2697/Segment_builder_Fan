import streamlit as st
import streamlit.components.v1 as components
import json
import uuid
from typing import Dict, List, Any


def render_sidebar(config: Dict) -> None:
    """
    Render the sidebar with draggable components - COMPATIBILITY FIXED
    """

    # Apply sidebar styling
    st.markdown("""
    <style>
    /* Sidebar Styling */
    .sidebar-section {
        margin-bottom: 24px;
    }

    .sidebar-title {
        font-size: 13px;
        font-weight: 700;
        color: #2c2c2c;
        text-transform: uppercase;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #e1e1e1;
    }

    .sidebar-count {
        background: #6e6e6e;
        color: white;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: 400;
        min-width: 20px;
        text-align: center;
    }

    .sidebar-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        margin-bottom: 2px;
        border-radius: 4px;
        cursor: move;
        transition: all 0.2s ease;
        border: 1px solid transparent;
        background: white;
        user-select: none;
    }

    .sidebar-item:hover {
        background: #f8f9fa;
        border-color: #e1e1e1;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .sidebar-item.dragging {
        opacity: 0.5;
        transform: rotate(3deg);
    }

    .sidebar-item-content {
        display: flex;
        align-items: center;
        flex: 1;
        gap: 8px;
    }

    .sidebar-item-icon {
        font-size: 16px;
        width: 20px;
        text-align: center;
    }

    .sidebar-item-name {
        font-size: 14px;
        color: #2c2c2c;
        font-weight: 400;
    }

    .sidebar-add-btn {
        width: 24px;
        height: 24px;
        border: 1px solid #d3d3d3;
        background: white;
        border-radius: 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #6e6e6e;
        transition: all 0.2s ease;
        font-size: 18px;
        line-height: 1;
    }

    .sidebar-add-btn:hover {
        background: #1473e6;
        color: white;
        border-color: #1473e6;
        transform: scale(1.1);
    }

    /* Collapsible sections */
    .sidebar-collapsible {
        cursor: pointer;
        user-select: none;
    }

    .sidebar-content {
        max-height: 400px;
        overflow-y: auto;
        transition: max-height 0.3s ease;
    }

    .sidebar-content.collapsed {
        max-height: 0;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

    # Get data from config
    dimensions = config.get('dimensions', [])
    metrics = config.get('metrics', [])
    segments = config.get('segments', [])

    # Search box at top
    render_search_box()

    # Filter items based on search
    search_term = st.session_state.get('sidebar_search', '')
    if search_term:
        dimensions = filter_items_by_search(dimensions, search_term)
        metrics = filter_items_by_search(metrics, search_term)
        segments = filter_items_by_search(segments, search_term)

    # Render sections
    render_dimensions_section_fixed(dimensions)
    render_metrics_section_fixed(metrics)

    if segments:
        render_segments_section_fixed(segments)


def render_search_box():
    """Render search box for filtering sidebar items - FIXED VERSION"""

    search_term = st.text_input(
        "Search components...",
        key="sidebar_search",
        placeholder="Type to search dimensions, metrics, segments..."
    )

    if search_term:
        st.session_state.sidebar_search = search_term.lower()
    else:
        st.session_state.sidebar_search = ""


def render_dimensions_section_fixed(dimensions: List[Dict]):
    """Render the dimensions section - COMPATIBILITY FIXED"""

    if not dimensions:
        return

    # Section header - Fixed with expander
    with st.expander(f"📊 DIMENSIONS ({len(dimensions)})", expanded=True):
        # Group dimensions by category
        categories = {}
        for dim in dimensions:
            category = dim.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(dim)

        # Render each category
        for category, items in categories.items():
            if len(categories) > 1:
                st.markdown(f"**{category}**")

            for item in items:
                render_draggable_item_fixed(item, '📊', 'dimension')


def render_metrics_section_fixed(metrics: List[Dict]):
    """Render the metrics section - COMPATIBILITY FIXED"""

    if not metrics:
        return

    # Section header - Fixed with expander
    with st.expander(f"📈 METRICS ({len(metrics)})", expanded=True):
        # Group metrics by category
        categories = {}
        for metric in metrics:
            category = metric.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(metric)

        # Render each category
        for category, items in categories.items():
            if len(categories) > 1:
                st.markdown(f"**{category}**")

            for item in items:
                render_draggable_item_fixed(item, '📈', 'metric')


def render_segments_section_fixed(segments: List[Dict]):
    """Render the segments section - COMPATIBILITY FIXED"""

    if not segments:
        return

    # Section header - Fixed with expander
    with st.expander(f"🎯 SEGMENTS ({len(segments)})", expanded=False):
        for segment in segments:
            render_draggable_segment_fixed(segment)


def render_draggable_item_fixed(item: Dict, icon: str, item_type: str):
    """Render a draggable dimension or metric item - COMPATIBILITY FIXED"""

    item_id = f"{item_type}_{item.get('field', item.get('id', uuid.uuid4().hex[:8]))}"

    # Create columns for layout
    col1, col2 = st.columns([4, 1])

    with col1:
        # Item display
        st.markdown(f"""
        <div class="sidebar-item-content">
            <span class="sidebar-item-icon">{icon}</span>
            <span class="sidebar-item-name">{item.get('name', 'Unknown')}</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Add button - FIXED: No label_visibility
        if st.button("➕", key=f"add_{item_id}", help=f"Add {item.get('name', 'item')} to segment"):
            add_to_segment_fixed(item, item_type)
            st.success(f"✅ Added {item.get('name')} to segment")
            st.rerun()


def render_draggable_segment_fixed(segment: Dict):
    """Render a draggable segment item - COMPATIBILITY FIXED"""

    segment_id = f"segment_{segment.get('id', uuid.uuid4().hex[:8])}"

    # Create columns for layout
    col1, col2 = st.columns([4, 1])

    with col1:
        # Segment display
        st.markdown(f"""
        <div class="sidebar-item-content">
            <span class="sidebar-item-icon">🎯</span>
            <div>
                <div class="sidebar-item-name">{segment.get('name', 'Unknown')}</div>
                {f'<div style="font-size: 12px; color: #6e6e6e;">{segment.get("description", "")[:50]}...</div>' if segment.get('description') else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Add button - FIXED: No label_visibility
        if st.button("➕", key=f"add_{segment_id}", help="Load segment"):
            add_segment_to_builder_fixed(segment)
            st.success(f"✅ Loaded segment: {segment.get('name')}")
            st.rerun()


def add_to_segment_fixed(item: Dict, item_type: str, category: str = ''):
    """Add a dimension or metric to the current segment - COMPATIBILITY FIXED"""

    # Import the function from segment_builder
    from src.components.segment_builder import add_item_to_segment

    try:
        add_item_to_segment(item, item_type)
    except Exception as e:
        st.error(f"Error adding item: {str(e)}")
        # Fallback: manual addition
        add_to_segment_fallback(item, item_type, category)


def add_to_segment_fallback(item: Dict, item_type: str, category: str = ''):
    """Fallback method to add item to segment"""

    new_condition = {
        'id': f"{item_type}_{item.get('field', uuid.uuid4().hex[:8])}_{uuid.uuid4().hex[:8]}",
        'field': item.get('field', ''),
        'name': item.get('name', 'Unknown'),
        'type': item_type,
        'category': category,
        'operator': 'equals',
        'value': '',
        'data_type': item.get('dataType', 'string')
    }

    # Add to current segment
    if not st.session_state.segment_definition.get('containers'):
        # Create first container
        st.session_state.segment_definition['containers'] = [{
            'id': f'container_{uuid.uuid4().hex[:8]}',
            'type': 'hit',
            'include': True,
            'conditions': [new_condition],
            'children': [],
            'logic': 'and'
        }]
    else:
        # Add to the first container
        if st.session_state.segment_definition['containers']:
            st.session_state.segment_definition['containers'][0]['conditions'].append(new_condition)


def add_segment_to_builder_fixed(segment: Dict):
    """Add a pre-built segment to the builder - COMPATIBILITY FIXED"""

    # Import the function from segment_builder
    from src.components.segment_builder import add_segment_to_builder

    try:
        add_segment_to_builder(segment)
    except Exception as e:
        st.error(f"Error loading segment: {str(e)}")
        # Fallback: manual loading
        add_segment_to_builder_fallback(segment)


def add_segment_to_builder_fallback(segment: Dict):
    """Fallback method to add segment to builder"""

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
        st.warning(f"Segment {segment.get('name', 'Unknown')} has no complete definition.")


def filter_items_by_search(items: List[Dict], search_term: str) -> List[Dict]:
    """Filter items based on search term"""

    if not search_term:
        return items

    filtered_items = []
    for item in items:
        # Search in name, field, and category
        searchable_text = f"{item.get('name', '')} {item.get('field', '')} {item.get('category', '')}".lower()
        if search_term in searchable_text:
            filtered_items.append(item)

    return filtered_items


# Alternative simple sidebar for maximum compatibility
def render_simple_sidebar(config: Dict):
    """
    Simple sidebar with maximum compatibility - no fancy features
    """

    st.markdown("## 📋 Components")

    # Search
    search_term = st.text_input("🔍 Search", placeholder="Type to search...")

    # Get data
    dimensions = config.get('dimensions', [])
    metrics = config.get('metrics', [])
    segments = config.get('segments', [])

    # Filter based on search
    if search_term:
        search_lower = search_term.lower()
        dimensions = [d for d in dimensions if search_lower in d.get('name', '').lower()]
        metrics = [m for m in metrics if search_lower in m.get('name', '').lower()]
        segments = [s for s in segments if search_lower in s.get('name', '').lower()]

    # Dimensions
    if dimensions:
        st.markdown(f"### 📊 Dimensions ({len(dimensions)})")
        for dim in dimensions:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📊 {dim.get('name', 'Unknown')}")
            with col2:
                if st.button("➕", key=f"simple_add_dim_{dim.get('field', uuid.uuid4().hex[:8])}", help="Add"):
                    add_to_segment_fallback(dim, 'dimension')
                    st.success(f"Added {dim.get('name')}")
                    st.rerun()

    # Metrics
    if metrics:
        st.markdown(f"### 📈 Metrics ({len(metrics)})")
        for metric in metrics:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📈 {metric.get('name', 'Unknown')}")
            with col2:
                if st.button("➕", key=f"simple_add_metric_{metric.get('field', uuid.uuid4().hex[:8])}", help="Add"):
                    add_to_segment_fallback(metric, 'metric')
                    st.success(f"Added {metric.get('name')}")
                    st.rerun()

    # Segments
    if segments:
        st.markdown(f"### 🎯 Segments ({len(segments)})")
        for segment in segments:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"🎯 {segment.get('name', 'Unknown')}")
            with col2:
                if st.button("🔄", key=f"simple_load_seg_{segment.get('id', uuid.uuid4().hex[:8])}", help="Load"):
                    add_segment_to_builder_fallback(segment)
                    st.success(f"Loaded {segment.get('name')}")
                    st.rerun()


# Utility function to get item icon
def get_item_icon(item_type: str) -> str:
    """Get icon for item type"""
    icons = {
        'dimension': '📊',
        'metric': '📈',
        'segment': '🎯'
    }
    return icons.get(item_type, '📄')


# Initialize sidebar search state
def initialize_sidebar_state():
    """Initialize sidebar state"""
    if 'sidebar_search' not in st.session_state:
        st.session_state.sidebar_search = ""

    # Apply sidebar styling
    st.markdown("""
    <style>
    /* Sidebar Styling */
    .sidebar-section {
        margin-bottom: 24px;
    }

    .sidebar-title {
        font-size: 13px;
        font-weight: 700;
        color: #2c2c2c;
        text-transform: uppercase;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #e1e1e1;
    }

    .sidebar-count {
        background: #6e6e6e;
        color: white;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: 400;
        min-width: 20px;
        text-align: center;
    }

    .sidebar-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        margin-bottom: 2px;
        border-radius: 4px;
        cursor: move;
        transition: all 0.2s ease;
        border: 1px solid transparent;
        background: white;
        user-select: none;
    }

    .sidebar-item:hover {
        background: #f8f9fa;
        border-color: #e1e1e1;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .sidebar-item.dragging {
        opacity: 0.5;
        transform: rotate(3deg);
    }

    .sidebar-item-content {
        display: flex;
        align-items: center;
        flex: 1;
        gap: 8px;
    }

    .sidebar-item-icon {
        font-size: 16px;
        width: 20px;
        text-align: center;
    }

    .sidebar-item-name {
        font-size: 14px;
        color: #2c2c2c;
        font-weight: 400;
    }

    .sidebar-add-btn {
        width: 24px;
        height: 24px;
        border: 1px solid #d3d3d3;
        background: white;
        border-radius: 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #6e6e6e;
        transition: all 0.2s ease;
        font-size: 18px;
        line-height: 1;
    }

    .sidebar-add-btn:hover {
        background: #1473e6;
        color: white;
        border-color: #1473e6;
        transform: scale(1.1);
    }

    /* Collapsible sections */
    .sidebar-collapsible {
        cursor: pointer;
        user-select: none;
    }

    .sidebar-content {
        max-height: 400px;
        overflow-y: auto;
        transition: max-height 0.3s ease;
    }

    .sidebar-content.collapsed {
        max-height: 0;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

    # Get data from config
    dimensions = config.get('dimensions', [])
    metrics = config.get('metrics', [])
    segments = config.get('segments', [])

    # Render sections
    render_dimensions_section(dimensions)
    render_metrics_section(metrics)

    if segments:
        render_segments_section(segments)

    # Initialize drag-and-drop functionality
    initialize_drag_drop_functionality()


def render_dimensions_section(dimensions: List[Dict]):
    """Render the dimensions section"""

    # Section header with expand/collapse
    col1, col2 = st.columns([1, 10])
    with col1:
        expanded = st.session_state.get('dimensions_expanded', True)
        if st.button("▼" if expanded else "▶", key="dimensions_toggle"):
            st.session_state.dimensions_expanded = not expanded
            st.rerun()

    with col2:
        st.markdown(f"""
        <div class="sidebar-title">
            📊 Dimensions
            <span class="sidebar-count">{len(dimensions)}</span>
        </div>
        """, unsafe_allow_html=True)

    # Content
    if st.session_state.get('dimensions_expanded', True):
        # Group dimensions by category
        categories = {}
        for dim in dimensions:
            category = dim.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(dim)

        # Render each category
        for category, items in categories.items():
            if len(categories) > 1:
                st.markdown(f"**{category}**")

            for item in items:
                render_draggable_item(item, '📊', 'dimension')


def render_metrics_section(metrics: List[Dict]):
    """Render the metrics section"""

    # Section header with expand/collapse
    col1, col2 = st.columns([1, 10])
    with col1:
        expanded = st.session_state.get('metrics_expanded', True)
        if st.button("▼" if expanded else "▶", key="metrics_toggle"):
            st.session_state.metrics_expanded = not expanded
            st.rerun()

    with col2:
        st.markdown(f"""
        <div class="sidebar-title">
            📈 Metrics
            <span class="sidebar-count">{len(metrics)}</span>
        </div>
        """, unsafe_allow_html=True)

    # Content
    if st.session_state.get('metrics_expanded', True):
        # Group metrics by category
        categories = {}
        for metric in metrics:
            category = metric.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(metric)

        # Render each category
        for category, items in categories.items():
            if len(categories) > 1:
                st.markdown(f"**{category}**")

            for item in items:
                render_draggable_item(item, '📈', 'metric')


def render_segments_section(segments: List[Dict]):
    """Render the segments section"""

    # Section header with expand/collapse
    col1, col2 = st.columns([1, 10])
    with col1:
        expanded = st.session_state.get('segments_expanded', True)
        if st.button("▼" if expanded else "▶", key="segments_toggle"):
            st.session_state.segments_expanded = not expanded
            st.rerun()

    with col2:
        st.markdown(f"""
        <div class="sidebar-title">
            🎯 Segments
            <span class="sidebar-count">{len(segments)}</span>
        </div>
        """, unsafe_allow_html=True)

    # Content
    if st.session_state.get('segments_expanded', True):
        for segment in segments:
            render_draggable_segment(segment)


def render_draggable_item(item: Dict, icon: str, item_type: str):
    """Render a draggable dimension or metric item"""

    item_id = f"{item_type}_{item.get('field', item.get('id', uuid.uuid4().hex[:8]))}"

    # Create the item HTML with drag attributes
    item_html = f"""
    <div class="sidebar-item" 
         draggable="true"
         data-item-id="{item_id}"
         data-name="{item.get('name', 'Unknown')}"
         data-field="{item.get('field', '')}"
         data-type="{item_type}"
         data-data-type="{item.get('dataType', 'string')}"
         data-category="{item.get('category', '')}"
         id="item_{item_id}">
        <div class="sidebar-item-content">
            <span class="sidebar-item-icon">{icon}</span>
            <span class="sidebar-item-name">{item.get('name', 'Unknown')}</span>
        </div>
        <button class="sidebar-add-btn" onclick="addItemToSegment('{item_id}')" title="Add to segment">
            +
        </button>
    </div>
    """

    st.markdown(item_html, unsafe_allow_html=True)

    # Add click handler for the + button
    if st.button("", key=f"add_{item_id}", help="Add to segment"):
        add_to_segment(item, item_type)


def render_draggable_segment(segment: Dict):
    """Render a draggable segment item"""

    segment_id = f"segment_{segment.get('id', uuid.uuid4().hex[:8])}"

    # Create the segment HTML
    segment_html = f"""
    <div class="sidebar-item"
         draggable="true"
         data-item-id="{segment_id}"
         data-name="{segment.get('name', 'Unknown')}"
         data-type="segment"
         id="item_{segment_id}">
        <div class="sidebar-item-content">
            <span class="sidebar-item-icon">🎯</span>
            <div>
                <div class="sidebar-item-name">{segment.get('name', 'Unknown')}</div>
                {f'<div style="font-size: 12px; color: #6e6e6e;">{segment.get("description", "")[:50]}...</div>' if segment.get('description') else ''}
            </div>
        </div>
        <button class="sidebar-add-btn" onclick="addSegmentToBuilder('{segment_id}')" title="Add to segment">
            +
        </button>
    </div>
    """

    st.markdown(segment_html, unsafe_allow_html=True)

    # Add click handler for the + button
    if st.button("", key=f"add_{segment_id}", help="Add segment"):
        add_segment_to_builder(segment)


def initialize_drag_drop_functionality():
    """Initialize drag-and-drop functionality with JavaScript"""

    drag_drop_js = """
    <script>
    // Drag and Drop Functionality
    let draggedItem = null;

    function initializeDragDrop() {
        // Add drag event listeners to all draggable items
        document.querySelectorAll('.sidebar-item[draggable="true"]').forEach(item => {
            item.addEventListener('dragstart', handleDragStart);
            item.addEventListener('dragend', handleDragEnd);
        });

        // Add drop event listeners to drop zones
        document.querySelectorAll('.drop-zone, .segment-container').forEach(zone => {
            zone.addEventListener('dragover', handleDragOver);
            zone.addEventListener('drop', handleDrop);
            zone.addEventListener('dragenter', handleDragEnter);
            zone.addEventListener('dragleave', handleDragLeave);
        });

        console.log('Drag and drop initialized');
    }

    function handleDragStart(e) {
        draggedItem = {
            id: this.dataset.itemId,
            name: this.dataset.name,
            field: this.dataset.field,
            type: this.dataset.type,
            dataType: this.dataset.dataType || 'string',
            category: this.dataset.category || ''
        };

        e.dataTransfer.setData('text/plain', JSON.stringify(draggedItem));
        e.dataTransfer.effectAllowed = 'copy';

        this.classList.add('dragging');
        console.log('Drag started:', draggedItem);
    }

    function handleDragEnd(e) {
        this.classList.remove('dragging');
        draggedItem = null;
    }

    function handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    }

    function handleDragEnter(e) {
        e.preventDefault();
        if (this.classList.contains('drop-zone') || this.classList.contains('segment-container')) {
            this.classList.add('drag-over');
        }
    }

    function handleDragLeave(e) {
        if (!this.contains(e.relatedTarget)) {
            this.classList.remove('drag-over');
        }
    }

    function handleDrop(e) {
        e.preventDefault();
        this.classList.remove('drag-over');

        if (draggedItem) {
            console.log('Item dropped:', draggedItem);

            // Get container ID if available
            const containerId = this.dataset.containerId || null;

            // Send message to Streamlit
            window.parent.postMessage({
                type: 'add_condition',
                data: draggedItem,
                containerId: containerId
            }, '*');

            // Also trigger Streamlit rerun
            if (window.streamlitRerun) {
                window.streamlitRerun();
            }
        }
    }

    // Button click handlers
    function addItemToSegment(itemId) {
        const element = document.getElementById('item_' + itemId);
        if (element) {
            const itemData = {
                id: element.dataset.itemId,
                name: element.dataset.name,
                field: element.dataset.field,
                type: element.dataset.type,
                dataType: element.dataset.dataType || 'string',
                category: element.dataset.category || ''
            };

            console.log('Adding item via button:', itemData);

            // Send message to Streamlit
            window.parent.postMessage({
                type: 'add_condition',
                data: itemData
            }, '*');
        }
    }

    function addSegmentToBuilder(segmentId) {
        console.log('Adding segment:', segmentId);

        // Send message to Streamlit
        window.parent.postMessage({
            type: 'add_segment',
            segmentId: segmentId
        }, '*');
    }

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', initializeDragDrop);

    // Reinitialize when content changes (for Streamlit updates)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                setTimeout(initializeDragDrop, 100);
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Initialize immediately as fallback
    setTimeout(initializeDragDrop, 1000);
    </script>
    """

    components.html(drag_drop_js, height=0)


def add_to_segment(item: Dict, item_type: str, category: str = ''):
    """Add a dimension or metric to the current segment"""

    new_condition = {
        'id': f"{item_type}_{item['field']}_{uuid.uuid4().hex[:8]}",
        'field': item['field'],
        'name': item['name'],
        'type': item_type,
        'category': category,
        'operator': 'equals',
        'value': '',
        'data_type': item.get('dataType', 'string')
    }

    # Add to current segment
    if not st.session_state.segment_definition.get('containers'):
        # Create first container
        st.session_state.segment_definition['containers'] = [{
            'id': f'container_{uuid.uuid4().hex[:8]}',
            'type': 'hit',
            'include': True,
            'conditions': [new_condition],
            'children': [],
            'logic': 'and'
        }]
    else:
        # Add to the first container
        if st.session_state.segment_definition['containers']:
            st.session_state.segment_definition['containers'][0]['conditions'].append(new_condition)

    st.success(f"Added {item['name']} to segment")
    st.rerun()


def add_segment_to_builder(segment: Dict):
    """Add a pre-built segment to the builder"""

    # Check if segment has a complete definition
    if 'definition' in segment and segment['definition']:
        # Load the complete segment definition
        st.session_state.segment_definition = segment['definition'].copy()
        st.success(f"Loaded segment: {segment['name']}")
    elif 'containers' in segment:
        # Use the segment structure directly
        st.session_state.segment_definition = {
            'name': segment.get('name', 'Imported Segment'),
            'description': segment.get('description', ''),
            'container_type': segment.get('container_type', 'hit'),
            'logic': segment.get('logic', 'and'),
            'containers': segment.get('containers', [])
        }
        st.success(f"Loaded segment: {segment['name']}")
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
            st.session_state.segment_definition['containers'] = [{
                'id': f'container_{uuid.uuid4().hex[:8]}',
                'type': 'hit',
                'include': True,
                'conditions': [new_condition],
                'children': [],
                'logic': 'and'
            }]
        else:
            st.session_state.segment_definition['containers'][0]['conditions'].append(new_condition)

        st.success(f"Added segment condition: {segment['name']}")

    st.rerun()


def handle_sidebar_messages():
    """Handle messages from sidebar drag-and-drop"""

    # This function can be called by the main app to handle messages
    # Implementation depends on your message handling setup
    pass


# Search functionality
def render_search_box():
    """Render search box for filtering sidebar items"""

    search_term = st.text_input(
        "Search components...",
        key="sidebar_search",
        placeholder="Type to search dimensions, metrics, segments..."
    )

    if search_term:
        st.session_state.sidebar_search = search_term.lower()
    else:
        st.session_state.sidebar_search = ""


def filter_items_by_search(items: List[Dict], search_term: str) -> List[Dict]:
    """Filter items based on search term"""

    if not search_term:
        return items

    filtered_items = []
    for item in items:
        # Search in name, field, and category
        searchable_text = f"{item.get('name', '')} {item.get('field', '')} {item.get('category', '')}".lower()
        if search_term in searchable_text:
            filtered_items.append(item)

    return filtered_items


# Utility functions
def get_item_icon(item_type: str) -> str:
    """Get icon for item type"""
    icons = {
        'dimension': '📊',
        'metric': '📈',
        'segment': '🎯'
    }
    return icons.get(item_type, '📄')


def format_item_name(item: Dict) -> str:
    """Format item name for display"""
    name = item.get('name', 'Unknown')
    if len(name) > 30:
        return name[:27] + '...'
    return name