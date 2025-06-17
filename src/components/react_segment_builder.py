import streamlit as st
import streamlit.components.v1 as components
import json

def render_react_segment_builder(config, segment_definition):
    """Render an enhanced React-based segment builder with seamless drag and drop"""
    
    # Convert config to JSON for JavaScript
    dimensions = []
    for cat in config.get('dimensions', []):
        for item in cat['items']:
            dimensions.append({
                'id': f"dim_{item['field']}",
                'name': item['name'],
                'field': item['field'],
                'category': cat['category'],
                'type': 'dimension',
                'dataType': item.get('type', 'string'),
                'values': item.get('values', [])
            })
    
    metrics = []
    for cat in config.get('metrics', []):
        for item in cat['items']:
            metrics.append({
                'id': f"met_{item['field']}",
                'name': item['name'],
                'field': item['field'],
                'category': cat['category'],
                'type': 'metric',
                'dataType': item.get('type', 'number')
            })
    
    # Fallback definitions for some sample segments
    fallback_definitions = {
        'High Value Customers': {
            'name': 'High Value Customers',
            'description': 'Visitors with revenue > $500',
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
                'id': 'container_mob_1',
                'type': 'hit',
                'include': True,
                'conditions': [{
                    'id': 'cond_dev_1',
                    'field': 'device_type',
                    'name': 'Device Type',
                    'type': 'dimension',
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
                'id': 'container_eng_1',
                'type': 'visit',
                'include': True,
                'conditions': [{
                    'id': 'cond_pv_1',
                    'field': 'pages_viewed',
                    'name': 'Pages Viewed',
                    'type': 'metric',
                    'operator': 'is greater than or equal to',
                    'value': 5,
                    'data_type': 'number'
                }],
                'logic': 'and'
            }],
            'logic': 'and'
        }
    }

    segments = list(config.get('segments', []))
    for seg in st.session_state.get('db_segments', []):
        if not any(s.get('name') == seg.get('name') for s in segments):
            segments.append(seg)

    for seg in segments:
        if 'definition' not in seg and seg.get('name') in fallback_definitions:
            seg['definition'] = fallback_definitions[seg['name']]
    
    # Current segment definition
    current_segment = json.dumps(segment_definition)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Source Sans Pro', Roboto, sans-serif;
                box-sizing: border-box;
            }}
            
            body {{
                margin: 0;
                padding: 0;
                background: #F5F5F5;
                color: #2C2C2C;
            }}
            
            .builder-wrapper {{
                display: flex;
                gap: 16px;
                padding: 16px;
                height: 100vh;
                overflow: hidden;
            }}
            
            /* Enhanced Sidebar */
            .sidebar {{
                width: 300px;
                background: #FFFFFF;
                border: 1px solid #E1E1E1;
                border-radius: 4px;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }}
            
            .sidebar-header {{
                padding: 12px 16px;
                border-bottom: 1px solid #E1E1E1;
                background: #FAFAFA;
            }}
            
            .search-box {{
                width: 100%;
                padding: 8px 12px 8px 32px;
                border: 1px solid #D3D3D3;
                border-radius: 4px;
                font-size: 13px;
                background: #FFFFFF url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTcuMzMzMzMgMTIuNjY2N0MxMC4yNzg5IDEyLjY2NjcgMTIuNjY2NyAxMC4yNzg5IDEyLjY2NjcgNy4zMzMzM0MxMi42NjY3IDQuMzg3ODEgMTAuMjc4OSAyIDcuMzMzMzMgMkM0LjM4NzgxIDIgMiA0LjM4NzgxIDIgNy4zMzMzM0MyIDEwLjI3ODkgNC4zODc4MSAxMi42NjY3IDcuMzMzMzMgMTIuNjY2N1oiIHN0cm9rZT0iIzZFNkU2RSIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KPHBhdGggZD0iTTE0IDE0TDExLjEgMTEuMSIgc3Ryb2tlPSIjNkU2RTZFIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+Cjwvc3ZnPg==') no-repeat;
                background-position: 8px center;
                background-size: 16px;
            }}
            
            .search-box:focus {{
                outline: none;
                border-color: #1473E6;
                box-shadow: 0 0 0 1px #1473E6;
            }}
            
            .sidebar-content {{
                flex: 1;
                overflow-y: auto;
                padding: 8px;
            }}
            
            /* Component sections */
            .component-section {{
                margin-bottom: 8px;
            }}
            
            .section-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 12px;
                background: #F8F8F8;
                border-radius: 4px;
                cursor: pointer;
                user-select: none;
                font-size: 12px;
                font-weight: 700;
                text-transform: uppercase;
                color: #323232;
                letter-spacing: 0.5px;
                margin-bottom: 4px;
            }}
            
            .section-header:hover {{
                background: #F0F0F0;
            }}
            
            .section-header.collapsed {{
                margin-bottom: 0;
            }}
            
            .section-count {{
                color: #E34850;
                font-weight: 700;
                font-size: 14px;
            }}
            
            .section-items {{
                display: block;
                transition: all 0.2s ease;
            }}
            
            .section-items.collapsed {{
                display: none;
            }}
            
            /* Component items */
            .component-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 6px 8px;
                margin: 2px 0;
                background: #FFFFFF;
                border: 1px solid #E8E8E8;
                border-radius: 3px;
                cursor: move;
                transition: all 0.15s ease;
                font-size: 13px;
                min-height: 32px;
                position: relative;
            }}
            
            .component-item:hover {{
                background: #F0F8FF;
                border-color: #1473E6;
                transform: translateX(2px);
                box-shadow: 0 1px 3px rgba(20, 115, 230, 0.15);
            }}
            
            .component-item.dragging {{
                opacity: 0.5;
                cursor: grabbing;
            }}
            
            .component-info {{
                display: flex;
                align-items: center;
                gap: 6px;
                flex: 1;
                overflow: hidden;
            }}
            
            .component-icon {{
                font-size: 14px;
                flex-shrink: 0;
            }}
            
            .component-name {{
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}
            
            .add-btn {{
                opacity: 0;
                background: none;
                border: none;
                color: #1473E6;
                font-size: 16px;
                cursor: pointer;
                padding: 2px 4px;
                transition: all 0.15s ease;
            }}
            
            .component-item:hover .add-btn {{
                opacity: 1;
            }}
            
            .add-btn:hover {{
                transform: scale(1.2);
                color: #0D66D0;
            }}
            
            /* Segment items */
            .segment-item {{
                padding: 8px;
                background: #FAFAFA;
                border-left: 3px solid #6B46C1;
            }}
            
            .segment-item:hover {{
                background: #F5F0FF;
                border-left-color: #553C9A;
            }}
            
            .segment-description {{
                font-size: 11px;
                color: #6E6E6E;
                margin-top: 2px;
                line-height: 1.3;
            }}
            
            /* Main area */
            .main-area {{
                flex: 1;
                background: #FFFFFF;
                border: 1px solid #E1E1E1;
                border-radius: 4px;
                padding: 20px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
            }}
            
            .segment-canvas {{
                flex: 1;
                background: #FAFAFA;
                border: 2px dashed #E1E1E1;
                border-radius: 4px;
                padding: 20px;
                min-height: 400px;
                transition: all 0.2s;
                position: relative;
            }}
            
            .segment-canvas.drag-over {{
                border-color: #1473E6;
                background: #F0F8FF;
                border-style: solid;
            }}
            
            .empty-state {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                min-height: 300px;
                color: #6E6E6E;
                text-align: center;
            }}
            
            .empty-state-icon {{
                font-size: 48px;
                margin-bottom: 16px;
                opacity: 0.3;
            }}
            
            .empty-state-text {{
                font-size: 14px;
                line-height: 1.5;
            }}
            
            /* Containers */
            .container {{
                background: #FFFFFF;
                border: 1px solid #E1E1E1;
                border-radius: 4px;
                padding: 16px;
                margin: 12px 0;
                position: relative;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            }}
            
            .container::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 4px;
                background: #FF6B00;
                border-radius: 4px 0 0 4px;
            }}
            
            .container.exclude::before {{
                background: #323232;
            }}
            
            .container-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
            }}
            
            .container-controls {{
                display: flex;
                gap: 16px;
                align-items: center;
            }}
            
            .radio-group {{
                display: flex;
                gap: 12px;
            }}
            
            .radio-label {{
                display: flex;
                align-items: center;
                gap: 4px;
                cursor: pointer;
                font-size: 13px;
            }}
            
            .radio-label input {{
                cursor: pointer;
            }}
            
            .include-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #E34850;
            }}
            
            .exclude-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #323232;
            }}
            
            /* Conditions */
            .condition {{
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px;
                background: #FAFAFA;
                border: 1px solid #E8E8E8;
                border-radius: 3px;
                margin: 6px 0;
            }}
            
            .condition-field {{
                flex: 1;
                display: flex;
                align-items: center;
                gap: 8px;
                background: #FFFFFF;
                border: 1px solid #E1E1E1;
                border-radius: 3px;
                padding: 6px 10px;
                font-size: 13px;
                min-width: 180px;
            }}
            
            .field-icon {{
                font-size: 14px;
            }}
            
            select, input {{
                background: #FFFFFF;
                border: 1px solid #D3D3D3;
                border-radius: 3px;
                padding: 6px 10px;
                font-size: 13px;
                color: #2C2C2C;
            }}
            
            select:focus, input:focus {{
                outline: none;
                border-color: #1473E6;
                box-shadow: 0 0 0 1px #1473E6;
            }}
            
            .operator-select {{
                min-width: 150px;
            }}
            
            .value-input {{
                min-width: 120px;
            }}
            
            .remove-btn {{
                background: transparent;
                border: none;
                color: #E34850;
                font-size: 16px;
                cursor: pointer;
                padding: 4px;
                opacity: 0.6;
                transition: all 0.15s ease;
            }}
            
            .remove-btn:hover {{
                opacity: 1;
                transform: scale(1.1);
            }}
            
            /* Logic operators */
            .logic-operator {{
                text-align: center;
                margin: 8px 0;
            }}
            
            .logic-select {{
                padding: 4px 12px;
                font-size: 12px;
                text-transform: uppercase;
                font-weight: 600;
                background: #F0F0F0;
                border: 1px solid #D3D3D3;
                border-radius: 3px;
            }}
            
            /* Add buttons */
            .add-condition-btn, .add-container-btn {{
                background: transparent;
                border: 1px dashed #D3D3D3;
                color: #6E6E6E;
                padding: 8px 16px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 13px;
                transition: all 0.15s ease;
                width: 100%;
                margin-top: 8px;
            }}
            
            .add-condition-btn:hover, .add-container-btn:hover {{
                border-color: #1473E6;
                color: #1473E6;
                background: #F0F8FF;
            }}
            
            /* Drag ghost */
            .drag-ghost {{
                position: fixed;
                pointer-events: none;
                z-index: 1000;
                opacity: 0.8;
                transform: rotate(2deg);
            }}
            
            /* Custom scrollbar */
            ::-webkit-scrollbar {{
                width: 6px;
                height: 6px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: #F5F5F5;
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: #D3D3D3;
                border-radius: 3px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: #B3B3B3;
            }}
        </style>
    </head>
    <body>
        <div class="builder-wrapper">
            <!-- Sidebar -->
            <div class="sidebar">
                <div class="sidebar-header">
                    <input type="text" class="search-box" placeholder="Search components..." id="searchBox" />
                </div>
                
                <div class="sidebar-content">
                    <!-- Dimensions -->
                    <div class="component-section">
                        <div class="section-header" onclick="toggleSection('dimensions')">
                            <span>📊 DIMENSIONS</span>
                            <span class="section-count">{len(dimensions)}</span>
                        </div>
                        <div class="section-items" id="dimensions-items"></div>
                    </div>
                    
                    <!-- Metrics -->
                    <div class="component-section">
                        <div class="section-header" onclick="toggleSection('metrics')">
                            <span>📈 METRICS</span>
                            <span class="section-count">{len(metrics)}</span>
                        </div>
                        <div class="section-items" id="metrics-items"></div>
                    </div>
                    
                    <!-- Segments -->
                    <div class="component-section">
                        <div class="section-header" onclick="toggleSection('segments')">
                            <span>🎯 SEGMENTS</span>
                            <span class="section-count">{len(segments)}</span>
                        </div>
                        <div class="section-items" id="segments-items"></div>
                    </div>
                </div>
            </div>
            
            <!-- Main Area -->
            <div class="main-area">
                <h3 style="margin-top: 0; color: #2C2C2C;">Segment Definition</h3>
                <div class="segment-canvas" id="segmentCanvas">
                    <div class="empty-state" id="emptyState">
                        <div class="empty-state-icon">🎯</div>
                        <div class="empty-state-text">
                            Drag components here to build your segment<br>
                            or click the + button next to items
                        </div>
                    </div>
                    <div id="segmentContent" style="display: none;"></div>
                </div>
            </div>
        </div>
        
        <script>
            // Data
            const dimensions = {json.dumps(dimensions)};
            const metrics = {json.dumps(metrics)};
            const segments = {json.dumps(segments)};
            let currentSegment = {current_segment};
            
            // Track drag state
            let draggedItem = null;
            let draggedElement = null;
            
            // Initialize
            function init() {{
                renderSidebar();
                renderSegment();
                setupEventListeners();
                setupDragAndDrop();
            }}
            
            function renderSidebar() {{
                // Render dimensions
                const dimContainer = document.getElementById('dimensions-items');
                dimensions.forEach(dim => {{
                    dimContainer.appendChild(createComponentItem(dim, '📊'));
                }});
                
                // Render metrics
                const metContainer = document.getElementById('metrics-items');
                metrics.forEach(met => {{
                    metContainer.appendChild(createComponentItem(met, '📈'));
                }});
                
                // Render segments
                const segContainer = document.getElementById('segments-items');
                segments.forEach(seg => {{
                    segContainer.appendChild(createSegmentItem(seg));
                }});
            }}
            
            function createComponentItem(data, icon) {{
                const div = document.createElement('div');
                div.className = 'component-item';
                div.draggable = true;
                div.dataset.itemData = JSON.stringify(data);
                
                div.innerHTML = `
                    <div class="component-info">
                        <span class="component-icon">${{icon}}</span>
                        <span class="component-name">${{data.name}}</span>
                    </div>
                    <button class="add-btn" onclick='addToSegment(${{JSON.stringify(data)}})'>➕</button>
                `;
                
                // Drag events
                div.addEventListener('dragstart', handleDragStart);
                div.addEventListener('dragend', handleDragEnd);
                
                return div;
            }}
            
            function createSegmentItem(seg) {{
                const div = document.createElement('div');
                div.className = 'component-item segment-item';
                div.draggable = true;
                div.dataset.segmentData = JSON.stringify(seg);
                
                div.innerHTML = `
                    <div style="flex: 1;">
                        <div class="component-info">
                            <span class="component-icon">🎯</span>
                            <span class="component-name">${{seg.name}}</span>
                        </div>
                        <div class="segment-description">${{seg.description}}</div>
                    </div>
                    <button class="add-btn" onclick='addSegmentToBuilder(${{JSON.stringify(seg)}})'>➕</button>
                `;
                
                div.addEventListener('dragstart', handleDragStart);
                div.addEventListener('dragend', handleDragEnd);
                
                return div;
            }}
            
            function handleDragStart(e) {{
                draggedElement = e.target;
                draggedElement.classList.add('dragging');
                
                // Store data
                if (e.target.dataset.itemData) {{
                    draggedItem = JSON.parse(e.target.dataset.itemData);
                    e.dataTransfer.setData('application/json', e.target.dataset.itemData);
                }} else if (e.target.dataset.segmentData) {{
                    draggedItem = JSON.parse(e.target.dataset.segmentData);
                    e.dataTransfer.setData('application/json', e.target.dataset.segmentData);
                }}
                
                e.dataTransfer.effectAllowed = 'copy';
                
                // Create custom drag image
                const ghost = e.target.cloneNode(true);
                ghost.className = 'drag-ghost ' + e.target.className;
                ghost.style.position = 'absolute';
                ghost.style.top = '-1000px';
                document.body.appendChild(ghost);
                e.dataTransfer.setDragImage(ghost, e.offsetX, e.offsetY);
                setTimeout(() => document.body.removeChild(ghost), 0);
            }}
            
            function handleDragEnd(e) {{
                if (draggedElement) {{
                    draggedElement.classList.remove('dragging');
                }}
                draggedElement = null;
                draggedItem = null;
            }}
            
            function setupDragAndDrop() {{
                const canvas = document.getElementById('segmentCanvas');
                
                canvas.addEventListener('dragover', (e) => {{
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'copy';
                    canvas.classList.add('drag-over');
                }});
                
                canvas.addEventListener('dragleave', (e) => {{
                    if (e.target === canvas) {{
                        canvas.classList.remove('drag-over');
                    }}
                }});
                
                canvas.addEventListener('drop', (e) => {{
                    e.preventDefault();
                    canvas.classList.remove('drag-over');
                    
                    if (draggedItem) {{
                        if (draggedItem.definition) {{
                            // It's a segment
                            addSegmentToBuilder(draggedItem);
                        }} else {{
                            // It's a dimension or metric
                            addToSegment(draggedItem);
                        }}
                    }}
                }});
            }}
            
            function addToSegment(data) {{
                if (!currentSegment.containers || currentSegment.containers.length === 0) {{
                    currentSegment.containers = [{{
                        id: 'container_' + Date.now(),
                        type: currentSegment.container_type || 'hit',
                        include: true,
                        conditions: [],
                        logic: 'and'
                    }}];
                }}
                
                const condition = {{
                    id: data.type + '_' + data.field + '_' + Date.now(),
                    field: data.field,
                    name: data.name,
                    type: data.type,
                    category: data.category || '',
                    operator: data.dataType === 'number' ? 'is greater than' : 'equals',
                    value: '',
                    data_type: data.dataType || 'string'
                }};
                
                currentSegment.containers[0].conditions.push(condition);
                renderSegment();
                sendToStreamlit();
            }}
            
            function addSegmentToBuilder(seg) {{
                if (seg.definition) {{
                    currentSegment = JSON.parse(JSON.stringify(seg.definition));
                }} else {{
                    // Create from segment data
                    currentSegment = {{
                        name: seg.name,
                        description: seg.description,
                        container_type: seg.container_type || 'hit',
                        containers: [],
                        logic: 'and'
                    }};
                }}
                renderSegment();
                sendToStreamlit();
            }}
            
            function renderSegment() {{
                const emptyState = document.getElementById('emptyState');
                const content = document.getElementById('segmentContent');
                
                if (!currentSegment.containers || currentSegment.containers.length === 0) {{
                    emptyState.style.display = 'flex';
                    content.style.display = 'none';
                }} else {{
                    emptyState.style.display = 'none';
                    content.style.display = 'block';
                    content.innerHTML = '';
                    
                    currentSegment.containers.forEach((container, idx) => {{
                        if (idx > 0) {{
                            // Add container logic operator
                            const logicDiv = document.createElement('div');
                            logicDiv.className = 'logic-operator';
                            logicDiv.innerHTML = `
                                <select class="logic-select" onchange="updateSegmentLogic(this.value)">
                                    <option value="and" ${{currentSegment.logic === 'and' ? 'selected' : ''}}>AND</option>
                                    <option value="or" ${{currentSegment.logic === 'or' ? 'selected' : ''}}>OR</option>
                                </select>
                            `;
                            content.appendChild(logicDiv);
                        }}
                        
                        content.appendChild(createContainer(container, idx));
                    }});
                    
                    // Add container button
                    const addBtn = document.createElement('button');
                    addBtn.className = 'add-container-btn';
                    addBtn.innerHTML = '➕ Add Container';
                    addBtn.onclick = addContainer;
                    content.appendChild(addBtn);
                }}
            }}
            
            function createContainer(container, idx) {{
                const div = document.createElement('div');
                div.className = 'container' + (container.include ? '' : ' exclude');
                
                // Header
                const header = document.createElement('div');
                header.className = 'container-header';
                header.innerHTML = `
                    <div class="container-controls">
                        <div class="radio-group">
                            <label class="radio-label">
                                <input type="radio" name="include_${{idx}}" value="include" 
                                       ${{container.include ? 'checked' : ''}}
                                       onchange="updateContainer(${{idx}}, 'include', true)">
                                <span class="include-dot"></span> Include
                            </label>
                            <label class="radio-label">
                                <input type="radio" name="include_${{idx}}" value="exclude" 
                                       ${{!container.include ? 'checked' : ''}}
                                       onchange="updateContainer(${{idx}}, 'include', false)">
                                <span class="exclude-dot"></span> Exclude
                            </label>
                        </div>
                        <select onchange="updateContainer(${{idx}}, 'type', this.value)">
                            <option value="hit" ${{container.type === 'hit' ? 'selected' : ''}}>Hit (Page View)</option>
                            <option value="visit" ${{container.type === 'visit' ? 'selected' : ''}}>Visit (Session)</option>
                            <option value="visitor" ${{container.type === 'visitor' ? 'selected' : ''}}>Visitor</option>
                        </select>
                    </div>
                    <button class="remove-btn" onclick="removeContainer(${{idx}})">✕</button>
                `;
                div.appendChild(header);
                
                // Conditions
                const conditionsDiv = document.createElement('div');
                container.conditions.forEach((condition, condIdx) => {{
                    if (condIdx > 0) {{
                        const logic = document.createElement('div');
                        logic.className = 'logic-operator';
                        logic.innerHTML = `
                            <select class="logic-select" onchange="updateContainer(${{idx}}, 'logic', this.value)">
                                <option value="and" ${{container.logic === 'and' ? 'selected' : ''}}>AND</option>
                                <option value="or" ${{container.logic === 'or' ? 'selected' : ''}}>OR</option>
                                <option value="then" ${{container.logic === 'then' ? 'selected' : ''}}>THEN</option>
                            </select>
                        `;
                        conditionsDiv.appendChild(logic);
                    }}
                    conditionsDiv.appendChild(createCondition(condition, idx, condIdx));
                }});
                div.appendChild(conditionsDiv);
                
                // Add condition button
                const addBtn = document.createElement('button');
                addBtn.className = 'add-condition-btn';
                addBtn.innerHTML = '➕ Add Condition';
                addBtn.onclick = () => {{
                    alert('Drag a dimension or metric from the left panel to add conditions');
                }};
                div.appendChild(addBtn);
                
                // Make container a drop zone
                div.addEventListener('dragover', (e) => {{
                    e.preventDefault();
                    e.stopPropagation();
                    div.style.borderColor = '#1473E6';
                    div.style.background = '#F0F8FF';
                }});
                
                div.addEventListener('dragleave', (e) => {{
                    e.preventDefault();
                    e.stopPropagation();
                    div.style.borderColor = '';
                    div.style.background = '';
                }});
                
                div.addEventListener('drop', (e) => {{
                    e.preventDefault();
                    e.stopPropagation();
                    div.style.borderColor = '';
                    div.style.background = '';
                    
                    if (draggedItem && !draggedItem.definition) {{
                        const condition = {{
                            id: draggedItem.type + '_' + draggedItem.field + '_' + Date.now(),
                            field: draggedItem.field,
                            name: draggedItem.name,
                            type: draggedItem.type,
                            category: draggedItem.category || '',
                            operator: draggedItem.dataType === 'number' ? 'is greater than' : 'equals',
                            value: '',
                            data_type: draggedItem.dataType || 'string'
                        }};
                        
                        currentSegment.containers[idx].conditions.push(condition);
                        renderSegment();
                        sendToStreamlit();
                    }}
                }});
                
                return div;
            }}
            
            function createCondition(condition, containerIdx, condIdx) {{
                const div = document.createElement('div');
                div.className = 'condition';
                
                const icon = condition.type === 'metric' ? '📈' : '📊';
                const operators = condition.data_type === 'number' 
                    ? ['equals', 'does not equal', 'is greater than', 'is less than', 'is greater than or equal to', 'is less than or equal to']
                    : ['equals', 'does not equal', 'contains', 'does not contain', 'starts with', 'ends with'];
                
                div.innerHTML = `
                    <div class="condition-field">
                        <span class="field-icon">${{icon}}</span>
                        <span>${{condition.name}}</span>
                    </div>
                    <select class="operator-select" onchange="updateCondition(${{containerIdx}}, ${{condIdx}}, 'operator', this.value)">
                        ${{operators.map(op => `<option value="${{op}}" ${{condition.operator === op ? 'selected' : ''}}>${{op}}</option>`).join('')}}
                    </select>
                    <input type="${{condition.data_type === 'number' ? 'number' : 'text'}}" 
                           class="value-input"
                           placeholder="Enter value" 
                           value="${{condition.value || ''}}"
                           onchange="updateCondition(${{containerIdx}}, ${{condIdx}}, 'value', this.value)">
                    <button class="remove-btn" onclick="removeCondition(${{containerIdx}}, ${{condIdx}})">✕</button>
                `;
                
                return div;
            }}
            
            function toggleSection(section) {{
                const items = document.getElementById(section + '-items');
                items.classList.toggle('collapsed');
            }}
            
            function setupEventListeners() {{
                // Search functionality
                const searchBox = document.getElementById('searchBox');
                searchBox.addEventListener('input', (e) => {{
                    const query = e.target.value.toLowerCase();
                    
                    document.querySelectorAll('.component-item').forEach(item => {{
                        const name = item.querySelector('.component-name').textContent.toLowerCase();
                        item.style.display = name.includes(query) ? 'flex' : 'none';
                    }});
                }});
            }}
            
            function addContainer() {{
                if (!currentSegment.containers) currentSegment.containers = [];
                currentSegment.containers.push({{
                    id: 'container_' + Date.now(),
                    type: currentSegment.container_type || 'hit',
                    include: true,
                    conditions: [],
                    logic: 'and'
                }});
                renderSegment();
                sendToStreamlit();
            }}
            
            function removeContainer(idx) {{
                currentSegment.containers.splice(idx, 1);
                renderSegment();
                sendToStreamlit();
            }}
            
            function updateContainer(idx, field, value) {{
                currentSegment.containers[idx][field] = value;
                renderSegment();
                sendToStreamlit();
            }}
            
            function removeCondition(containerIdx, condIdx) {{
                currentSegment.containers[containerIdx].conditions.splice(condIdx, 1);
                renderSegment();
                sendToStreamlit();
            }}
            
            function updateCondition(containerIdx, condIdx, field, value) {{
                currentSegment.containers[containerIdx].conditions[condIdx][field] = value;
                sendToStreamlit();
            }}
            
            function updateSegmentLogic(value) {{
                currentSegment.logic = value;
                sendToStreamlit();
            }}
            
            function sendToStreamlit() {{
                // Send updated segment back to Streamlit
                window.parent.postMessage({{
                    type: 'segmentUpdate',
                    segment: currentSegment
                }}, '*');
            }}
            
            // Initialize on load
            init();
        </script>
    </body>
    </html>
    """
    
    # Listen for messages from iframe
    component_value = components.html(html_content, height=700, scrolling=True)
    
    # Handle updates from the React component
    if component_value:
        try:
            # Parse the message
            import re
            match = re.search(r'"segment":\s*({.*?})\s*}', component_value)
            if match:
                segment_data = json.loads(match.group(1))
                st.session_state.segment_definition = segment_data
                st.session_state.preview_data = None  # Clear preview to force regeneration
                st.session_state.last_preview_segment = None
        except:
            pass
    
    return component_value