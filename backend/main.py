"""
Main FastAPI application for the chatbot.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat

# Create FastAPI app
app = FastAPI(
    title="ChatBot API",
    description="A modular chatbot API with FAQ, GPT-4, and fallback handling",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to ChatBot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat/",
            "health": "/chat/health",
            "faqs": "/chat/faqs",
            "faqs_semantic": "/chat/faqs/semantic",
            "rebuild_embeddings": "/chat/faqs/rebuild-embeddings",
            "adapter_upsert": "/chat/faqs/adapter/upsert",
            "adapter_rebuild": "/chat/faqs/adapter/rebuild-embeddings",
            "logs": "/chat/logs",
            "stats": "/chat/stats",
            "performance": "/chat/performance"
        }
    }


@app.get("/health")
async def health_check():
    """Global health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 