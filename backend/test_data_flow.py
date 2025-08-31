#!/usr/bin/env python3
"""
Test data flow between admin interface and FAQ service
"""

import sqlite3
import os
from services.faq import FAQService

def test_data_flow():
    print("🔍 Testing Data Flow Between Services")
    print("=" * 50)
    
    # Test 1: Direct database access
    print("\n1️⃣ Direct Database Access:")
    try:
        conn = sqlite3.connect("data/faqs.db")
        conn.row_factory = sqlite3.Row
        
        # Check current data
        cursor = conn.execute("SELECT COUNT(*) FROM faqs")
        count = cursor.fetchone()[0]
        print(f"   📊 Current FAQ count: {count}")
        
        if count > 0:
            cursor = conn.execute("SELECT * FROM faqs ORDER BY created_at DESC LIMIT 3")
            rows = cursor.fetchall()
            print(f"   📝 Latest FAQs:")
            for i, row in enumerate(rows):
                print(f"      {i+1}. ID: {row['id']}, Q: {row['question'][:40]}...")
        
        conn.close()
        print("   ✅ Direct access successful")
        
    except Exception as e:
        print(f"   ❌ Direct access failed: {e}")
    
    # Test 2: FAQ Service access
    print("\n2️⃣ FAQ Service Access:")
    try:
        faq_service = FAQService()
        
        # Test search functionality
        test_questions = [
            "سلام",  # Greeting
            "What is your work?",  # Company question
            "How are you?",  # General question
        ]
        
        for question in test_questions:
            answer = faq_service.search_faq(question)
            if answer:
                print(f"   🔍 '{question}' -> Found: {answer[:50]}...")
            else:
                print(f"   🔍 '{question}' -> No answer found")
        
        print("   ✅ FAQ service access successful")
        
    except Exception as e:
        print(f"   ❌ FAQ service access failed: {e}")
    
    # Test 3: Add test data directly
    print("\n3️⃣ Adding Test Data Directly:")
    try:
        conn = sqlite3.connect("data/faqs.db")
        conn.row_factory = sqlite3.Row
        
        # Add a test FAQ
        test_question = "TEST_QUESTION_FOR_DEBUGGING"
        test_answer = "This is a test answer to verify data persistence"
        
        # Check if it already exists
        cursor = conn.execute("SELECT id FROM faqs WHERE question = ?", (test_question,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"   ℹ️ Test question already exists (ID: {existing['id']})")
        else:
            # Insert test data
            cursor = conn.execute(
                "INSERT INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, datetime('now'), datetime('now'))",
                (test_question, test_answer, "test")
            )
            conn.commit()
            print(f"   ✅ Added test FAQ with ID: {cursor.lastrowid}")
        
        # Verify it was added
        cursor = conn.execute("SELECT * FROM faqs WHERE question = ?", (test_question,))
        row = cursor.fetchone()
        if row:
            print(f"   ✅ Test FAQ verified in database: {row['answer']}")
        else:
            print(f"   ❌ Test FAQ not found after insertion")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Test data insertion failed: {e}")
    
    # Test 4: Check if FAQ service can see the test data
    print("\n4️⃣ FAQ Service Reading Test Data:")
    try:
        faq_service = FAQService()
        answer = faq_service.search_faq("TEST_QUESTION_FOR_DEBUGGING")
        if answer:
            print(f"   ✅ FAQ service found test data: {answer[:50]}...")
        else:
            print(f"   ❌ FAQ service cannot find test data")
            
        # Try partial search too
        answer_partial = faq_service.search_faq_partial("TEST_QUESTION")
        if answer_partial:
            print(f"   ✅ FAQ service partial search found: {answer_partial[:50]}...")
        else:
            print(f"   ❌ FAQ service partial search failed")
        
    except Exception as e:
        print(f"   ❌ FAQ service test data check failed: {e}")
    
    # Test 5: Clean up test data
    print("\n5️⃣ Cleaning Up Test Data:")
    try:
        conn = sqlite3.connect("data/faqs.db")
        conn.row_factory = sqlite3.Row
        
        # Remove test data
        cursor = conn.execute("DELETE FROM faqs WHERE question LIKE 'TEST_%'")
        deleted_count = cursor.rowcount
        conn.commit()
        print(f"   🧹 Removed {deleted_count} test FAQs")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Test data cleanup failed: {e}")

if __name__ == "__main__":
    test_data_flow()

