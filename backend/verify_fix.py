#!/usr/bin/env python3
"""
Verify that the database path fix is working
"""

import os
import sqlite3
from services.faq import FAQService

def verify_fix():
    print("🔍 Verifying Database Path Fix")
    print("=" * 40)
    
    # Check current working directory
    cwd = os.getcwd()
    print(f"📁 Current directory: {cwd}")
    
    # Check if we're in the right place
    if not cwd.endswith('backend'):
        print("⚠️  Warning: Not in backend directory")
    
    # Test 1: Check database paths
    print("\n1️⃣ Database Paths:")
    
    # FAQ Service path
    faq_service = FAQService()
    faq_db_path = os.path.abspath(faq_service.db_path)
    print(f"   FAQ Service: {faq_db_path}")
    
    # Admin Interface path (simulated)
    admin_db_path = os.path.abspath("data/faqs.db")
    print(f"   Admin Interface: {admin_db_path}")
    
    # Check if they're the same
    same_path = faq_db_path == admin_db_path
    print(f"   Same path? {'✅ YES' if same_path else '❌ NO'}")
    
    if not same_path:
        print("   🔴 This is the problem! Different database files!")
        return False
    
    # Test 2: Check database connectivity
    print("\n2️⃣ Database Connectivity:")
    try:
        conn = sqlite3.connect("data/faqs.db")
        conn.row_factory = sqlite3.Row
        
        # Check table structure
        cursor = conn.execute("PRAGMA table_info(faqs)")
        columns = cursor.fetchall()
        print(f"   ✅ Table exists with {len(columns)} columns")
        
        # Check row count
        cursor = conn.execute("SELECT COUNT(*) FROM faqs")
        count = cursor.fetchone()[0]
        print(f"   📊 Database has {count} FAQs")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False
    
    # Test 3: Test FAQ service functionality
    print("\n3️⃣ FAQ Service Functionality:")
    try:
        # Test search
        test_question = "سلام"
        answer = faq_service.search_faq(test_question)
        if answer:
            print(f"   ✅ Found answer for '{test_question}': {answer[:50]}...")
        else:
            print(f"   ❌ No answer found for '{test_question}'")
        
        # Test getting all FAQs
        all_faqs = faq_service.get_all_faqs()
        print(f"   📋 Service can read {len(all_faqs)} FAQs")
        
    except Exception as e:
        print(f"   ❌ FAQ service test failed: {e}")
        return False
    
    print("\n✅ All tests passed! The fix should be working.")
    print("\n💡 To test the complete fix:")
    print("   1. Start the admin interface: python admin_interface.py")
    print("   2. Add a new FAQ through the web interface")
    print("   3. Check if the chatbot can find it")
    
    return True

if __name__ == "__main__":
    success = verify_fix()
    if not success:
        print("\n❌ Fix verification failed. There may still be issues.")

