#!/usr/bin/env python3
"""
Test script for the greeting system.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_greeting():
    """Test the greeting functionality."""
    print("Testing ChatBot Greeting System...")
    print("=" * 50)
    
    # Test 1: Greeting detection
    greetings = ["سلام", "hello", "hi", "شروع", "start"]
    
    for greeting in greetings:
        print(f"\nTesting greeting: '{greeting}'")
        try:
            response = requests.post(
                f"{BASE_URL}/chat/",
                json={"message": greeting},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response']}")
                print(f"   Source: {data['source']}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Test 2: FAQ lookup
    print(f"\n{'='*50}")
    print("Testing FAQ Lookup...")
    
    questions = [
        "What is your name?",
        "Tell me a joke",
        "How are you?",
        "What time is it?",
        "What do you do?",
        "What is your company?",
        "شرکت شما چه کاری انجام می‌دهد؟",
        "شما چه کاری انجام می‌دهید؟"
    ]
    
    for question in questions:
        print(f"\nTesting question: '{question}'")
        try:
            response = requests.post(
                f"{BASE_URL}/chat/",
                json={"message": question},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response']}")
                print(f"   Source: {data['source']}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Test 3: Get stats
    print(f"\n{'='*50}")
    print("Testing Stats Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/chat/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Total FAQs: {stats['total_faqs']}")
            print(f"   Categories: {stats['categories']}")
            print(f"   Category Counts: {stats['category_counts']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_greeting()
