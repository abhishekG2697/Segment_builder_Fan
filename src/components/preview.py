import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.database.queries import execute_segment_query, get_db_connection
from src.utils.query_builder import build_sql_from_segment
import json

def render_preview():
    """Render the preview panel with enhanced data handling"""
    
    # Custom CSS for preview panel - ALL LIGHT BACKGROUNDS
    st.markdown("""
    <style>
    /* Force light theme everywhere */
    :root {
        --primary-color: #1473E6 !important;
        --text-dark: #2C2C2C !important;
        --text-light: #6E6E6E !important;
        --bg-white: #FFFFFF !important;
        --bg-light: #F5F5F5 !important;
        --border-color: #E1E1E1 !important;
    }
    
    /* Preview panel styling */
    .preview-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .preview-controls {
        display: flex;
        gap: 12px;
        align-items: center;
    }
    
    .preview-control-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .control-label {
        font-size: 11px;
        color: var(--text-light);
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Fix ALL inputs, selects, and checkboxes - WHITE BACKGROUNDS */
    input, select, textarea,
    .stDateInput > div > div > input,
    .stSelectbox > div > div > div,
    .stCheckbox > label,
    .stNumberInput > div > div > input,
    [data-baseweb="input"],
    [data-baseweb="select"] {
        background-color: var(--bg-white) !important;
        color: var(--text-dark) !important;
        border: 1px solid #D3D3D3 !important;
    }
    
    /* Metrics cards */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 20px;
    }
    
    .metric-card {
        background: var(--bg-white);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 16px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--text-dark);
        margin-bottom: 4px;
    }
    
    .metric-label {
        font-size: 12px;
        color: var(--text-light);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Data table styling */
    .dataframe {
        font-size: 12px !important;
        background: var(--bg-white) !important;
    }
    
    .dataframe th {
        background-color: #F8F8F8 !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 11px !important;
        letter-spacing: 0.5px !important;
        color: var(--text-dark) !important;
    }
    
    .dataframe td {
        background-color: var(--bg-white) !important;
        color: var(--text-dark) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab"] {
        font-size: 13px !important;
        padding: 8px 16px !important;
        background-color: transparent !important;
        color: var(--text-dark) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: var(--text-dark) !important;
        border-bottom: 2px solid var(--text-dark) !important;
    }
    
    /* Fix ALL buttons - WHITE BACKGROUNDS */
    button,
    .stButton > button,
    .stDownloadButton > button {
        background-color: var(--bg-white) !important;
        border: 1px solid #D3D3D3 !important;
        color: var(--text-dark) !important;
    }
    
    button:hover,
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #F0F8FF !important;
        border-color: var(--primary-color) !important;
        color: var(--primary-color) !important;
    }
    
    /* Primary refresh button */
    .stButton > button[key="refresh_preview_btn"] {
        background-color: #E8F5FF !important;
        color: var(--primary-color) !important;
        border: 1px solid var(--primary-color) !important;
    }
    
    .stButton > button[key="refresh_preview_btn"]:hover {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    
    /* Checkbox styling - white background */
    .stCheckbox > label {
        background-color: transparent !important;
        color: var(--text-dark) !important;
    }
    
    .stCheckbox > label > span {
        background-color: transparent !important;
        color: var(--text-dark) !important;
    }
    
    /* Fix checkbox text color */
    .stCheckbox > label > div[data-testid="stMarkdownContainer"] > p {
        color: var(--text-dark) !important;
    }
    
    /* Export container */
    .export-container {
        display: flex;
        gap: 12px;
        margin-top: 20px;
    }
    
    /* SQL display */
    .sql-container {
        background: #F8F8F8;
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 12px;
        font-family: monospace;
        font-size: 12px;
        max-height: 300px;
        overflow: auto;
        color: var(--text-dark);
    }
    
    /* Multiselect styling - fix black background */
    [data-baseweb="tag"] {
        background-color: #E8F5E9 !important;
        color: #2E7D32 !important;
        border: 1px solid #81C784 !important;
    }
    
    /* Fix multiselect container */
    .stMultiSelect > div > div {
        background-color: var(--bg-white) !important;
    }
    
    /* Fix expander backgrounds */
    .streamlit-expanderHeader {
        background-color: #F8F8F8 !important;
        color: var(--text-dark) !important;
    }
    
    .streamlit-expanderContent {
        background-color: var(--bg-white) !important;
    }
    
    /* Override any dark backgrounds */
    [style*="background-color: rgb(38, 39, 48)"],
    [style*="background-color: rgb(49, 51, 63)"],
    [style*="background: rgb(38, 39, 48)"],
    [style*="background: rgb(49, 51, 63)"] {
        background-color: var(--bg-white) !important;
    }
    
    /* Ensure all text is dark */
    p, span, div, label, td, th {
        color: var(--text-dark) !important;
    }
    
    /* Info/warning/error boxes */
    .stAlert {
        background-color: #E8F5FF !important;
        color: var(--text-dark) !important;
        border: 1px solid var(--primary-color) !important;
    }
    
    /* Fix calendar/date picker - ALL LIGHT BACKGROUNDS */
    .stDateInput > div > div > div,
    [data-baseweb="calendar"],
    [data-baseweb="datepicker"],
    [data-baseweb="popover"] {
        background-color: var(--bg-white) !important;
        color: var(--text-dark) !important;
    }
    
    /* Calendar days */
    [data-baseweb="calendar"] div {
        background-color: var(--bg-white) !important;
        color: var(--text-dark) !important;
    }
    
    /* Calendar selected day */
    [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    
    /* Calendar hover */
    [data-baseweb="calendar"] div:hover {
        background-color: var(--bg-lighter) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Segment Preview")
    
    # Preview controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        # Date range selector (optional)
        use_date_filter = st.checkbox("Apply date range", value=False, key="use_date_filter")
        if use_date_filter:
            date_range = st.date_input(
                "Date Range",
                value=(datetime.now() - timedelta(days=30), datetime.now()),
                key="preview_date_range"
            )
        else:
            date_range = None
    
    with col2:
        # Sample size
        st.markdown('<div class="control-label">Sample Size</div>', unsafe_allow_html=True)
        sample_options = [100, 500, 1000, 5000, 10000, "All"]
        sample_size = st.selectbox(
            "Sample Size",
            options=sample_options,
            index=0,
            key="preview_sample_size",
            label_visibility="collapsed"
        )
        st.session_state.preview_limit = sample_size if sample_size != "All" else None
    
    with col3:
        # View mode
        st.markdown('<div class="control-label">View Mode</div>', unsafe_allow_html=True)
        view_mode = st.selectbox(
            "View Mode",
            ["Quick View", "Full Analysis"],
            key="preview_view_mode",
            label_visibility="collapsed"
        )
    
    with col4:
        st.markdown('<div class="control-label">Actions</div>', unsafe_allow_html=True)
        if st.button("🔄 Refresh", key="refresh_preview_btn", type="primary", use_container_width=True):
            st.session_state.preview_data = None
            st.rerun()
    
    # Debug info for segment definition
    with st.expander("🔍 Current Segment Definition (Debug)", expanded=False):
        if st.session_state.segment_definition:
            st.json(st.session_state.segment_definition)
        else:
            st.info("No segment defined")
    
    # Check if we have a segment defined
    if not st.session_state.segment_definition.get('containers'):
        # Show helpful message
        st.info("👈 Build a segment in the Segment Builder tab to see preview data")
        
        # Show sample data
        show_sample_data()
    else:
        # Check if specific segment was selected
        segment_options = ["Current Segment"] + [s.get('name', 'Unnamed') for s in st.session_state.get('db_segments', [])]
        selected_segment = st.selectbox(
            "Select Segment to Preview",
            options=segment_options,
            index=segment_options.index(st.session_state.get('preview_segment_selector', 'Current Segment')),
            key="preview_segment_selector"
        )
        
        # Load selected segment if not current
        if selected_segment != "Current Segment":
            # Find and load the selected segment
            for seg in st.session_state.get('db_segments', []):
                if seg.get('name') == selected_segment:
                    if 'definition' in seg:
                        st.session_state.preview_segment = seg['definition']
                    else:
                        st.session_state.preview_segment = seg
                    break
        else:
            st.session_state.preview_segment = st.session_state.segment_definition
        
        # Generate or display preview
        if st.session_state.preview_data is None or st.session_state.get('preview_segment') != st.session_state.get('last_preview_segment'):
            with st.spinner("Generating preview..."):
                generate_preview()
                st.session_state.last_preview_segment = st.session_state.get('preview_segment')
        
        # Display results
        if st.session_state.preview_data is not None:
            if st.session_state.preview_data.empty:
                show_no_data_message()
            else:
                render_preview_results(view_mode)

def generate_preview():
    """Generate preview data with better error handling"""
    try:
        # Get the segment to preview
        preview_segment = st.session_state.get('preview_segment', st.session_state.segment_definition)
        
        # Ensure we have a valid segment definition
        if not preview_segment:
            st.warning("No segment definition found")
            st.session_state.preview_data = pd.DataFrame()
            return
        
        # Build SQL query
        sql_query = build_sql_from_segment(preview_segment)
        
        # Add date filter if enabled
        if st.session_state.get('use_date_filter') and st.session_state.get('preview_date_range'):
            date_range = st.session_state.preview_date_range
            if len(date_range) == 2:
                date_clause = f" AND h.timestamp BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
                if "ORDER BY" in sql_query:
                    sql_query = sql_query.replace("ORDER BY", date_clause + " ORDER BY")
                else:
                    sql_query = sql_query + date_clause
        
        # Add limit
        limit = st.session_state.get('preview_limit', 100)
        if limit and "LIMIT" not in sql_query:
            sql_query = f"{sql_query} LIMIT {limit}"
        
        # Show SQL query for debugging
        with st.expander("🔍 Generated SQL Query", expanded=False):
            st.code(sql_query, language='sql')
        
        # Execute query
        conn = get_db_connection()
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        
        # Store in session state
        st.session_state.preview_data = df
        
        if df.empty:
            st.warning("No data matches the current segment definition")
            # Show debug info
            show_debug_info()
        else:
            st.success(f"✅ Found {len(df):,} records matching your segment")
            
    except Exception as e:
        st.error(f"Error generating preview: {str(e)}")
        st.session_state.preview_data = pd.DataFrame()
        
        # Show debugging info
        with st.expander("Debug Information", expanded=True):
            st.write("**Error:**", str(e))
            st.write("**Segment Definition:**")
            st.json(preview_segment)
            try:
                sql_query = build_sql_from_segment(preview_segment)
                st.write("**Generated SQL:**")
                st.code(sql_query, language='sql')
            except Exception as sql_error:
                st.write("**SQL Generation Error:**", str(sql_error))

def show_debug_info():
    """Show debugging information when no data matches"""
    conn = get_db_connection()
    
    # Check what values exist in the database
    st.markdown("### 🔍 Database Values Check")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Check for specific values in segment
        if st.session_state.segment_definition.get('containers'):
            for container in st.session_state.segment_definition['containers']:
                for condition in container.get('conditions', []):
                    field = condition.get('field')
                    value = condition.get('value')
                    
                    if field and value:
                        # Check if this value exists
                        check_query = f"""
                        SELECT COUNT(*) as count 
                        FROM hits 
                        WHERE {field} = '{value}'
                        """
                        try:
                            result = pd.read_sql_query(check_query, conn)
                            count = result.iloc[0]['count']
                            if count == 0:
                                st.warning(f"❌ No records found with {field} = '{value}'")
                            else:
                                st.success(f"✅ Found {count} records with {field} = '{value}'")
                        except:
                            st.error(f"Could not check {field}")
    
    with col2:
        # Show available values
        st.markdown("**Available Values in Database:**")
        
        # Get unique values for common fields
        for field in ['device_type', 'browser_name', 'page_type', 'traffic_source']:
            try:
                query = f"SELECT DISTINCT {field}, COUNT(*) as count FROM hits GROUP BY {field} ORDER BY count DESC LIMIT 5"
                df = pd.read_sql_query(query, conn)
                st.write(f"**{field}:**")
                for _, row in df.iterrows():
                    st.write(f"- {row[field]}: {row['count']:,} records")
            except:
                pass
    
    conn.close()

def show_sample_data():
    """Show sample data when no segment is defined"""
    try:
        conn = get_db_connection()
        
        # Get sample data
        sample_query = """
        SELECT 
            h.hit_id,
            h.timestamp,
            h.user_id,
            h.session_id,
            h.page_title,
            h.device_type,
            h.browser_name,
            h.country,
            h.revenue,
            h.time_on_page
        FROM hits h
        ORDER BY h.timestamp DESC
        LIMIT 100
        """
        
        df = pd.read_sql_query(sample_query, conn)
        conn.close()
        
        if not df.empty:
            # Show sample metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Sample Records", f"{len(df):,}")
            with col2:
                st.metric("Unique Users", f"{df['user_id'].nunique():,}")
            with col3:
                st.metric("Total Revenue", f"${df['revenue'].sum():,.2f}")
            with col4:
                st.metric("Avg Time on Page", f"{df['time_on_page'].mean():.0f}s")
            
            # Show data preview
            st.markdown("#### Sample Data")
            st.dataframe(
                df.head(50),
                use_container_width=True,
                height=400
            )
            
    except Exception as e:
        st.error(f"Error loading sample data: {str(e)}")

def show_no_data_message():
    """Show helpful message when no data matches"""
    st.warning("No data matches the current segment definition")
    
    # Show debugging help
    with st.expander("💡 Troubleshooting Tips", expanded=True):
        st.markdown("""
        **Common issues:**
        1. **Case sensitivity**: Values are case-sensitive. 'Mobile' ≠ 'mobile'
        2. **Exact matching**: Make sure values match exactly as in database
        3. **Date ranges**: Check if data exists in selected date range
        4. **Field mapping**: Some fields may have different names in the database
        
        **Quick checks:**
        """)
        
        # Show current segment conditions
        if st.session_state.segment_definition.get('containers'):
            st.markdown("**Your segment conditions:**")
            for i, container in enumerate(st.session_state.segment_definition['containers']):
                st.write(f"Container {i+1}: {container.get('type', 'hit')} - {'Include' if container.get('include', True) else 'Exclude'}")
                for condition in container.get('conditions', []):
                    st.write(f"  - {condition.get('name', 'Field')}: {condition.get('operator', 'equals')} '{condition.get('value', '')}'")
        
        # Show available values
        show_available_values()

def show_available_values():
    """Show available values in database"""
    conn = get_db_connection()
    
    st.markdown("**Available values in database:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Device types
        device_query = "SELECT DISTINCT device_type, COUNT(*) as count FROM hits GROUP BY device_type ORDER BY count DESC"
        device_df = pd.read_sql_query(device_query, conn)
        st.markdown("**Device Types:**")
        st.dataframe(device_df, use_container_width=True, height=150)
    
    with col2:
        # Browsers
        browser_query = "SELECT DISTINCT browser_name, COUNT(*) as count FROM hits GROUP BY browser_name ORDER BY count DESC LIMIT 10"
        browser_df = pd.read_sql_query(browser_query, conn)
        st.markdown("**Browser Names:**")
        st.dataframe(browser_df, use_container_width=True, height=150)
    
    # Page types
    page_query = "SELECT DISTINCT page_type, COUNT(*) as count FROM hits GROUP BY page_type ORDER BY count DESC"
    page_df = pd.read_sql_query(page_query, conn)
    st.markdown("**Page Types:**")
    st.dataframe(page_df, use_container_width=True, height=150)
    
    # Traffic sources
    traffic_query = "SELECT DISTINCT traffic_source, COUNT(*) as count FROM hits GROUP BY traffic_source ORDER BY count DESC"
    traffic_df = pd.read_sql_query(traffic_query, conn)
    st.markdown("**Traffic Sources:**")
    st.dataframe(traffic_df, use_container_width=True, height=150)
    
    conn.close()

def render_preview_results(view_mode="Quick View"):
    """Render preview results with enhanced visualizations"""
    df = st.session_state.preview_data
    
    if df.empty:
        show_no_data_message()
        return
    
    # Summary metrics
    render_metrics_cards(df)
    
    # Tabs for different views
    if view_mode == "Quick View":
        tab1, tab2, tab3 = st.tabs(["📊 Data Table", "📈 Visualizations", "💾 Export"])
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Data Table", "📈 Trends", "🎯 Distribution", "🔍 Analysis", "💾 Export"])
    
    with tab1:
        render_data_table(df)
    
    with tab2:
        if view_mode == "Quick View":
            render_quick_visualizations(df)
        else:
            render_trend_analysis(df)
    
    with tab3:
        if view_mode == "Quick View":
            render_export_options(df)
        else:
            render_distribution_analysis(df)
    
    if view_mode == "Full Analysis":
        with tab4:
            render_detailed_analysis(df)
        
        with tab5:
            render_export_options(df)

def render_metrics_cards(df):
    """Render summary metrics in cards"""
    st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(df):,}</div>
            <div class="metric-label">Total Hits</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        unique_sessions = df['session_id'].nunique() if 'session_id' in df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_sessions:,}</div>
            <div class="metric-label">Unique Sessions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        unique_visitors = df['user_id'].nunique() if 'user_id' in df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_visitors:,}</div>
            <div class="metric-label">Unique Visitors</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_revenue = df['revenue'].sum() if 'revenue' in df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${total_revenue:,.0f}</div>
            <div class="metric-label">Total Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_data_table(df):
    """Render interactive data table"""
    st.markdown("#### Data Table")
    
    # Column selector
    available_columns = df.columns.tolist()
    default_columns = ['timestamp', 'user_id', 'page_title', 'device_type', 
                      'browser_name', 'revenue', 'country']
    default_columns = [col for col in default_columns if col in available_columns]
    
    selected_columns = st.multiselect(
        "Select columns to display",
        options=available_columns,
        default=default_columns[:8],
        key="preview_column_selector"
    )
    
    if selected_columns:
        # Format timestamp if present
        display_df = df[selected_columns].copy()
        if 'timestamp' in display_df.columns:
            display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Display with pagination
        rows_per_page = st.number_input(
            "Rows per page",
            min_value=10,
            max_value=1000,
            value=50,
            step=10,
            key="rows_per_page"
        )
        
        st.dataframe(
            display_df.head(rows_per_page),
            use_container_width=True,
            height=400
        )
        
        st.caption(f"Showing {min(rows_per_page, len(display_df))} of {len(display_df):,} rows")

def render_quick_visualizations(df):
    """Render quick visualizations"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Device distribution
        if 'device_type' in df.columns:
            fig = px.pie(
                df['device_type'].value_counts().reset_index(),
                values='count',
                names='device_type',
                title="Device Type Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Browser distribution
        if 'browser_name' in df.columns:
            browser_counts = df['browser_name'].value_counts().head(5)
            fig = px.bar(
                x=browser_counts.values,
                y=browser_counts.index,
                orientation='h',
                title="Top 5 Browsers",
                color_discrete_sequence=['#1473E6']
            )
            fig.update_layout(
                height=300,
                xaxis_title="Count",
                yaxis_title="",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Time series if timestamp available
    if 'timestamp' in df.columns:
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_counts = df.groupby('date').size().reset_index(name='count')
        
        fig = px.line(
            daily_counts,
            x='date',
            y='count',
            title="Daily Hit Trend",
            line_shape='spline'
        )
        fig.update_traces(line_color='#1473E6', line_width=2)
        fig.update_layout(
            height=300,
            xaxis_title="Date",
            yaxis_title="Hits",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

def render_export_options(df):
    """Render export options with white background buttons"""
    st.markdown("#### Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV export
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"segment_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Excel export
        try:
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Segment Data', index=False)
            
            st.download_button(
                label="📥 Download Excel",
                data=buffer.getvalue(),
                file_name=f"segment_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except:
            st.info("Excel export requires openpyxl")
    
    with col3:
        # JSON export
        json_str = df.to_json(orient='records', indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"segment_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Segment definition export
    st.markdown("#### Export Segment Definition")
    segment_json = json.dumps(st.session_state.segment_definition, indent=2)
    st.download_button(
        label="📥 Download Segment Definition (JSON)",
        data=segment_json,
        file_name=f"segment_definition_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )

# Additional analysis functions for Full Analysis mode
def render_trend_analysis(df):
    """Render trend analysis"""
    if 'timestamp' in df.columns:
        df['datetime'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['datetime'].dt.date
        df['hour'] = df['datetime'].dt.hour
        
        # Daily trend
        daily_stats = df.groupby('date').agg({
            'hit_id': 'count',
            'user_id': 'nunique',
            'revenue': 'sum'
        }).reset_index()
        daily_stats.columns = ['Date', 'Hits', 'Unique Visitors', 'Revenue']
        
        fig = go.Figure()
        
        # Hits line
        fig.add_trace(go.Scatter(
            x=daily_stats['Date'],
            y=daily_stats['Hits'],
            mode='lines+markers',
            name='Hits',
            line=dict(color='#1473E6', width=2),
            yaxis='y'
        ))
        
        # Revenue bars
        fig.add_trace(go.Bar(
            x=daily_stats['Date'],
            y=daily_stats['Revenue'],
            name='Revenue',
            marker_color='#70AD47',
            opacity=0.6,
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Daily Trends",
            xaxis_title="Date",
            yaxis=dict(title="Hits", side='left'),
            yaxis2=dict(title="Revenue ($)", overlaying='y', side='right'),
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Hourly pattern
        hourly_hits = df.groupby('hour').size().reset_index(name='hits')
        
        fig2 = px.bar(
            hourly_hits,
            x='hour',
            y='hits',
            title="Hourly Activity Pattern",
            color_discrete_sequence=['#1473E6']
        )
        fig2.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Hits",
            height=300
        )
        st.plotly_chart(fig2, use_container_width=True)

def render_distribution_analysis(df):
    """Render distribution analysis"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Page type distribution
        if 'page_type' in df.columns:
            page_dist = df['page_type'].value_counts()
            fig = px.bar(
                x=page_dist.values,
                y=page_dist.index,
                orientation='h',
                title="Page Type Distribution",
                color_discrete_sequence=['#1473E6']
            )
            fig.update_layout(
                xaxis_title="Count",
                yaxis_title="",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Traffic source distribution
        if 'traffic_source' in df.columns:
            traffic_dist = df['traffic_source'].value_counts()
            fig = px.pie(
                values=traffic_dist.values,
                names=traffic_dist.index,
                title="Traffic Source Distribution",
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Geographic distribution
    if 'country' in df.columns:
        country_dist = df['country'].value_counts().head(10)
        fig = px.bar(
            x=country_dist.index,
            y=country_dist.values,
            title="Top 10 Countries",
            color_discrete_sequence=['#1473E6']
        )
        fig.update_layout(
            xaxis_title="Country",
            yaxis_title="Hits",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

def render_detailed_analysis(df):
    """Render detailed analysis"""
    st.markdown("#### Detailed Analysis")
    
    # User behavior metrics
    if all(col in df.columns for col in ['user_id', 'session_id', 'revenue']):
        user_stats = df.groupby('user_id').agg({
            'hit_id': 'count',
            'session_id': 'nunique',
            'revenue': 'sum'
        }).describe()
        
        st.markdown("**User Behavior Statistics**")
        st.dataframe(user_stats.round(2), use_container_width=True)
    
    # Top pages
    if 'page_title' in df.columns:
        st.markdown("**Top 10 Pages**")
        top_pages = df['page_title'].value_counts().head(10).reset_index()
        top_pages.columns = ['Page', 'Hits']
        st.dataframe(top_pages, use_container_width=True, hide_index=True)
    
    # Conversion funnel (if applicable)
    if 'page_type' in df.columns:
        funnel_order = ['Home', 'Category', 'Product', 'Checkout']
        funnel_data = []
        
        for page_type in funnel_order:
            if page_type in df['page_type'].values:
                count = len(df[df['page_type'] == page_type])
                funnel_data.append({'Stage': page_type, 'Count': count})
        
        if funnel_data:
            funnel_df = pd.DataFrame(funnel_data)
            fig = px.funnel(
                funnel_df,
                x='Count',
                y='Stage',
                title="Page Type Funnel"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)