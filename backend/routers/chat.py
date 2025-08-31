"""
Chat router with the /chat endpoint.
"""

import os
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from dotenv import load_dotenv
import time

from services.faq_adapter import get_faq_backend, get_all_faqs, upsert_faq, bulk_upsert_faqs
from services.gpt import GPTService
from services.fallback import FallbackService
from services.embeddings import semantic_search, ensure_faq_embeddings
from utils.response_check import is_vague_response
from utils.performance import get_performance_summary

# Load environment variables
load_dotenv()

# Initialize services
gpt_service = GPTService()
fallback_service = FallbackService()

# Configuration from environment
SEMANTIC_TOP_K = int(os.getenv("SEMANTIC_TOP_K", "3"))
SEMANTIC_THRESHOLD = float(os.getenv("SEMANTIC_THRESHOLD", "0.82"))

# Performance optimization: Cache FAQ items
_faq_cache = None
_faq_cache_timestamp = 0
CACHE_TTL = 300  # 5 minutes cache TTL

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    source: str  # "greeting", "faq", "faq_semantic", "gpt", or "fallback"
    metadata: Optional[Dict] = None
    response_time_ms: Optional[int] = None


class FAQRequest(BaseModel):
    """Request model for FAQ operations."""
    question: str
    answer: str
    category: Optional[str] = "general"
    id: Optional[str] = None


def _get_cached_faqs() -> List[Dict]:
    """Get FAQ items with caching for performance."""
    global _faq_cache, _faq_cache_timestamp
    
    current_time = time.time()
    
    # Return cached data if still valid
    if _faq_cache is not None and (current_time - _faq_cache_timestamp) < CACHE_TTL:
        return _faq_cache
    
    # Load fresh data and cache it
    try:
        _faq_cache = get_all_faqs()
        _faq_cache_timestamp = current_time
        return _faq_cache
    except Exception as e:
        print(f"Error loading FAQs: {e}")
        return []


def _clear_faq_cache():
    """Clear the FAQ cache (call when FAQs are updated)."""
    global _faq_cache, _faq_cache_timestamp
    _faq_cache = None
    _faq_cache_timestamp = 0


async def _process_greeting(message: str) -> Optional[ChatResponse]:
    """Process greeting messages asynchronously."""
    if _is_greeting(message):
        greeting_response = _get_greeting_response()
        return ChatResponse(response=greeting_response, source="greeting")
    return None


async def _process_semantic_search(message: str, faq_items: List[Dict]) -> Optional[ChatResponse]:
    """Process semantic search asynchronously."""
    if not faq_items:
        return None
    
    # Get event loop once at the beginning
    loop = asyncio.get_event_loop()
    
    # Check if any items are missing embeddings and compute them if needed
    items_missing_embeddings = [item for item in faq_items if not item.get("embedding")]
    if items_missing_embeddings:
        print(f"Computing embeddings for {len(items_missing_embeddings)} items...")
        # Run embedding computation in thread pool to avoid blocking
        updated_items = await loop.run_in_executor(
            None, ensure_faq_embeddings, faq_items, False
        )
        faq_items = updated_items
    
    # Try semantic search
    semantic_results = await loop.run_in_executor(
        None, semantic_search, message, faq_items, SEMANTIC_TOP_K
    )
    
    if semantic_results and semantic_results[0]["score"] >= SEMANTIC_THRESHOLD:
        best_match = semantic_results[0]
        return ChatResponse(
            response=best_match["item"]["answer"],
            source="faq_semantic",
            metadata={
                "score": best_match["score"],
                "matched_question": best_match["item"]["question"]
            }
        )
    
    return None


async def _process_exact_match(message: str, faq_items: List[Dict]) -> Optional[ChatResponse]:
    """Process exact and partial matching asynchronously."""
    # Try exact match
    faq_answer = _search_faq_exact(message, faq_items)
    if faq_answer:
        return ChatResponse(response=faq_answer, source="faq")
    
    # Try partial match
    faq_answer = _search_faq_partial(message, faq_items)
    if faq_answer:
        return ChatResponse(response=faq_answer, source="faq")
    
    return None


async def _process_gpt_with_context(message: str, semantic_results: List[Dict]) -> Optional[ChatResponse]:
    """Process GPT response with context asynchronously."""
    loop = asyncio.get_event_loop()
    
    if semantic_results:
        # Create context from top FAQ candidates for RAG-lite
        context_prompt = "If any of the provided FAQs answer the user, use them verbatim; otherwise answer normally.\n\nRelevant FAQs:\n"
        for result in semantic_results[:3]:  # Top 3 candidates
            context_prompt += f"Q: {result['item']['question']}\nA: {result['item']['answer']}\n\n"
        
        # Add user question
        context_prompt += f"User question: {message}"
        
        gpt_response = await loop.run_in_executor(
            None, gpt_service.get_response, context_prompt
        )
    else:
        # No semantic results, use original message
        gpt_response = await loop.run_in_executor(
            None, gpt_service.get_response, message
        )
    
    if not gpt_response:
        # If GPT service fails, return fallback
        fallback_response = fallback_service.get_fallback_response(message)
        return ChatResponse(response=fallback_response, source="fallback")
    
    # Check if GPT response is vague
    if is_vague_response(gpt_response):
        # If vague, return fallback response
        fallback_response = fallback_service.get_fallback_response(message)
        return ChatResponse(response=fallback_response, source="fallback")
    
    # Return GPT's answer if not vague
    return ChatResponse(response=gpt_response, source="gpt")


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Optimized chat endpoint that processes user messages with improved performance:
    1. Uses caching for FAQ data
    2. Processes steps concurrently where possible
    3. Reduces API calls through better flow control
    4. Provides response time metrics
    """
    start_time = time.time()
    
    try:
        message = request.message.strip()
        
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get cached FAQ items
        faq_items = _get_cached_faqs()
        
        # Step 1: Check if message is a greeting (fast local check)
        greeting_response = await _process_greeting(message)
        if greeting_response:
            response_time = int((time.time() - start_time) * 1000)
            greeting_response.response_time_ms = response_time
            return greeting_response
        
        # Step 2: Try semantic search (most expensive operation)
        semantic_response = await _process_semantic_search(message, faq_items)
        if semantic_response:
            response_time = int((time.time() - start_time) * 1000)
            semantic_response.response_time_ms = response_time
            return semantic_response
        
        # Step 3: Try exact/partial match (fast local check)
        exact_match_response = await _process_exact_match(message, faq_items)
        if exact_match_response:
            response_time = int((time.time() - start_time) * 1000)
            exact_match_response.response_time_ms = response_time
            return exact_match_response
        
        # Step 4: If not found in FAQ, send to GPT-4 with context
        # Get semantic results for context (without threshold check)
        semantic_results = []
        if faq_items:
            loop = asyncio.get_event_loop()
            semantic_results = await loop.run_in_executor(
                None, semantic_search, message, faq_items, SEMANTIC_TOP_K
            )
        
        gpt_response = await _process_gpt_with_context(message, semantic_results)
        if gpt_response:
            response_time = int((time.time() - start_time) * 1000)
            gpt_response.response_time_ms = response_time
            return gpt_response
        
        # Fallback if all else fails
        fallback_response = fallback_service.get_fallback_response(message)
        response_time = int((time.time() - start_time) * 1000)
        return ChatResponse(
            response=fallback_response, 
            source="fallback",
            response_time_ms=response_time
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (e.g., validation) without converting to 500
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/faqs")
async def get_faqs(category: Optional[str] = None):
    """Get all FAQs, optionally filtered by category."""
    try:
        faqs = get_all_faqs()
        
        if category:
            faqs = [f for f in faqs if f.get("category", "").lower() == category.lower()]
        
        return faqs
    except Exception as e:
        print(f"Error getting FAQs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/faqs")
async def add_faq(request: FAQRequest):
    """Add a new FAQ."""
    try:
        created = upsert_faq(
            question=request.question,
            answer=request.answer,
            id=request.id,
            category=request.category
        )
        if not created:
            raise HTTPException(status_code=500, detail="Failed to add FAQ")
        
        # Clear cache to ensure fresh data
        _clear_faq_cache()
        
        return created
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding FAQ: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/faqs/semantic")
async def add_faq_semantic(request: FAQRequest):
    """Add a new FAQ with automatic embedding computation."""
    try:
        created = upsert_faq(
            question=request.question,
            answer=request.answer,
            id=request.id,
            category=request.category
        )
        if not created:
            raise HTTPException(status_code=500, detail="Failed to add FAQ")
        return created
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding FAQ: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/faqs/rebuild-embeddings")
async def rebuild_embeddings():
    """Force recompute and persist embeddings for all FAQ entries."""
    try:
        # Get all FAQs from the backend
        faq_items = get_all_faqs()
        
        if not faq_items:
            return {"updated_count": 0, "message": "No FAQs found to rebuild embeddings"}
        
        # Recompute all embeddings
        updated_items = ensure_faq_embeddings(faq_items, force=True)
        
        # Clear cache to ensure fresh data
        _clear_faq_cache()
        
        return {
            "updated_count": len(updated_items), 
            "message": f"Rebuilt embeddings for {len(updated_items)} FAQ entries"
        }
    except Exception as e:
        print(f"Error rebuilding embeddings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/faqs/adapter/upsert")
async def adapter_upsert_faq(request: FAQRequest):
    """Upsert a FAQ item via the configured backend."""
    try:
        result = upsert_faq(
            question=request.question,
            answer=request.answer,
            id=request.id,
            category=request.category
        )
        if not result:
            raise HTTPException(status_code=500, detail="Failed to upsert FAQ")
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error upserting FAQ via adapter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/faqs/adapter/rebuild-embeddings")
async def adapter_rebuild_embeddings():
    """Rebuild embeddings for all FAQ entries via the configured backend."""
    try:
        # Get all FAQs from the backend
        faq_items = get_all_faqs()
        
        if not faq_items:
            return {"updated_count": 0, "message": "No FAQs found to rebuild embeddings"}
        
        # Recompute all embeddings
        updated_items = ensure_faq_embeddings(faq_items, force=True)
        
        return {
            "updated_count": len(updated_items), 
            "message": f"Rebuilt embeddings for {len(updated_items)} FAQ entries via adapter"
        }
    except Exception as e:
        print(f"Error rebuilding embeddings via adapter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/faqs/{faq_id}")
async def update_faq(faq_id: str, request: FAQRequest):
    """Update an existing FAQ by id."""
    try:
        updated = upsert_faq(
            question=request.question,
            answer=request.answer,
            id=faq_id,
            category=request.category
        )
        if not updated:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        # Clear cache to ensure fresh data
        _clear_faq_cache()
        
        return updated
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating FAQ: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/faqs/categories")
async def list_categories():
    try:
        faqs = get_all_faqs()
        categories = set(f.get("category", "general") for f in faqs)
        return sorted(list(categories))
    except Exception as e:
        print(f"Error listing categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/faqs/{faq_id}")
async def delete_faq(faq_id: str):
    """Delete a FAQ by id."""
    try:
        from services.faq_adapter import delete_faq as delete_faq_adapter
        deleted = delete_faq_adapter(faq_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        # Clear cache to ensure fresh data
        _clear_faq_cache()
        
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting FAQ: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/logs")
async def get_fallback_logs(limit: Optional[int] = 10):
    """Get recent fallback logs."""
    try:
        logs = fallback_service.get_logs(limit=limit)
        return logs
    except Exception as e:
        print(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats")
async def get_chat_stats():
    """Get chat statistics including FAQ count and categories."""
    try:
        faqs = get_all_faqs()
        categories = set(f.get("category", "general") for f in faqs)
        
        # Count FAQs with embeddings
        faqs_with_embeddings = sum(1 for f in faqs if f.get("embedding") is not None)
        
        # Get backend info
        backend = get_faq_backend()
        backend_type = backend.__class__.__name__.replace("FAQBackend", "").lower()
        
        return {
            "total_faqs": len(faqs),
            "faqs_with_embeddings": faqs_with_embeddings,
            "backend_type": backend_type,
            "categories": sorted(list(categories)),
            "category_counts": {cat: len([f for f in faqs if f["category"] == cat]) for cat in categories},
            "semantic_config": {
                "top_k": SEMANTIC_TOP_K,
                "threshold": SEMANTIC_THRESHOLD
            }
        }
    except Exception as e:
        print(f"Error getting chat stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/performance")
async def get_performance_stats():
    """Get performance statistics and recommendations."""
    try:
        return get_performance_summary()
    except Exception as e:
        print(f"Error getting performance stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Helper functions for backward compatibility
def _is_greeting(message: str) -> bool:
    """Check if the message is a greeting."""
    greetings = [
        'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
        'سلام', 'درود', 'خوش آمدید', 'سلام علیکم', 'صبخ بخیر', 'عصر بخیر',
        'start', 'begin', 'شروع', 'آغاز', 'چت', 'chat'
    ]
    
    message_lower = message.lower().strip()
    return any(greeting in message_lower for greeting in greetings)


def _get_greeting_response() -> str:
    """Get a random greeting response."""
    import random
    
    greetings = [
        "سلام! 👋 خوش آمدید! چطور می‌تونم کمکتون کنم؟",
        "درود! 😊 من بات هوشمند زیمر هستم. چطور می‌تونم کمکتون کنم؟",
        "سلام علیکم! 🌟 خوشحالم که با شما صحبت می‌کنم. چطور می‌تونم کمکتون کنم؟",
        "Hi there! 👋 Welcome! How can I help you today?",
        "Hello! 😊 I'm your AI assistant. How can I be of service?"
    ]
    
    return random.choice(greetings)


def _search_faq_exact(question: str, faq_items: List[Dict]) -> Optional[str]:
    """Search for FAQ answer with exact match (case-insensitive)."""
    question_lower = question.strip().lower()
    
    for item in faq_items:
        if item.get("question", "").lower() == question_lower:
            return item.get("answer")
    
    return None


def _search_faq_partial(question: str, faq_items: List[Dict]) -> Optional[str]:
    """Enhanced partial matching with multiple strategies."""
    q = question.strip().lower()
    
    # Strategy 1: Check if user question contains FAQ question
    for item in faq_items:
        item_question = item.get("question", "").lower()
        if item_question in q:
            return item.get("answer")
    
    # Strategy 2: Check if FAQ question contains user question
    for item in faq_items:
        item_question = item.get("question", "").lower()
        if q in item_question:
            return item.get("answer")
    
    # Strategy 3: Check for word overlap
    words = q.split()
    if len(words) > 1:
        for word in words:
            if len(word) > 2:  # Only check words longer than 2 characters
                for item in faq_items:
                    item_question = item.get("question", "").lower()
                    if word in item_question:
                        return item.get("answer")
    
    return None