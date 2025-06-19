"""
Complete app.py - Main Streamlit Application
Replaces all problematic legacy components with modern React implementation
Works with existing SQLite database (502K+ records)
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def main():
    """Main application entry point"""

    # Page configuration
    st.set_page_config(
        page_title="Adobe Analytics Segment Builder",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Check if database exists
    db_path = Path("data/analytics.db")
    if not db_path.exists():
        st.error("❌ Database not found at data/analytics.db")
        st.info("Please ensure your SQLite database is located at: data/analytics.db")
        st.stop()

    # Import and render the modern segment builder
    try:
        from components.modern_segment_builder import render_modern_segment_builder
        render_modern_segment_builder()
    except ImportError as e:
        st.error(f"❌ Import error: {e}")
        st.info("Please ensure all component files are properly created.")
        st.code("""
        # Expected file structure:
        src/
        ├── components/
        │   └── modern_segment_builder.py
        └── database/
            └── database_integration.py
        """)


if __name__ == "__main__":
    main()