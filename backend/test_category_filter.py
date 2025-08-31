#!/usr/bin/env python3
"""
Test script for category filtering functionality
"""

import sqlite3
import os
from datetime import datetime

def test_category_filter():
    """Test the category filtering functionality."""
    
    # Test database path
    db_path = "data/faqs.db"
    
    print("🧪 Testing Category Filter Functionality")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Get all FAQs
        faqs = conn.execute("SELECT * FROM faqs").fetchall()
        print(f"✅ Found {len(faqs)} FAQs in database")
        
        # Get categories
        categories = conn.execute("SELECT DISTINCT category FROM faqs WHERE category IS NOT NULL").fetchall()
        print(f"✅ Found {len(categories)} categories:")
        
        # Get category counts
        category_counts = {}
        for cat in categories:
            count = conn.execute("SELECT COUNT(*) FROM faqs WHERE category = ?", (cat['category'],)).fetchone()[0]
            category_counts[cat['category']] = count
            print(f"   - {cat['category']}: {count} FAQs")
        
        # Test filtering by category
        print("\n🔍 Testing category filtering:")
        for category in categories:
            cat_name = category['category']
            filtered_faqs = conn.execute("SELECT * FROM faqs WHERE category = ?", (cat_name,)).fetchall()
            print(f"   - {cat_name}: {len(filtered_faqs)} FAQs found")
            
            # Show first FAQ as example
            if filtered_faqs:
                first_faq = filtered_faqs[0]
                print(f"     Example: {first_faq['question'][:50]}...")
        
        conn.close()
        print("\n✅ Category filtering test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing category filtering: {e}")
        return False

if __name__ == "__main__":
    test_category_filter()

