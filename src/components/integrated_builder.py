import streamlit as st
import streamlit.components.v1 as components
import json

def render_integrated_builder(config, segment_definition):
    """Render an integrated drag and drop builder with sidebar and segment area"""
    
    # Convert config to JSON for JavaScript
    dimensions = []
    for cat in config.get('dimensions', []):
        for item in cat['items']:
            dimensions.append({
                'name': item['name'],
                'field': item['field'],
                'category': cat['category'],
                'type': 'dimension',
                'dataType': item.get('type', 'string')
            })
    
    metrics = []
    for cat in config.get('metrics', []):
        for item in cat['items']:
            metrics.append({
                'name': item['name'],
                'field': item['field'],
                'category': cat['category'],
                'type': 'metric',
                'dataType': item.get('type', 'number')
            })
    
    segments = config.get('segments', [])
    
    # Current segment definition
    current_segment = json.dumps(segment_definition)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
                gap: 20px;
                padding: 20px;
                height: 100vh;
                overflow: hidden;
            }}
            
            /* Sidebar Styles */
            .sidebar {{
                width: 280px;
                background: #FFFFFF;
                border: 1px solid #E1E1E1;
                border-radius: 4px;
                overflow-y: auto;
                padding: 16px;
            }}
            
            .search-box {{
                width: 100%;
                padding: 8px 12px 8px 32px;
                border: 1px solid #D3D3D3;
                border-radius: 4px;
                margin-bottom: 16px;
                font-size: 14px;
            }}
            
            .component-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 0;
                margin-bottom: 8px;
                font-size: 13px;
                font-weight: 700;
                text-transform: uppercase;
                color: #2C2C2C;
            }}
            
            .component-count {{
                color: #E34850;
                font-weight: 700;
                font-size: 18px;
            }}
            
            .sidebar-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px;
                margin: 4px 0;
                background: #FFFFFF;
                border: 1px solid #E1E1E1;
                border-radius: 4px;
                cursor: move;
                transition: all 0.15s ease;
            }}
            
            .sidebar-item:hover {{
                background: #F0F8FF;
                border-color: #1473E6;
                transform: translateX(2px);
            }}
            
            .sidebar-item.dragging {{
                opacity: 0.5;
            }}
            
            .item-content {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .add-btn {{
                background: transparent;
                border: none;
                color: #2C2C2C;
                font-size: 18px;
                cursor: pointer;
                padding: 2px 6px;
            }}
            
            .add-btn:hover {{
                color: #1473E6;
            }}
            
            /* Main Area Styles */
            .main-area {{
                flex: 1;
                background: #FFFFFF;
                border: 1px solid #E1E1E1;
                border-radius: 4px;
                padding: 20px;
                overflow-y: auto;
            }}
            
            .drop-zone {{
                min-height: 200px;
                background: #FAFAFA;
                border: 1px solid #E1E1E1;
                border-radius: 4px;
                padding: 40px;
                text-align: center;
                transition: all 0.2s;
            }}
            
            .drop-zone.drag-over {{
                border-color: #1473E6;
                background: #F0F8FF;
            }}
            
            .container {{
                background: #FFFFFF;
                border: 1px solid #E1E1E1;
                border-radius: 4px;
                padding: 16px;
                margin: 12px 0;
                position: relative;
            }}
            
            .container::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 3px;
                background: #FF6B00;
                border-radius: 4px 0 0 4px;
            }}
            
            .container-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
            }}
            
            .container-controls {{
                display: flex;
                gap: 16px;
                align-items: center;
            }}
            
            .condition {{
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 8px 0;
            }}
            
            .condition-field {{
                flex: 1;
                background: #FFFFFF;
                border: 1px solid #D3D3D3;
                border-radius: 4px;
                padding: 8px 12px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            select, input {{
                background: #FFFFFF;
                border: 1px solid #D3D3D3;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 14px;
                color: #2C2C2C;
            }}
            
            .remove-btn {{
                background: transparent;
                border: none;
                color: #2C2C2C;
                font-size: 18px;
                cursor: pointer;
                padding: 4px;
            }}
            
            .remove-btn:hover {{
                color: #E34850;
            }}
            
            .add-rule-btn {{
                background: transparent;
                border: none;
                color: #2C2C2C;
                font-size: 14px;
                cursor: pointer;
                padding: 8px 0;
                text-align: left;
            }}
            
            .add-rule-btn:hover {{
                color: #1473E6;
            }}
            
            .logic-operator {{
                margin: 8px 0;
                text-align: left;
            }}
        </style>
    </head>
    <body>
        <div class="builder-wrapper">
            <!-- Sidebar -->
            <div class="sidebar">
                <input type="text" class="search-box" placeholder="Search components..." />
                
                <!-- Dimensions -->
                <div class="component-section">
                    <div class="component-header">
                        <span>📊 DIMENSIONS</span>
                        <span class="component-count">{len(dimensions)}</span>
                    </div>
                    <div id="dimensions-list">
                        <!-- Dimensions will be added here -->
                    </div>
                </div>
                
                <!-- Metrics -->
                <div class="component-section" style="margin-top: 16px;">
                    <div class="component-header">
                        <span>📈 METRICS</span>
                        <span class="component-count">{len(metrics)}</span>
                    </div>
                    <div id="metrics-list">
                        <!-- Metrics will be added here -->
                    </div>
                </div>
                
                <!-- Segments -->
                <div class="component-section" style="margin-top: 16px;">
                    <div class="component-header">
                        <span>🎯 SEGMENTS</span>
                        <span class="component-count">{len(segments)}</span>
                    </div>
                    <div id="segments-list">
                        <!-- Segments will be added here -->
                    </div>
                </div>
            </div>
            
            <!-- Main Area -->
            <div class="main-area">
                <h3>Segment Definition</h3>
                <div id="segment-area">
                    <!-- Segment containers will be added here -->
                </div>
            </div>
        </div>
        
        <script>
            // Data from Python
            const dimensions = {json.dumps(dimensions)};
            const metrics = {json.dumps(metrics)};
            const segments = {json.dumps(segments)};
            let currentSegment = {current_segment};
            
            // Initialize sidebar
            function initializeSidebar() {{
                // Add dimensions
                const dimList = document.getElementById('dimensions-list');
                dimensions.forEach(dim => {{
                    const item = createSidebarItem(dim, '📊');
                    dimList.appendChild(item);
                }});
                
                // Add metrics
                const metList = document.getElementById('metrics-list');
                metrics.forEach(met => {{
                    const item = createSidebarItem(met, '📈');
                    metList.appendChild(item);
                }});
                
                // Add segments
                const segList = document.getElementById('segments-list');
                segments.forEach(seg => {{
                    const item = createSidebarItem({{...seg, type: 'segment'}}, '🎯');
                    segList.appendChild(item);
                }});
            }}
            
            function createSidebarItem(data, icon) {{
                const div = document.createElement('div');
                div.className = 'sidebar-item';
                div.draggable = true;
                
                div.innerHTML = `
                    <div class="item-content">
                        <span>${{icon}}</span>
                        <span>${{data.name}}</span>
                    </div>
                    <button class="add-btn" onclick="addToSegment(${{JSON.stringify(data).replace(/"/g, '&quot;')}})">➕</button>
                `;
                
                // Add drag event listeners
                div.addEventListener('dragstart', (e) => {{
                    e.dataTransfer.effectAllowed = 'copy';
                    e.dataTransfer.setData('text/plain', JSON.stringify(data));
                    div.classList.add('dragging');
                }});
                
                div.addEventListener('dragend', () => {{
                    div.classList.remove('dragging');
                }});
                
                return div;
            }}
            
            function addToSegment(data) {{
                if (!currentSegment.containers || currentSegment.containers.length === 0) {{
                    currentSegment.containers = [{{
                        id: 'container_' + Date.now(),
                        type: 'hit',
                        include: true,
                        conditions: [],
                        logic: 'and'
                    }}];
                }}
                
                const condition = {{
                    id: data.type + '_' + data.field + '_' + Date.now(),
                    field: data.field || '',
                    name: data.name,
                    type: data.type,
                    category: data.category || '',
                    operator: 'equals',
                    value: '',
                    data_type: data.dataType || 'string'
                }};
                
                currentSegment.containers[0].conditions.push(condition);
                renderSegment();
                sendToStreamlit();
            }}
            
            function renderSegment() {{
                const segmentArea = document.getElementById('segment-area');
                
                if (!currentSegment.containers || currentSegment.containers.length === 0) {{
                    segmentArea.innerHTML = `
                        <div class="drop-zone" id="dropZone">
                            <p style="color: #6E6E6E; margin: 0; font-size: 14px;">
                                Drag dimensions, metrics, or segments here to build your segment<br>
                                or click the + button next to items in the left panel
                            </p>
                        </div>
                        <button class="add-rule-btn" onclick="addContainer()" style="margin-top: 16px;">
                            <span style="font-size: 18px;">➕</span> Add Container
                        </button>
                    `;
                    setupDropZone();
                }} else {{
                    segmentArea.innerHTML = '';
                    currentSegment.containers.forEach((container, idx) => {{
                        segmentArea.appendChild(createContainer(container, idx));
                    }});
                    
                    const addBtn = document.createElement('button');
                    addBtn.className = 'add-rule-btn';
                    addBtn.innerHTML = '<span style="font-size: 18px;">➕</span> Add Container';
                    addBtn.onclick = addContainer;
                    addBtn.style.marginTop = '16px';
                    segmentArea.appendChild(addBtn);
                }}
            }}
            
            function createContainer(container, idx) {{
                const div = document.createElement('div');
                div.className = 'container';
                
                // Container header
                const header = document.createElement('div');
                header.className = 'container-header';
                header.innerHTML = `
                    <div class="container-controls">
                        <label>
                            <input type="radio" name="include_${{idx}}" value="include" ${{container.include ? 'checked' : ''}}
                                   onchange="updateContainer(${{idx}}, 'include', true)">
                            <span style="color: #E34850;">●</span> Include
                        </label>
                        <label>
                            <input type="radio" name="include_${{idx}}" value="exclude" ${{!container.include ? 'checked' : ''}}
                                   onchange="updateContainer(${{idx}}, 'include', false)">
                            <span style="color: #2C2C2C;">●</span> Exclude
                        </label>
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
                container.conditions.forEach((condition, condIdx) => {{
                    if (condIdx > 0) {{
                        const logic = document.createElement('div');
                        logic.className = 'logic-operator';
                        logic.innerHTML = `
                            <select onchange="updateContainer(${{idx}}, 'logic', this.value)">
                                <option value="and" ${{container.logic === 'and' ? 'selected' : ''}}>And</option>
                                <option value="or" ${{container.logic === 'or' ? 'selected' : ''}}>Or</option>
                                <option value="then" ${{container.logic === 'then' ? 'selected' : ''}}>Then</option>
                            </select>
                        `;
                        div.appendChild(logic);
                    }}
                    div.appendChild(createCondition(condition, idx, condIdx));
                }});
                
                // Add rule button
                const addRuleBtn = document.createElement('button');
                addRuleBtn.className = 'add-rule-btn';
                addRuleBtn.innerHTML = '<span style="font-size: 18px;">➕</span> Add Rule';
                addRuleBtn.onclick = () => alert('Drag a dimension or metric from the left panel');
                div.appendChild(addRuleBtn);
                
                return div;
            }}
            
            function createCondition(condition, containerIdx, condIdx) {{
                const div = document.createElement('div');
                div.className = 'condition';
                
                const icon = condition.type === 'dimension' ? '📊' : '📈';
                
                div.innerHTML = `
                    <div class="condition-field">
                        <span>${{icon}}</span>
                        <span>${{condition.name}}</span>
                    </div>
                    <select onchange="updateCondition(${{containerIdx}}, ${{condIdx}}, 'operator', this.value)">
                        <option value="equals" ${{condition.operator === 'equals' ? 'selected' : ''}}>equals</option>
                        <option value="not_equals" ${{condition.operator === 'not_equals' ? 'selected' : ''}}>does not equal</option>
                        <option value="contains" ${{condition.operator === 'contains' ? 'selected' : ''}}>contains</option>
                        <option value="greater_than" ${{condition.operator === 'greater_than' ? 'selected' : ''}}>greater than</option>
                        <option value="less_than" ${{condition.operator === 'less_than' ? 'selected' : ''}}>less than</option>
                    </select>
                    <input type="text" placeholder="Enter Value" value="${{condition.value || ''}}"
                           onchange="updateCondition(${{containerIdx}}, ${{condIdx}}, 'value', this.value)">
                    <button class="remove-btn" onclick="removeCondition(${{containerIdx}}, ${{condIdx}})">✕</button>
                `;
                
                return div;
            }}
            
            function setupDropZone() {{
                const dropZone = document.getElementById('dropZone');
                if (!dropZone) return;
                
                dropZone.addEventListener('dragover', (e) => {{
                    e.preventDefault();
                    dropZone.classList.add('drag-over');
                }});
                
                dropZone.addEventListener('dragleave', () => {{
                    dropZone.classList.remove('drag-over');
                }});
                
                dropZone.addEventListener('drop', (e) => {{
                    e.preventDefault();
                    dropZone.classList.remove('drag-over');
                    
                    try {{
                        const data = JSON.parse(e.dataTransfer.getData('text/plain'));
                        addToSegment(data);
                    }} catch (err) {{
                        console.error('Drop error:', err);
                    }}
                }});
            }}
            
            function addContainer() {{
                if (!currentSegment.containers) currentSegment.containers = [];
                currentSegment.containers.push({{
                    id: 'container_' + Date.now(),
                    type: 'hit',
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
            
            function sendToStreamlit() {{
                // Send updated segment back to Streamlit
                window.parent.postMessage({{
                    type: 'segmentUpdate',
                    segment: currentSegment
                }}, '*');
            }}
            
            // Initialize
            initializeSidebar();
            renderSegment();
        </script>
    </body>
    </html>
    """
    
    return components.html(html_content, height=600, scrolling=True)