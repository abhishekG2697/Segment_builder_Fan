import sqlite3
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import random
import numpy as np

def initialize_database():
    """Initialize the SQLite database with tables and sample data"""
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Database path
    db_path = data_dir / "analytics.db"
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create tables
    create_tables(cursor)
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM hits")
    if cursor.fetchone()[0] == 0:
        # Generate sample data
        print("Generating sample data...")
        generate_sample_data(conn)
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized at: {db_path}")

def create_tables(cursor):
    """Create the necessary tables"""
    
    # Hits table (page views/events)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hits (
        hit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME NOT NULL,
        user_id TEXT NOT NULL,
        session_id TEXT NOT NULL,
        page_url TEXT,
        page_title TEXT,
        page_type TEXT,
        browser_name TEXT,
        browser_version TEXT,
        device_type TEXT,
        country TEXT,
        city TEXT,
        traffic_source TEXT,
        traffic_medium TEXT,
        campaign TEXT,
        revenue REAL DEFAULT 0,
        products_viewed INTEGER DEFAULT 0,
        cart_additions INTEGER DEFAULT 0,
        time_on_page INTEGER DEFAULT 0,
        bounce INTEGER DEFAULT 0
    )
    """)
    
    # Create indexes for hits table
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hits_timestamp ON hits(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hits_user_id ON hits(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hits_session_id ON hits(session_id)")
    
    # Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        start_time DATETIME NOT NULL,
        end_time DATETIME NOT NULL,
        total_hits INTEGER DEFAULT 0,
        total_revenue REAL DEFAULT 0,
        session_duration INTEGER DEFAULT 0,
        pages_viewed INTEGER DEFAULT 0
    )
    """)
    
    # Create indexes for sessions table
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time)")
    
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        first_seen DATETIME NOT NULL,
        last_seen DATETIME NOT NULL,
        user_type TEXT,
        total_sessions INTEGER DEFAULT 0,
        total_revenue REAL DEFAULT 0,
        total_orders INTEGER DEFAULT 0,
        avg_session_duration INTEGER DEFAULT 0
    )
    """)
    
    # Segments table (for saved segments)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS segments (
        segment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        definition TEXT NOT NULL,
        container_type TEXT,
        created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT,
        usage_count INTEGER DEFAULT 0,
        tags TEXT
    )
    """)

def generate_sample_data(conn):
    """Generate sample analytics data"""
    
    # Configuration
    num_users = 10000
    avg_sessions_per_user = 5
    avg_hits_per_session = 10
    days_back = 30
    
    # Reference data
    browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Other']
    browser_weights = [0.65, 0.15, 0.10, 0.08, 0.02]
    
    devices = ['Desktop', 'Mobile', 'Tablet']
    device_weights = [0.50, 0.40, 0.10]
    
    countries = ['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'JP', 'IN']
    country_weights = [0.40, 0.15, 0.10, 0.08, 0.07, 0.07, 0.07, 0.06]
    
    traffic_sources = ['Direct', 'Organic', 'Paid', 'Social', 'Email', 'Referral']
    source_weights = [0.25, 0.30, 0.20, 0.10, 0.10, 0.05]
    
    page_types = ['Home', 'Category', 'Product', 'Search', 'Checkout', 'Account']
    page_weights = [0.20, 0.25, 0.30, 0.10, 0.05, 0.10]
    
    # Generate data
    hits_data = []
    sessions_data = []
    users_data = []
    
    # Generate users
    for i in range(num_users):
        user_id = f"user_{i:06d}"
        first_seen = datetime.now() - timedelta(days=random.randint(0, days_back * 2))
        user_type = random.choice(['New', 'Returning', 'Registered'])
        
        user_sessions = []
        user_revenue = 0
        user_orders = 0
        
        # Generate sessions for user
        num_sessions = max(1, int(np.random.poisson(avg_sessions_per_user)))
        for j in range(num_sessions):
            session_id = f"{user_id}_session_{j}"
            session_start = first_seen + timedelta(
                days=random.randint(0, days_back),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            session_hits = []
            session_revenue = 0
            
            # Generate hits for session
            num_hits = max(1, int(np.random.poisson(avg_hits_per_session)))
            for k in range(num_hits):
                hit_time = session_start + timedelta(minutes=random.randint(0, 30))
                
                page_type = np.random.choice(page_types, p=page_weights)
                page_url = f"/{page_type.lower()}/{random.randint(1, 100)}"
                page_title = f"{page_type} Page {random.randint(1, 100)}"
                
                # Generate hit data
                hit = {
                    'timestamp': hit_time,
                    'user_id': user_id,
                    'session_id': session_id,
                    'page_url': page_url,
                    'page_title': page_title,
                    'page_type': page_type,
                    'browser_name': np.random.choice(browsers, p=browser_weights),
                    'browser_version': f"{random.randint(80, 120)}.0",
                    'device_type': np.random.choice(devices, p=device_weights),
                    'country': np.random.choice(countries, p=country_weights),
                    'city': f"City_{random.randint(1, 50)}",
                    'traffic_source': np.random.choice(traffic_sources, p=source_weights),
                    'traffic_medium': random.choice(['cpc', 'organic', 'email', 'social', 'none']),
                    'campaign': f"campaign_{random.randint(1, 20)}" if random.random() > 0.7 else None,
                    'revenue': random.uniform(10, 500) if page_type == 'Checkout' and random.random() > 0.3 else 0,
                    'products_viewed': random.randint(1, 5) if page_type == 'Product' else 0,
                    'cart_additions': random.randint(1, 3) if page_type == 'Product' and random.random() > 0.5 else 0,
                    'time_on_page': random.randint(10, 300),
                    'bounce': 1 if k == 0 and num_hits == 1 else 0
                }
                
                hits_data.append(hit)
                session_hits.append(hit)
                session_revenue += hit['revenue']
                
                if hit['revenue'] > 0:
                    user_orders += 1
            
            # Create session record
            session_end = session_hits[-1]['timestamp'] + timedelta(seconds=session_hits[-1]['time_on_page'])
            session_duration = int((session_end - session_start).total_seconds())
            
            session = {
                'session_id': session_id,
                'user_id': user_id,
                'start_time': session_start,
                'end_time': session_end,
                'total_hits': len(session_hits),
                'total_revenue': session_revenue,
                'session_duration': session_duration,
                'pages_viewed': len(set(h['page_url'] for h in session_hits))
            }
            
            sessions_data.append(session)
            user_sessions.append(session)
            user_revenue += session_revenue
        
        # Create user record
        last_seen = max(s['end_time'] for s in user_sessions)
        avg_duration = sum(s['session_duration'] for s in user_sessions) // len(user_sessions)
        
        user = {
            'user_id': user_id,
            'first_seen': first_seen,
            'last_seen': last_seen,
            'user_type': user_type,
            'total_sessions': len(user_sessions),
            'total_revenue': user_revenue,
            'total_orders': user_orders,
            'avg_session_duration': avg_duration
        }
        
        users_data.append(user)
        
        # Progress indicator
        if (i + 1) % 1000 == 0:
            print(f"Generated data for {i + 1} users...")
    
    # Insert data into database
    print("Inserting data into database...")
    
    # Convert to DataFrames
    hits_df = pd.DataFrame(hits_data)
    sessions_df = pd.DataFrame(sessions_data)
    users_df = pd.DataFrame(users_data)
    
    # Insert into database
    hits_df.to_sql('hits', conn, if_exists='append', index=False)
    sessions_df.to_sql('sessions', conn, if_exists='append', index=False)
    users_df.to_sql('users', conn, if_exists='append', index=False)
    
    print(f"Sample data generation complete!")
    print(f"- Users: {len(users_data):,}")
    print(f"- Sessions: {len(sessions_data):,}")
    print(f"- Hits: {len(hits_data):,}")

if __name__ == "__main__":
    initialize_database()