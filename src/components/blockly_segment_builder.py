import streamlit as st
import streamlit.components.v1 as components
import json

def render_blockly_segment_builder(config, segment_definition):
    """Render a Blockly-based visual segment builder"""
    
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
    
    # Current segment definition
    current_segment = json.dumps(segment_definition)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://unpkg.com/blockly/blockly.min.js"></script>
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
            
            .builder-container {{
                display: flex;
                flex-direction: column;
                height: 100vh;
                background: #F5F5F5;
            }}
            
            .header {{
                background: #FFFFFF;
                border-bottom: 1px solid #E1E1E1;
                padding: 16px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .blockly-container {{
                flex: 1;
                position: relative;
                background: #FFFFFF;
                border: 1px solid #E1E1E1;
                margin: 16px;
                border-radius: 4px;
            }}
            
            #blocklyDiv {{
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
            }}
            
            .controls {{
                background: #FFFFFF;
                border-top: 1px solid #E1E1E1;
                padding: 16px;
                display: flex;
                gap: 16px;
                align-items: center;
            }}
            
            button {{
                background: #FFFFFF;
                border: 1px solid #D3D3D3;
                color: #2C2C2C;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }}
            
            button:hover {{
                background: #F5F5F5;
                border-color: #1473E6;
                color: #1473E6;
            }}
            
            button.primary {{
                background: #1473E6;
                color: white;
                border: none;
            }}
            
            button.primary:hover {{
                background: #0D66D0;
            }}
            
            .output {{
                background: #F5F5F5;
                padding: 8px;
                border: 1px solid #E1E1E1;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
                max-height: 100px;
                overflow-y: auto;
                flex: 1;
            }}
        </style>
    </head>
    <body>
        <div class="builder-container">
            <div class="header">
                <h3>Visual Segment Builder (Blockly)</h3>
                <button onclick="resetWorkspace()">Reset</button>
            </div>
            
            <div class="blockly-container">
                <div id="blocklyDiv"></div>
            </div>
            
            <div class="controls">
                <button class="primary" onclick="generateSegment()">Generate Segment</button>
                <div class="output" id="output">Drag blocks to build your segment...</div>
            </div>
        </div>
        
        <xml xmlns="https://developers.google.com/blockly/xml" id="toolbox" style="display: none">
            <category name="Containers" colour="#FF6B00">
                <block type="container_hit"></block>
                <block type="container_visit"></block>
                <block type="container_visitor"></block>
            </category>
            
            <category name="Logic" colour="#1473E6">
                <block type="logic_and"></block>
                <block type="logic_or"></block>
                <block type="logic_then"></block>
                <block type="logic_not"></block>
            </category>
            
            <category name="Dimensions" colour="#5AA3E0">
                <block type="dimension_equals"></block>
                <block type="dimension_contains"></block>
                <block type="dimension_starts_with"></block>
                <block type="dimension_exists"></block>
            </category>
            
            <category name="Metrics" colour="#44B556">
                <block type="metric_greater_than"></block>
                <block type="metric_less_than"></block>
                <block type="metric_equals"></block>
                <block type="metric_between"></block>
            </category>
            
            <category name="Values" colour="#9E9E9E">
                <block type="text_value"></block>
                <block type="number_value"></block>
                <block type="field_selector"></block>
            </category>
        </xml>
        
        <script>
            // Data from Python
            const dimensions = {json.dumps(dimensions)};
            const metrics = {json.dumps(metrics)};
            let currentSegment = {current_segment};
            
            // Define custom blocks
            Blockly.defineBlocksWithJsonArray([
                // Container blocks
                {{
                    "type": "container_hit",
                    "message0": "Hit Container %1 %2",
                    "args0": [
                        {{
                            "type": "field_dropdown",
                            "name": "MODE",
                            "options": [["Include", "include"], ["Exclude", "exclude"]]
                        }},
                        {{
                            "type": "input_statement",
                            "name": "CONDITIONS"
                        }}
                    ],
                    "colour": "#FF6B00",
                    "tooltip": "Hit level container",
                    "output": "Container"
                }},
                {{
                    "type": "container_visit",
                    "message0": "Visit Container %1 %2",
                    "args0": [
                        {{
                            "type": "field_dropdown",
                            "name": "MODE",
                            "options": [["Include", "include"], ["Exclude", "exclude"]]
                        }},
                        {{
                            "type": "input_statement",
                            "name": "CONDITIONS"
                        }}
                    ],
                    "colour": "#FF6B00",
                    "tooltip": "Visit/Session level container",
                    "output": "Container"
                }},
                {{
                    "type": "container_visitor",
                    "message0": "Visitor Container %1 %2",
                    "args0": [
                        {{
                            "type": "field_dropdown",
                            "name": "MODE",
                            "options": [["Include", "include"], ["Exclude", "exclude"]]
                        }},
                        {{
                            "type": "input_statement",
                            "name": "CONDITIONS"
                        }}
                    ],
                    "colour": "#FF6B00",
                    "tooltip": "Visitor level container",
                    "output": "Container"
                }},
                
                // Logic blocks
                {{
                    "type": "logic_and",
                    "message0": "%1 AND %2",
                    "args0": [
                        {{"type": "input_value", "name": "A"}},
                        {{"type": "input_value", "name": "B"}}
                    ],
                    "inputsInline": true,
                    "output": "Boolean",
                    "colour": "#1473E6"
                }},
                {{
                    "type": "logic_or",
                    "message0": "%1 OR %2",
                    "args0": [
                        {{"type": "input_value", "name": "A"}},
                        {{"type": "input_value", "name": "B"}}
                    ],
                    "inputsInline": true,
                    "output": "Boolean",
                    "colour": "#1473E6"
                }},
                {{
                    "type": "logic_then",
                    "message0": "%1 THEN %2",
                    "args0": [
                        {{"type": "input_value", "name": "A"}},
                        {{"type": "input_value", "name": "B"}}
                    ],
                    "inputsInline": true,
                    "output": "Boolean",
                    "colour": "#1473E6"
                }},
                {{
                    "type": "logic_not",
                    "message0": "NOT %1",
                    "args0": [{{"type": "input_value", "name": "BOOL"}}],
                    "output": "Boolean",
                    "colour": "#1473E6"
                }},
                
                // Dimension blocks
                {{
                    "type": "dimension_equals",
                    "message0": "%1 equals %2",
                    "args0": [
                        {{
                            "type": "field_dropdown",
                            "name": "FIELD",
                            "options": [
                                {(', '.join([f'["{d["name"]}", "{d["field"]}"]' for d in dimensions[:5]]))}
                            ]
                        }},
                        {{"type": "input_value", "name": "VALUE", "check": "String"}}
                    ],
                    "inputsInline": true,
                    "output": "Boolean",
                    "colour": "#5AA3E0"
                }},
                {{
                    "type": "dimension_contains",
                    "message0": "%1 contains %2",
                    "args0": [
                        {{
                            "type": "field_dropdown",
                            "name": "FIELD",
                            "options": [
                                {(', '.join([f'["{d["name"]}", "{d["field"]}"]' for d in dimensions[:5]]))}
                            ]
                        }},
                        {{"type": "input_value", "name": "VALUE", "check": "String"}}
                    ],
                    "inputsInline": true,
                    "output": "Boolean",
                    "colour": "#5AA3E0"
                }},
                
                // Metric blocks
                {{
                    "type": "metric_greater_than",
                    "message0": "%1 > %2",
                    "args0": [
                        {{
                            "type": "field_dropdown",
                            "name": "FIELD",
                            "options": [
                                {(', '.join([f'["{m["name"]}", "{m["field"]}"]' for m in metrics[:5]]))}
                            ]
                        }},
                        {{"type": "input_value", "name": "VALUE", "check": "Number"}}
                    ],
                    "inputsInline": true,
                    "output": "Boolean",
                    "colour": "#44B556"
                }},
                {{
                    "type": "metric_less_than",
                    "message0": "%1 < %2",
                    "args0": [
                        {{
                            "type": "field_dropdown",
                            "name": "FIELD",
                            "options": [
                                {(', '.join([f'["{m["name"]}", "{m["field"]}"]' for m in metrics[:5]]))}
                            ]
                        }},
                        {{"type": "input_value", "name": "VALUE", "check": "Number"}}
                    ],
                    "inputsInline": true,
                    "output": "Boolean",
                    "colour": "#44B556"
                }},
                
                // Value blocks
                {{
                    "type": "text_value",
                    "message0": "%1",
                    "args0": [{{
                        "type": "field_input",
                        "name": "TEXT",
                        "text": "value"
                    }}],
                    "output": "String",
                    "colour": "#9E9E9E"
                }},
                {{
                    "type": "number_value",
                    "message0": "%1",
                    "args0": [{{
                        "type": "field_number",
                        "name": "NUM",
                        "value": 0
                    }}],
                    "output": "Number",
                    "colour": "#9E9E9E"
                }}
            ]);
            
            // Initialize Blockly
            const workspace = Blockly.inject('blocklyDiv', {{
                toolbox: document.getElementById('toolbox'),
                grid: {{
                    spacing: 20,
                    length: 3,
                    colour: '#E1E1E1',
                    snap: true
                }},
                zoom: {{
                    controls: true,
                    wheel: true,
                    startScale: 1.0,
                    maxScale: 3,
                    minScale: 0.3,
                    scaleSpeed: 1.2
                }},
                theme: {{
                    'base': Blockly.Themes.Classic,
                    'componentStyles': {{
                        'workspaceBackgroundColour': '#FFFFFF',
                        'toolboxBackgroundColour': '#F5F5F5',
                        'flyoutBackgroundColour': '#F5F5F5',
                        'scrollbarColour': '#D3D3D3'
                    }}
                }}
            }});
            
            // Generate segment from blocks
            function generateSegment() {{
                const blocks = workspace.getTopBlocks();
                const segment = {{
                    name: currentSegment.name || 'New Segment',
                    description: currentSegment.description || '',
                    container_type: 'hit',
                    containers: [],
                    logic: 'and'
                }};
                
                blocks.forEach(block => {{
                    if (block.type.startsWith('container_')) {{
                        const container = parseContainer(block);
                        if (container) {{
                            segment.containers.push(container);
                            // Set container type from first container
                            if (segment.containers.length === 1) {{
                                segment.container_type = container.type;
                            }}
                        }}
                    }}
                }});
                
                // Display result
                document.getElementById('output').textContent = JSON.stringify(segment, null, 2);
                
                // Send to Streamlit
                window.parent.postMessage({{
                    type: 'segmentUpdate',
                    segment: segment
                }}, '*');
            }}
            
            function parseContainer(block) {{
                const type = block.type.replace('container_', '');
                const mode = block.getFieldValue('MODE');
                const conditions = [];
                
                // Parse conditions from connected blocks
                const conditionsInput = block.getInput('CONDITIONS');
                if (conditionsInput && conditionsInput.connection && conditionsInput.connection.targetConnection) {{
                    const conditionBlock = conditionsInput.connection.targetConnection.getSourceBlock();
                    const condition = parseCondition(conditionBlock);
                    if (condition) {{
                        conditions.push(condition);
                    }}
                }}
                
                return {{
                    id: 'container_' + Date.now(),
                    type: type,
                    include: mode === 'include',
                    conditions: conditions,
                    logic: 'and'
                }};
            }}
            
            function parseCondition(block) {{
                if (!block) return null;
                
                if (block.type.startsWith('dimension_')) {{
                    const field = block.getFieldValue('FIELD');
                    const valueBlock = block.getInputTargetBlock('VALUE');
                    const value = valueBlock ? valueBlock.getFieldValue('TEXT') : '';
                    
                    return {{
                        id: 'cond_' + Date.now(),
                        field: field,
                        name: getDimensionName(field),
                        type: 'dimension',
                        operator: getOperatorFromBlockType(block.type),
                        value: value,
                        data_type: 'string'
                    }};
                }} else if (block.type.startsWith('metric_')) {{
                    const field = block.getFieldValue('FIELD');
                    const valueBlock = block.getInputTargetBlock('VALUE');
                    const value = valueBlock ? valueBlock.getFieldValue('NUM') : 0;
                    
                    return {{
                        id: 'cond_' + Date.now(),
                        field: field,
                        name: getMetricName(field),
                        type: 'metric',
                        operator: getOperatorFromBlockType(block.type),
                        value: value,
                        data_type: 'number'
                    }};
                }}
                
                return null;
            }}
            
            function getOperatorFromBlockType(blockType) {{
                const operatorMap = {{
                    'dimension_equals': 'equals',
                    'dimension_contains': 'contains',
                    'dimension_starts_with': 'starts with',
                    'dimension_exists': 'exists',
                    'metric_greater_than': 'is greater than',
                    'metric_less_than': 'is less than',
                    'metric_equals': 'equals',
                    'metric_between': 'is between'
                }};
                return operatorMap[blockType] || 'equals';
            }}
            
            function getDimensionName(field) {{
                const dim = dimensions.find(d => d.field === field);
                return dim ? dim.name : field;
            }}
            
            function getMetricName(field) {{
                const met = metrics.find(m => m.field === field);
                return met ? met.name : field;
            }}
            
            function resetWorkspace() {{
                workspace.clear();
                document.getElementById('output').textContent = 'Drag blocks to build your segment...';
            }}
            
            // Load existing segment if available
            if (currentSegment.containers && currentSegment.containers.length > 0) {{
                // TODO: Convert segment to blocks
                document.getElementById('output').textContent = 'Existing segment loaded. Edit using blocks.';
            }}
        </script>
    </body>
    </html>
    """
    
    return components.html(html_content, height=700, scrolling=False)