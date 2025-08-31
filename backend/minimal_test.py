#!/usr/bin/env python3
"""
Minimal test to identify the issue.
"""

print("Starting minimal test...")

try:
    print("1. Testing basic Python...")
    print("Python is working")
    
    print("2. Testing imports...")
    import os
    print("os imported")
    
    import sqlite3
    print("sqlite3 imported")
    
    print("3. Testing database file...")
    db_path = "data/faqs.db"
    if os.path.exists(db_path):
        print(f"Database exists: {db_path}")
        print(f"Size: {os.path.getsize(db_path)} bytes")
    else:
        print("Database file not found!")
    
    print("4. Testing database connection...")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables found: {tables}")
        
        if tables:
            cursor = conn.execute("SELECT COUNT(*) FROM faqs")
            count = cursor.fetchone()[0]
            print(f"FAQ count: {count}")
    
    print("5. Testing service import...")
    import sys
    sys.path.append('.')
    
    from services.faq import FAQService
    print("FAQService imported successfully!")
    
    print("6. Testing service creation...")
    faq_service = FAQService()
    print("FAQService created successfully!")
    
    print("7. Testing greeting detection...")
    result = faq_service.is_greeting("سلام")
    print(f"Greeting detection result: {result}")
    
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error occurred: {e}")
    import traceback
    traceback.print_exc()
