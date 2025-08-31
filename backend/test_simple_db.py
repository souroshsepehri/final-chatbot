#!/usr/bin/env python3
"""
Simple database test to check connectivity and data
"""

import sqlite3
import os

def test_simple_db():
    print("🔍 Simple Database Test")
    print("=" * 30)
    
    # Check current directory
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Check if data directory exists
    data_dir = "data"
    print(f"📂 Data directory exists: {os.path.exists(data_dir)}")
    
    # Check if database exists
    db_path = "data/faqs.db"
    print(f"🗄️ Database exists: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        # Try to connect and read
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            # Check table structure
            cursor = conn.execute("PRAGMA table_info(faqs)")
            columns = cursor.fetchall()
            print(f"📋 Table columns: {len(columns)}")
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
            # Check row count
            cursor = conn.execute("SELECT COUNT(*) FROM faqs")
            count = cursor.fetchone()[0]
            print(f"📊 Total FAQs: {count}")
            
            # Show some sample data
            if count > 0:
                cursor = conn.execute("SELECT * FROM faqs LIMIT 3")
                rows = cursor.fetchall()
                print(f"📝 Sample data:")
                for i, row in enumerate(rows):
                    print(f"   {i+1}. Q: {row['question'][:50]}...")
                    print(f"      A: {row['answer'][:50]}...")
            
            conn.close()
            print("✅ Database access successful")
            
        except Exception as e:
            print(f"❌ Database access failed: {e}")
    else:
        print("❌ Database file not found")

if __name__ == "__main__":
    test_simple_db()

