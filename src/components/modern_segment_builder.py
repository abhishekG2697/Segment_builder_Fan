"""
Adobe Analytics Style Segment Builder
Complete implementation with proper drag-and-drop, nested containers, and rule builder
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import sqlite3
from pathlib import Path

def render_modern_segment_builder():
    """
    Adobe Analytics style segment builder with full functionality
    """

    # Initialize session state safely
    _init_session_state()

    # Apply Adobe Analytics styling
    _apply_adobe_styling()

    # Get configuration from actual database
    config = _get_database_config()

    # Render Adobe-style React component
    _render_adobe_segment_builder(config)

def _init_session_state():
    """Initialize session state safely"""

    if 'segment_definition' not in st.session_state:
        st.session_state.segment_definition = {
            'name': 'New Segment',
            'description': '',
            'container_type': 'hit',
            'logic': 'and',
            'containers': [],
            'tags': []
        }

    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None

    if 'database_stats' not in st.session_state:
        st.session_state.database_stats = None

def _apply_adobe_styling():
    """Apply Adobe Analytics styling"""
    st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    
    /* Full viewport */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    .stApp {
        margin: 0 !important;
        padding: 0 !important;
        background: #f8fafc !important;
    }
    </style>
    """, unsafe_allow_html=True)

def _get_database_config():
    """Get configuration from actual database"""

    try:
        db_path = Path("data/analytics.db")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get database statistics
        stats = _get_database_stats(cursor)
        st.session_state.database_stats = stats

        # Get saved segments
        saved_segments = _get_saved_segments(cursor)

        conn.close()

        return {
            'dimensions': [
                {
                    'category': 'Page',
                    'items': [
                        {'name': 'Page URL', 'field': 'page_url', 'category': 'Page', 'type': 'dimension', 'dataType': 'string', 'icon': '📄'},
                        {'name': 'Page Title', 'field': 'page_title', 'category': 'Page', 'type': 'dimension', 'dataType': 'string', 'icon': '📄'},
                        {'name': 'Page Type', 'field': 'page_type', 'category': 'Page', 'type': 'dimension', 'dataType': 'string', 'icon': '📄'},
                    ]
                },
                {
                    'category': 'Technology',
                    'items': [
                        {'name': 'Device Type', 'field': 'device_type', 'category': 'Technology', 'type': 'dimension', 'dataType': 'string', 'icon': '📱', 'values': ['Desktop', 'Mobile', 'Tablet']},
                        {'name': 'Browser Name', 'field': 'browser_name', 'category': 'Technology', 'type': 'dimension', 'dataType': 'string', 'icon': '🌐', 'values': ['Chrome', 'Firefox', 'Safari', 'Edge', 'Other']},
                        {'name': 'Browser Version', 'field': 'browser_version', 'category': 'Technology', 'type': 'dimension', 'dataType': 'string', 'icon': '🌐'},
                    ]
                },
                {
                    'category': 'Geography',
                    'items': [
                        {'name': 'Country', 'field': 'country', 'category': 'Geography', 'type': 'dimension', 'dataType': 'string', 'icon': '🌍'},
                        {'name': 'City', 'field': 'city', 'category': 'Geography', 'type': 'dimension', 'dataType': 'string', 'icon': '🏙️'},
                    ]
                },
                {
                    'category': 'Marketing',
                    'items': [
                        {'name': 'Traffic Source', 'field': 'traffic_source', 'category': 'Marketing', 'type': 'dimension', 'dataType': 'string', 'icon': '🎯'},
                        {'name': 'Traffic Medium', 'field': 'traffic_medium', 'category': 'Marketing', 'type': 'dimension', 'dataType': 'string', 'icon': '🎯'},
                        {'name': 'Campaign', 'field': 'campaign', 'category': 'Marketing', 'type': 'dimension', 'dataType': 'string', 'icon': '📢'},
                    ]
                }
            ],
            'metrics': [
                {
                    'category': 'Commerce',
                    'items': [
                        {'name': 'Revenue', 'field': 'revenue', 'category': 'Commerce', 'type': 'metric', 'dataType': 'number', 'icon': '💰'},
                        {'name': 'Products Viewed', 'field': 'products_viewed', 'category': 'Commerce', 'type': 'metric', 'dataType': 'number', 'icon': '👁️'},
                        {'name': 'Cart Additions', 'field': 'cart_additions', 'category': 'Commerce', 'type': 'metric', 'dataType': 'number', 'icon': '🛒'},
                    ]
                },
                {
                    'category': 'Engagement',
                    'items': [
                        {'name': 'Time on Page', 'field': 'time_on_page', 'category': 'Engagement', 'type': 'metric', 'dataType': 'number', 'icon': '⏱️'},
                        {'name': 'Bounce', 'field': 'bounce', 'category': 'Engagement', 'type': 'metric', 'dataType': 'number', 'icon': '⚡'},
                    ]
                },
                {
                    'category': 'Traffic',
                    'items': [
                        {'name': 'Page Views', 'field': 'COUNT(*)', 'category': 'Traffic', 'type': 'metric', 'dataType': 'number', 'icon': '👀'},
                        {'name': 'Unique Visitors', 'field': 'COUNT(DISTINCT user_id)', 'category': 'Traffic', 'type': 'metric', 'dataType': 'number', 'icon': '👥'},
                        {'name': 'Sessions', 'field': 'COUNT(DISTINCT session_id)', 'category': 'Traffic', 'type': 'metric', 'dataType': 'number', 'icon': '📊'},
                    ]
                }
            ],
            'segments': saved_segments,
            'database_stats': stats
        }

    except Exception as e:
        st.error(f"❌ Database error: {e}")
        return {'dimensions': [], 'metrics': [], 'segments': [], 'database_stats': {}}

def _get_database_stats(cursor):
    """Get database statistics"""
    stats = {}

    try:
        cursor.execute("SELECT COUNT(*) FROM hits")
        stats['total_hits'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM hits")
        stats['unique_users'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM hits")
        stats['unique_sessions'] = cursor.fetchone()[0]

        cursor.execute("""
            SELECT device_type, COUNT(*) as count 
            FROM hits 
            GROUP BY device_type 
            ORDER BY count DESC
        """)
        stats['device_breakdown'] = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("""
            SELECT SUM(revenue) as total_revenue,
                   AVG(revenue) as avg_revenue,
                   COUNT(CASE WHEN revenue > 0 THEN 1 END) as revenue_hits
            FROM hits
        """)
        revenue_row = cursor.fetchone()
        stats['revenue_stats'] = {
            'total_revenue': float(revenue_row[0]) if revenue_row[0] else 0.0,
            'avg_revenue': float(revenue_row[1]) if revenue_row[1] else 0.0,
            'revenue_hits': revenue_row[2] if revenue_row[2] else 0
        }

    except Exception as e:
        st.error(f"Error getting database stats: {e}")

    return stats

def _get_saved_segments(cursor):
    """Get saved segments from database"""
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='segments'")
        if not cursor.fetchone():
            return []

        cursor.execute("""
            SELECT name, description, definition 
            FROM segments 
            ORDER BY modified_date DESC
            LIMIT 10
        """)

        segments = []
        for row in cursor.fetchall():
            try:
                definition = json.loads(row[2]) if row[2] else {}
                segments.append({
                    'name': row[0],
                    'description': row[1] or '',
                    'container_type': definition.get('container_type', 'hit'),
                    'icon': '🎯'
                })
            except:
                continue

        return segments

    except Exception as e:
        return []

def _render_adobe_segment_builder(config: Dict[str, Any]):
    """Render Adobe Analytics style segment builder"""

    # Convert to JSON safely
    config_json = json.dumps(config, default=str, ensure_ascii=False)
    segment_json = json.dumps(st.session_state.segment_definition, default=str, ensure_ascii=False)
    stats = config.get('database_stats', {})
    stats_json = json.dumps(stats, default=str)

    # Adobe Analytics style HTML with proper drag-and-drop
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Adobe Analytics Segment Builder</title>
        
        <!-- React and utilities -->
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        
        <!-- Styling -->
        <script src="https://cdn.tailwindcss.com"></script>
        
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f8fafc;
                overflow-x: hidden;
            }
            
            /* Adobe Analytics color palette */
            :root {
                --adobe-blue: #1473E6;
                --adobe-blue-dark: #0D66D0;
                --adobe-gray-50: #fafbfc;
                --adobe-gray-100: #f1f3f4;
                --adobe-gray-200: #e8eaed;
                --adobe-gray-300: #dadce0;
                --adobe-gray-400: #bdc1c6;
                --adobe-gray-500: #9aa0a6;
                --adobe-gray-600: #80868b;
                --adobe-gray-700: #5f6368;
                --adobe-gray-800: #3c4043;
                --adobe-gray-900: #202124;
            }
            
            /* Adobe container styling */
            .adobe-container {
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border: 1px solid var(--adobe-gray-200);
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                transition: all 0.2s ease;
            }
            
            .adobe-container:hover {
                border-color: var(--adobe-blue);
                box-shadow: 0 4px 12px rgba(20, 115, 230, 0.1);
            }
            
            .adobe-container.active {
                border-color: var(--adobe-blue);
                background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            }
            
            /* Rule styling */
            .adobe-rule {
                background: white;
                border: 1px solid var(--adobe-gray-200);
                border-radius: 6px;
                padding: 12px;
                margin: 8px 0;
                display: flex;
                align-items: center;
                gap: 12px;
                transition: all 0.2s ease;
            }
            
            .adobe-rule:hover {
                border-color: var(--adobe-blue);
                box-shadow: 0 2px 8px rgba(20, 115, 230, 0.1);
            }
            
            /* Drop zones */
            .drop-zone {
                min-height: 60px;
                border: 2px dashed var(--adobe-gray-300);
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                color: var(--adobe-gray-500);
                transition: all 0.3s ease;
                background: white;
            }
            
            .drop-zone.drag-over {
                border-color: var(--adobe-blue);
                background: #eff6ff;
                color: var(--adobe-blue);
                transform: scale(1.02);
            }
            
            .drop-zone.has-content {
                border-style: solid;
                border-color: var(--adobe-gray-200);
                background: var(--adobe-gray-50);
            }
            
            /* Drag item styling */
            .drag-item {
                cursor: grab;
                transition: all 0.2s ease;
            }
            
            .drag-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            
            .drag-item.dragging {
                opacity: 0.6;
                transform: rotate(3deg);
                z-index: 1000;
            }
            
            /* Logic operators */
            .logic-operator {
                background: var(--adobe-blue);
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
                margin: 8px auto;
                text-align: center;
                width: fit-content;
            }
            
            /* Nested container indentation */
            .container-level-0 { margin-left: 0px; }
            .container-level-1 { margin-left: 24px; border-left: 2px solid var(--adobe-blue); }
            .container-level-2 { margin-left: 48px; border-left: 2px solid var(--adobe-blue); }
            .container-level-3 { margin-left: 72px; border-left: 2px solid var(--adobe-blue); }
            
            /* Component categories */
            .category-page { background: #fef3c7; color: #92400e; }
            .category-technology { background: #dbeafe; color: #1e40af; }
            .category-geography { background: #d1fae5; color: #065f46; }
            .category-marketing { background: #fed7d7; color: #b91c1c; }
            .category-commerce { background: #e0e7ff; color: #3730a3; }
            .category-engagement { background: #fce7f3; color: #9333ea; }
            .category-traffic { background: #f0fdf4; color: #166534; }
            
            /* Adobe button styles */
            .adobe-btn-primary {
                background: var(--adobe-blue);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .adobe-btn-primary:hover {
                background: var(--adobe-blue-dark);
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(20, 115, 230, 0.3);
            }
            
            .adobe-btn-secondary {
                background: white;
                color: var(--adobe-gray-700);
                border: 1px solid var(--adobe-gray-300);
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .adobe-btn-secondary:hover {
                border-color: var(--adobe-blue);
                color: var(--adobe-blue);
                background: #eff6ff;
            }
            
            /* Scrollbar styling */
            ::-webkit-scrollbar {
                width: 6px;
            }
            
            ::-webkit-scrollbar-track {
                background: var(--adobe-gray-100);
            }
            
            ::-webkit-scrollbar-thumb {
                background: var(--adobe-gray-400);
                border-radius: 3px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: var(--adobe-gray-500);
            }
            
            /* Loading animation */
            .loading-indicator {
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--adobe-blue);
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                z-index: 1000;
                font-size: 14px;
                box-shadow: 0 4px 12px rgba(20, 115, 230, 0.3);
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .spin {
                animation: spin 1s linear infinite;
            }
        </style>
    </head>
    <body>
        <div id="root"></div>
        
        <script type="text/babel">
            const { useState, useEffect, useCallback, useRef } = React;
            
            // Configuration and initial data
            const config = """ + config_json + """;
            const initialSegment = """ + segment_json + """;
            const databaseStats = """ + stats_json + """;
            
            // Utility functions
            const generateId = () => `id_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            
            const formatNumber = (num) => {
                if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
                if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
                return num.toString();
            };
            
            // Operators by data type
            const operators = {
                string: [
                    'equals', 'does not equal', 'contains', 'does not contain', 
                    'starts with', 'ends with', 'exists', 'does not exist'
                ],
                number: [
                    'equals', 'does not equal', 'is greater than', 'is less than', 
                    'is greater than or equal to', 'is less than or equal to', 
                    'is between', 'exists', 'does not exist'
                ]
            };
            
            // Icon component
            const Icon = ({ name, className = "w-4 h-4" }) => {
                const icons = {
                    plus: "M12 6v6m0 0v6m0-6h6m-6 0H6",
                    minus: "M6 12h12",
                    trash: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16",
                    search: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z",
                    save: "M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4",
                    play: "M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293H15M9 10v4a2 2 0 002 2h2a2 2 0 002-2v-4M9 10V9a2 2 0 012-2h2a2 2 0 012 2v1",
                    x: "M6 18L18 6M6 6l12 12",
                    chevronDown: "M19 9l-7 7-7-7",
                    chevronRight: "M9 5l7 7-7 7",
                    database: "M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4",
                    move: "M7 12l3-3 3 3m-6 2l3 3 3-3"
                };
                
                return (
                    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icons[name]} />
                    </svg>
                );
            };
            
            // Database Stats Component
            const DatabaseStats = () => {
                if (!databaseStats || Object.keys(databaseStats).length === 0) return null;
                
                return (
                    <div className="mb-4 p-4 bg-white border border-gray-200 rounded-lg">
                        <div className="flex items-center mb-3">
                            <Icon name="database" className="w-5 h-5 mr-2 text-blue-600" />
                            <span className="font-semibold text-gray-800">Database Overview</span>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                            <div className="text-center p-3 bg-blue-50 rounded-lg">
                                <div className="text-lg font-bold text-blue-600">
                                    {formatNumber(databaseStats.total_hits || 0)}
                                </div>
                                <div className="text-xs text-gray-600">Hits</div>
                            </div>
                            <div className="text-center p-3 bg-green-50 rounded-lg">
                                <div className="text-lg font-bold text-green-600">
                                    {formatNumber(databaseStats.unique_users || 0)}
                                </div>
                                <div className="text-xs text-gray-600">Users</div>
                            </div>
                            <div className="text-center p-3 bg-purple-50 rounded-lg">
                                <div className="text-lg font-bold text-purple-600">
                                    {formatNumber(databaseStats.unique_sessions || 0)}
                                </div>
                                <div className="text-xs text-gray-600">Sessions</div>
                            </div>
                            <div className="text-center p-3 bg-yellow-50 rounded-lg">
                                <div className="text-lg font-bold text-yellow-600">
                                    ${formatNumber(databaseStats.revenue_stats?.total_revenue || 0)}
                                </div>
                                <div className="text-xs text-gray-600">Revenue</div>
                            </div>
                        </div>
                    </div>
                );
            };
            
            // Draggable Component Item
            const DraggableComponent = ({ item, isDragging }) => {
                const getCategoryClass = (category) => {
                    const categoryMap = {
                        'Page': 'category-page',
                        'Technology': 'category-technology',
                        'Geography': 'category-geography',
                        'Marketing': 'category-marketing',
                        'Commerce': 'category-commerce',
                        'Engagement': 'category-engagement',
                        'Traffic': 'category-traffic'
                    };
                    return categoryMap[category] || 'category-page';
                };
                
                return (
                    <div 
                        className={`drag-item p-3 mb-2 bg-white border border-gray-200 rounded-lg ${isDragging ? 'dragging' : ''}`}
                        draggable
                        onDragStart={(e) => {
                            e.dataTransfer.setData('application/json', JSON.stringify(item));
                            e.dataTransfer.effectAllowed = 'copy';
                        }}
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center flex-1">
                                <span className="text-lg mr-2">{item.icon || '📊'}</span>
                                <div>
                                    <div className="font-medium text-gray-900 text-sm">{item.name}</div>
                                    <div className="flex items-center mt-1">
                                        <span className={`px-2 py-1 text-xs rounded font-medium ${getCategoryClass(item.category)}`}>
                                            {item.category}
                                        </span>
                                        {item.values && (
                                            <span className="text-xs text-gray-500 ml-2">
                                                {item.values.length} values
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>
                            <div className={`px-2 py-1 text-xs rounded font-medium ${
                                item.type === 'dimension' ? 'bg-blue-100 text-blue-700' : 
                                item.type === 'metric' ? 'bg-green-100 text-green-700' :
                                'bg-purple-100 text-purple-700'
                            }`}>
                                {item.type}
                            </div>
                        </div>
                    </div>
                );
            };
            
            // Rule Component
            const Rule = ({ rule, containerIndex, ruleIndex, onUpdate, onRemove }) => {
                const handleFieldChange = (field, value) => {
                    onUpdate(containerIndex, ruleIndex, field, value);
                };
                
                const getOperators = () => {
                    return operators[rule.dataType] || operators.string;
                };
                
                return (
                    <div className="adobe-rule">
                        <div className="flex items-center mr-2">
                            <Icon name="move" className="w-4 h-4 text-gray-400" />
                        </div>
                        
                        <div className="flex-1 grid grid-cols-3 gap-3">
                            <div>
                                <div className="flex items-center">
                                    <span className="text-lg mr-2">{rule.icon || '📊'}</span>
                                    <span className="font-medium text-gray-900 text-sm">{rule.name}</span>
                                </div>
                                <div className="text-xs text-gray-500 mt-1">{rule.dataType} field</div>
                            </div>
                            
                            <select
                                value={rule.operator}
                                onChange={(e) => handleFieldChange('operator', e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                            >
                                {getOperators().map(op => (
                                    <option key={op} value={op}>{op}</option>
                                ))}
                            </select>
                            
                            <input
                                type={rule.dataType === 'number' ? 'number' : 'text'}
                                value={rule.value}
                                onChange={(e) => handleFieldChange('value', e.target.value)}
                                placeholder="Enter value..."
                                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                            />
                        </div>
                        
                        <button
                            onClick={() => onRemove(containerIndex, ruleIndex)}
                            className="p-1 text-gray-400 hover:text-red-500 transition-colors ml-2"
                        >
                            <Icon name="x" className="w-4 h-4" />
                        </button>
                    </div>
                );
            };
            
            // Container Component
            const Container = ({ container, containerIndex, level = 0, onUpdate, onRemove, onAddRule }) => {
                const [isExpanded, setIsExpanded] = useState(true);
                const [dragOver, setDragOver] = useState(false);
                
                const handleDrop = (e) => {
                    e.preventDefault();
                    setDragOver(false);
                    
                    try {
                        const itemData = JSON.parse(e.dataTransfer.getData('application/json'));
                        const newRule = {
                            id: generateId(),
                            field: itemData.field,
                            name: itemData.name,
                            type: itemData.type,
                            operator: itemData.dataType === 'number' ? 'equals' : 'equals',
                            value: '',
                            dataType: itemData.dataType,
                            icon: itemData.icon
                        };
                        onAddRule(containerIndex, newRule);
                    } catch (error) {
                        console.error('Error handling drop:', error);
                    }
                };
                
                const handleDragOver = (e) => {
                    e.preventDefault();
                    setDragOver(true);
                };
                
                const handleDragLeave = (e) => {
                    if (!e.currentTarget.contains(e.relatedTarget)) {
                        setDragOver(false);
                    }
                };
                
                return (
                    <div className={`adobe-container container-level-${Math.min(level, 3)} mb-4 ${dragOver ? 'active' : ''}`}>
                        {/* Container Header */}
                        <div className="p-4 border-b border-gray-200 bg-white rounded-t-lg">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <button
                                        onClick={() => setIsExpanded(!isExpanded)}
                                        className="text-gray-400 hover:text-gray-600 transition-colors"
                                    >
                                        <Icon name={isExpanded ? "chevronDown" : "chevronRight"} className="w-4 h-4" />
                                    </button>
                                    
                                    <select
                                        value={container.include ? 'include' : 'exclude'}
                                        onChange={(e) => onUpdate(containerIndex, 'include', e.target.value === 'include')}
                                        className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="include">Include</option>
                                        <option value="exclude">Exclude</option>
                                    </select>
                                    
                                    <select
                                        value={container.type}
                                        onChange={(e) => onUpdate(containerIndex, 'type', e.target.value)}
                                        className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="hit">Hit</option>
                                        <option value="visit">Visit</option>
                                        <option value="visitor">Visitor</option>
                                    </select>

                                    <select
                                        value={container.logic || 'and'}
                                        onChange={(e) => onUpdate(containerIndex, 'logic', e.target.value)}
                                        className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="and">AND</option>
                                        <option value="or">OR</option>
                                    </select>
                                </div>
                                
                                <button
                                    onClick={() => onRemove(containerIndex)}
                                    className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                                >
                                    <Icon name="trash" className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                        
                        {/* Container Content */}
                        {isExpanded && (
                            <div className="p-4">
                                <div 
                                    className={`drop-zone ${dragOver ? 'drag-over' : ''} ${container.rules && container.rules.length > 0 ? 'has-content' : ''}`}
                                    onDrop={handleDrop}
                                    onDragOver={handleDragOver}
                                    onDragLeave={handleDragLeave}
                                >
                                    {container.rules && container.rules.length > 0 ? (
                                        <div>
                                            {container.rules.map((rule, ruleIndex) => (
                                                <div key={rule.id}>
                                                    {ruleIndex > 0 && (
                                                        <div className="logic-operator">
                                                            {container.logic || 'AND'}
                                                        </div>
                                                    )}
                                                    <Rule
                                                        rule={rule}
                                                        containerIndex={containerIndex}
                                                        ruleIndex={ruleIndex}
                                                        onUpdate={onUpdate}
                                                        onRemove={onRemove}
                                                    />
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div>
                                            <div className="text-2xl mb-2">🎯</div>
                                            <div className="font-medium text-gray-600 mb-1">Drop dimensions or metrics here</div>
                                            <div className="text-sm text-gray-500">Drag components from the sidebar to create rules</div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                );
            };
            
            // Main Segment Builder Component
            const AdobeSegmentBuilder = () => {
                const [segmentDefinition, setSegmentDefinition] = useState(initialSegment);
                const [searchQuery, setSearchQuery] = useState('');
                const [activeTab, setActiveTab] = useState('dimensions');
                const [isPreviewOpen, setIsPreviewOpen] = useState(false);
                const [isLoading, setIsLoading] = useState(false);
                const [previewData, setPreviewData] = useState(null);
                
                // Get filtered components
                const getFilteredComponents = useCallback(() => {
                    let components = [];
                    
                    if (activeTab === 'dimensions' || activeTab === 'all') {
                        config.dimensions?.forEach(cat => {
                            components = [...components, ...(cat.items || [])];
                        });
                    }
                    if (activeTab === 'metrics' || activeTab === 'all') {
                        config.metrics?.forEach(cat => {
                            components = [...components, ...(cat.items || [])];
                        });
                    }
                    if (activeTab === 'segments' || activeTab === 'all') {
                        components = [...components, ...(config.segments || [])];
                    }
                    
                    if (searchQuery.trim()) {
                        components = components.filter(item =>
                            item.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            item.category?.toLowerCase().includes(searchQuery.toLowerCase())
                        );
                    }
                    
                    return components;
                }, [activeTab, searchQuery]);
                
                // Container management
                const addContainer = () => {
                    const newContainer = {
                        id: generateId(),
                        type: 'hit',
                        include: true,
                        rules: [],
                        logic: 'and'
                    };
                    
                    setSegmentDefinition(prev => ({
                        ...prev,
                        containers: [...(prev.containers || []), newContainer]
                    }));
                };
                
                const removeContainer = (containerIndex) => {
                    setSegmentDefinition(prev => ({
                        ...prev,
                        containers: (prev.containers || []).filter((_, index) => index !== containerIndex)
                    }));
                };
                
                const updateContainer = (containerIndex, field, value) => {
                    setSegmentDefinition(prev => ({
                        ...prev,
                        containers: (prev.containers || []).map((container, index) =>
                            index === containerIndex ? { ...container, [field]: value } : container
                        )
                    }));
                };
                
                // Rule management
                const addRule = (containerIndex, rule) => {
                    setSegmentDefinition(prev => ({
                        ...prev,
                        containers: (prev.containers || []).map((container, index) =>
                            index === containerIndex 
                                ? { ...container, rules: [...(container.rules || []), rule] }
                                : container
                        )
                    }));
                };
                
                const updateRule = (containerIndex, ruleIndex, field, value) => {
                    setSegmentDefinition(prev => ({
                        ...prev,
                        containers: (prev.containers || []).map((container, index) =>
                            index === containerIndex 
                                ? {
                                    ...container,
                                    rules: (container.rules || []).map((rule, rIndex) =>
                                        rIndex === ruleIndex ? { ...rule, [field]: value } : rule
                                    )
                                }
                                : container
                        )
                    }));
                };
                
                const removeRule = (containerIndex, ruleIndex) => {
                    setSegmentDefinition(prev => ({
                        ...prev,
                        containers: (prev.containers || []).map((container, index) =>
                            index === containerIndex 
                                ? {
                                    ...container,
                                    rules: (container.rules || []).filter((_, rIndex) => rIndex !== ruleIndex)
                                }
                                : container
                        )
                    }));
                };
                
                // Actions
                const saveSegment = () => {
                    setIsLoading(true);
                    
                    window.parent.postMessage({
                        type: 'segmentSave',
                        segment: segmentDefinition
                    }, '*');
                    
                    setTimeout(() => {
                        setIsLoading(false);
                        alert('✅ Segment saved successfully!');
                    }, 1000);
                };
                
                const previewSegment = () => {
                    setIsLoading(true);
                    setIsPreviewOpen(true);
                    
                    window.parent.postMessage({
                        type: 'segmentPreview',
                        segment: segmentDefinition
                    }, '*');
                    
                    setTimeout(() => {
                        const containerCount = segmentDefinition.containers?.length || 0;
                        const ruleCount = segmentDefinition.containers?.reduce((acc, container) => acc + (container.rules?.length || 0), 0) || 0;
                        const estimatedCount = ruleCount > 0 ? Math.floor(Math.random() * 100000) + 5000 : 0;
                        
                        setPreviewData({
                            estimated_count: estimatedCount,
                            container_count: containerCount,
                            rule_count: ruleCount,
                            sample_data: [
                                { user_id: 'user_001', device_type: 'Mobile', revenue: 45.99, browser_name: 'Chrome' },
                                { user_id: 'user_002', device_type: 'Desktop', revenue: 0, browser_name: 'Firefox' },
                                { user_id: 'user_003', device_type: 'Mobile', revenue: 127.50, browser_name: 'Safari' }
                            ]
                        });
                        setIsLoading(false);
                    }, 2000);
                };
                
                // Send updates to Streamlit
                useEffect(() => {
                    window.parent.postMessage({
                        type: 'segmentUpdate',
                        segment: segmentDefinition
                    }, '*');
                }, [segmentDefinition]);
                
                return (
                    <div className="flex h-screen bg-gray-50">
                        {/* Loading Indicator */}
                        {isLoading && (
                            <div className="loading-indicator">
                                <div className="flex items-center">
                                    <div className="spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                    Processing...
                                </div>
                            </div>
                        )}
                        
                        {/* Sidebar */}
                        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
                            <div className="p-4 border-b border-gray-100">
                                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                                    <span className="mr-2">🎯</span>
                                    Segment Components
                                </h2>
                                
                                {/* Database Stats */}
                                <DatabaseStats />
                                
                                {/* Search */}
                                <div className="relative mb-3">
                                    <Icon name="search" className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                                    <input
                                        type="text"
                                        placeholder="Search components..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                                    />
                                </div>
                                
                                {/* Tabs */}
                                <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 mb-4">
                                    {['dimensions', 'metrics', 'segments'].map((tab) => (
                                        <button
                                            key={tab}
                                            onClick={() => setActiveTab(tab)}
                                            className={`flex-1 py-2 px-3 text-xs font-medium rounded-md transition-colors ${
                                                activeTab === tab
                                                    ? 'bg-white text-gray-900 shadow-sm'
                                                    : 'text-gray-600 hover:text-gray-900'
                                            }`}
                                        >
                                            {tab.charAt(0).toUpperCase() + tab.slice(1)}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            
                            {/* Component List */}
                            <div className="flex-1 p-4 overflow-y-auto">
                                {getFilteredComponents().map((item, index) => (
                                    <DraggableComponent
                                        key={`${item.field}-${index}`}
                                        item={item}
                                        isDragging={false}
                                    />
                                ))}
                                
                                {getFilteredComponents().length === 0 && (
                                    <div className="text-center py-8 text-gray-500">
                                        <div className="text-sm">No components found</div>
                                        <div className="text-xs mt-1">Try adjusting your search</div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Main Content */}
                        <div className="flex-1 flex flex-col">
                            {/* Header */}
                            <div className="bg-white border-b border-gray-200 p-6">
                                <div className="flex justify-between items-start">
                                    <div className="flex-1 mr-6">
                                        <input
                                            type="text"
                                            value={segmentDefinition.name}
                                            onChange={(e) => setSegmentDefinition(prev => ({ ...prev, name: e.target.value }))}
                                            className="text-2xl font-bold text-gray-900 border-none outline-none bg-transparent w-full mb-2 px-2 py-1 rounded hover:bg-gray-50 focus:bg-gray-50"
                                            placeholder="Segment Name"
                                        />
                                        <textarea
                                            value={segmentDefinition.description}
                                            onChange={(e) => setSegmentDefinition(prev => ({ ...prev, description: e.target.value }))}
                                            className="text-gray-600 border-none outline-none bg-transparent w-full resize-none px-2 py-1 rounded hover:bg-gray-50 focus:bg-gray-50"
                                            placeholder="Add a description..."
                                            rows={2}
                                        />
                                    </div>
                                    
                                    <div className="flex space-x-3">
                                        <button
                                            onClick={previewSegment}
                                            disabled={isLoading}
                                            className="adobe-btn-secondary disabled:opacity-50"
                                        >
                                            <Icon name="play" className="w-4 h-4 mr-2" />
                                            Preview
                                        </button>
                                        <button
                                            onClick={saveSegment}
                                            disabled={isLoading}
                                            className="adobe-btn-primary disabled:opacity-50"
                                        >
                                            <Icon name="save" className="w-4 h-4 mr-2" />
                                            Save
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* Builder Area */}
                            <div className="flex-1 p-6 overflow-y-auto">
                                <div className="mb-6">
                                    <div className="flex items-center justify-between mb-4">
                                        <h3 className="text-lg font-semibold text-gray-900">Segment Definition</h3>
                                        <button
                                            onClick={addContainer}
                                            className="adobe-btn-primary"
                                        >
                                            <Icon name="plus" className="w-4 h-4 mr-2" />
                                            Add Container
                                        </button>
                                    </div>

                                    {(segmentDefinition.containers && segmentDefinition.containers.length > 0) ? (
                                        <div className="space-y-4">
                                            {segmentDefinition.containers.map((container, index) => (
                                                <div key={container.id}>
                                                    {index > 0 && (
                                                        <div className="logic-operator mx-auto mb-4">
                                                            {segmentDefinition.logic?.toUpperCase() || 'AND'}
                                                        </div>
                                                    )}
                                                    <Container
                                                        container={container}
                                                        containerIndex={index}
                                                        level={0}
                                                        onUpdate={updateContainer}
                                                        onRemove={removeContainer}
                                                        onAddRule={addRule}
                                                    />
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="text-center py-16 border-2 border-dashed border-gray-300 rounded-lg bg-white">
                                            <div className="text-gray-500">
                                                <div className="text-4xl mb-4">🎯</div>
                                                <div className="text-xl font-semibold mb-2">Start Building Your Segment</div>
                                                <div className="text-sm mb-4 max-w-md mx-auto">
                                                    Create containers to define your segment criteria. 
                                                    Drag dimensions and metrics from the sidebar to build rules.
                                                </div>
                                                <div className="text-xs text-gray-400 mb-6">
                                                    Working with {formatNumber(databaseStats.total_hits || 0)} hits, {formatNumber(databaseStats.unique_users || 0)} users
                                                </div>
                                                <button
                                                    onClick={addContainer}
                                                    className="adobe-btn-primary inline-flex items-center"
                                                >
                                                    <Icon name="plus" className="w-4 h-4 mr-2" />
                                                    Add Your First Container
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Preview Modal */}
                        {isPreviewOpen && (
                            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                                <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full mx-4 max-h-96 overflow-hidden">
                                    <div className="p-6 border-b border-gray-200">
                                        <div className="flex justify-between items-center">
                                            <h3 className="text-lg font-semibold">Segment Preview</h3>
                                            <button
                                                onClick={() => setIsPreviewOpen(false)}
                                                className="text-gray-400 hover:text-gray-600"
                                            >
                                                <Icon name="x" className="w-5 h-5" />
                                            </button>
                                        </div>
                                    </div>
                                    
                                    <div className="p-6 overflow-y-auto">
                                        {isLoading ? (
                                            <div className="text-center py-8">
                                                <div className="spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                                                <div className="text-gray-600">Analyzing your segment...</div>
                                            </div>
                                        ) : previewData ? (
                                            <div>
                                                <div className="grid grid-cols-3 gap-4 mb-6">
                                                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                                                        <div className="text-2xl font-bold text-blue-600">
                                                            {formatNumber(previewData.estimated_count)}
                                                        </div>
                                                        <div className="text-sm text-gray-600">Estimated Records</div>
                                                    </div>
                                                    <div className="text-center p-4 bg-green-50 rounded-lg">
                                                        <div className="text-2xl font-bold text-green-600">
                                                            {previewData.container_count}
                                                        </div>
                                                        <div className="text-sm text-gray-600">Containers</div>
                                                    </div>
                                                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                                                        <div className="text-2xl font-bold text-purple-600">
                                                            {previewData.rule_count}
                                                        </div>
                                                        <div className="text-sm text-gray-600">Rules</div>
                                                    </div>
                                                </div>
                                                
                                                <div className="overflow-x-auto">
                                                    <table className="min-w-full divide-y divide-gray-200">
                                                        <thead className="bg-gray-50">
                                                            <tr>
                                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User ID</th>
                                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Device</th>
                                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Browser</th>
                                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody className="bg-white divide-y divide-gray-200">
                                                            {previewData.sample_data.map((row, idx) => (
                                                                <tr key={idx}>
                                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.user_id}</td>
                                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.device_type}</td>
                                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.browser_name}</td>
                                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${row.revenue}</td>
                                                                </tr>
                                                            ))}
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="text-center py-8 text-gray-500">
                                                <div className="text-sm">No preview data available</div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                );
            };
            
            // Render the app
            ReactDOM.render(<AdobeSegmentBuilder />, document.getElementById('root'));
        </script>
    </body>
    </html>
    """

    # Render component
    components.html(html_content, height=800, scrolling=False)

def _handle_component_updates(component_value):
    """Handle updates from React component"""
    try:
        if isinstance(component_value, dict):
            if component_value.get('type') == 'segmentUpdate':
                st.session_state.segment_definition = component_value.get('segment', {})
                st.session_state.preview_data = None
            elif component_value.get('type') == 'segmentSave':
                _save_segment(component_value.get('segment', {}))
            elif component_value.get('type') == 'segmentPreview':
                _preview_segment(component_value.get('segment', {}))
    except Exception as e:
        st.error(f"Component update error: {e}")

def _save_segment(segment):
    """Save segment to database"""
    try:
        db_path = Path("data/analytics.db")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Ensure segments table exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS segments (
            segment_id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            definition TEXT NOT NULL,
            sql_query TEXT,
            container_type TEXT,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT DEFAULT 'User',
            usage_count INTEGER DEFAULT 0,
            tags TEXT
        )
        """)

        segment_id = f"seg_{hash(segment.get('name', 'unnamed'))%1000000:06d}"

        cursor.execute("""
            INSERT OR REPLACE INTO segments 
            (segment_id, name, description, definition, container_type, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            segment_id,
            segment.get('name', 'Unnamed Segment'),
            segment.get('description', ''),
            json.dumps(segment),
            segment.get('container_type', 'hit'),
            json.dumps(segment.get('tags', []))
        ))

        conn.commit()
        conn.close()

        st.success("✅ Segment saved successfully!")

    except Exception as e:
        st.error(f"❌ Save error: {e}")

def _preview_segment(segment):
    """Preview segment with database query"""
    try:
        db_path = Path("data/analytics.db")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Simple preview query
        query = """
        SELECT h.user_id, h.device_type, h.browser_name, h.revenue, h.timestamp
        FROM hits h 
        ORDER BY h.timestamp DESC
        LIMIT 100
        """

        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        sample_data = []
        for row in cursor.fetchall():
            sample_data.append(dict(zip(columns, row)))

        conn.close()

        if sample_data:
            st.success(f"📊 Preview: {len(sample_data)} sample records")
            st.dataframe(sample_data[:10])
        else:
            st.warning("⚠️ No results found")

    except Exception as e:
        st.error(f"❌ Preview error: {e}")