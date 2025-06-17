#!/usr/bin/env python3
"""
Setup script for Segment Builder application
Creates necessary directories and initializes the database
"""

import os
import sys
from pathlib import Path

def create_project_structure():
    """Create all necessary directories"""
    directories = [
        "src",
        "src/components",
        "src/database",
        "src/models",
        "src/utils",
        "src/styles",
        "data",
        "segments",
        "segments/library"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_init_files():
    """Create __init__.py files"""
    init_dirs = [
        "src",
        "src/components",
        "src/database",
        "src/models",
        "src/utils"
    ]
    
    for directory in init_dirs:
        init_file = Path(directory) / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"✓ Created {init_file}")

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        "streamlit",
        "pandas",
        "numpy",
        "sqlalchemy",
        "pyyaml",
        "plotly"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("\n⚠️  Missing packages detected:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease run: pip install -r requirements.txt")
        return False
    
    print("✓ All dependencies installed")
    return True

def main():
    print("🚀 Setting up Segment Builder Application\n")
    
    # Create project structure
    print("Creating project structure...")
    create_project_structure()
    create_init_files()
    
    # Check dependencies
    print("\nChecking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize database
    print("\nInitializing database...")
    try:
        from src.database.init_db import initialize_database
        initialize_database()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("You can manually initialize by running: python src/database/init_db.py")
    
    print("\n✅ Setup complete!")
    print("\nTo run the application:")
    print("  streamlit run app.py")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()