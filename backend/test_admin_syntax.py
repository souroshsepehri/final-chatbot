#!/usr/bin/env python3
"""
Test script to verify admin interface syntax and basic functionality
"""

print("🔍 Testing Admin Interface...")

try:
    # Test imports
    print("✅ Testing imports...")
    import admin_interface
    print("✅ All imports successful")
    
    # Test database connection function
    print("✅ Testing database connection...")
    conn = admin_interface.get_db_connection()
    print("✅ Database connection successful")
    
    # Test FAQ count
    count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
    print(f"✅ Database has {count} FAQs")
    
    conn.close()
    print("✅ Database connection closed")
    
    # Test Flask app
    print("✅ Testing Flask app...")
    app = admin_interface.app
    print(f"✅ Flask app created: {type(app)}")
    
    print("\n🎉 All tests passed! Admin interface is ready to use.")
    print("💡 You can now run: python admin_interface.py")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

