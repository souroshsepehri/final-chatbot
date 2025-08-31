#!/usr/bin/env python3
"""
Check and fix FAQ database.
"""

import sqlite3
import json
import os

def check_database():
    """Check what's currently in the database."""
    print("🔍 Checking FAQ Database...")
    
    db_path = "data/faqs.db"
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    with sqlite3.connect(db_path) as conn:
        # Check total count
        cursor = conn.execute("SELECT COUNT(*) FROM faqs")
        total = cursor.fetchone()[0]
        print(f"📊 Total FAQs in database: {total}")
        
        # Check for company questions
        company_questions = [
            "What do you do?",
            "What is your company?",
            "شرکت شما چه کاری انجام می‌دهد؟",
            "شما چه کاری انجام می‌دهید؟"
        ]
        
        print("\n🔍 Checking for company questions...")
        for question in company_questions:
            cursor = conn.execute("SELECT answer FROM faqs WHERE question = ?", (question,))
            result = cursor.fetchone()
            if result:
                print(f"✅ Found: {question}")
                print(f"   Answer: {result[0]}")
            else:
                print(f"❌ Missing: {question}")
        
        # Show all questions
        print(f"\n📝 All questions in database:")
        cursor = conn.execute("SELECT question FROM faqs ORDER BY question")
        questions = cursor.fetchall()
        for i, (question,) in enumerate(questions, 1):
            print(f"   {i}. {question}")

def reload_faqs():
    """Reload FAQs from JSON file."""
    print("\n🔄 Reloading FAQs from JSON...")
    
    json_path = "data/custom_faq.json"
    if not os.path.exists(json_path):
        print("❌ JSON file not found!")
        return
    
    # Read JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    faqs = data.get("faqs", [])
    print(f"📖 Found {len(faqs)} FAQs in JSON")
    
    # Clear and reload database
    db_path = "data/faqs.db"
    with sqlite3.connect(db_path) as conn:
        # Clear existing data
        conn.execute("DELETE FROM faqs")
        print("🗑️ Cleared existing database")
        
        # Insert new data
        for faq in faqs:
            question = faq.get("question", "").strip()
            answer = faq.get("answer", "").strip()
            if question and answer:
                conn.execute(
                    "INSERT INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, datetime('now'), datetime('now'))",
                    (question, answer, "general")
                )
        
        conn.commit()
        print(f"✅ Inserted {len(faqs)} FAQs into database")

def test_company_questions():
    """Test if company questions work now."""
    print("\n🧪 Testing company questions...")
    
    try:
        from services.faq import FAQService
        faq_service = FAQService()
        
        test_questions = [
            "What do you do?",
            "What is your company?",
            "شرکت شما چه کاری انجام می‌دهد؟",
            "شما چه کاری انجام می‌دهید؟"
        ]
        
        for question in test_questions:
            print(f"\nQ: {question}")
            answer = faq_service.search_faq(question)
            if answer:
                print(f"A: {answer}")
                if "اتوماسیون هوش مصنوعی" in answer:
                    print("✅ Correct answer found!")
                else:
                    print("❌ Wrong answer!")
            else:
                print("❌ No answer found!")
                
    except Exception as e:
        print(f"❌ Error testing: {e}")

def main():
    """Main function."""
    print("🔧 FAQ Database Check and Fix Tool")
    print("=" * 50)
    
    # Check current state
    check_database()
    
    # Ask if user wants to reload
    print("\n" + "=" * 50)
    response = input("Do you want to reload FAQs from JSON? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        reload_faqs()
        check_database()
        test_company_questions()
    else:
        print("Skipping reload.")

if __name__ == "__main__":
    main()
