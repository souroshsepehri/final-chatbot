#!/usr/bin/env python3
"""
Test script for the admin interface.
"""

import os
import sqlite3
import sys

def test_database_connection():
    """Test if we can connect to the database."""
    print("🔍 Testing database connection...")
    
    # Check if database file exists
    db_path = os.path.join(os.path.dirname(__file__), "data", "faqs.db")
    print(f"Database path: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    print("✅ Database file exists")
    
    # Try to connect
    try:
        conn = sqlite3.connect(db_path)
        print("✅ Database connection successful")
        
        # Check if faqs table exists
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
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_flask_import():
    """Test if Flask can be imported."""
    print("\n🔍 Testing Flask import...")
    
    try:
        import flask
        print(f"✅ Flask imported successfully (version: {flask.__version__})")
        return True
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False

def test_admin_interface_import():
    """Test if we can import the admin interface."""
    print("\n🔍 Testing admin interface import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Try to import the admin interface
        import admin_interface
        print("✅ Admin interface imported successfully")
        
        # Check if it has the required functions
        if hasattr(admin_interface, 'app'):
            print("✅ Flask app found")
        else:
            print("❌ Flask app not found")
            return False
            
        if hasattr(admin_interface, 'get_db_connection'):
            print("✅ Database connection function found")
        else:
            print("❌ Database connection function not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Admin interface import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_interface_startup():
    """Test if the admin interface can start without errors."""
    print("\n🔍 Testing admin interface startup...")
    
    try:
        # Import the admin interface
        import admin_interface
        
        # Check if the app can be created
        app = admin_interface.app
        print("✅ Flask app created successfully")
        
        # Check if routes are registered
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        print(f"✅ Found {len(routes)} routes:")
        for route in routes:
            print(f"   - {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ Admin interface startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Admin Interface Test Suite")
    print("=" * 40)
    
    tests = [
        test_database_connection,
        test_flask_import,
        test_admin_interface_import,
        test_admin_interface_startup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The admin interface should work.")
        print("\n🚀 To start the admin interface, run:")
        print("   python admin_interface.py")
        print("   Then open http://localhost:5000 in your browser")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("\n💡 Common solutions:")
        print("   1. Install Flask: pip install flask==3.0.0")
        print("   2. Make sure you're in the backend directory")
        print("   3. Check if the database file exists")

if __name__ == "__main__":
    main()

