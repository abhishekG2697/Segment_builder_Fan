#!/usr/bin/env python3
"""
Debug script to check database contents and fix data issues
"""

import sqlite3
import pandas as pd
from pathlib import Path

def check_database():
    """Check database contents and data formats"""
    db_path = Path("data/analytics.db")
    
    if not db_path.exists():
        print("❌ Database not found! Please run init_db.py first.")
        return
    
    conn = sqlite3.connect(str(db_path))
    
    print("🔍 Checking database contents...\n")
    
    # Check tables
    tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
    tables = pd.read_sql_query(tables_query, conn)
    print("📊 Tables found:")
    print(tables)
    print()
    
    # Check hits table structure
    print("📋 Hits table structure:")
    hits_info = pd.read_sql_query("PRAGMA table_info(hits)", conn)
    print(hits_info[['name', 'type']])
    print()
    
    # Check sample data
    print("📊 Sample data from hits table:")
    sample_hits = pd.read_sql_query("SELECT * FROM hits LIMIT 5", conn)
    print(sample_hits)
    print()
    
    # Check device types
    print("📱 Device types in database:")
    device_types = pd.read_sql_query(
        "SELECT device_type, COUNT(*) as count FROM hits GROUP BY device_type ORDER BY count DESC", 
        conn
    )
    print(device_types)
    print()
    
    # Check browser names
    print("🌐 Browser names in database:")
    browsers = pd.read_sql_query(
        "SELECT browser_name, COUNT(*) as count FROM hits GROUP BY browser_name ORDER BY count DESC", 
        conn
    )
    print(browsers)
    print()
    
    # Check for Mobile device type specifically
    print("📱 Checking for 'Mobile' device type:")
    mobile_count = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM hits WHERE device_type = 'Mobile'", 
        conn
    )
    print(f"Records with device_type='Mobile': {mobile_count.iloc[0]['count']}")
    
    # Check case sensitivity
    print("\n🔤 Checking case variations:")
    case_check = pd.read_sql_query(
        """
        SELECT device_type, COUNT(*) as count 
        FROM hits 
        WHERE LOWER(device_type) = 'mobile' 
        GROUP BY device_type
        """, 
        conn
    )
    print(case_check)
    print()
    
    # Check total records
    total_hits = pd.read_sql_query("SELECT COUNT(*) as total FROM hits", conn).iloc[0]['total']
    total_users = pd.read_sql_query("SELECT COUNT(DISTINCT user_id) as total FROM hits", conn).iloc[0]['total']
    total_sessions = pd.read_sql_query("SELECT COUNT(DISTINCT session_id) as total FROM hits", conn).iloc[0]['total']
    
    print(f"📊 Total Statistics:")
    print(f"- Total hits: {total_hits:,}")
    print(f"- Total unique users: {total_users:,}")
    print(f"- Total unique sessions: {total_sessions:,}")
    
    conn.close()

def fix_data_issues():
    """Fix common data issues"""
    db_path = Path("data/analytics.db")
    conn = sqlite3.connect(str(db_path))
    
    print("\n🔧 Fixing data issues...")
    
    # Check if we need to update device types
    cursor = conn.cursor()
    
    # Get current device type distribution
    device_check = pd.read_sql_query(
        "SELECT device_type, COUNT(*) as count FROM hits GROUP BY device_type", 
        conn
    )
    
    print("Current device types:")
    print(device_check)
    
    # If no Mobile devices exist, update some records
    mobile_count = conn.execute("SELECT COUNT(*) FROM hits WHERE device_type = 'Mobile'").fetchone()[0]
    
    if mobile_count == 0:
        print("\n⚠️  No 'Mobile' devices found. Creating some mobile records...")
        
        # Update 30% of records to be Mobile
        cursor.execute("""
            UPDATE hits 
            SET device_type = 'Mobile' 
            WHERE hit_id IN (
                SELECT hit_id FROM hits 
                ORDER BY RANDOM() 
                LIMIT (SELECT COUNT(*) * 0.3 FROM hits)
            )
        """)
        
        conn.commit()
        
        # Verify the update
        new_mobile_count = conn.execute("SELECT COUNT(*) FROM hits WHERE device_type = 'Mobile'").fetchone()[0]
        print(f"✅ Updated {new_mobile_count} records to device_type='Mobile'")
    else:
        print(f"✅ Found {mobile_count} records with device_type='Mobile'")
    
    conn.close()

if __name__ == "__main__":
    print("🚀 Database Debug Tool\n")
    check_database()
    
    # Ask if user wants to fix issues
    response = input("\nDo you want to fix data issues? (y/n): ")
    if response.lower() == 'y':
        fix_data_issues()
        print("\n✅ Done! Re-checking database...")
        check_database()
