# FAQ Adapter System

This document describes the new FAQ adapter system that allows the chatbot to use different data sources (JSON, REST API, or database) while maintaining semantic search functionality.

## Overview

The FAQ adapter provides a unified interface for accessing FAQ data from multiple sources:
- **JSON Backend**: Local file storage (default)
- **API Backend**: REST API integration
- **Database Backend**: SQL database (future implementation)

All backends support the same operations and maintain semantic search capabilities through embeddings.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Chat Router   │───▶│  FAQ Adapter     │───▶│  Backend       │
│                 │    │                  │    │                 │
│ - /chat/        │    │ - BaseFAQBackend │    │ - JSON          │
│ - /faqs/*       │    │ - Factory        │    │ - API           │
│ - /stats        │    │ - Normalization  │    │ - Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Configuration

### Environment Variables

```bash
# FAQ Backend Selection
FAQ_BACKEND=json        # "json", "api", or "db"

# API Backend Configuration
FAQ_API_BASE=https://your-interface.example.com
FAQ_API_KEY=your_api_key_here

# Database Configuration (future)
DATABASE_URL=postgresql://user:password@localhost/dbname

# Semantic Search Configuration
EMBEDDING_MODEL=text-embedding-3-small
SEMANTIC_THRESHOLD=0.82
SEMANTIC_TOP_K=3
```

### Backend Selection

The system automatically selects the appropriate backend based on `FAQ_BACKEND`:

1. **JSON Backend** (`FAQ_BACKEND=json`)
   - Default backend
   - Uses local `data/custom_faq.json` file
   - Full CRUD operations with embeddings

2. **API Backend** (`FAQ_BACKEND=api`)
   - Requires `FAQ_API_BASE` environment variable
   - Optional `FAQ_API_KEY` for authentication
   - Integrates with external REST API

3. **Database Backend** (`FAQ_BACKEND=db`)
   - Requires `DATABASE_URL` environment variable
   - Currently a placeholder for future SQLAlchemy implementation

## API Endpoints

### Standard FAQ Endpoints

- **GET** `/chat/faqs` - Get all FAQs
- **POST** `/chat/faqs` - Add new FAQ
- **POST** `/chat/faqs/semantic` - Add FAQ with auto-embedding
- **PUT** `/chat/faqs/{id}` - Update FAQ
- **DELETE** `/chat/faqs/{id}` - Delete FAQ

### Adapter-Specific Endpoints

- **POST** `/chat/faqs/adapter/upsert` - Upsert FAQ via configured backend
- **POST** `/chat/faqs/adapter/rebuild-embeddings` - Rebuild embeddings via backend

### Embedding Management

- **POST** `/chat/faqs/rebuild-embeddings` - Rebuild all embeddings
- **GET** `/chat/stats` - View backend type and embedding status

## Backend Implementations

### JSON Backend

```python
# Automatically wraps existing FAQSimpleService
backend = JSONFAQBackend("data/custom_faq.json")

# Operations
items = backend.get_all()
result = backend.upsert("Question?", "Answer!", category="general")
count = backend.bulk_upsert([item1, item2, item3])
deleted = backend.delete("faq-123")
```

**Features:**
- Local file storage
- Automatic embedding computation
- Full CRUD operations
- Category support
- Timestamp tracking

### API Backend

```python
# Configured via environment variables
backend = APIFAQBackend()

# Expected API endpoints:
# GET  /faqs          - List all FAQs
# POST /faqs          - Create new FAQ
# PUT  /faqs/{id}     - Update FAQ
# DELETE /faqs/{id}   - Delete FAQ
# POST /faqs/bulk     - Bulk operations (optional)
```

**Features:**
- REST API integration
- Bearer token authentication
- Bulk operations support
- Automatic retry logic
- Response normalization

**API Response Format:**
```json
{
  "faqs": [
    {
      "id": "faq-123",
      "question": "What is...?",
      "answer": "The answer is...",
      "category": "general",
      "embedding": [0.1, 0.2, ...],
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### Database Backend (Future)

```python
# Placeholder for SQLAlchemy implementation
backend = DBFAQBackend()

# TODO: Implement with SQLAlchemy
# - Connection pooling
# - Migration support
# - Transaction management
# - Index optimization
```

## Data Normalization

All backends automatically normalize data to a standard format:

```python
{
    "id": "faq-abc12345",           # Auto-generated if missing
    "question": "Question text",     # Required, stripped
    "answer": "Answer text",         # Required, stripped
    "category": "general",           # Default: "general"
    "embedding": [0.1, 0.2, ...],   # Optional float array
    "created_at": "2024-01-01T00:00:00",  # Auto-generated if missing
    "updated_at": "2024-01-01T00:00:00"   # Auto-generated if missing
}
```

## Semantic Search Integration

The adapter maintains full semantic search functionality:

1. **Automatic Embedding Detection**: Checks for missing embeddings on each request
2. **Embedding Computation**: Generates embeddings for new/missing items
3. **Persistent Storage**: Saves embeddings back to the configured backend
4. **Fallback Support**: Falls back to direct file persistence if adapter fails

## Usage Examples

### Switching Backends

```bash
# Use JSON backend (default)
export FAQ_BACKEND=json

# Use API backend
export FAQ_BACKEND=api
export FAQ_API_BASE=https://api.example.com
export FAQ_API_KEY=your_key_here

# Use database backend (future)
export FAQ_BACKEND=db
export DATABASE_URL=postgresql://user:pass@localhost/db
```

### Adding FAQs via Adapter

```bash
# Add FAQ via configured backend
curl -X POST "http://localhost:8000/chat/faqs/adapter/upsert" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I reset my password?",
    "answer": "Go to settings and click reset password.",
    "category": "account"
  }'
```

### Rebuilding Embeddings

```bash
# Rebuild all embeddings via backend
curl -X POST "http://localhost:8000/chat/faqs/adapter/rebuild-embeddings"
```

### Checking Backend Status

```bash
# View backend type and embedding status
curl "http://localhost:8000/chat/stats"
```

## Error Handling

### Backend Initialization Errors

- **Missing Environment Variables**: Falls back to JSON backend
- **Invalid Configuration**: Logs error and uses fallback
- **Connection Failures**: Graceful degradation with error messages

### Operation Errors

- **Network Issues**: Retry logic for API operations
- **Data Validation**: Normalization errors are logged and handled
- **Embedding Failures**: Fallback to zero vectors with warnings

### Fallback Strategy

1. **Primary Backend**: Attempts configured backend
2. **JSON Fallback**: Falls back to local JSON if primary fails
3. **Error Logging**: Comprehensive error logging for debugging

## Performance Considerations

### Caching

- **In-Memory Cache**: FAQ items cached in memory
- **Cache Invalidation**: Automatic invalidation on updates
- **Lazy Loading**: Embeddings computed on-demand

### Batch Operations

- **Bulk Upserts**: Efficient batch processing for multiple items
- **Embedding Batching**: Computes multiple embeddings simultaneously
- **API Optimization**: Uses bulk endpoints when available

### Network Optimization

- **Connection Pooling**: Reuses HTTP connections for API calls
- **Timeout Handling**: Configurable timeouts for external APIs
- **Retry Logic**: Automatic retry for transient failures

## Migration Guide

### From JSON to API

1. **Configure API Backend**:
   ```bash
   export FAQ_BACKEND=api
   export FAQ_API_BASE=https://your-api.com
   export FAQ_API_KEY=your_key
   ```

2. **Migrate Data**:
   ```bash
   # Export from JSON
   curl "http://localhost:8000/chat/faqs" > faqs_export.json
   
   # Import to API (via your API's import endpoint)
   # This depends on your API implementation
   ```

3. **Verify Migration**:
   ```bash
   curl "http://localhost:8000/chat/stats"
   # Should show "backend_type": "api"
   ```

### From API to Database

1. **Implement Database Backend**:
   - Extend `DBFAQBackend` class
   - Implement SQLAlchemy models
   - Add migration scripts

2. **Update Configuration**:
   ```bash
   export FAQ_BACKEND=db
   export DATABASE_URL=postgresql://...
   ```

## Troubleshooting

### Common Issues

1. **Backend Not Initializing**:
   - Check environment variables
   - Verify API endpoints are accessible
   - Check authentication credentials

2. **Embeddings Not Persisting**:
   - Verify backend permissions
   - Check network connectivity
   - Review error logs

3. **Performance Issues**:
   - Monitor embedding computation time
   - Check API response times
   - Verify cache invalidation

### Debug Information

```bash
# Check backend status
curl "http://localhost:8000/chat/stats"

# View system logs
tail -f backend.log

# Test backend connectivity
python -c "from services.faq_adapter import get_faq_backend; print(get_faq_backend())"
```

## Future Enhancements

### Planned Features

- **Database Backend**: Full SQLAlchemy implementation
- **Redis Caching**: Distributed caching support
- **Async Operations**: Non-blocking I/O for better performance
- **Metrics Collection**: Performance monitoring and analytics
- **Multi-Tenant Support**: Isolated FAQ spaces per organization

### Extension Points

- **Custom Backends**: Implement `BaseFAQBackend` for custom data sources
- **Authentication Plugins**: Custom auth mechanisms for API backends
- **Data Transformers**: Custom normalization logic
- **Validation Rules**: Backend-specific validation

## API Reference

### BaseFAQBackend

```python
class BaseFAQBackend(ABC):
    @abstractmethod
    def get_all(self) -> List[Dict]: ...
    
    @abstractmethod
    def upsert(self, question: str, answer: str, 
               id: Optional[str] = None, category: str = "general",
               embedding: Optional[List[float]] = None) -> Dict: ...
    
    @abstractmethod
    def bulk_upsert(self, items: List[Dict]) -> int: ...
    
    @abstractmethod
    def delete(self, id: str) -> bool: ...
    
    def normalize_item(self, item: Dict) -> Dict: ...
```

### Factory Function

```python
def get_faq_backend() -> BaseFAQBackend:
    """Get configured FAQ backend based on environment."""
    mode = os.getenv("FAQ_BACKEND", "json").lower()
    # Returns appropriate backend instance
```

### Convenience Functions

```python
def get_all_faqs() -> List[Dict]: ...
def upsert_faq(question: str, answer: str, ...) -> Dict: ...
def bulk_upsert_faqs(items: List[Dict]) -> int: ...
def delete_faq(id: str) -> bool: ...
```

## License

MIT License - Same as the main project.

































