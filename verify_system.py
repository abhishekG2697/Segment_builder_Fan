# STEP 5: Create this as verify_system.py to check everything is set up correctly

import sys
import os
from pathlib import Path
import sqlite3
import yaml

def check_system():
    """Verify the system is set up correctly"""
    
    print("🔍 SYSTEM VERIFICATION")
    print("=" * 50)
    
    # Check Python version
    print(f"✅ Python version: {sys.version}")
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    print(f"✅ Current directory: {current_dir}")
    
    # Check required files
    required_files = [
        'config.yaml',
        'src/components/segment_builder.py',
        'src/components/sidebar.py',
        'src/database/queries.py',
        'src/database/init_db.py'
    ]
    
    print("\n📁 CHECKING FILES:")
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")
    
    # Check config.yaml
    print("\n⚙️ CHECKING CONFIG:")
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        dimensions_count = sum(len(cat['items']) for cat in config.get('dimensions', []))
        metrics_count = sum(len(cat['items']) for cat in config.get('metrics', []))
        
        print(f"✅ Config loaded successfully")
        print(f"   - Dimensions: {dimensions_count}")
        print(f"   - Metrics: {metrics_count}")
        
    except Exception as e:
        print(f"❌ Config error: {e}")
    
    # Check database
    print("\n🗄️ CHECKING DATABASE:")
    db_path = Path("data/analytics.db")
    
    if db_path.exists():
        print(f"✅ Database exists: {db_path}")
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"   - Tables: {', '.join(tables)}")
            
            # Check hits table
            if 'hits' in tables:
                cursor.execute("SELECT COUNT(*) FROM hits")
                hit_count = cursor.fetchone()[0]
                print(f"   - Total hits: {hit_count:,}")
                
                # Check for Mobile devices specifically
                cursor.execute("SELECT COUNT(*) FROM hits WHERE device_type = 'Mobile'")
                mobile_count = cursor.fetchone()[0]
                print(f"   - Mobile hits: {mobile_count:,}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Database error: {e}")
    else:
        print(f"❌ Database missing: {db_path}")
        print("   Run: python src/database/init_db.py")
    
    # Check imports
    print("\n📦 CHECKING IMPORTS:")
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit not installed")
    
    try:
        import pandas
        print(f"✅ Pandas {pandas.__version__}")
    except ImportError:
        print("❌ Pandas not installed")
    
    try:
        import plotly
        print(f"✅ Plotly {plotly.__version__}")
    except ImportError:
        print("❌ Plotly not installed")
    
    # Check if we can import our modules
    print("\n🔧 CHECKING CUSTOM MODULES:")
    try:
        sys.path.append(str(Path.cwd()))
        from src.database.queries import save_segment, get_db_connection
        print("✅ Database queries module")
    except Exception as e:
        print(f"❌ Database queries error: {e}")
    
    try:
        from src.components.sidebar import render_sidebar
        print("✅ Sidebar component")
    except Exception as e:
        print(f"❌ Sidebar component error: {e}")
    
    try:
        from src.components.segment_builder import render_segment_builder
        print("✅ Segment builder component")
    except Exception as e:
        print(f"❌ Segment builder component error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 VERIFICATION COMPLETE")
    print("\nIf all items show ✅, your system should work correctly.")
    print("If any show ❌, fix those issues first before running the app.")

if __name__ == "__main__":
    check_system()