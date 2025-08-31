#!/usr/bin/env python3
"""
Test company questions to make sure they work.
"""

def test_company_questions():
    """Test if company questions return the correct answer."""
    print("🧪 Testing Company Questions...")
    
    try:
        from services.faq import FAQService
        faq_service = FAQService()
        
        # Test questions
        test_cases = [
            ("What do you do?", "ما یک شرکت اتوماسیون هوش مصنوعی هستیم"),
            ("What is your company?", "ما یک شرکت اتوماسیون هوش مصنوعی هستیم"),
            ("شرکت شما چه کاری انجام می‌دهد؟", "ما یک شرکت اتوماسیون هوش مصنوعی هستیم"),
            ("شما چه کاری انجام می‌دهید؟", "ما یک شرکت اتوماسیون هوش مصنوعی هستیم")
        ]
        
        all_passed = True
        
        for question, expected_answer in test_cases:
            print(f"\nQ: {question}")
            answer = faq_service.search_faq(question)
            
            if answer:
                print(f"A: {answer}")
                if answer == expected_answer:
                    print("✅ Correct answer!")
                else:
                    print("❌ Wrong answer!")
                    all_passed = False
            else:
                print("❌ No answer found!")
                all_passed = False
        
        if all_passed:
            print("\n🎉 All company questions are working correctly!")
        else:
            print("\n❌ Some company questions are not working.")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_company_questions()

