"""
Embeddings service for semantic question matching using OpenAI embeddings.
"""

import os
import json
import hashlib
import time
from typing import List, Dict, Optional
import numpy as np
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmbeddingsService:
    """Service for handling embeddings and semantic search."""
    
    def __init__(self):
        """Initialize the embeddings service."""
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")  # Use older model for compatibility
        self.embedding_dimension = 1536  # Default for text-embedding-ada-002
        
        # Performance optimization: Cache embeddings
        self._embedding_cache = {}
        self._cache_timestamp = {}
        self._cache_ttl = 3600  # 1 hour cache TTL
        
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached embedding is still valid."""
        if cache_key not in self._cache_timestamp:
            return False
        return (time.time() - self._cache_timestamp[cache_key]) < self._cache_ttl
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a text using OpenAI API with caching.
        
        Args:
            text (str): Text to embed
            
        Returns:
            List[float]: 1536-dimensional embedding vector
        """
        if not text.strip():
            return [0.0] * self.embedding_dimension
        
        # Check cache first
        cache_key = self._get_cache_key(text)
        if cache_key in self._embedding_cache and self._is_cache_valid(cache_key):
            return self._embedding_cache[cache_key]
        
        try:
            response = openai.Embedding.create(
                model=self.model,
                input=text
            )
            embedding = response['data'][0]['embedding']
            
            # Cache the result
            self._embedding_cache[cache_key] = embedding
            self._cache_timestamp[cache_key] = time.time()
            
            return embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dimension
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts in a single API call (batch processing).
        
        Args:
            texts (List[str]): List of texts to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter out empty texts and check cache
        valid_texts = []
        cached_embeddings = []
        cache_keys = []
        
        for text in texts:
            if text.strip():
                cache_key = self._get_cache_key(text)
                cache_keys.append(cache_key)
                
                if cache_key in self._embedding_cache and self._is_cache_valid(cache_key):
                    cached_embeddings.append(self._embedding_cache[cache_key])
                else:
                    valid_texts.append(text)
                    cached_embeddings.append(None)  # Placeholder
            else:
                cached_embeddings.append([0.0] * self.embedding_dimension)
        
        # Get embeddings for uncached texts
        if valid_texts:
            try:
                response = openai.Embedding.create(
                    model=self.model,
                    input=valid_texts
                )
                
                # Update cache and results
                valid_idx = 0
                for i, cache_key in enumerate(cache_keys):
                    if cached_embeddings[i] is None:  # Wasn't cached
                        embedding = response['data'][valid_idx]['embedding']
                        cached_embeddings[i] = embedding
                        self._embedding_cache[cache_key] = embedding
                        self._cache_timestamp[cache_key] = time.time()
                        valid_idx += 1
                        
            except Exception as e:
                print(f"Error getting batch embeddings: {e}")
                # Fill missing embeddings with zero vectors
                for i, embedding in enumerate(cached_embeddings):
                    if embedding is None:
                        cached_embeddings[i] = [0.0] * self.embedding_dimension
        
        return cached_embeddings
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            a (List[float]): First vector
            b (List[float]): Second vector
            
        Returns:
            float: Cosine similarity score between 0 and 1
        """
        try:
            a_array = np.array(a)
            b_array = np.array(b)
            
            # Normalize vectors
            a_norm = np.linalg.norm(a_array)
            b_norm = np.linalg.norm(b_array)
            
            if a_norm == 0 or b_norm == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(a_array, b_array) / (a_norm * b_norm)
            return float(similarity)
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def ensure_faq_embeddings(self, faq_items: List[Dict], force: bool = False) -> List[Dict]:
        """
        Ensure all FAQ items have embeddings. Compute missing ones and persist via adapter.
        Uses batch processing for better performance.
        
        Args:
            faq_items (List[Dict]): List of FAQ items
            force (bool): Force recomputation of all embeddings
            
        Returns:
            List[Dict]: Updated FAQ items with embeddings
        """
        if not faq_items:
            return []
        
        # Identify items needing embeddings
        items_needing_embeddings = []
        items_with_embeddings = []
        
        for item in faq_items:
            if force or "embedding" not in item or item["embedding"] is None:
                items_needing_embeddings.append(item)
            else:
                items_with_embeddings.append(item)
        
        # Batch process embeddings for items that need them
        if items_needing_embeddings:
            print(f"Computing embeddings for {len(items_needing_embeddings)} items...")
            
            # Extract questions for batch processing
            questions = [item.get("question", "") for item in items_needing_embeddings]
            
            # Get embeddings in batch
            embeddings = self.get_embeddings_batch(questions)
            
            # Update items with embeddings
            for item, embedding in zip(items_needing_embeddings, embeddings):
                item["embedding"] = embedding
        
        # Combine all items
        updated_items = items_with_embeddings + items_needing_embeddings
        
        # Persist back via adapter instead of direct file access
        self._persist_faq_items_via_adapter(updated_items)
        
        return updated_items
    
    def semantic_search(self, query: str, faq_items: List[Dict], top_k: int = 3) -> List[Dict]:
        """
        Perform semantic search on FAQ items.
        
        Args:
            query (str): User query
            faq_items (List[Dict]): List of FAQ items with embeddings
            top_k (int): Number of top results to return
            
        Returns:
            List[Dict]: Top k items with scores, sorted by similarity
        """
        if not faq_items:
            return []
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        
        # Calculate similarities
        scored_items = []
        for item in faq_items:
            if "embedding" in item and item["embedding"]:
                score = self.cosine_similarity(query_embedding, item["embedding"])
                scored_items.append({
                    "item": item,
                    "score": score
                })
        
        # Sort by score (descending) and return top_k
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        return scored_items[:top_k]
    
    def _persist_faq_items_via_adapter(self, items: List[Dict]) -> None:
        """
        Persist FAQ items with embeddings via the FAQ adapter.
        
        Args:
            items (List[Dict]): FAQ items to persist
        """
        try:
            # Import here to avoid circular imports
            from .faq_adapter import bulk_upsert_faqs
            
            count = bulk_upsert_faqs(items)
            print(f"Persisted {count} FAQ items with embeddings via adapter")
            
        except Exception as e:
            print(f"Error persisting FAQ items via adapter: {e}")
            # Fallback to direct file persistence for backward compatibility
            self._persist_faq_items_direct(items)
    
    def _persist_faq_items_direct(self, items: List[Dict]) -> None:
        """
        Fallback method for direct file persistence (backward compatibility).
        
        Args:
            items (List[Dict]): FAQ items to persist
        """
        try:
            json_path = "data/custom_faq.json"
            
            # Load existing structure if it exists
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"faqs": []}
            
            # Update the faqs array
            data["faqs"] = items
            
            # Write back to file
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"Persisted {len(items)} FAQ items with embeddings (direct file)")
            
        except Exception as e:
            print(f"Error persisting FAQ items directly: {e}")


# Global instance
embeddings_service = EmbeddingsService()


# Convenience functions for external use
def get_embedding(text: str) -> List[float]:
    """Get embedding for text."""
    return embeddings_service.get_embedding(text)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    return embeddings_service.cosine_similarity(a, b)


def ensure_faq_embeddings(faq_items: List[Dict], force: bool = False) -> List[Dict]:
    """Ensure all FAQ items have embeddings."""
    return embeddings_service.ensure_faq_embeddings(faq_items, force)


def semantic_search(query: str, faq_items: List[Dict], top_k: int = 3) -> List[Dict]:
    """Perform semantic search on FAQ items."""
    return embeddings_service.semantic_search(query, faq_items, top_k)


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Get embeddings for multiple texts in batch."""
    return embeddings_service.get_embeddings_batch(texts)
