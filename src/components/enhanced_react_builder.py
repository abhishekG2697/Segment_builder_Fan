import streamlit as st
import json
import uuid
from typing import Dict, List, Any, Optional


def render_enhanced_react_segment_builder(config: Dict, current_segment: Dict = None) -> str:
    """
    Render the enhanced React segment builder with nested container support
    """

    # Get data from config
    dimensions = config.get('dimensions', [])
    metrics = config.get('metrics', [])
    segments = config.get('segments', [])

    # Set default segment if none provided
    if not current_segment:
        current_segment = {
            'name': 'New Segment',
            'description': '',
            'container_type': 'hit',
            'logic': 'and',
            'containers': []
        }

    # Generate HTML with embedded React component
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Adobe Analytics Segment Builder</title>
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Adobe Clean', 'Source Sans Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f5f5;
            }}

            /* Component-specific styles */
            .segment-builder {{
                display: flex;
                height: 100vh;
                font-family: 'Adobe Clean', 'Source Sans Pro', sans-serif;
                color: #2c2c2c;
                background: #f5f5f5;
            }}

            .sidebar {{
                width: 280px;
                background: white;
                border-right: 1px solid #e1e1e1;
                overflow-y: auto;
                flex-shrink: 0;
            }}

            .sidebar-content {{
                padding: 16px;
            }}

            .sidebar-section {{
                margin-bottom: 24px;
            }}

            .sidebar-title {{
                font-size: 13px;
                font-weight: 700;
                color: #2c2c2c;
                text-transform: uppercase;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #e1e1e1;
            }}

            .sidebar-count {{
                background: #6e6e6e;
                color: white;
                border-radius: 12px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: 400;
                min-width: 20px;
                text-align: center;
            }}

            .sidebar-item {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 10px 12px;
                margin-bottom: 2px;
                border-radius: 4px;
                cursor: move;
                transition: all 0.2s ease;
                border: 1px solid transparent;
                background: white;
            }}

            .sidebar-item:hover {{
                background: #f8f9fa;
                border-color: #e1e1e1;
                transform: translateY(-1px);
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}

            .sidebar-item.dragging {{
                opacity: 0.5;
                transform: rotate(3deg);
            }}

            .sidebar-item-content {{
                display: flex;
                align-items: center;
                flex: 1;
                gap: 8px;
            }}

            .sidebar-item-icon {{
                font-size: 16px;
                width: 20px;
                text-align: center;
            }}

            .sidebar-item-name {{
                font-size: 14px;
                color: #2c2c2c;
                font-weight: 400;
            }}

            .sidebar-add-btn {{
                width: 28px;
                height: 28px;
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
            }}

            .sidebar-add-btn:hover {{
                background: #1473e6;
                color: white;
                border-color: #1473e6;
                transform: scale(1.1);
            }}

            .main-area {{
                flex: 1;
                display: flex;
                flex-direction: column;
                background: white;
                overflow: hidden;
            }}

            .segment-header {{
                padding: 16px 24px;
                border-bottom: 1px solid #e1e1e1;
                background: white;
                flex-shrink: 0;
            }}

            .segment-title {{
                font-size: 18px;
                font-weight: 400;
                color: #2c2c2c;
                margin: 0;
            }}

            .builder-interface {{
                flex: 1;
                padding: 24px;
                overflow-y: auto;
                background: #fafafa;
            }}

            .segment-definition {{
                min-height: 100%;
                position: relative;
            }}

            .empty-state {{
                text-align: center;
                padding: 80px 20px;
                color: #6e6e6e;
                border: 2px dashed #d3d3d3;
                border-radius: 12px;
                background: white;
                margin: 40px 0;
            }}

            .empty-state-icon {{
                font-size: 64px;
                margin-bottom: 20px;
                opacity: 0.7;
            }}

            .empty-state-text {{
                font-size: 16px;
                line-height: 1.5;
                color: #6e6e6e;
            }}

            .container-wrapper {{
                margin-bottom: 16px;
                position: relative;
            }}

            .container {{
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                background: white;
                transition: all 0.3s ease;
                overflow: hidden;
            }}

            .container:hover {{
                border-color: #1473e6;
                box-shadow: 0 4px 16px rgba(20, 115, 230, 0.15);
            }}

            .container.drag-over {{
                border-color: #12b886;
                background: #f0fff4;
                box-shadow: 0 4px 16px rgba(18, 184, 134, 0.2);
            }}

            .container-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 16px 20px;
                background: linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%);
                border-bottom: 1px solid #e1e1e1;
            }}

            .container-controls {{
                display: flex;
                align-items: center;
                gap: 16px;
            }}

            .collapse-btn {{
                background: none;
                border: none;
                cursor: pointer;
                color: #6e6e6e;
                padding: 4px;
                border-radius: 4px;
                display: flex;
                align-items: center;
                transition: all 0.2s ease;
            }}

            .collapse-btn:hover {{
                background: #e1e1e1;
                color: #2c2c2c;
            }}

            .drag-handle {{
                color: #6e6e6e;
                cursor: grab;
                padding: 4px;
                border-radius: 4px;
                transition: all 0.2s ease;
            }}

            .drag-handle:hover {{
                background: #e1e1e1;
                color: #2c2c2c;
            }}

            .drag-handle:active {{
                cursor: grabbing;
            }}

            .radio-group {{
                display: flex;
                gap: 20px;
                align-items: center;
            }}

            .radio-label {{
                display: flex;
                align-items: center;
                font-size: 14px;
                cursor: pointer;
                font-weight: 500;
                gap: 6px;
            }}

            .radio-label input[type="radio"] {{
                margin: 0;
                transform: scale(1.2);
            }}

            .include-dot {{
                color: #12b886;
                font-size: 12px;
                margin-left: 4px;
            }}

            .exclude-dot {{
                color: #e34850;
                font-size: 12px;
                margin-left: 4px;
            }}

            .container-type, .container-logic, .condition-logic, .segment-logic {{
                border: 1px solid #d3d3d3;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background: white;
                color: #2c2c2c;
                font-weight: 500;
                min-width: 100px;
                transition: all 0.2s ease;
            }}

            .container-type:focus, .container-logic:focus, .condition-logic:focus, .segment-logic:focus {{
                outline: none;
                border-color: #1473e6;
                box-shadow: 0 0 0 3px rgba(20, 115, 230, 0.15);
            }}

            .container-actions {{
                display: flex;
                gap: 8px;
            }}

            .action-btn {{
                width: 32px;
                height: 32px;
                border: 1px solid #d3d3d3;
                background: white;
                border-radius: 6px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #6e6e6e;
                transition: all 0.2s ease;
            }}

            .action-btn:hover {{
                transform: translateY(-1px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }}

            .add-container-btn:hover {{
                background: #1473e6;
                color: white;
                border-color: #1473e6;
            }}

            .remove-container-btn:hover {{
                background: #e34850;
                color: white;
                border-color: #e34850;
            }}

            .container-content {{
                padding: 20px;
            }}

            .empty-container {{
                text-align: center;
                padding: 30px 20px;
                color: #6e6e6e;
                font-size: 14px;
                border: 2px dashed #d3d3d3;
                border-radius: 8px;
                background: #fafafa;
            }}

            .condition {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 16px;
                border: 1px solid #e1e1e1;
                border-radius: 8px;
                background: white;
                margin-bottom: 12px;
                transition: all 0.2s ease;
            }}

            .condition:hover {{
                border-color: #1473e6;
                box-shadow: 0 2px 8px rgba(20, 115, 230, 0.1);
            }}

            .condition-content {{
                display: flex;
                align-items: center;
                gap: 12px;
                flex: 1;
            }}

            .condition-icon {{
                font-size: 18px;
                width: 24px;
                text-align: center;
            }}

            .condition-name {{
                font-weight: 600;
                min-width: 140px;
                color: #2c2c2c;
            }}

            .condition-operator {{
                min-width: 160px;
                border: 1px solid #d3d3d3;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background: white;
                color: #2c2c2c;
            }}

            .condition-value {{
                flex: 1;
                border: 1px solid #d3d3d3;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background: white;
                color: #2c2c2c;
            }}

            .condition-value:focus, .condition-operator:focus {{
                outline: none;
                border-color: #1473e6;
                box-shadow: 0 0 0 3px rgba(20, 115, 230, 0.15);
            }}

            .condition-remove {{
                width: 32px;
                height: 32px;
                border: 1px solid #d3d3d3;
                background: white;
                border-radius: 6px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #6e6e6e;
                transition: all 0.2s ease;
            }}

            .condition-remove:hover {{
                background: #e34850;
                color: white;
                border-color: #e34850;
                transform: scale(1.1);
            }}

            .logic-operator {{
                text-align: center;
                margin: 12px 0;
            }}

            .container-logic-operator {{
                text-align: center;
                margin: 20px 0;
                position: relative;
            }}

            .container-logic-operator::before,
            .container-logic-operator::after {{
                content: '';
                position: absolute;
                top: 50%;
                width: 100px;
                height: 1px;
                background: #d3d3d3;
            }}

            .container-logic-operator::before {{
                left: 0;
            }}

            .container-logic-operator::after {{
                right: 0;
            }}

            .add-root-container {{
                text-align: center;
                margin-top: 40px;
            }}

            .add-root-container button {{
                background: linear-gradient(135deg, #1473e6 0%, #0d66d0 100%);
                color: white;
                border: none;
                padding: 16px 32px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 10px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(20, 115, 230, 0.3);
            }}

            .add-root-container button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(20, 115, 230, 0.4);
            }}

            .add-root-container button:active {{
                transform: translateY(0);
            }}

            /* Nested container indentation styles */
            .container-wrapper[data-level="1"] {{
                margin-left: 24px;
                position: relative;
            }}

            .container-wrapper[data-level="2"] {{
                margin-left: 48px;
                position: relative;
            }}

            .container-wrapper[data-level="3"] {{
                margin-left: 72px;
                position: relative;
            }}

            .container-wrapper[data-level="4"] {{
                margin-left: 96px;
                position: relative;
            }}

            /* Connection lines for nested containers */
            .container-wrapper[data-level]:not([data-level="0"])::before {{
                content: '';
                position: absolute;
                left: -12px;
                top: 0;
                bottom: 0;
                width: 2px;
                background: #e1e1e1;
            }}

            .container-wrapper[data-level]:not([data-level="0"])::after {{
                content: '';
                position: absolute;
                left: -12px;
                top: 24px;
                width: 12px;
                height: 2px;
                background: #e1e1e1;
            }}

            /* Scrollbar styling */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}

            ::-webkit-scrollbar-track {{
                background: #f1f1f1;
                border-radius: 4px;
            }}

            ::-webkit-scrollbar-thumb {{
                background: #c1c1c1;
                border-radius: 4px;
            }}

            ::-webkit-scrollbar-thumb:hover {{
                background: #a8a8a8;
            }}
        </style>
    </head>
    <body>
        <div id="root"></div>

        <script type="text/babel">
            const {{ useState, useRef, useCallback, useEffect }} = React;

            const NestedSegmentBuilder = () => {{
                // Initialize data from Python
                const [dimensions] = useState({json.dumps(dimensions)});
                const [metrics] = useState({json.dumps(metrics)});
                const [segments] = useState({json.dumps(segments)});

                const [segment, setSegment] = useState({json.dumps(current_segment)});
                const [draggedItem, setDraggedItem] = useState(null);
                const [collapsedContainers, setCollapsedContainers] = useState(new Set());
                const [hoveredContainer, setHoveredContainer] = useState(null);

                const dropZoneRef = useRef(null);

                // Generate unique IDs
                const generateId = () => Date.now().toString(36) + Math.random().toString(36).substr(2, 9);

                // Container management functions
                const createNewContainer = (type = 'hit', include = true) => ({{
                    id: generateId(),
                    type,
                    include,
                    logic: 'and',
                    conditions: [],
                    children: []
                }});

                // Find container by path
                const findContainerByPath = (containers, path) => {{
                    if (!path || path.length === 0) return null;

                    let current = containers[path[0]];
                    for (let i = 1; i < path.length; i++) {{
                        if (!current || !current.children) return null;
                        current = current.children[path[i]];
                    }}
                    return current;
                }};

                // Update container at path
                const updateContainerAtPath = (path, updater) => {{
                    setSegment(prev => {{
                        const newSegment = {{ ...prev }};

                        if (path.length === 1) {{
                            newSegment.containers[path[0]] = updater(newSegment.containers[path[0]]);
                        }} else {{
                            const parent = findContainerByPath(newSegment.containers, path.slice(0, -1));
                            if (parent) {{
                                parent.children[path[path.length - 1]] = updater(parent.children[path[path.length - 1]]);
                            }}
                        }}

                        return newSegment;
                    }});
                }};

                // Add container
                const addContainer = (parentPath = null) => {{
                    const newContainer = createNewContainer();

                    setSegment(prev => {{
                        const newSegment = {{ ...prev }};

                        if (!parentPath) {{
                            // Add at root level
                            newSegment.containers.push(newContainer);
                        }} else {{
                            // Add as child
                            const parent = findContainerByPath(newSegment.containers, parentPath);
                            if (parent) {{
                                parent.children.push(newContainer);
                            }}
                        }}

                        return newSegment;
                    }});
                }};

                // Remove container
                const removeContainer = (path) => {{
                    setSegment(prev => {{
                        const newSegment = {{ ...prev }};

                        if (path.length === 1) {{
                            newSegment.containers.splice(path[0], 1);
                        }} else {{
                            const parent = findContainerByPath(newSegment.containers, path.slice(0, -1));
                            if (parent) {{
                                parent.children.splice(path[path.length - 1], 1);
                            }}
                        }}

                        return newSegment;
                    }});
                }};

                // Add condition to container
                const addConditionToContainer = (item, containerPath) => {{
                    const condition = {{
                        id: generateId(),
                        field: item.field,
                        name: item.name,
                        type: item.type,
                        operator: item.dataType === 'number' ? 'equals' : 'equals',
                        value: '',
                        data_type: item.dataType
                    }};

                    updateContainerAtPath(containerPath, (container) => ({{
                        ...container,
                        conditions: [...container.conditions, condition]
                    }}));
                }};

                // Remove condition
                const removeCondition = (containerPath, conditionIndex) => {{
                    updateContainerAtPath(containerPath, (container) => ({{
                        ...container,
                        conditions: container.conditions.filter((_, index) => index !== conditionIndex)
                    }}));
                }};

                // Update condition
                const updateCondition = (containerPath, conditionIndex, field, value) => {{
                    updateContainerAtPath(containerPath, (container) => {{
                        const newConditions = [...container.conditions];
                        newConditions[conditionIndex] = {{ ...newConditions[conditionIndex], [field]: value }};
                        return {{ ...container, conditions: newConditions }};
                    }});
                }};

                // Toggle container collapse
                const toggleCollapse = (containerId) => {{
                    setCollapsedContainers(prev => {{
                        const newSet = new Set(prev);
                        if (newSet.has(containerId)) {{
                            newSet.delete(containerId);
                        }} else {{
                            newSet.add(containerId);
                        }}
                        return newSet;
                    }});
                }};

                // Drag and drop handlers
                const handleDragStart = (e, item) => {{
                    setDraggedItem(item);
                    e.dataTransfer.effectAllowed = 'copy';
                    e.target.classList.add('dragging');
                }};

                const handleDragEnd = (e) => {{
                    e.target.classList.remove('dragging');
                    setDraggedItem(null);
                }};

                const handleDragOver = (e) => {{
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'copy';
                }};

                const handleDrop = (e, containerPath) => {{
                    e.preventDefault();
                    e.stopPropagation();

                    if (draggedItem) {{
                        addConditionToContainer(draggedItem, containerPath);
                        setDraggedItem(null);
                    }}

                    // Remove drag-over class
                    e.currentTarget.classList.remove('drag-over');
                }};

                const handleDragEnter = (e) => {{
                    e.preventDefault();
                    e.currentTarget.classList.add('drag-over');
                }};

                const handleDragLeave = (e) => {{
                    e.preventDefault();
                    if (!e.currentTarget.contains(e.relatedTarget)) {{
                        e.currentTarget.classList.remove('drag-over');
                    }}
                }};

                // Send data to Streamlit
                const sendToStreamlit = useCallback(() => {{
                    if (typeof window !== 'undefined' && window.parent) {{
                        window.parent.postMessage({{
                            type: 'segment_update',
                            data: segment
                        }}, '*');
                    }}
                }}, [segment]);

                // Send updates to Streamlit when segment changes
                useEffect(() => {{
                    sendToStreamlit();
                }}, [segment, sendToStreamlit]);

                // Render sidebar item
                const renderSidebarItem = (item, icon) => (
                    <div
                        key={{item.id}}
                        className="sidebar-item"
                        draggable
                        onDragStart={{(e) => handleDragStart(e, item)}}
                        onDragEnd={{handleDragEnd}}
                    >
                        <div className="sidebar-item-content">
                            <span className="sidebar-item-icon">{{icon}}</span>
                            <span className="sidebar-item-name">{{item.name}}</span>
                        </div>
                        <button
                            className="sidebar-add-btn"
                            onClick={{() => {{
                                if (segment.containers.length === 0) {{
                                    addContainer();
                                }}
                                const lastContainerPath = [segment.containers.length - 1];
                                addConditionToContainer(item, lastContainerPath);
                            }}}}
                            title="Add to segment"
                        >
                            +
                        </button>
                    </div>
                );

                // Render condition
                const renderCondition = (condition, containerPath, conditionIndex) => (
                    <div key={{condition.id}} className="condition">
                        <div className="condition-content">
                            <span className="condition-icon">
                                {{condition.type === 'dimension' ? '📊' : '📈'}}
                            </span>
                            <span className="condition-name">{{condition.name}}</span>
                            <select
                                value={{condition.operator}}
                                onChange={{(e) => updateCondition(containerPath, conditionIndex, 'operator', e.target.value)}}
                                className="condition-operator"
                            >
                                <option value="equals">equals</option>
                                <option value="not_equals">does not equal</option>
                                <option value="contains">contains</option>
                                <option value="not_contains">does not contain</option>
                                <option value="starts_with">starts with</option>
                                <option value="ends_with">ends with</option>
                                {{condition.data_type === 'number' && (
                                    <>
                                        <option value="greater_than">greater than</option>
                                        <option value="less_than">less than</option>
                                        <option value="greater_equal">greater than or equal</option>
                                        <option value="less_equal">less than or equal</option>
                                    </>
                                )}}
                            </select>
                            <input
                                type={{condition.data_type === 'number' ? 'number' : 'text'}}
                                value={{condition.value}}
                                onChange={{(e) => updateCondition(containerPath, conditionIndex, 'value', e.target.value)}}
                                placeholder="Enter value..."
                                className="condition-value"
                            />
                        </div>
                        <button
                            className="condition-remove"
                            onClick={{() => removeCondition(containerPath, conditionIndex)}}
                            title="Remove condition"
                        >
                            ×
                        </button>
                    </div>
                );

                // Render container recursively
                const renderContainer = (container, path, level = 0) => {{
                    const isCollapsed = collapsedContainers.has(container.id);
                    const hasChildren = container.children && container.children.length > 0;
                    const hasConditions = container.conditions && container.conditions.length > 0;
                    const hasContent = hasChildren || hasConditions;

                    return (
                        <div key={{container.id}} className="container-wrapper" data-level={{level}}>
                            <div
                                className="container"
                                onDragOver={{handleDragOver}}
                                onDrop={{(e) => handleDrop(e, path)}}
                                onDragEnter={{handleDragEnter}}
                                onDragLeave={{handleDragLeave}}
                            >
                                <div className="container-header">
                                    <div className="container-controls">
                                        {{hasContent && (
                                            <button
                                                className="collapse-btn"
                                                onClick={{() => toggleCollapse(container.id)}}
                                                title={{isCollapsed ? "Expand container" : "Collapse container"}}
                                            >
                                                {{isCollapsed ? '▶' : '▼'}}
                                            </button>
                                        )}}

                                        {{level > 0 && <span className="drag-handle" title="Drag to reorder">⋮⋮</span>}}

                                        <div className="radio-group">
                                            <label className="radio-label">
                                                <input
                                                    type="radio"
                                                    name={{`include_${{container.id}}`}}
                                                    checked={{container.include}}
                                                    onChange={{() => updateContainerAtPath(path, (c) => ({{...c, include: true}}))}}
                                                />
                                                <span className="include-dot">●</span> Include
                                            </label>
                                            <label className="radio-label">
                                                <input
                                                    type="radio"
                                                    name={{`include_${{container.id}}`}}
                                                    checked={{!container.include}}
                                                    onChange={{() => updateContainerAtPath(path, (c) => ({{...c, include: false}}))}}
                                                />
                                                <span className="exclude-dot">●</span> Exclude
                                            </label>
                                        </div>

                                        <select
                                            value={{container.type}}
                                            onChange={{(e) => updateContainerAtPath(path, (c) => ({{...c, type: e.target.value}}))}}
                                            className="container-type"
                                        >
                                            <option value="hit">Hit</option>
                                            <option value="visit">Visit</option>
                                            <option value="visitor">Visitor</option>
                                        </select>

                                        {{level > 0 && (
                                            <select
                                                value={{container.logic}}
                                                onChange={{(e) => updateContainerAtPath(path, (c) => ({{...c, logic: e.target.value}}))}}
                                                className="container-logic"
                                            >
                                                <option value="and">AND</option>
                                                <option value="or">OR</option>
                                                <option value="then">THEN</option>
                                            </select>
                                        )}}
                                    </div>

                                    <div className="container-actions">
                                        <button
                                            className="action-btn add-container-btn"
                                            onClick={{() => addContainer(path)}}
                                            title="Add nested container"
                                        >
                                            +
                                        </button>
                                        <button
                                            className="action-btn remove-container-btn"
                                            onClick={{() => removeContainer(path)}}
                                            title="Remove container"
                                        >
                                            ×
                                        </button>
                                    </div>
                                </div>

                                {{!isCollapsed && (
                                    <div className="container-content">
                                        {{/* Conditions */}}
                                        {{container.conditions.map((condition, index) => (
                                            <div key={{condition.id}}>
                                                {{index > 0 && (
                                                    <div className="logic-operator">
                                                        <select
                                                            value={{container.logic}}
                                                            onChange={{(e) => updateContainerAtPath(path, (c) => ({{...c, logic: e.target.value}}))}}
                                                            className="condition-logic"
                                                        >
                                                            <option value="and">AND</option>
                                                            <option value="or">OR</option>
                                                            <option value="then">THEN</option>
                                                        </select>
                                                    </div>
                                                )}}
                                                {{renderCondition(condition, path, index)}}
                                            </div>
                                        ))}}

                                        {{/* Empty state */}}
                                        {{container.conditions.length === 0 && container.children.length === 0 && (
                                            <div className="empty-container">
                                                <p>Drag components here or use the + buttons</p>
                                            </div>
                                        )}}
                                    </div>
                                )}}
                            </div>

                            {{/* Render child containers */}}
                            {{!isCollapsed && container.children && container.children.map((child, index) => (
                                <div key={{child.id}}>
                                    {{index > 0 && level === 0 && (
                                        <div className="container-logic-operator">
                                            <select
                                                value={{segment.logic}}
                                                onChange={{(e) => setSegment(prev => ({{...prev, logic: e.target.value}}))}}
                                                className="segment-logic"
                                            >
                                                <option value="and">AND</option>
                                                <option value="or">OR</option>
                                            </select>
                                        </div>
                                    )}}
                                    {{renderContainer(child, [...path, index], level + 1)}}
                                </div>
                            ))}}
                        </div>
                    );
                }};

                return (
                    <div className="segment-builder">
                        {{/* Sidebar */}}
                        <div className="sidebar">
                            <div className="sidebar-content">
                                <div className="sidebar-section">
                                    <div className="sidebar-title">
                                        Dimensions
                                        <span className="sidebar-count">{{dimensions.length}}</span>
                                    </div>
                                    {{dimensions.map(dim => renderSidebarItem(dim, '📊'))}}
                                </div>

                                <div className="sidebar-section">
                                    <div className="sidebar-title">
                                        Metrics
                                        <span className="sidebar-count">{{metrics.length}}</span>
                                    </div>
                                    {{metrics.map(metric => renderSidebarItem(metric, '📈'))}}
                                </div>

                                {{segments.length > 0 && (
                                    <div className="sidebar-section">
                                        <div className="sidebar-title">
                                            Segments
                                            <span className="sidebar-count">{{segments.length}}</span>
                                        </div>
                                        {{segments.map(seg => renderSidebarItem(seg, '🎯'))}}
                                    </div>
                                )}}
                            </div>
                        </div>

                        {{/* Main Area */}}
                        <div className="main-area">
                            <div className="segment-header">
                                <h2 className="segment-title">Segment Definition</h2>
                            </div>

                            <div className="builder-interface">
                                <div className="segment-definition" ref={{dropZoneRef}}>
                                    {{segment.containers.length === 0 ? (
                                        <div className="empty-state">
                                            <div className="empty-state-icon">🎯</div>
                                            <div className="empty-state-text">
                                                Drag components here to build your segment<br />
                                                or click the + button next to items
                                            </div>
                                        </div>
                                    ) : (
                                        segment.containers.map((container, index) => (
                                            <div key={{container.id}}>
                                                {{index > 0 && (
                                                    <div className="container-logic-operator">
                                                        <select
                                                            value={{segment.logic}}
                                                            onChange={{(e) => setSegment(prev => ({{...prev, logic: e.target.value}}))}}
                                                            className="segment-logic"
                                                        >
                                                            <option value="and">AND</option>
                                                            <option value="or">OR</option>
                                                        </select>
                                                    </div>
                                                )}}
                                                {{renderContainer(container, [index], 0)}}
                                            </div>
                                        ))
                                    )}}

                                    <div className="add-root-container">
                                        <button onClick={{() => addContainer()}}>
                                            <span style={{{fontSize: '18px'}}}>+</span>
                                            Add Container
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                );
            }};

            // Render the component
            ReactDOM.render(<NestedSegmentBuilder />, document.getElementById('root'));
        </script>
    </body>
    </html>
    """

    # Use Streamlit's HTML component to render
    st.components.v1.html(html_content, height=600, scrolling=False)

    return "enhanced_react_segment_builder_rendered"


def handle_segment_update_messages():
    """
    Handle messages from the React component
    """
    # This would be called in your main Streamlit app to handle updates
    # You can use st.session_state to store the updated segment data
    pass


# Additional utility functions for the enhanced builder

def flatten_containers(containers, level=0):
    """
    Flatten nested containers for analysis and export
    """
    flat_containers = []

    for container in containers:
        flat_container = {
            **container,
            'level': level,
            'children': []  # Remove children from flattened version
        }
        flat_containers.append(flat_container)

        # Recursively flatten children
        if container.get('children'):
            flat_containers.extend(flatten_containers(container['children'], level + 1))

    return flat_containers


def validate_nested_segment(segment_definition):
    """
    Validate a nested segment definition
    """
    errors = []
    warnings = []

    if not segment_definition:
        errors.append("Segment definition is empty")
        return errors, warnings

    containers = segment_definition.get('containers', [])

    if not containers:
        errors.append("Segment must have at least one container")
        return errors, warnings

    def validate_container(container, path="root"):
        container_errors = []
        container_warnings = []

        # Check required fields
        if not container.get('type'):
            container_errors.append(f"Container at {path} missing type")

        if 'include' not in container:
            container_errors.append(f"Container at {path} missing include/exclude setting")

        # Check conditions
        conditions = container.get('conditions', [])
        if not conditions and not container.get('children'):
            container_warnings.append(f"Container at {path} has no conditions or child containers")

        for i, condition in enumerate(conditions):
            if not condition.get('field'):
                container_errors.append(f"Condition {i} at {path} missing field")
            if not condition.get('operator'):
                container_errors.append(f"Condition {i} at {path} missing operator")
            if condition.get('value') == '':
                container_warnings.append(f"Condition {i} at {path} has empty value")

        # Validate children recursively
        children = container.get('children', [])
        for i, child in enumerate(children):
            child_errors, child_warnings = validate_container(child, f"{path}.children[{i}]")
            container_errors.extend(child_errors)
            container_warnings.extend(child_warnings)

        return container_errors, container_warnings

    # Validate each root container
    for i, container in enumerate(containers):
        container_errors, container_warnings = validate_container(container, f"containers[{i}]")
        errors.extend(container_errors)
        warnings.extend(container_warnings)

    return errors, warnings


def export_to_adobe_analytics_format(segment_definition):
    """
    Export segment definition to Adobe Analytics compatible JSON format
    """
    if not segment_definition:
        return None

    def convert_container(container):
        adobe_container = {
            "func": "container",
            "context": container.get('type', 'hit'),
            "pred": {
                "func": "and" if container.get('logic', 'and') == 'and' else "or",
                "preds": []
            }
        }

        # Add conditions
        for condition in container.get('conditions', []):
            adobe_condition = {
                "func": condition.get('operator', 'equals'),
                "dim": condition.get('field'),
                "val": condition.get('value')
            }
            adobe_container["pred"]["preds"].append(adobe_condition)

        # Add child containers
        for child in container.get('children', []):
            adobe_container["pred"]["preds"].append(convert_container(child))

        # Handle include/exclude
        if not container.get('include', True):
            adobe_container = {
                "func": "not",
                "pred": adobe_container
            }

        return adobe_container

    # Build the main segment structure
    adobe_segment = {
        "name": segment_definition.get('name', 'Unnamed Segment'),
        "description": segment_definition.get('description', ''),
        "definition": {
            "func": segment_definition.get('logic', 'and'),
            "preds": []
        }
    }

    # Convert containers
    for container in segment_definition.get('containers', []):
        adobe_segment["definition"]["preds"].append(convert_container(container))

    return adobe_segment


def calculate_segment_complexity_score(segment_definition):
    """
    Calculate complexity score for nested segments
    """
    if not segment_definition:
        return 0

    score = 0

    def score_container(container, depth=0):
        container_score = 0

        # Base score for container
        container_score += 1

        # Depth penalty (nested containers are more complex)
        container_score += depth * 2

        # Conditions score
        conditions = container.get('conditions', [])
        container_score += len(conditions)

        # Complex operators add more complexity
        for condition in conditions:
            operator = condition.get('operator', 'equals')
            if operator in ['not_equals', 'not_contains', 'greater_than', 'less_than']:
                container_score += 1
            elif operator in ['greater_equal', 'less_equal']:
                container_score += 2

        # Logic complexity
        if container.get('logic') in ['or', 'then']:
            container_score += 1

        # Exclude containers are more complex
        if not container.get('include', True):
            container_score += 2

        # Recursively score children
        for child in container.get('children', []):
            container_score += score_container(child, depth + 1)

        return container_score

    # Score all containers
    for container in segment_definition.get('containers', []):
        score += score_container(container)

    # Segment-level logic complexity
    if segment_definition.get('logic') == 'or':
        score += 1

    return score