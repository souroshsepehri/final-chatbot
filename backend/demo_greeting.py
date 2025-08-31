#!/usr/bin/env python3
"""
Demonstration script for the greeting system.
This script shows how the greeting detection and FAQ matching work.
"""

import sqlite3
import os
from datetime import datetime

class DemoFAQService:
    """Demo version of the FAQ service to show functionality."""
    
    def __init__(self, db_path: str = "data/faqs.db"):
        self.db_path = db_path
        self._init_demo_db()
    
    def _init_demo_db(self):
        """Initialize demo database with sample data."""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS faqs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL UNIQUE,
                    answer TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'general',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Insert demo data
            demo_data = [
                ("سلام", "سلام علیکم! خوش آمدید! چطور می‌تونم کمکتون کنم؟"),
                ("hello", "Hello! Welcome! How can I help you today?"),
                ("What is your name?", "My name is ChatBot, and I'm here to help you with your questions!"),
                ("Tell me a joke", "Why don't scientists trust atoms? Because they make up everything! 😄"),
                ("How are you?", "I'm doing well, thank you for asking! How can I assist you today?"),
                ("شروع", "سلام! بله، بیایید شروع کنیم! چطور می‌تونم کمکتون کنم؟"),
                ("start", "Hello! Yes, let's get started! How can I help you?"),
                ("What do you do?", "ما یک شرکت اتوماسیون هوش مصنوعی هستیم"),
                ("What is your company?", "ما یک شرکت اتوماسیون هوش مصنوعی هستیم"),
                ("شرکت شما چه کاری انجام می‌دهد؟", "ما یک شرکت اتوماسیون هوش مصنوعی هستیم"),
                ("شما چه کاری انجام می‌دهید؟", "ما یک شرکت اتوماسیون هوش مصنوعی هستیم"),
            ]
            
            now = datetime.utcnow().isoformat()
            for question, answer in demo_data:
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO faqs (question, answer, created_at, updated_at) VALUES (?, ?, ?, ?)",
                        (question, answer, now, now)
                    )
                except:
                    pass
            
            conn.commit()
    
    def is_greeting(self, message: str) -> bool:
        """Check if the message is a greeting."""
        greetings = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
            'سلام', 'درود', 'خوش آمدید', 'سلام علیکم', 'صبخ بخیر', 'عصر بخیر',
            'start', 'begin', 'شروع', 'آغاز', 'چت', 'chat'
        ]
        
        message_lower = message.lower().strip()
        return any(greeting in message_lower for greeting in greetings)
    
    def get_greeting_response(self) -> str:
        """Get a random greeting response."""
        greetings = [
            "سلام! 👋 خوش آمدید! چطور می‌تونم کمکتون کنم؟",
            "درود! 😊 من بات هوشمند زیمر هستم. چطور می‌تونم کمکتون کنم؟",
            "سلام علیکم! 🌟 خوشحالم که با شما صحبت می‌کنم. چطور می‌تونم کمکتون کنم؟",
            "Hi there! 👋 Welcome! How can I help you today?",
            "Hello! 😊 I'm your AI assistant. How can I be of service?"
        ]
        
        import random
        return random.choice(greetings)
    
    def search_faq(self, question: str) -> str:
        """Search for FAQ answer with multiple strategies."""
        question = question.strip().lower()
        
        with sqlite3.connect(self.db_path) as conn:
            # Strategy 1: Exact match
            row = conn.execute(
                "SELECT answer FROM faqs WHERE lower(question) = lower(?)",
                (question,)
            ).fetchone()
            if row:
                return f"FAQ Answer: {row[0]}"
            
            # Strategy 2: Partial match
            row = conn.execute(
                "SELECT answer FROM faqs WHERE lower(?) LIKE '%' || lower(question) || '%'",
                (question,)
            ).fetchone()
            if row:
                return f"Partial FAQ Match: {row[0]}"
            
            # Strategy 3: Word overlap
            words = question.split()
            if len(words) > 1:
                for word in words:
                    if len(word) > 2:
                        row = conn.execute(
                            "SELECT answer FROM faqs WHERE lower(question) LIKE '%' || lower(?) || '%'",
                            (word,)
                        ).fetchone()
                        if row:
                            return f"Word Match ('{word}'): {row[0]}"
        
        return "No FAQ found - would use GPT-4 or fallback"

def demo_greeting_system():
    """Demonstrate the greeting system."""
    print("🤖 ChatBot Greeting System Demo")
    print("=" * 50)
    
    # Initialize demo service
    faq_service = DemoFAQService()
    
    # Test cases
    test_cases = [
        "سلام",
        "hello",
        "hi there",
        "شروع",
        "start conversation",
        "What is your name?",
        "Tell me a joke",
        "How are you doing?",
        "What's the weather like?",
        "What do you do?",
        "What is your company?",
        "شرکت شما چه کاری انجام می‌دهد؟",
        "شما چه کاری انجام می‌دهید؟",
        "random question that won't match"
    ]
    
    for test_input in test_cases:
        print(f"\n📝 Input: '{test_input}'")
        
        # Check if it's a greeting
        if faq_service.is_greeting(test_input):
            response = faq_service.get_greeting_response()
            print(f"🎯 Detected as GREETING")
            print(f"💬 Response: {response}")
        else:
            # Try to find FAQ answer
            response = faq_service.search_faq(test_input)
            print(f"🔍 FAQ Lookup Result: {response}")
        
        print("-" * 40)
    
    # Show database stats
    print(f"\n📊 Database Statistics:")
    with sqlite3.connect("data/faqs.db") as conn:
        count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
        print(f"   Total FAQs: {count}")
        
        categories = conn.execute("SELECT DISTINCT category FROM faqs").fetchall()
        print(f"   Categories: {[cat[0] for cat in categories]}")

if __name__ == "__main__":
    demo_greeting_system()
