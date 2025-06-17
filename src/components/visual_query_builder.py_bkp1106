import streamlit as st
import streamlit.components.v1 as components
import json

def render_visual_query_builder(config, segment_definition):
    """Render a visual query builder with condition tree"""
    
    # Convert config to JSON for JavaScript
    dimensions = []
    for cat in config.get('dimensions', []):
        for item in cat['items']:
            dimensions.append({
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
                'name': item['name'],
                'field': item['field'],
                'category': cat['category'],
                'type': 'metric',
                'dataType': item.get('type', 'number')
            })
    
    # Operators by data type
    operators = {
        'string': ['equals', 'does not equal', 'contains', 'does not contain', 'starts with', 'ends with', 'exists', 'does not exist'],
        'number': ['equals', 'does not equal', 'is greater than', 'is less than', 'is greater than or equal to', 'is less than or equal to', 'is between', 'exists', 'does not exist']
    }
    
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
                padding: 20px;
                background: #F5F5F5;
                color: #2C2C2C;
            }}
            
            .query-builder {{
                background: #FFFFFF;
                border: 1px solid #E1E1E1;
                border-radius: 8px;
                padding: 20px;
            }}
            
            .container-selector {{
                margin-bottom: 20px;
                padding: 16px;
                background: #F8F8F8;
                border-radius: 4px;
            }}
            
            .container-selector label {{
                margin-right: 16px;
                font-weight: 500;
                color: #2C2C2C;
            }}
            
            /* FIX: Ensure all selects and inputs have white background */
            select, input {{
                background: #FFFFFF !important;
                border: 1px solid #D3D3D3;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                color: #2C2C2C !important;
                margin: 0 4px;
            }}
            
            select:focus, input:focus {{
                outline: none;
                border-color: #1473E6;
                box-shadow: 0 0 0 1px #1473E6;
            }}
            
            input::placeholder {{
                color: #9E9E9E;
                font-weight: 300;
            }}
            
            /* FIX: Dropdown options */
            option {{
                background-color: #FFFFFF !important;
                color: #2C2C2C !important;
            }}
            
            .query-group {{
                background: #FAFAFA;
                border: 1px solid #E1E1E1;
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
                position: relative;
            }}
            
            .query-group.include {{
                border-left: 4px solid #E34850;
            }}
            
            .query-group.exclude {{
                border-left: 4px solid #2C2C2C;
            }}
            
            .group-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
            }}
            
            .group-controls {{
                display: flex;
                gap: 12px;
                align-items: center;
            }}
            
            /* FIX: Radio buttons and labels */
            .group-controls label {{
                color: #2C2C2C !important;
                cursor: pointer;
            }}
            
            .group-controls input[type="radio"] {{
                margin-right: 4px;
                cursor: pointer;
            }}
            
            .logic-selector {{
                background: #FFFFFF !important;
                border: 1px solid #D3D3D3;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 13px;
                color: #2C2C2C !important;
            }}
            
            .condition {{
                background: #FFFFFF;
                border: 1px solid #E1E1E1;
                border-radius: 4px;
                padding: 12px;
                margin: 8px 0;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .condition-field {{
                flex: 1;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .field-icon {{
                font-size: 16px;
            }}
            
            .field-selector {{
                min-width: 200px;
                background-color: #FFFFFF !important;
                color: #2C2C2C !important;
            }}
            
            .operator-selector {{
                min-width: 150px;
                background-color: #FFFFFF !important;
                color: #2C2C2C !important;
            }}
            
            .value-input {{
                min-width: 150px;
                background-color: #FFFFFF !important;
                color: #2C2C2C !important;
            }}
            
            /* FIX: All buttons have white background */
            button {{
                background: #FFFFFF !important;
                border: 1px solid #D3D3D3;
                color: #2C2C2C !important;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.15s;
            }}
            
            button:hover {{
                background: #F5F5F5 !important;
                border-color: #1473E6;
                color: #1473E6 !important;
            }}
            
            button.primary {{
                background: #1473E6 !important;
                color: white !important;
                border: none;
            }}
            
            button.primary:hover {{
                background: #0D66D0 !important;
                color: white !important;
            }}
            
            button.remove {{
                background: transparent !important;
                border: none;
                color: #E34850 !important;
                padding: 4px 8px;
                font-size: 18px;
            }}
            
            button.remove:hover {{
                color: #C92030 !important;
                background: transparent !important;
            }}
            
            .add-button {{
                background: #FFFFFF !important;
                border: 1px dashed #D3D3D3;
                color: #6E6E6E !important;
                width: 100%;
                margin-top: 8px;
                padding: 12px;
            }}
            
            .add-button:hover {{
                border-color: #1473E6;
                color: #1473E6 !important;
                background: #F0F8FF !important;
            }}
            
            .logic-operator {{
                text-align: center;
                padding: 8px;
                font-weight: 600;
                color: #1473E6;
                text-transform: uppercase;
                font-size: 13px;
            }}
            
            .empty-state {{
                text-align: center;
                padding: 40px;
                color: #6E6E6E;
            }}
            
            .output-section {{
                margin-top: 20px;
                padding: 16px;
                background: #F5F5F5;
                border: 1px solid #E1E1E1;
                border-radius: 4px;
            }}
            
            .output-section h4 {{
                margin: 0 0 8px 0;
                color: #2C2C2C;
            }}
            
            .output-code {{
                background: #FFFFFF;
                border: 1px solid #E1E1E1;
                border-radius: 4px;
                padding: 12px;
                font-family: monospace;
                font-size: 12px;
                white-space: pre-wrap;
                max-height: 200px;
                overflow-y: auto;
                color: #2C2C2C;
            }}
        </style>
    </head>
    <body>
        <div class="query-builder">
            <div class="container-selector">
                <label>Container Type:</label>
                <select id="containerType" onchange="updateContainerType()">
                    <option value="hit">Hit (Page View)</option>
                    <option value="visit" selected>Visit (Session)</option>
                    <option value="visitor">Visitor</option>
                </select>
            </div>
            
            <div id="queryArea">
                <!-- Query groups will be added here -->
            </div>
            
            <button class="add-button" onclick="addContainer()">
                ➕ Add Container
            </button>
            
            <div class="output-section">
                <h4>Generated Segment</h4>
                <div class="output-code" id="output">
                    No conditions defined yet...
                </div>
            </div>
        </div>
        
        <script>
            // Data from Python
            const dimensions = {json.dumps(dimensions)};
            const metrics = {json.dumps(metrics)};
            const operators = {json.dumps(operators)};
            let currentSegment = {current_segment};
            
            // Initialize
            function init() {{
                if (currentSegment.containers && currentSegment.containers.length > 0) {{
                    // Load existing segment
                    document.getElementById('containerType').value = currentSegment.container_type || 'visit';
                    currentSegment.containers.forEach((container, idx) => {{
                        addContainer(container);
                    }});
                }} else {{
                    // Start with one empty container
                    addContainer();
                }}
                updateOutput();
            }}
            
            function addContainer(containerData = null) {{
                const queryArea = document.getElementById('queryArea');
                const containerId = 'container_' + Date.now();
                
                const containerDiv = document.createElement('div');
                containerDiv.className = 'query-group ' + (containerData && !containerData.include ? 'exclude' : 'include');
                containerDiv.id = containerId;
                
                containerDiv.innerHTML = `
                    <div class="group-header">
                        <div class="group-controls">
                            <label>
                                <input type="radio" name="${{containerId}}_mode" value="include" 
                                       ${{!containerData || containerData.include ? 'checked' : ''}}
                                       onchange="updateContainerMode('${{containerId}}', true)">
                                <span style="color: #E34850;">●</span> Include
                            </label>
                            <label>
                                <input type="radio" name="${{containerId}}_mode" value="exclude" 
                                       ${{containerData && !containerData.include ? 'checked' : ''}}
                                       onchange="updateContainerMode('${{containerId}}', false)">
                                <span style="color: #2C2C2C;">●</span> Exclude
                            </label>
                            <select class="logic-selector" onchange="updateContainerLogic('${{containerId}}', this.value)">
                                <option value="and" ${{!containerData || containerData.logic === 'and' ? 'selected' : ''}}>AND</option>
                                <option value="or" ${{containerData && containerData.logic === 'or' ? 'selected' : ''}}>OR</option>
                                <option value="then" ${{containerData && containerData.logic === 'then' ? 'selected' : ''}}>THEN</option>
                            </select>
                        </div>
                        <button class="remove" onclick="removeContainer('${{containerId}}')">✕</button>
                    </div>
                    <div class="conditions" id="${{containerId}}_conditions">
                        <!-- Conditions will be added here -->
                    </div>
                    <button class="add-button" onclick="addCondition('${{containerId}}')">
                        ➕ Add Condition
                    </button>
                `;
                
                queryArea.appendChild(containerDiv);
                
                // Add existing conditions
                if (containerData && containerData.conditions) {{
                    containerData.conditions.forEach(condition => {{
                        addCondition(containerId, condition);
                    }});
                }} else {{
                    // Add one empty condition
                    addCondition(containerId);
                }}
            }}
            
            function addCondition(containerId, conditionData = null) {{
                const conditionsDiv = document.getElementById(containerId + '_conditions');
                const conditionId = 'condition_' + Date.now();
                
                // Add logic operator if not first condition
                if (conditionsDiv.children.length > 0) {{
                    const logicDiv = document.createElement('div');
                    logicDiv.className = 'logic-operator';
                    logicDiv.textContent = document.querySelector(`#${{containerId}} .logic-selector`).value.toUpperCase();
                    conditionsDiv.appendChild(logicDiv);
                }}
                
                const conditionDiv = document.createElement('div');
                conditionDiv.className = 'condition';
                conditionDiv.id = conditionId;
                
                // Build field options
                const allFields = [...dimensions, ...metrics];
                const fieldOptions = allFields.map(f => 
                    `<option value="${{f.field}}" data-type="${{f.type}}" data-datatype="${{f.dataType}}">${{f.name}}</option>`
                ).join('');
                
                conditionDiv.innerHTML = `
                    <div class="condition-field">
                        <span class="field-icon">${{conditionData && conditionData.type === 'metric' ? '📈' : '📊'}}</span>
                        <select class="field-selector" onchange="updateField('${{conditionId}}', this)">
                            <option value="">Select field...</option>
                            ${{fieldOptions}}
                        </select>
                        <select class="operator-selector" onchange="updateOperator('${{conditionId}}', this.value)">
                            <option value="">Select operator...</option>
                        </select>
                        <input type="text" class="value-input" placeholder="Enter value..." 
                               onchange="updateValue('${{conditionId}}', this.value)">
                    </div>
                    <button class="remove" onclick="removeCondition('${{containerId}}', '${{conditionId}}')">✕</button>
                `;
                
                conditionsDiv.appendChild(conditionDiv);
                
                // Set existing values
                if (conditionData) {{
                    const fieldSelect = conditionDiv.querySelector('.field-selector');
                    fieldSelect.value = conditionData.field || '';
                    updateField(conditionId, fieldSelect);
                    
                    const operatorSelect = conditionDiv.querySelector('.operator-selector');
                    operatorSelect.value = conditionData.operator || '';
                    
                    const valueInput = conditionDiv.querySelector('.value-input');
                    valueInput.value = conditionData.value || '';
                }}
                
                updateOutput();
            }}
            
            function updateField(conditionId, fieldSelect) {{
                const selectedOption = fieldSelect.options[fieldSelect.selectedIndex];
                const dataType = selectedOption.getAttribute('data-datatype') || 'string';
                const fieldType = selectedOption.getAttribute('data-type');
                
                // Update icon
                const icon = fieldSelect.parentElement.querySelector('.field-icon');
                icon.textContent = fieldType === 'metric' ? '📈' : '📊';
                
                // Update operators
                const operatorSelect = fieldSelect.parentElement.querySelector('.operator-selector');
                const operatorOptions = operators[dataType] || operators.string;
                operatorSelect.innerHTML = '<option value="">Select operator...</option>' + 
                    operatorOptions.map(op => `<option value="${{op}}">${{op}}</option>`).join('');
                
                // Update value input type
                const valueInput = fieldSelect.parentElement.querySelector('.value-input');
                valueInput.type = dataType === 'number' ? 'number' : 'text';
                
                updateOutput();
            }}
            
            function updateOperator(conditionId, operator) {{
                const condition = document.getElementById(conditionId);
                const valueInput = condition.querySelector('.value-input');
                
                // Hide value input for exists/does not exist
                if (operator === 'exists' || operator === 'does not exist') {{
                    valueInput.style.display = 'none';
                }} else {{
                    valueInput.style.display = 'block';
                }}
                
                updateOutput();
            }}
            
            function updateValue(conditionId, value) {{
                updateOutput();
            }}
            
            function updateContainerType() {{
                updateOutput();
            }}
            
            function updateContainerMode(containerId, include) {{
                const container = document.getElementById(containerId);
                container.className = 'query-group ' + (include ? 'include' : 'exclude');
                updateOutput();
            }}
            
            function updateContainerLogic(containerId, logic) {{
                // Update logic operators between conditions
                const conditionsDiv = document.getElementById(containerId + '_conditions');
                const logicOperators = conditionsDiv.querySelectorAll('.logic-operator');
                logicOperators.forEach(op => {{
                    op.textContent = logic.toUpperCase();
                }});
                updateOutput();
            }}
            
            function removeContainer(containerId) {{
                document.getElementById(containerId).remove();
                updateOutput();
            }}
            
            function removeCondition(containerId, conditionId) {{
                const condition = document.getElementById(conditionId);
                const conditionsDiv = document.getElementById(containerId + '_conditions');
                
                // Remove preceding logic operator if exists
                const prevSibling = condition.previousElementSibling;
                if (prevSibling && prevSibling.className === 'logic-operator') {{
                    prevSibling.remove();
                }} else {{
                    // Remove following logic operator if this is the first condition
                    const nextSibling = condition.nextElementSibling;
                    if (nextSibling && nextSibling.className === 'logic-operator') {{
                        nextSibling.remove();
                    }}
                }}
                
                condition.remove();
                updateOutput();
            }}
            
            function updateOutput() {{
                const segment = {{
                    name: currentSegment.name || 'New Segment',
                    description: currentSegment.description || '',
                    container_type: document.getElementById('containerType').value,
                    containers: [],
                    logic: 'and'
                }};
                
                // Get all containers
                const containers = document.querySelectorAll('.query-group');
                containers.forEach(container => {{
                    const include = container.querySelector('input[type="radio"]:checked').value === 'include';
                    const logic = container.querySelector('.logic-selector').value;
                    const conditions = [];
                    
                    // Get all conditions
                    container.querySelectorAll('.condition').forEach(condition => {{
                        const fieldSelect = condition.querySelector('.field-selector');
                        const operatorSelect = condition.querySelector('.operator-selector');
                        const valueInput = condition.querySelector('.value-input');
                        
                        if (fieldSelect.value && operatorSelect.value) {{
                            const selectedField = fieldSelect.options[fieldSelect.selectedIndex];
                            conditions.push({{
                                field: fieldSelect.value,
                                name: selectedField.textContent,
                                type: selectedField.getAttribute('data-type'),
                                operator: operatorSelect.value,
                                value: valueInput.value,
                                data_type: selectedField.getAttribute('data-datatype')
                            }});
                        }}
                    }});
                    
                    if (conditions.length > 0) {{
                        segment.containers.push({{
                            id: container.id,
                            type: segment.container_type,
                            include: include,
                            conditions: conditions,
                            logic: logic
                        }});
                    }}
                }});
                
                // Display output
                document.getElementById('output').textContent = JSON.stringify(segment, null, 2);
                
                // Send to Streamlit
                window.parent.postMessage({{
                    type: 'segmentUpdate',
                    segment: segment
                }}, '*');
            }}
            
            // Initialize on load
            init();
        </script>
    </body>
    </html>
    """
    
    return components.html(html_content, height=800, scrolling=True)