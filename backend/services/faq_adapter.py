"""
FAQ Adapter service with pluggable backends for different data sources.
"""

import os
import json
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union
from datetime import datetime
import uuid

from .faq_simple import FAQSimpleService


class BaseFAQBackend(ABC):
    """Abstract base class for FAQ backends."""
    
    @abstractmethod
    def get_all(self) -> List[Dict]:
        """
        Get all FAQ items.
        
        Returns:
            List[Dict]: List of FAQ items with structure:
                {id, question, answer, embedding?, category?, created_at?, updated_at?}
        """
        pass
    
    @abstractmethod
    def upsert(self, question: str, answer: str, id: Optional[str] = None, 
               category: str = "general", embedding: Optional[List[float]] = None) -> Dict:
        """
        Upsert a FAQ item.
        
        Args:
            question (str): FAQ question
            answer (str): FAQ answer
            id (Optional[str]): FAQ ID, generated if None
            category (str): FAQ category
            embedding (Optional[List[float]]): Pre-computed embedding
            
        Returns:
            Dict: Created/updated FAQ item
        """
        pass
    
    @abstractmethod
    def bulk_upsert(self, items: List[Dict]) -> int:
        """
        Bulk upsert FAQ items.
        
        Args:
            items (List[Dict]): List of FAQ items to upsert
            
        Returns:
            int: Number of items successfully upserted
        """
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """
        Delete a FAQ item by ID.
        
        Args:
            id (str): FAQ ID to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        pass
    
    def normalize_item(self, item: Dict) -> Dict:
        """
        Normalize FAQ item to standard format.
        
        Args:
            item (Dict): Raw FAQ item from backend
            
        Returns:
            Dict: Normalized FAQ item
        """
        normalized = {
            "id": item.get("id", f"faq-{str(uuid.uuid4())[:8]}"),
            "question": str(item.get("question", "")).strip(),
            "answer": str(item.get("answer", "")).strip(),
            "category": str(item.get("category", "general")).strip(),
            "embedding": item.get("embedding"),
            "created_at": item.get("created_at", datetime.utcnow().isoformat()),
            "updated_at": item.get("updated_at", datetime.utcnow().isoformat())
        }
        
        # Ensure required fields are not empty
        if not normalized["question"] or not normalized["answer"]:
            raise ValueError("Question and answer cannot be empty")
        
        return normalized


class JSONFAQBackend(BaseFAQBackend):
    """JSON file-based FAQ backend (wraps existing FAQSimpleService)."""
    
    def __init__(self, json_path: str = "data/custom_faq.json"):
        """Initialize JSON backend."""
        self.faq_service = FAQSimpleService(json_path)
    
    def get_all(self) -> List[Dict]:
        """Get all FAQ items from JSON file."""
        try:
            items = self.faq_service.load_faq_items()
            return [self.normalize_item(item) for item in items]
        except Exception as e:
            print(f"Error loading FAQs from JSON: {e}")
            return []
    
    def upsert(self, question: str, answer: str, id: Optional[str] = None,
               category: str = "general", embedding: Optional[List[float]] = None) -> Dict:
        """Upsert FAQ item to JSON file."""
        try:
            # Use the existing service's upsert method
            result = self.faq_service.upsert_faq(
                question=question,
                answer=answer,
                id=id,
                category=category,
                with_embedding=embedding is None  # Only compute if not provided
            )
            
            # If embedding was provided, update it
            if embedding is not None and result:
                result["embedding"] = embedding
                # Save the updated item
                items = self.faq_service.load_faq_items()
                for item in items:
                    if item.get("id") == result["id"]:
                        item["embedding"] = embedding
                        break
                self.faq_service.save_faq_items(items)
            
            return self.normalize_item(result) if result else {}
            
        except Exception as e:
            print(f"Error upserting FAQ to JSON: {e}")
            return {}
    
    def bulk_upsert(self, items: List[Dict]) -> int:
        """Bulk upsert FAQ items to JSON file."""
        try:
            count = 0
            for item in items:
                result = self.upsert(
                    question=item["question"],
                    answer=item["answer"],
                    id=item.get("id"),
                    category=item.get("category", "general"),
                    embedding=item.get("embedding")
                )
                if result:
                    count += 1
            return count
        except Exception as e:
            print(f"Error bulk upserting FAQs to JSON: {e}")
            return 0
    
    def delete(self, id: str) -> bool:
        """Delete FAQ item from JSON file."""
        try:
            return self.faq_service.delete_faq(id)
        except Exception as e:
            print(f"Error deleting FAQ from JSON: {e}")
            return False


class APIFAQBackend(BaseFAQBackend):
    """REST API-based FAQ backend."""
    
    def __init__(self):
        """Initialize API backend."""
        self.base_url = os.getenv("FAQ_API_BASE")
        self.api_key = os.getenv("FAQ_API_KEY")
        
        if not self.base_url:
            raise ValueError("FAQ_API_BASE environment variable is required for API backend")
        
        # Ensure base URL doesn't end with slash
        self.base_url = self.base_url.rstrip("/")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to FAQ API."""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {}
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except Exception as e:
            print(f"Error making API request: {e}")
            return None
    
    def get_all(self) -> List[Dict]:
        """Get all FAQ items from API."""
        try:
            response = self._make_request("GET", "/faqs")
            if response and isinstance(response, list):
                return [self.normalize_item(item) for item in response]
            elif response and "faqs" in response:
                return [self.normalize_item(item) for item in response["faqs"]]
            else:
                print(f"Unexpected API response format: {response}")
                return []
        except Exception as e:
            print(f"Error getting FAQs from API: {e}")
            return []
    
    def upsert(self, question: str, answer: str, id: Optional[str] = None,
               category: str = "general", embedding: Optional[List[float]] = None) -> Dict:
        """Upsert FAQ item via API."""
        try:
            data = {
                "question": question,
                "answer": answer,
                "category": category
            }
            
            if embedding is not None:
                data["embedding"] = embedding
            
            if id:
                # Update existing item
                response = self._make_request("PUT", f"/faqs/{id}", data)
            else:
                # Create new item
                response = self._make_request("POST", "/faqs", data)
            
            if response:
                return self.normalize_item(response)
            else:
                return {}
                
        except Exception as e:
            print(f"Error upserting FAQ via API: {e}")
            return {}
    
    def bulk_upsert(self, items: List[Dict]) -> int:
        """Bulk upsert FAQ items via API."""
        try:
            # Check if API supports bulk operations
            bulk_endpoint = "/faqs/bulk"
            
            # Try bulk endpoint first
            response = self._make_request("POST", bulk_endpoint, {"faqs": items})
            if response:
                return len(items)
            
            # Fallback to individual upserts
            count = 0
            for item in items:
                result = self.upsert(
                    question=item["question"],
                    answer=item["answer"],
                    id=item.get("id"),
                    category=item.get("category", "general"),
                    embedding=item.get("embedding")
                )
                if result:
                    count += 1
            
            return count
            
        except Exception as e:
            print(f"Error bulk upserting FAQs via API: {e}")
            return 0
    
    def delete(self, id: str) -> bool:
        """Delete FAQ item via API."""
        try:
            response = self._make_request("DELETE", f"/faqs/{id}")
            return response is not None
        except Exception as e:
            print(f"Error deleting FAQ via API: {e}")
            return False


class DBFAQBackend(BaseFAQBackend):
    """Database-based FAQ backend (skeleton for future implementation)."""
    
    def __init__(self):
        """Initialize database backend."""
        self.database_url = os.getenv("DATABASE_URL")
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required for database backend")
        
        # TODO: Implement with SQLAlchemy
        # For now, this is a placeholder that will raise NotImplementedError
        print("⚠️  Database backend is not yet implemented. Use JSON or API backend instead.")
    
    def get_all(self) -> List[Dict]:
        """Get all FAQ items from database."""
        # TODO: Implement with SQLAlchemy
        raise NotImplementedError("Database backend not yet implemented")
    
    def upsert(self, question: str, answer: str, id: Optional[str] = None,
               category: str = "general", embedding: Optional[List[float]] = None) -> Dict:
        """Upsert FAQ item to database."""
        # TODO: Implement with SQLAlchemy
        raise NotImplementedError("Database backend not yet implemented")
    
    def bulk_upsert(self, items: List[Dict]) -> int:
        """Bulk upsert FAQ items to database."""
        # TODO: Implement with SQLAlchemy
        raise NotImplementedError("Database backend not yet implemented")
    
    def delete(self, id: str) -> bool:
        """Delete FAQ item from database."""
        # TODO: Implement with SQLAlchemy
        raise NotImplementedError("Database backend not yet implemented")


def get_faq_backend() -> BaseFAQBackend:
    """
    Factory function to get the appropriate FAQ backend based on environment.
    
    Returns:
        BaseFAQBackend: Configured FAQ backend instance
        
    Raises:
        ValueError: If backend configuration is invalid
    """
    mode = os.getenv("FAQ_BACKEND", "json").lower()
    
    try:
        if mode == "json":
            return JSONFAQBackend()
        elif mode == "api":
            return APIFAQBackend()
        elif mode == "db":
            return DBFAQBackend()
        else:
            print(f"⚠️  Unknown FAQ_BACKEND mode: {mode}. Falling back to JSON.")
            return JSONFAQBackend()
    except Exception as e:
        print(f"❌ Error initializing {mode} backend: {e}")
        print("🔄 Falling back to JSON backend...")
        return JSONFAQBackend()


# Convenience functions for external use
def get_all_faqs() -> List[Dict]:
    """Get all FAQ items from the configured backend."""
    backend = get_faq_backend()
    return backend.get_all()


def upsert_faq(question: str, answer: str, id: Optional[str] = None,
               category: str = "general", embedding: Optional[List[float]] = None) -> Dict:
    """Upsert a FAQ item via the configured backend."""
    backend = get_faq_backend()
    return backend.upsert(question, answer, id, category, embedding)


def bulk_upsert_faqs(items: List[Dict]) -> int:
    """Bulk upsert FAQ items via the configured backend."""
    backend = get_faq_backend()
    return backend.bulk_upsert(items)


def delete_faq(id: str) -> bool:
    """Delete a FAQ item via the configured backend."""
    backend = get_faq_backend()
    return backend.delete(id)

































