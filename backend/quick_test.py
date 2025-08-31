#!/usr/bin/env python3
import sqlite3
from services.faq import FAQService

print("🔍 Quick FAQ Service Test")
print("=" * 30)

# Test 1: Direct database read
print("\n1️⃣ Direct Database Read:")
try:
    conn = sqlite3.connect("data/faqs.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT COUNT(*) FROM faqs")
    count = cursor.fetchone()[0]
    print(f"   Database has {count} FAQs")
    
    if count > 0:
        cursor = conn.execute("SELECT question FROM faqs LIMIT 3")
        questions = cursor.fetchall()
        print("   Sample questions:")
        for i, row in enumerate(questions):
            print(f"      {i+1}. {row['question']}")
    
    conn.close()
    print("   ✅ Direct read successful")
except Exception as e:
    print(f"   ❌ Direct read failed: {e}")

# Test 2: FAQ Service read
print("\n2️⃣ FAQ Service Read:")
try:
    faq_service = FAQService()
    
    # Try to get all FAQs
    all_faqs = faq_service.get_all_faqs()
    print(f"   FAQ Service found {len(all_faqs)} FAQs")
    
    if all_faqs:
        print("   Sample FAQs from service:")
        for i, faq in enumerate(all_faqs[:3]):
            print(f"      {i+1}. Q: {faq['question'][:40]}...")
    
    print("   ✅ FAQ Service read successful")
except Exception as e:
    print(f"   ❌ FAQ Service read failed: {e}")

print("\n✅ Test completed!")
