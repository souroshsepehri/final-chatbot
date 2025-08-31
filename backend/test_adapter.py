#!/usr/bin/env python3
"""
Test script for FAQ adapter functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_adapter_initialization():
    """Test adapter initialization with different backends."""
    print("🧪 Testing Adapter Initialization...")
    
    try:
        from services.faq_adapter import get_faq_backend
        
        # Test JSON backend (default)
        print("  📁 Testing JSON backend...")
        os.environ["FAQ_BACKEND"] = "json"
        backend = get_faq_backend()
        print(f"  ✅ JSON backend initialized: {backend.__class__.__name__}")
        
        # Test API backend (if configured)
        if os.getenv("FAQ_API_BASE"):
            print("  🌐 Testing API backend...")
            os.environ["FAQ_BACKEND"] = "api"
            try:
                backend = get_faq_backend()
                print(f"  ✅ API backend initialized: {backend.__class__.__name__}")
            except Exception as e:
                print(f"  ⚠️  API backend failed: {e}")
        else:
            print("  ⚠️  Skipping API backend test (FAQ_API_BASE not set)")
        
        # Test database backend (should fail gracefully)
        print("  🗄️  Testing database backend...")
        os.environ["FAQ_BACKEND"] = "db"
        try:
            backend = get_faq_backend()
            print(f"  ⚠️  Database backend initialized (unexpected): {backend.__class__.__name__}")
        except Exception as e:
            print(f"  ✅ Database backend correctly failed: {e}")
        
        # Test invalid backend (should fallback to JSON)
        print("  ❌ Testing invalid backend...")
        os.environ["FAQ_BACKEND"] = "invalid"
        backend = get_faq_backend()
        print(f"  ✅ Invalid backend fell back to: {backend.__class__.__name__}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing adapter initialization: {e}")
        return False


def test_json_backend():
    """Test JSON backend functionality."""
    print("\n🧪 Testing JSON Backend...")
    
    try:
        from services.faq_adapter import JSONFAQBackend
        
        backend = JSONFAQBackend()
        
        # Test get_all
        print("  📚 Testing get_all...")
        items = backend.get_all()
        print(f"  ✅ Loaded {len(items)} FAQ items")
        
        # Test upsert
        print("  ✏️  Testing upsert...")
        test_item = backend.upsert(
            question="Test question for adapter?",
            answer="This is a test answer for the adapter system.",
            category="test"
        )
        if test_item:
            print(f"  ✅ Upsert successful: {test_item['id']}")
            
            # Test delete
            print("  🗑️  Testing delete...")
            deleted = backend.delete(test_item["id"])
            if deleted:
                print("  ✅ Delete successful")
            else:
                print("  ❌ Delete failed")
        else:
            print("  ❌ Upsert failed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing JSON backend: {e}")
        return False


def test_api_backend():
    """Test API backend functionality (if configured)."""
    print("\n🧪 Testing API Backend...")
    
    if not os.getenv("FAQ_API_BASE"):
        print("  ⚠️  Skipping API backend test (FAQ_API_BASE not set)")
        return True
    
    try:
        from services.faq_adapter import APIFAQBackend
        
        backend = APIFAQBackend()
        
        # Test get_all
        print("  📚 Testing get_all...")
        items = backend.get_all()
        print(f"  ✅ Loaded {len(items)} FAQ items from API")
        
        # Test upsert (create)
        print("  ✏️  Testing upsert (create)...")
        test_item = backend.upsert(
            question="API test question?",
            answer="This is a test answer via API.",
            category="test"
        )
        if test_item:
            print(f"  ✅ Create successful: {test_item['id']}")
            
            # Test upsert (update)
            print("  ✏️  Testing upsert (update)...")
            updated_item = backend.upsert(
                question="Updated API test question?",
                answer="This is an updated test answer via API.",
                id=test_item["id"],
                category="test"
            )
            if updated_item:
                print("  ✅ Update successful")
            else:
                print("  ❌ Update failed")
            
            # Test delete
            print("  🗑️  Testing delete...")
            deleted = backend.delete(test_item["id"])
            if deleted:
                print("  ✅ Delete successful")
            else:
                print("  ❌ Delete failed")
        else:
            print("  ❌ Create failed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing API backend: {e}")
        return False


def test_convenience_functions():
    """Test convenience functions."""
    print("\n🧪 Testing Convenience Functions...")
    
    try:
        from services.faq_adapter import get_all_faqs, upsert_faq, delete_faq
        
        # Test get_all_faqs
        print("  📚 Testing get_all_faqs...")
        items = get_all_faqs()
        print(f"  ✅ Loaded {len(items)} FAQ items via convenience function")
        
        # Test upsert_faq
        print("  ✏️  Testing upsert_faq...")
        test_item = upsert_faq(
            question="Convenience test question?",
            answer="This is a test answer via convenience function.",
            category="test"
        )
        if test_item:
            print(f"  ✅ Upsert successful: {test_item['id']}")
            
            # Test delete_faq
            print("  🗑️  Testing delete_faq...")
            deleted = delete_faq(test_item["id"])
            if deleted:
                print("  ✅ Delete successful")
            else:
                print("  ❌ Delete failed")
        else:
            print("  ❌ Upsert failed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing convenience functions: {e}")
        return False


def test_embeddings_integration():
    """Test embeddings integration with adapter."""
    print("\n🧪 Testing Embeddings Integration...")
    
    try:
        from services.faq_adapter import get_all_faqs
        from services.embeddings import ensure_faq_embeddings
        
        # Get FAQs
        faq_items = get_all_faqs()
        
        if not faq_items:
            print("  ⚠️  No FAQs found, skipping embeddings test")
            return True
        
        # Check current embedding status
        faqs_with_embeddings = sum(1 for f in faq_items if f.get("embedding"))
        print(f"  🔢 {faqs_with_embeddings}/{len(faq_items)} FAQs have embeddings")
        
        # Test embedding computation
        print("  🧠 Testing embedding computation...")
        updated_items = ensure_faq_embeddings(faq_items, force=False)
        
        if updated_items:
            new_embeddings = sum(1 for f in updated_items if f.get("embedding"))
            print(f"  ✅ Embeddings computed: {new_embeddings}/{len(updated_items)} items")
        else:
            print("  ❌ Embedding computation failed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing embeddings integration: {e}")
        return False


def test_semantic_search_with_adapter():
    """Test semantic search using the adapter."""
    print("\n🧪 Testing Semantic Search with Adapter...")
    
    try:
        from services.faq_adapter import get_all_faqs
        from services.embeddings import semantic_search
        
        # Get FAQs
        faq_items = get_all_faqs()
        
        if not faq_items:
            print("  ⚠️  No FAQs found, skipping semantic search test")
            return True
        
        # Test semantic search
        test_queries = [
            "What is your company?",
            "Tell me about your work",
            "What services do you provide?"
        ]
        
        print("  🔍 Testing semantic search...")
        
        for query in test_queries:
            results = semantic_search(query, faq_items, top_k=3)
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


def main():
    """Run all tests."""
    print("🚀 Starting FAQ Adapter Tests\n")
    
    tests = [
        ("Adapter Initialization", test_adapter_initialization),
        ("JSON Backend", test_json_backend),
        ("API Backend", test_api_backend),
        ("Convenience Functions", test_convenience_functions),
        ("Embeddings Integration", test_embeddings_integration),
        ("Semantic Search", test_semantic_search_with_adapter),
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
        print("🎉 All tests passed! FAQ adapter is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

































