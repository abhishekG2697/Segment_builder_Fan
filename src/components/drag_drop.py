import streamlit.components.v1 as components
import json

def render_drag_drop_builder():
    """Render the drag and drop segment builder interface"""
    
    drag_drop_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }
            
            .builder-container {
                display: flex;
                gap: 20px;
                min-height: 500px;
            }
            
            .sidebar {
                width: 300px;
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
                max-height: 600px;
                overflow-y: auto;
            }
            
            .main-area {
                flex: 1;
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
            }
            
            .component-section {
                margin-bottom: 20px;
            }
            
            .component-header {
                font-weight: 600;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .draggable-item {
                padding: 10px;
                margin: 5px 0;
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                cursor: move;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .draggable-item:hover {
                transform: translateX(5px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .dimension-item {
                border-left: 3px solid #1473e6;
                background: #e3f2ff;
            }
            
            .metric-item {
                border-left: 3px solid #ffc107;
                background: #fff3cd;
            }
            
            .segment-item {
                border-left: 3px solid #dc3545;
                background: #f8d7da;
            }
            
            .drop-zone {
                min-height: 400px;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                padding: 20px;
                transition: all 0.2s;
            }
            
            .drop-zone.drag-over {
                border-color: #1473e6;
                background: #e3f2ff;
            }
            
            .container {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }
            
            .container-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 15px;
            }
            
            .container-type {
                font-weight: 600;
                color: #2c3e50;
            }
            
            .condition {
                display: flex;
                align-items: center;
                gap: 10px;
                background: white;
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                margin: 8px 0;
            }
            
            .condition-field {
                flex: 1;
                font-weight: 500;
            }
            
            .condition-operator {
                min-width: 120px;
            }
            
            .condition-value {
                min-width: 150px;
            }
            
            select, input {
                padding: 6px 10px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-size: 14px;
            }
            
            button {
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s;
            }
            
            .btn-primary {
                background: #1473e6;
                color: white;
            }
            
            .btn-primary:hover {
                background: #0d66d0;
            }
            
            .btn-danger {
                background: #dc3545;
                color: white;
            }
            
            .logic-operator {
                text-align: center;
                padding: 10px;
                font-weight: 600;
                color: #1473e6;
                text-transform: uppercase;
            }
            
            .empty-state {
                text-align: center;
                color: #6c757d;
                padding: 40px;
            }
        </style>
    </head>
    <body>
        <div class="builder-container">
            <div class="sidebar">
                <h3>Components</h3>
                
                <div class="component-section">
                    <div class="component-header">
                        📊 Dimensions
                    </div>
                    <div class="draggable-item dimension-item" draggable="true" data-type="dimension" data-field="page_url" data-name="Page URL">
                        <span>📄</span> Page URL
                    </div>
                    <div class="draggable-item dimension-item" draggable="true" data-type="dimension" data-field="browser_name" data-name="Browser">
                        <span>🌐</span> Browser
                    </div>
                    <div class="draggable-item dimension-item" draggable="true" data-type="dimension" data-field="device_type" data-name="Device Type">
                        <span>📱</span> Device Type
                    </div>
                    <div class="draggable-item dimension-item" draggable="true" data-type="dimension" data-field="country" data-name="Country">
                        <span>🌍</span> Country
                    </div>
                </div>
                
                <div class="component-section">
                    <div class="component-header">
                        📈 Metrics
                    </div>
                    <div class="draggable-item metric-item" draggable="true" data-type="metric" data-field="revenue" data-name="Revenue">
                        <span>💰</span> Revenue
                    </div>
                    <div class="draggable-item metric-item" draggable="true" data-type="metric" data-field="pages_viewed" data-name="Pages Viewed">
                        <span>👁️</span> Pages Viewed
                    </div>
                    <div class="draggable-item metric-item" draggable="true" data-type="metric" data-field="time_on_page" data-name="Time on Page">
                        <span>⏱️</span> Time on Page
                    </div>
                </div>
                
                <div class="component-section">
                    <div class="component-header">
                        🎯 Segments
                    </div>
                    <div class="draggable-item segment-item" draggable="true" data-type="segment" data-name="High Value Customers">
                        <span>💎</span> High Value Customers
                    </div>
                    <div class="draggable-item segment-item" draggable="true" data-type="segment" data-name="Mobile Users">
                        <span>📱</span> Mobile Users
                    </div>
                </div>
            </div>
            
            <div class="main-area">
                <h3>Segment Definition</h3>
                <div class="drop-zone" id="dropZone">
                    <div class="empty-state">
                        Drag components here to build your segment
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let draggedElement = null;
            let containers = [];

            function createContainer() {
                return {
                    id: 'container_' + Math.random().toString(36).substr(2,5),
                    type: 'visit',
                    include: true,
                    conditions: [],
                    logic: 'and',
                    children: []
                };
            }
            
            // Drag start
            document.querySelectorAll('.draggable-item').forEach(item => {
                item.addEventListener('dragstart', (e) => {
                    draggedElement = e.target;
                    e.dataTransfer.effectAllowed = 'copy';
                });
            });
            
            // Drop zone events
            const dropZone = document.getElementById('dropZone');
            
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
            });
            
            dropZone.addEventListener('dragleave', (e) => {
                dropZone.classList.remove('drag-over');
            });
            
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
                
                if (draggedElement) {
                    const type = draggedElement.dataset.type;
                    const field = draggedElement.dataset.field;
                    const name = draggedElement.dataset.name;
                    
                    addConditionToSegment(type, field, name);
                    updateStreamlit();
                }
            });
            
            function addConditionToSegment(type, field, name, path='0') {
                // Clear empty state
                if (containers.length === 0) {
                    dropZone.innerHTML = '';
                    addContainer();
                }

                const target = getContainerByPath(path);
                if (!target) return;

                const condition = {
                    type: type,
                    field: field,
                    name: name,
                    operator: 'equals',
                    value: ''
                };
                target.conditions.push(condition);
                renderSegment();
            }

            function addContainer(path=null) {
                const newC = createContainer();
                if (!path) {
                    containers.push(newC);
                } else {
                    const parent = getContainerByPath(path);
                    if (parent) parent.children.push(newC);
                }
            }

            function getContainerByPath(path) {
                const parts = path.split('-').map(p => parseInt(p));
                let obj = null;
                let arr = containers;
                for (let i=0; i<parts.length; i++) {
                    obj = arr[parts[i]];
                    if (!obj) return null;
                    if (i < parts.length-1) arr = obj.children;
                }
                return obj;
            }
            
            function renderSegment() {
                dropZone.innerHTML = '';

                containers.forEach((container, idx) => {
                    renderContainer(container, `${idx}`, dropZone, 0);
                });

                const addContainerBtn = document.createElement('button');
                addContainerBtn.className = 'btn-primary';
                addContainerBtn.textContent = '+ Add Container';
                addContainerBtn.onclick = () => {
                    addContainer();
                    renderSegment();
                    updateStreamlit();
                };
                addContainerBtn.style.marginTop = '20px';
                dropZone.appendChild(addContainerBtn);
            }

            function renderContainer(container, path, parentEl, level) {
                const containerEl = document.createElement('div');
                containerEl.className = 'container';
                containerEl.style.marginLeft = (level * 20) + 'px';

                containerEl.innerHTML = `
                    <div class="container-header">
                        <div>
                            <select class="container-type" data-path="${path}">
                                <option value="hit" ${container.type === 'hit' ? 'selected' : ''}>Hit (Page View)</option>
                                <option value="visit" ${container.type === 'visit' ? 'selected' : ''}>Visit (Session)</option>
                                <option value="visitor" ${container.type === 'visitor' ? 'selected' : ''}>Visitor</option>
                            </select>
                            <label>
                                <input type="radio" name="include_${path}" value="include" ${container.include ? 'checked' : ''}> Include
                            </label>
                            <label>
                                <input type="radio" name="include_${path}" value="exclude" ${!container.include ? 'checked' : ''}> Exclude
                            </label>
                        </div>
                        <button class="btn-danger" onclick="removeContainer('${path}')">Remove</button>
                    </div>
                `;

                container.conditions.forEach((condition, cIdx) => {
                    if (cIdx > 0) {
                        containerEl.innerHTML += `<div class="logic-operator">${container.logic.toUpperCase()}</div>`;
                    }
                    const conditionEl = document.createElement('div');
                    conditionEl.className = 'condition';
                    conditionEl.innerHTML = `
                        <div class="condition-field">${condition.name}</div>
                        <select class="condition-operator" data-path="${path}" data-condition="${cIdx}">
                            <option value="equals">equals</option>
                            <option value="not_equals">does not equal</option>
                            <option value="contains">contains</option>
                            <option value="greater_than">greater than</option>
                            <option value="less_than">less than</option>
                        </select>
                        <input type="text" class="condition-value" placeholder="Enter value"
                               data-path="${path}" data-condition="${cIdx}"
                               value="${condition.value}">
                        <button class="btn-danger" onclick="removeCondition('${path}', ${cIdx})">×</button>`;
                    containerEl.appendChild(conditionEl);
                });

                containerEl.innerHTML += `<button class="btn-primary" onclick="addConditionToSegmentPrompt('${path}')" style="margin-top:10px;">+ Add Condition</button>`;
                containerEl.innerHTML += `<button class="btn-primary" onclick="addContainer('${path}')" style="margin-left:10px;">+ Add Subcontainer</button>`;

                containerEl.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    containerEl.classList.add('drag-over');
                });
                containerEl.addEventListener('dragleave', () => {
                    containerEl.classList.remove('drag-over');
                });
                containerEl.addEventListener('drop', (e) => {
                    e.preventDefault();
                    containerEl.classList.remove('drag-over');
                    if (draggedElement) {
                        const type = draggedElement.dataset.type;
                        const field = draggedElement.dataset.field;
                        const name = draggedElement.dataset.name;
                        addConditionToSegment(type, field, name, path);
                        updateStreamlit();
                    }
                });

                parentEl.appendChild(containerEl);

                container.children.forEach((child, idx) => {
                    renderContainer(child, `${path}-${idx}`, parentEl, level + 1);
                });
            }
            
            function removeContainer(path) {
                const parts = path.split('-').map(p => parseInt(p));
                let arr = containers;
                for (let i=0; i<parts.length-1; i++) {
                    arr = arr[parts[i]].children;
                }
                arr.splice(parts[parts.length-1], 1);
                renderSegment();
                updateStreamlit();
            }

            function removeCondition(path, condIdx) {
                const target = getContainerByPath(path);
                if (target) {
                    target.conditions.splice(condIdx, 1);
                    renderSegment();
                    updateStreamlit();
                }
            }

            function addConditionToSegmentPrompt(path) {
                alert('Select a dimension or metric from the left panel');
            }
            
            function updateStreamlit() {
                // Send data back to Streamlit
                window.parent.postMessage({
                    type: 'segmentUpdate',
                    containers: containers
                }, '*');
            }
            
            // Listen for changes
            document.addEventListener('change', (e) => {
                if (e.target.classList.contains('container-type')) {
                    const path = e.target.dataset.path;
                    const c = getContainerByPath(path);
                    if (c) c.type = e.target.value;
                }
                else if (e.target.classList.contains('condition-operator')) {
                    const path = e.target.dataset.path;
                    const condIdx = parseInt(e.target.dataset.condition);
                    const c = getContainerByPath(path);
                    if (c) c.conditions[condIdx].operator = e.target.value;
                }
                else if (e.target.classList.contains('condition-value')) {
                    const path = e.target.dataset.path;
                    const condIdx = parseInt(e.target.dataset.condition);
                    const c = getContainerByPath(path);
                    if (c) c.conditions[condIdx].value = e.target.value;
                }
                else if (e.target.type === 'radio') {
                    const path = e.target.name.replace('include_', '');
                    const c = getContainerByPath(path);
                    if (c) c.include = e.target.value === 'include';
                }
                
                updateStreamlit();
            });
        </script>
    </body>
    </html>
    """
    
    return components.html(drag_drop_html, height=700, scrolling=False)