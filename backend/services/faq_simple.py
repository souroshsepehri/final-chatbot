"""
Simple FAQ service for the new JSON format with embeddings support.
"""

import os
import json
import random
from typing import Optional, Dict, List
from datetime import datetime
import uuid

from .embeddings import get_embedding, ensure_faq_embeddings


class FAQSimpleService:
    """Service to handle FAQ storage and lookups using JSON with embeddings."""
    
    def __init__(self, json_path: str = "data/custom_faq.json"):
        """
        Initialize the FAQ service.
        
        Args:
            json_path (str): Path to the JSON file
        """
        self.json_path = json_path
        self._cache = None
        self._cache_timestamp = None
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        
        # Initialize or migrate the JSON file
        self._init_or_migrate_json()
    
    def _init_or_migrate_json(self) -> None:
        """Initialize JSON file or migrate from old format."""
        if not os.path.exists(self.json_path):
            # Create new file with empty structure
            self._save_faq_items([])
            return
        
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Check if this is the old format (key->value map)
            if "faqs" not in data and isinstance(data, dict):
                # This is the old format, migrate it
                print("Migrating from old FAQ format...")
                self._migrate_old_format(data)
            elif "faqs" in data:
                # This is already the new format
                print("FAQ file is already in new format")
            else:
                # Unknown format, create new
                print("Unknown FAQ format, creating new structure")
                self._save_faq_items([])
                
        except Exception as e:
            print(f"Error reading FAQ file: {e}")
            self._save_faq_items([])
    
    def _migrate_old_format(self, old_data: Dict) -> None:
        """Migrate from old key->value format to new object array format."""
        try:
            new_items = []
            
            for question, answer in old_data.items():
                if isinstance(answer, dict):
                    # Handle case where answer is already an object
                    item = {
                        "id": f"faq-{str(uuid.uuid4())[:8]}",
                        "question": question,
                        "answer": answer.get("answer", str(answer)),
                        "category": answer.get("category", "general"),
                        "embedding": None  # Will be computed later
                    }
                else:
                    # Simple key->value format
                    item = {
                        "id": f"faq-{str(uuid.uuid4())[:8]}",
                        "question": question,
                        "answer": str(answer),
                        "category": "general",
                        "embedding": None  # Will be computed later
                    }
                new_items.append(item)
            
            # Save migrated data
            self._save_faq_items(new_items)
            print(f"Migrated {len(new_items)} FAQs to new format")
            
            # Compute embeddings for migrated items
            ensure_faq_embeddings(new_items, force=True)
            
        except Exception as e:
            print(f"Error during migration: {e}")
            # Fallback to empty structure
            self._save_faq_items([])
    
    def _load_faq_items(self) -> List[Dict]:
        """Load FAQ items from JSON file."""
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("faqs", [])
        except Exception as e:
            print(f"Error loading FAQ items: {e}")
            return []
    
    def _save_faq_items(self, items: List[Dict]) -> None:
        """Save FAQ items to JSON file."""
        try:
            data = {"faqs": items}
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving FAQ items: {e}")
    
    def load_faq_items(self) -> List[Dict]:
        """Load FAQ items in the new object format."""
        return self._load_faq_items()
    
    def save_faq_items(self, items: List[Dict]) -> None:
        """Save FAQ items to JSON file."""
        self._save_faq_items(items)
        self.invalidate_cache()
    
    def upsert_faq(self, question: str, answer: str, id: Optional[str] = None, 
                   with_embedding: bool = True, category: str = "general") -> Dict:
        """
        Upsert a FAQ item.
        
        Args:
            question (str): FAQ question
            answer (str): FAQ answer
            id (Optional[str]): FAQ ID, generated if None
            with_embedding (bool): Whether to compute embedding
            category (str): FAQ category
            
        Returns:
            Dict: Created/updated FAQ item
        """
        items = self._load_faq_items()
        
        # Check if question already exists
        existing_item = None
        for item in items:
            if item.get("question", "").lower() == question.lower():
                existing_item = item
                break
        
        if existing_item:
            # Update existing item
            existing_item["answer"] = answer
            existing_item["category"] = category
            if with_embedding:
                existing_item["embedding"] = get_embedding(question)
            existing_item["updated_at"] = datetime.utcnow().isoformat()
        else:
            # Create new item
            new_item = {
                "id": id or f"faq-{str(uuid.uuid4())[:8]}",
                "question": question,
                "answer": answer,
                "category": category,
                "embedding": get_embedding(question) if with_embedding else None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            items.append(new_item)
            existing_item = new_item
        
        # Save and invalidate cache
        self._save_faq_items(items)
        self.invalidate_cache()
        
        return existing_item
    
    def get_all_faqs(self, category: Optional[str] = None) -> List[Dict]:
        """Get all FAQs, optionally filtered by category."""
        items = self._load_faq_items()
        
        if category:
            items = [item for item in items if item.get("category", "").lower() == category.lower()]
        
        # Sort by latest update
        items.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return items
    
    def search_faq_exact(self, question: str) -> Optional[str]:
        """Search for FAQ answer with exact match (case-insensitive)."""
        items = self._load_faq_items()
        question_lower = question.strip().lower()
        
        for item in items:
            if item.get("question", "").lower() == question_lower:
                return item.get("answer")
        
        return None
    
    def search_faq_partial(self, question: str) -> Optional[str]:
        """Enhanced partial matching with multiple strategies."""
        items = self._load_faq_items()
        q = question.strip().lower()
        
        # Strategy 1: Check if user question contains FAQ question
        for item in items:
            item_question = item.get("question", "").lower()
            if item_question in q:
                return item.get("answer")
        
        # Strategy 2: Check if FAQ question contains user question
        for item in items:
            item_question = item.get("question", "").lower()
            if q in item_question:
                return item.get("answer")
        
        # Strategy 3: Check for word overlap
        words = q.split()
        if len(words) > 1:
            for word in words:
                if len(word) > 2:  # Only check words longer than 2 characters
                    for item in items:
                        item_question = item.get("question", "").lower()
                        if word in item_question:
                            return item.get("answer")
        
        return None
    
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
        
        return random.choice(greetings)
    
    def list_categories(self) -> List[str]:
        """List all FAQ categories."""
        items = self._load_faq_items()
        categories = set(item.get("category", "general") for item in items)
        return sorted(list(categories))
    
    def delete_faq(self, faq_id: str) -> bool:
        """Delete a FAQ by ID."""
        items = self._load_faq_items()
        original_count = len(items)
        
        items = [item for item in items if item.get("id") != faq_id]
        
        if len(items) < original_count:
            self._save_faq_items(items)
            self.invalidate_cache()
            return True
        
        return False
    
    def rebuild_embeddings(self) -> int:
        """Rebuild all FAQ embeddings. Returns count of updated items."""
        items = self._load_faq_items()
        updated_items = ensure_faq_embeddings(items, force=True)
        self.invalidate_cache()
        return len(updated_items)
    
    def invalidate_cache(self) -> None:
        """Invalidate the in-memory cache."""
        self._cache = None
        self._cache_timestamp = None


# Global instance
faq_simple_service = FAQSimpleService()
