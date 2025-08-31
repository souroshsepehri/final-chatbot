#!/usr/bin/env python3
"""
Demo script for semantic search functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def demo_semantic_search():
    """Demonstrate semantic search with various question phrasings."""
    print("🎭 Semantic Search Demo")
    print("=" * 50)
    
    try:
        from services.faq_simple import faq_simple_service
        from services.embeddings import semantic_search
        
        # Load FAQs
        print("📚 Loading FAQ items...")
        faqs = faq_simple_service.load_faq_items()
        
        if not faqs:
            print("❌ No FAQs found. Please add some FAQs first.")
            return
        
        print(f"✅ Loaded {len(faqs)} FAQ items")
        
        # Check embeddings
        faqs_with_embeddings = sum(1 for f in faqs if f.get("embedding") is not None)
        print(f"🔢 {faqs_with_embeddings} FAQs have embeddings")
        
        if faqs_with_embeddings == 0:
            print("⚠️  No FAQs have embeddings. Computing them now...")
            from services.embeddings import ensure_faq_embeddings
            faqs = ensure_faq_embeddings(faqs, force=True)
            print("✅ Embeddings computed!")
        
        # Demo queries for different intents
        demo_queries = [
            # Business hours intent
            ("Business Hours", [
                "What are your business hours?",
                "When are you open?",
                "What time do you close?",
                "ساعت کاری شما چیه؟",
                "چه ساعتی بازید؟",
                "Are you open on weekends?"
            ]),
            
            # Company info intent
            ("Company Info", [
                "What does your company do?",
                "What is your company?",
                "Tell me about your work",
                "What services do you provide?",
                "شرکت شما چه کاری انجام می‌دهد؟",
                "شما چه کاری انجام می‌دهید؟"
            ]),
            
            # Greeting intent
            ("Greeting", [
                "Hello",
                "Hi there",
                "سلام",
                "درود",
                "Good morning",
                "شروع"
            ])
        ]
        
        print("\n🔍 Testing Semantic Search...")
        print("-" * 50)
        
        for intent, queries in demo_queries:
            print(f"\n📋 Intent: {intent}")
            print("-" * 30)
            
            for query in queries:
                print(f"\n❓ Query: '{query}'")
                
                # Perform semantic search
                results = semantic_search(query, faqs, top_k=3)
                
                if results:
                    best_match = results[0]
                    score = best_match["score"]
                    matched_question = best_match["item"]["question"]
                    answer = best_match["item"]["answer"]
                    
                    print(f"   🎯 Best match: '{matched_question}'")
                    print(f"   📊 Similarity score: {score:.4f}")
                    print(f"   💬 Answer: {answer[:100]}{'...' if len(answer) > 100 else ''}")
                    
                    # Show if this would be returned by the chat system
                    threshold = float(os.getenv("SEMANTIC_THRESHOLD", "0.82"))
                    if score >= threshold:
                        print(f"   ✅ Would be returned (score ≥ {threshold})")
                    else:
                        print(f"   ⚠️  Below threshold (score < {threshold})")
                else:
                    print("   ❌ No results found")
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


def demo_add_faq():
    """Demonstrate adding a new FAQ with automatic embedding."""
    print("\n📝 Adding New FAQ Demo")
    print("=" * 50)
    
    try:
        from services.faq_simple import faq_simple_service
        
        # Add a new FAQ
        question = "What is your return policy?"
        answer = "We offer a 30-day return policy for all products. Contact our support team to initiate a return."
        category = "policies"
        
        print(f"❓ Question: {question}")
        print(f"💬 Answer: {answer}")
        print(f"🏷️  Category: {category}")
        
        # Add the FAQ
        new_faq = faq_simple_service.upsert_faq(
            question=question,
            answer=answer,
            category=category,
            with_embedding=True
        )
        
        print(f"✅ FAQ added with ID: {new_faq['id']}")
        print(f"🔢 Embedding computed: {'Yes' if new_faq.get('embedding') else 'No'}")
        
        # Test semantic search with variations
        print("\n🔍 Testing with variations...")
        variations = [
            "What's your return policy?",
            "Can I return items?",
            "How do returns work?",
            "Return policy details"
        ]
        
        faqs = faq_simple_service.load_faq_items()
        
        for variation in variations:
            print(f"\n❓ Variation: '{variation}'")
            results = semantic_search(variation, faqs, top_k=1)
            
            if results:
                score = results[0]["score"]
                print(f"   📊 Similarity score: {score:.4f}")
                
                threshold = float(os.getenv("SEMANTIC_THRESHOLD", "0.82"))
                if score >= threshold:
                    print(f"   ✅ Would match (score ≥ {threshold})")
                else:
                    print(f"   ⚠️  Below threshold (score < {threshold})")
            else:
                print("   ❌ No results found")
        
    except Exception as e:
        print(f"❌ Error during FAQ demo: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run the demo."""
    print("🚀 Semantic Search Demo")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ Please set your OpenAI API key in the .env file")
        print("   Copy config.env.example to .env and add your actual API key")
        return
    
    print("✅ OpenAI API key configured")
    
    # Run demos
    demo_semantic_search()
    demo_add_faq()
    
    print("\n" + "=" * 50)
    print("🎭 Demo completed! Check the output above to see semantic search in action.")
    print("\n💡 Tips:")
    print("   - Adjust SEMANTIC_THRESHOLD in .env to fine-tune matching")
    print("   - Use /chat/faqs/rebuild-embeddings to update all embeddings")
    print("   - Check /chat/stats to see embedding status")


if __name__ == "__main__":
    main()







