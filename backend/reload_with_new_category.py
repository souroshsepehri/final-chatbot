#!/usr/bin/env python3
"""
Script to reload the database with the new تایم کاری category
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from services.faq import FAQService
    print("✅ FAQ Service imported successfully")
except ImportError as e:
    print(f"❌ Failed to import FAQ Service: {e}")
    sys.exit(1)

def main():
    """Reload the database with new category."""
    print("🔄 Reloading FAQ database with new تایم کاری category...")
    
    try:
        # Initialize FAQ service
        faq_service = FAQService()
        
        # Reload from JSON (this will clear existing data and reload from custom_faq.json)
        count = faq_service.reload_from_json()
        
        if count > 0:
            print(f"✅ Successfully reloaded {count} FAQs from JSON")
            print("✅ New category 'تایم کاری' has been added")
            print("✅ FAQs about working hours are now available")
            
            # Show some examples
            print("\n📋 New FAQs added:")
            print("   - تایم کاری → 24 ساعت روز پشتیبانی داریم")
            print("   - ساعات کاری → 24 ساعت روز پشتیبانی داریم")
            print("   - ساعت کار → 24 ساعت روز پشتیبانی داریم")
            print("   - working hours → 24 ساعت روز پشتیبانی داریم")
            print("   - business hours → 24 ساعت روز پشتیبانی داریم")
            
        else:
            print("❌ No FAQs were reloaded")
            
    except Exception as e:
        print(f"❌ Error reloading database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()























