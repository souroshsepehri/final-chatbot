# Semantic Search FAQ System

This document describes the new semantic question matching system that allows the chatbot to recognize paraphrased questions and return the correct answer without manually entering all variants.

## Features

- **Semantic Question Matching**: Uses OpenAI embeddings to find similar questions
- **Automatic Embedding Generation**: Computes embeddings when FAQs are added/updated
- **Configurable Thresholds**: Adjustable similarity thresholds for precision/recall
- **RAG-lite Integration**: Provides relevant FAQ context to GPT when no exact match is found
- **Backward Compatibility**: Automatically migrates existing FAQ formats

## Configuration

### Environment Variables

Create a `.env` file in the backend directory with:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Embedding Model Configuration
EMBEDDING_MODEL=text-embedding-3-small

# Semantic Search Configuration
SEMANTIC_TOP_K=3
SEMANTIC_THRESHOLD=0.82
```

### Threshold Tuning

- **If you get false positives** (wrong answers): Raise `SEMANTIC_THRESHOLD` (e.g., 0.86)
- **If you miss matches** (no answers found): Lower `SEMANTIC_THRESHOLD` (e.g., 0.78)

## New Endpoints

### POST /chat/faqs/semantic
Add a new FAQ with automatic embedding computation.

**Request Body:**
```json
{
  "question": "What are your business hours?",
  "answer": "We are open from 9 AM to 5 PM.",
  "category": "business"
}
```

**Response:**
```json
{
  "id": "faq-abc12345",
  "question": "What are your business hours?",
  "answer": "We are open from 9 AM to 5 PM.",
  "category": "business",
  "embedding": [0.123, 0.456, ...],
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### POST /chat/faqs/rebuild-embeddings
Force recompute and persist embeddings for all FAQ entries.

**Response:**
```json
{
  "updated_count": 25,
  "message": "Rebuilt embeddings for 25 FAQ entries"
}
```

## How It Works

### 1. Semantic Search Flow
1. User sends a question
2. System computes embedding for the question
3. Compares with all FAQ embeddings using cosine similarity
4. Returns best match if similarity ≥ threshold
5. Falls back to exact match if no semantic match found

### 2. RAG-lite Integration
When no FAQ match is found:
1. Top K FAQ candidates are retrieved based on semantic similarity
2. These are provided as context to GPT
3. GPT can use the FAQ answers verbatim or generate new responses

### 3. Embedding Management
- Embeddings are automatically computed when FAQs are added/updated
- Use `/chat/faqs/rebuild-embeddings` after bulk changes
- Embeddings are stored in the JSON file alongside FAQ data

## Data Format

### New FAQ Structure
```json
{
  "faqs": [
    {
      "id": "faq-abc12345",
      "question": "What are your business hours?",
      "answer": "We are open from 9 AM to 5 PM.",
      "category": "business",
      "embedding": [0.123, 0.456, ...],
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### Migration
The system automatically detects and migrates old FAQ formats:
- Old key→value maps are converted to the new object array format
- Unique IDs are generated for each FAQ
- Embeddings are computed for migrated items

## Performance Considerations

- **Embedding Computation**: First-time embedding generation may take a few seconds
- **Similarity Calculation**: Uses numpy for efficient vector operations
- **Caching**: In-memory cache with automatic invalidation on updates
- **Batch Operations**: Use rebuild-embeddings endpoint for bulk updates

## Example Usage

### Testing Semantic Matching
Try these variations of the same question:
- "What are your business hours?"
- "When are you open?"
- "What time do you close?"
- "ساعت کاری شما چیه؟"
- "چه ساعتی بازید؟"

All should return the same answer if the similarity threshold is met.

### Adding New FAQs
```bash
curl -X POST "http://localhost:8000/chat/faqs/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I contact support?",
    "answer": "You can reach us at support@example.com or call 1-800-SUPPORT",
    "category": "support"
  }'
```

### Rebuilding Embeddings
```bash
curl -X POST "http://localhost:8000/chat/faqs/rebuild-embeddings"
```

## Troubleshooting

### Common Issues

1. **No embeddings generated**: Check OpenAI API key and quota
2. **Low similarity scores**: Verify question quality and consider lowering threshold
3. **High false positives**: Increase threshold value
4. **Missing matches**: Decrease threshold value

### Debug Information
Check the `/chat/stats` endpoint for:
- Total FAQ count
- FAQs with embeddings
- Current semantic configuration

## Dependencies

- `numpy==1.26.4` - For efficient vector operations
- `openai==1.3.7` - For embedding generation
- `python-dotenv==1.0.0` - For environment variable management

## Future Enhancements

- **Vector Database**: Replace JSON storage with dedicated vector DB
- **Batch Embedding**: Process multiple questions simultaneously
- **Embedding Caching**: Cache embeddings to reduce API calls
- **Multi-language Support**: Language-specific embedding models







