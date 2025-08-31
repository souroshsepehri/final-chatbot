# ChatBot API

A modular FastAPI chatbot with FAQ, GPT-4, semantic search, pluggable backends, and fallback handling capabilities.

## Features

- **FAQ System**: Local knowledge base with exact match lookups
- **Semantic Search**: AI-powered question matching using OpenAI embeddings
- **Pluggable Backends**: Support for JSON, REST API, and database sources
- **GPT-4 Integration**: OpenAI API integration for dynamic responses
- **Response Quality Check**: Filters out vague or overly long responses
- **Fallback Handling**: Persian fallback message for unanswered questions
- **CORS Support**: Configured for frontend integration
- **Modular Architecture**: Clean separation of concerns

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── routers/
│   └── chat.py            # Chat endpoint router
├── services/
│   ├── gpt.py             # GPT-4 API service
│   ├── faq.py             # FAQ lookup service (legacy)
│   ├── faq_simple.py      # New FAQ service with embeddings
│   ├── faq_adapter.py     # Pluggable FAQ backend adapter
│   ├── embeddings.py      # Semantic search service
│   └── fallback.py        # Fallback response service
├── utils/
│   └── response_check.py  # Response quality checker
├── data/
│   ├── custom_faq.json    # Local knowledge base
│   └── fallback_logs.txt  # Unanswered questions log
├── config.env.example     # Environment variables template
├── requirements.txt       # Python dependencies
├── SEMANTIC_SEARCH_README.md # Detailed semantic search docs
├── ADAPTER_README.md      # FAQ adapter system docs
├── test_semantic.py       # Semantic search tests
├── test_adapter.py        # Adapter system tests
└── demo_semantic.py       # Semantic search demo
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Copy `config.env.example` to `.env` and add your configuration:
   ```bash
   # OpenAI API Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # FAQ Backend Configuration
   FAQ_BACKEND=json        # "json", "api", or "db"
   FAQ_API_BASE=https://your-interface.example.com  # For API backend
   FAQ_API_KEY=your_api_key_here                    # For API backend
   
   # Database Configuration (for future use)
   DATABASE_URL=postgresql://user:password@localhost/dbname
   
   # Semantic Search Configuration
   EMBEDDING_MODEL=text-embedding-3-small
   SEMANTIC_TOP_K=3
   SEMANTIC_THRESHOLD=0.82
   ```

3. **Run the Application**:
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## FAQ Backend Configuration

The system supports multiple FAQ data sources through a pluggable adapter:

### JSON Backend (Default)
```bash
export FAQ_BACKEND=json
```
- Uses local `data/custom_faq.json` file
- Full CRUD operations with embeddings
- Automatic migration from old formats

### API Backend
```bash
export FAQ_BACKEND=api
export FAQ_API_BASE=https://your-interface.example.com
export FAQ_API_KEY=your_api_key_here
```
- Integrates with external REST API
- Bearer token authentication
- Bulk operations support

### Database Backend (Future)
```bash
export FAQ_BACKEND=db
export DATABASE_URL=postgresql://user:pass@localhost/db
```
- Placeholder for SQLAlchemy implementation
- Full database integration planned

## API Endpoints

### Chat Endpoint
- **POST** `/chat/`
- **Body**: `{"message": "Your question here"}`
- **Response**: `{"response": "Answer", "source": "faq|faq_semantic|gpt|fallback", "metadata": {...}}`

### Health Check
- **GET** `/health` - Global health check
- **GET** `/chat/health` - Chat service health check

### FAQ Management
- **GET** `/chat/faqs` - Get all FAQs
- **POST** `/chat/faqs` - Add new FAQ with embedding
- **POST** `/chat/faqs/semantic` - Add new FAQ with automatic embedding
- **POST** `/chat/faqs/rebuild-embeddings` - Rebuild all embeddings
- **PUT** `/chat/faqs/{id}` - Update FAQ
- **DELETE** `/chat/faqs/{id}` - Delete FAQ

### Adapter Endpoints
- **POST** `/chat/faqs/adapter/upsert` - Upsert FAQ via configured backend
- **POST** `/chat/faqs/adapter/rebuild-embeddings` - Rebuild embeddings via backend

### Logs & Stats
- **GET** `/chat/logs?limit=10` - Get recent fallback logs
- **GET** `/chat/stats` - Get chat statistics, backend type, and embedding status

## Semantic Search Features

### Automatic Question Matching
The chatbot now recognizes paraphrased questions using AI embeddings:
- "What are your business hours?" → "When are you open?" → "ساعت کاری شما چیه؟"
- All return the same answer if similarity ≥ threshold

### RAG-lite Integration
When no FAQ match is found:
- Top K FAQ candidates are retrieved based on semantic similarity
- These are provided as context to GPT for better responses
- GPT can use FAQ answers verbatim or generate new responses

### Configuration
- **SEMANTIC_THRESHOLD**: Adjust precision/recall (default: 0.82)
- **SEMANTIC_TOP_K**: Number of candidates to retrieve (default: 3)
- **EMBEDDING_MODEL**: OpenAI embedding model (default: text-embedding-3-small)

## Usage Examples

### Basic Chat Request
```bash
curl -X POST "http://localhost:8000/chat/" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is your name?"}'
```

### Add FAQ via Adapter
```bash
curl -X POST "http://localhost:8000/chat/faqs/adapter/upsert" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "How do I reset my password?", 
       "answer": "Go to settings and click reset password.",
       "category": "account"
     }'
```

### Rebuild Embeddings via Adapter
```bash
curl -X POST "http://localhost:8000/chat/faqs/adapter/rebuild-embeddings"
```

### Check Backend Status
```bash
curl "http://localhost:8000/chat/stats"
```

## Response Flow

1. **Greeting Check**: Detects greeting messages
2. **Semantic Search**: Tries semantic matching with FAQ embeddings
3. **Exact Match**: Falls back to exact match if semantic search fails
4. **Partial Match**: Tries partial matching strategies
5. **GPT-4 with Context**: Sends to GPT with top FAQ candidates as context
6. **Quality Check**: Analyzes GPT response for vagueness
7. **Fallback**: Returns Persian fallback if response is vague

## Testing & Demo

### Run Tests
```bash
# Test semantic search functionality
python test_semantic.py

# Test adapter system
python test_adapter.py
```

### Run Demo
```bash
python demo_semantic.py
```

## Configuration

### FAQ Backend Selection
- **JSON**: Local file storage with full CRUD
- **API**: External REST API integration
- **Database**: Future SQLAlchemy implementation

### Semantic Search
- **Threshold Tuning**: 
  - False positives → Raise threshold (e.g., 0.86)
  - Missing matches → Lower threshold (e.g., 0.78)
- **Model**: text-embedding-3-small (1536 dimensions)
- **Performance**: Uses numpy for efficient vector operations

### GPT Service
- Model: GPT-4 (configurable)
- Max tokens: 150 (configurable)
- Temperature: 0.7 (configurable)

### Response Quality Check
- Vague phrases detection
- Word count limit: 100 words
- Hedging words analysis

### CORS
- Allowed origin: `http://localhost:3000`
- All methods and headers allowed

## Error Handling

- Graceful handling of API failures
- Fallback responses for service errors
- Comprehensive logging of unanswered questions
- Input validation and sanitization
- Automatic embedding generation with fallback
- Backend fallback strategy (JSON → API → Error)

## Development

### Adding New Features
1. Create new service in `services/` directory
2. Add router endpoints in `routers/` directory
3. Update main.py to include new routers
4. Add tests and documentation

### Extending Backends
1. Implement `BaseFAQBackend` abstract class
2. Add backend type to factory function
3. Update environment configuration
4. Add tests for new backend

### Testing
```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest

# Run semantic search tests
python test_semantic.py

# Run adapter tests
python test_adapter.py
```

## Migration

The system automatically migrates existing FAQ formats:
- Old key→value maps → New object array format
- Unique IDs generated automatically
- Embeddings computed for migrated items
- Backward compatible with existing functionality

### Switching Backends
```bash
# From JSON to API
export FAQ_BACKEND=api
export FAQ_API_BASE=https://your-api.com
export FAQ_API_KEY=your_key

# From API to Database (future)
export FAQ_BACKEND=db
export DATABASE_URL=postgresql://...
```

## Performance Considerations

### Caching
- In-memory cache with automatic invalidation
- Efficient vector operations with numpy
- Lazy loading of embeddings

### Batch Operations
- Bulk upserts for multiple items
- Simultaneous embedding computation
- API bulk endpoints when available

### Network Optimization
- HTTP connection pooling
- Configurable timeouts
- Automatic retry logic

## Troubleshooting

### Common Issues
1. **Backend Not Initializing**: Check environment variables and connectivity
2. **Embeddings Not Persisting**: Verify backend permissions and network
3. **Performance Issues**: Monitor embedding computation and API response times

### Debug Information
```bash
# Check backend status and type
curl "http://localhost:8000/chat/stats"

# Test backend connectivity
python -c "from services.faq_adapter import get_faq_backend; print(get_faq_backend())"
```

## License

MIT License 