#!/usr/bin/env python3
"""
Debug startup script for the admin interface.
"""

import os
import sys
import traceback

def main():
    """Start the admin interface with detailed logging."""
    print("🔍 Debug Admin Interface Startup")
    print("=" * 40)
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Check if we're in the right place
    if not os.path.exists("admin_interface.py"):
        print("❌ admin_interface.py not found in current directory")
        print("💡 Make sure you're in the backend directory")
        return
    
    # Check if data directory exists
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"❌ {data_dir} directory not found")
        print("💡 Creating data directory...")
        os.makedirs(data_dir, exist_ok=True)
        print("✅ Data directory created")
    else:
        print(f"✅ {data_dir} directory exists")
    
    # Check if custom_faq.json exists
    json_path = os.path.join(data_dir, "custom_faq.json")
    if os.path.exists(json_path):
        print(f"✅ {json_path} exists")
    else:
        print(f"❌ {json_path} not found")
    
    # Check if database exists
    db_path = os.path.join(data_dir, "faqs.db")
    if os.path.exists(db_path):
        print(f"✅ {db_path} exists")
        # Check file size
        size = os.path.getsize(db_path)
        print(f"   Database size: {size} bytes")
    else:
        print(f"❌ {db_path} not found (will be created)")
    
    # Try to import Flask
    print("\n🔍 Checking Flask...")
    try:
        import flask
        print(f"✅ Flask {flask.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        print("💡 Install Flask: pip install flask==3.0.0")
        return
    
    # Try to import the admin interface
    print("\n🔍 Importing admin interface...")
    try:
        import admin_interface
        print("✅ Admin interface imported successfully")
        
        # Check if it has the required components
        if hasattr(admin_interface, 'app'):
            print("✅ Flask app found")
        else:
            print("❌ Flask app not found")
            return
            
        if hasattr(admin_interface, 'get_db_connection'):
            print("✅ Database connection function found")
        else:
            print("❌ Database connection function not found")
            return
        
    except Exception as e:
        print(f"❌ Admin interface import failed: {e}")
        traceback.print_exc()
        return
    
    # Try to test database connection
    print("\n🔍 Testing database connection...")
    try:
        conn = admin_interface.get_db_connection()
        print("✅ Database connection successful")
        
        # Check if table exists
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='faqs'")
        if cursor.fetchone():
            print("✅ faqs table exists")
            
            # Check table structure
            cursor = conn.execute("PRAGMA table_info(faqs)")
            columns = cursor.fetchall()
            print(f"✅ Table has {len(columns)} columns:")
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
            # Check if there's data
            cursor = conn.execute("SELECT COUNT(*) FROM faqs")
            count = cursor.fetchone()[0]
            print(f"✅ Table has {count} rows")
            
        else:
            print("❌ faqs table not found!")
            return
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        traceback.print_exc()
        return
    
    # All tests passed, start the interface
    print("\n🎉 All tests passed! Starting admin interface...")
    print("=" * 40)
    
    try:
        admin_interface.app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Failed to start admin interface: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
