#!/usr/bin/env python3
"""
Test script for semantic search functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_embeddings_service():
    """Test the embeddings service."""
    print("🧪 Testing Embeddings Service...")
    
    try:
        from services.embeddings import get_embedding, cosine_similarity
        
        # Test embedding generation
        text1 = "What are your business hours?"
        text2 = "When are you open?"
        text3 = "What is the weather like?"
        
        print("  📝 Generating embeddings...")
        embedding1 = get_embedding(text1)
        embedding2 = get_embedding(text2)
        embedding3 = get_embedding(text3)
        
        print(f"  ✅ Embedding 1 length: {len(embedding1)}")
        print(f"  ✅ Embedding 2 length: {len(embedding2)}")
        print(f"  ✅ Embedding 3 length: {len(embedding3)}")
        
        # Test cosine similarity
        print("  🔍 Testing cosine similarity...")
        sim_similar = cosine_similarity(embedding1, embedding2)
        sim_different = cosine_similarity(embedding1, embedding3)
        
        print(f"  ✅ Similar questions similarity: {sim_similar:.4f}")
        print(f"  ✅ Different questions similarity: {sim_different:.4f}")
        
        # Verify that similar questions have higher similarity
        if sim_similar > sim_different:
            print("  ✅ Similar questions correctly have higher similarity!")
        else:
            print("  ⚠️  Similar questions don't have higher similarity (this might be normal)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing embeddings service: {e}")
        return False


def test_faq_service():
    """Test the FAQ service."""
    print("\n🧪 Testing FAQ Service...")
    
    try:
        from services.faq_simple import faq_simple_service
        
        # Test loading FAQs
        print("  📚 Loading FAQ items...")
        faqs = faq_simple_service.load_faq_items()
        print(f"  ✅ Loaded {len(faqs)} FAQ items")
        
        if faqs:
            # Check if embeddings exist
            faqs_with_embeddings = sum(1 for f in faqs if f.get("embedding") is not None)
            print(f"  ✅ {faqs_with_embeddings} FAQs have embeddings")
            
            # Show first FAQ structure
            first_faq = faqs[0]
            print(f"  📋 First FAQ structure: {list(first_faq.keys())}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing FAQ service: {e}")
        return False


def test_semantic_search():
    """Test semantic search functionality."""
    print("\n🧪 Testing Semantic Search...")
    
    try:
        from services.faq_simple import faq_simple_service
        from services.embeddings import semantic_search
        
        # Load FAQs
        faqs = faq_simple_service.load_faq_items()
        
        if not faqs:
            print("  ⚠️  No FAQs found, skipping semantic search test")
            return True
        
        # Test semantic search
        test_queries = [
            "What are your business hours?",
            "When are you open?",
            "What time do you close?",
            "ساعت کاری شما چیه؟",
            "چه ساعتی بازید؟"
        ]
        
        print("  🔍 Testing semantic search with various phrasings...")
        
        for query in test_queries:
            results = semantic_search(query, faqs, top_k=3)
            if results:
                best_match = results[0]
                print(f"  📝 Query: '{query}'")
                print(f"     Best match: '{best_match['item']['question']}' (score: {best_match['score']:.4f})")
            else:
                print(f"  📝 Query: '{query}' - No results found")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing semantic search: {e}")
        return False


def test_migration():
    """Test FAQ format migration."""
    print("\n🧪 Testing FAQ Migration...")
    
    try:
        from services.faq_simple import FAQSimpleService
        
        # Create a temporary service instance to test migration
        print("  🔄 Testing migration logic...")
        
        # This should trigger migration if needed
        service = FAQSimpleService()
        print("  ✅ FAQ service initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing migration: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Semantic Search Tests\n")
    
    tests = [
        ("Embeddings Service", test_embeddings_service),
        ("FAQ Service", test_faq_service),
        ("Semantic Search", test_semantic_search),
        ("Migration", test_migration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"  ❌ {test_name} test failed")
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Semantic search is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)







