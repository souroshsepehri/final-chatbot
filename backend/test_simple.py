#!/usr/bin/env python3
"""
Simple test script to check if the basic services work.
"""

def test_basic_imports():
    """Test basic Python imports."""
    try:
        print("Testing basic imports...")
        import sqlite3
        print("✅ sqlite3 imported successfully")
        
        import os
        print("✅ os imported successfully")
        
        import json
        print("✅ json imported successfully")
        
        from datetime import datetime
        print("✅ datetime imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_faq_service():
    """Test FAQ service import and basic functionality."""
    try:
        print("\nTesting FAQ service...")
        from services.faq import FAQService
        print("✅ FAQService imported successfully")
        
        # Try to create an instance
        faq_service = FAQService()
        print("✅ FAQService instance created successfully")
        
        # Test basic methods
        result = faq_service.is_greeting("سلام")
        print(f"✅ Greeting detection works: {result}")
        
        return True
    except Exception as e:
        print(f"❌ FAQ service error: {e}")
        return False

def test_database_connection():
    """Test database connection."""
    try:
        print("\nTesting database connection...")
        import sqlite3
        
        db_path = "data/faqs.db"
        if os.path.exists(db_path):
            print(f"✅ Database file exists: {db_path}")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM faqs")
                count = cursor.fetchone()[0]
                print(f"✅ Database connection successful, FAQ count: {count}")
        else:
            print(f"❌ Database file not found: {db_path}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Simple ChatBot Service Test")
    print("=" * 40)
    
    tests = [
        test_basic_imports,
        test_faq_service,
        test_database_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The services should work.")
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
