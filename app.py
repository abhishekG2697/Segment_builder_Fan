import streamlit as st
import yaml
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.components.sidebar import render_sidebar
from src.components.segment_builder import render_segment_builder
from src.components.preview import render_preview
from src.components.library import render_library
from src.database.init_db import initialize_database

# MUST BE FIRST - Set light theme
st.set_page_config(
    page_title="Segment Builder - Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced light theme with all UI fixes
st.markdown("""
<style>
    /* Force light theme everywhere */
    :root {
        --primary-color: #1473E6 !important;
        --background-color: #FFFFFF !important;
        --secondary-background-color: #F5F5F5 !important;
        --text-color: #2C2C2C !important;
        --font: "Source Sans Pro", sans-serif !important;
    }
    
    /* Override all Streamlit dark theme elements */
    .stApp, .main, [data-testid="stAppViewContainer"] {
        background-color: #F5F5F5 !important;
    }
    
    /* Sidebar light background */
    section[data-testid="stSidebar"], 
    section[data-testid="stSidebar"] > div,
    [data-testid="stSidebarNav"] {
        background-color: #FFFFFF !important;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: transparent !important;
        color: #2C2C2C !important;
    }
    
    /* All text should be dark */
    p, span, div, label, .stMarkdown, .stText, h1, h2, h3, h4, h5, h6 {
        color: #2C2C2C !important;
    }
    
    /* Input fields - white background */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
        border: 1px solid #D3D3D3 !important;
    }
    
    /* Select boxes and dropdowns */
    .stSelectbox > div > div > div {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
    }
    
    [data-baseweb="select"] > div,
    [role="listbox"] {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
    }
    
    /* Buttons - white background by default */
    .stButton > button {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
        border: 1px solid #D3D3D3 !important;
    }
    
    .stButton > button:hover {
        background-color: #F5F5F5 !important;
        border-color: #1473E6 !important;
        color: #1473E6 !important;
    }
    
    /* Primary buttons */
    .stButton > button[type="primary"] {
        background-color: #1473E6 !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton > button[type="primary"]:hover {
        background-color: #0D66D0 !important;
    }
    
    /* Download buttons - white background */
    .stDownloadButton > button {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
        border: 1px solid #D3D3D3 !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #F5F5F5 !important;
        border-color: #1473E6 !important;
        color: #1473E6 !important;
    }
    
    /* Checkboxes - white background */
    .stCheckbox > label {
        background-color: transparent !important;
        color: #2C2C2C !important;
    }
    
    .stCheckbox > label > div {
        background-color: transparent !important;
    }
    
    .stCheckbox input[type="checkbox"] {
        accent-color: #1473E6 !important;
    }
    
    /* Include/Exclude Radio Styling */
    .stRadio > div[role="radiogroup"] {
        display: flex !important;
        gap: 16px !important;
        background: transparent !important;
    }
    
    .stRadio > div[role="radiogroup"] > label {
        display: flex !important;
        align-items: center !important;
        background: transparent !important;
        cursor: pointer;
        font-size: 13px !important;
        position: relative;
        padding-left: 20px !important;
    }
    
    /* Green dot for Include (first radio) */
    .stRadio > div[role="radiogroup"] > label:first-child::before {
        content: '●';
        position: absolute;
        left: 0;
        color: #12B886;
        font-size: 12px;
        top: 50%;
        transform: translateY(-50%);
    }
    
    /* Red dot for Exclude (second radio) */
    .stRadio > div[role="radiogroup"] > label:nth-child(2)::before {
        content: '●';
        position: absolute;
        left: 0;
        color: #E34850;
        font-size: 12px;
        top: 50%;
        transform: translateY(-50%);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 1px solid #E1E1E1 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: #6E6E6E !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #2C2C2C !important;
        border-bottom: 2px solid #2C2C2C !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #F8F8F8 !important;
        color: #2C2C2C !important;
        border: 1px solid #E1E1E1 !important;
    }
    
    /* Data tables */
    .stDataFrame {
        background-color: #FFFFFF !important;
    }
    
    [data-testid="stDataFrameContainer"] {
        background-color: #FFFFFF !important;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E1E1E1 !important;
        border-radius: 4px !important;
        padding: 1rem !important;
    }
    
    /* Multi-select tags */
    [data-baseweb="tag"] {
        background-color: #E8F5E9 !important;
        color: #2E7D32 !important;
        border: 1px solid #81C784 !important;
    }
    
    /* Calendar/Date picker */
    [data-baseweb="calendar"],
    [data-baseweb="datepicker"] {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F5F5F5;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #D3D3D3;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #A0A0A0;
    }
    
    /* Percentage display fix */
    .segment-match-percentage {
        font-size: 36px !important;
        font-weight: 700 !important;
        color: #1473E6 !important;
        line-height: 1 !important;
        word-break: normal !important;
        overflow-wrap: normal !important;
    }
    
    /* Ensure all containers have light background */
    div[data-testid="stVerticalBlock"],
    div[data-testid="stHorizontalBlock"],
    div[data-testid="column"] {
        background-color: transparent !important;
    }
    
    /* Fix for any remaining dark elements */
    * {
        scrollbar-color: #D3D3D3 #F5F5F5;
    }
</style>
""", unsafe_allow_html=True)

# Load configuration
@st.cache_resource
def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

# Initialize database
@st.cache_resource
def init_db():
    initialize_database()
    return True

# Initialize session state
def init_session_state():
    if 'segment_definition' not in st.session_state:
        st.session_state.segment_definition = {
            'name': 'New Segment',
            'description': '',
            'container_type': 'visit',
            'containers': [],
            'logic': 'and'
        }
    
    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None

    if 'preview_segment_selector' not in st.session_state:
        st.session_state.preview_segment_selector = "Current Segment"
    
    if 'saved_segments' not in st.session_state:
        st.session_state.saved_segments = []
    
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    if 'preview_limit' not in st.session_state:
        st.session_state.preview_limit = 100

def main():
    # Load configuration
    config = load_config()
    
    # Initialize database
    init_db()
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.markdown("""
    <div style="background-color: #FFFFFF; padding: 12px 20px; margin: -1rem -1rem 1rem -1rem; border-bottom: 1px solid #E1E1E1;">
        <h2 style="color: #2C2C2C; font-weight: 400; margin: 0; font-size: 18px;">Build segments | Analytics</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        render_sidebar(config)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🔨 Segment Builder", "📊 Preview", "📚 Library"])
    
    # Update active tab based on session state
    if st.session_state.active_tab == 0:
        with tab1:
            render_segment_builder(config)
        with tab2:
            render_preview()
        with tab3:
            render_library()
    elif st.session_state.active_tab == 1:
        with tab1:
            render_segment_builder(config)
        with tab2:
            render_preview()
        with tab3:
            render_library()
    elif st.session_state.active_tab == 2:
        with tab1:
            render_segment_builder(config)
        with tab2:
            render_preview()
        with tab3:
            render_library()
    else:
        # Default rendering
        with tab1:
            render_segment_builder(config)
        with tab2:
            render_preview()
        with tab3:
            render_library()

if __name__ == "__main__":
    main()