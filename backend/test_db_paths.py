#!/usr/bin/env python3
"""
Test script to verify database paths and connectivity
"""

import os
import sqlite3
from services.faq import FAQService

def test_database_paths():
    print("🔍 Testing Database Paths and Connectivity")
    print("=" * 50)
    
    # Get current working directory
    cwd = os.getcwd()
    print(f"📁 Current working directory: {cwd}")
    
    # Test FAQ Service database path
    print("\n🔧 FAQ Service Database:")
    faq_service = FAQService()
    faq_db_path = os.path.abspath(faq_service.db_path)
    print(f"   Path: {faq_db_path}")
    print(f"   Exists: {os.path.exists(faq_db_path)}")
    
    # Test Admin Interface database path (simulated)
    print("\n🔧 Admin Interface Database (simulated):")
    admin_db_path = os.path.abspath("data/faqs.db")
    print(f"   Path: {admin_db_path}")
    print(f"   Exists: {os.path.exists(admin_db_path)}")
    
    # Check if they're the same
    print(f"\n🔍 Same database file? {faq_db_path == admin_db_path}")
    
    # Test database connectivity
    print("\n🔌 Testing Database Connectivity:")
    try:
        # Test FAQ Service connection
        with faq_service._connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
            print(f"   ✅ FAQ Service: Connected, {count} FAQs found")
    except Exception as e:
        print(f"   ❌ FAQ Service: Connection failed - {e}")
    
    try:
        # Test direct connection to the same path
        conn = sqlite3.connect("data/faqs.db")
        conn.row_factory = sqlite3.Row
        count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
        conn.close()
        print(f"   ✅ Direct connection: Connected, {count} FAQs found")
    except Exception as e:
        print(f"   ❌ Direct connection: Failed - {e}")
    
    # Check data directory contents
    print("\n📂 Data Directory Contents:")
    data_dir = "data"
    if os.path.exists(data_dir):
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                print(f"   📄 {item} ({size} bytes)")
            else:
                print(f"   📁 {item}/")
    else:
        print("   ❌ Data directory does not exist")
    
    # Check if custom_faq.json exists
    json_path = "data/custom_faq.json"
    print(f"\n📋 Custom FAQ JSON:")
    print(f"   Path: {os.path.abspath(json_path)}")
    print(f"   Exists: {os.path.exists(json_path)}")
    if os.path.exists(json_path):
        size = os.path.getsize(json_path)
        print(f"   Size: {size} bytes")

if __name__ == "__main__":
    test_database_paths()

