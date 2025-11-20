# Async Support in Mini RAG

Mini RAG now supports asynchronous operations for better performance, especially when processing multiple queries concurrently or integrating with async web frameworks.

## 🚀 What's New

### Async Methods Added

1. **EmbeddingModel**
   - `embed_query_async()` - Async query embedding generation
   - `embed_chunks_async()` - Async batch chunk embedding

2. **VectorStore**
   - `search_async()` - Async vector similarity search

3. **AgenticRAG**
   - `rewrite_query_async()` - Async query rewriting
   - `retrieve_async()` - Async retrieval with parallel query processing
   - `generate_answer_async()` - Async answer generation
   - `query_async()` - Complete async RAG pipeline

## 📖 Usage Examples

### Basic Async Query

```python
import asyncio
from mini import AgenticRAG, EmbeddingModel, VectorStore

async def main():
    embedding_model = EmbeddingModel()
    vector_store = VectorStore(
        uri="your-milvus-uri",
        token="your-token",
        collection_name="docs",
        dimension=1536
    )
    
    rag = AgenticRAG(vector_store=vector_store, embedding_model=embedding_model)
    
    # Async query
    response = await rag.query_async("What is the budget?")
    print(response.answer)

asyncio.run(main())
```

### Concurrent Queries

One of the main benefits of async is processing multiple queries concurrently:

```python
async def process_multiple_queries():
    queries = [
        "What is the budget?",
        "What are the key findings?",
        "What initiatives were announced?"
    ]
    
    # Process all queries in parallel
    responses = await asyncio.gather(*[rag.query_async(q) for q in queries])
    
    for query, response in zip(queries, responses):
        print(f"Q: {query}")
        print(f"A: {response.answer}\n")
```

### Async Retrieval Only

You can also use async retrieval independently:

```python
# Multiple query variations
queries = ["budget allocation", "funding", "financial plan"]

# Retrieve chunks asynchronously (queries processed in parallel)
chunks = await rag.retrieve_async(queries, top_k=10)

for chunk in chunks:
    print(f"Score: {chunk.score}, Text: {chunk.text[:100]}...")
```

### Integration with FastAPI

Async support makes it easy to integrate with async web frameworks:

```python
from fastapi import FastAPI
from mini import AgenticRAG, EmbeddingModel, VectorStore

app = FastAPI()

# Initialize RAG (do this once at startup)
rag = None

@app.on_event("startup")
async def startup():
    global rag
    embedding_model = EmbeddingModel()
    vector_store = VectorStore(...)
    rag = AgenticRAG(vector_store=vector_store, embedding_model=embedding_model)

@app.post("/query")
async def query_endpoint(query: str):
    response = await rag.query_async(query)
    return {
        "answer": response.answer,
        "sources": len(response.retrieved_chunks)
    }
```

## ⚡ Performance Benefits

### Parallel Processing

When processing multiple queries, async methods run them concurrently:

- **Sync**: Query 1 → Query 2 → Query 3 (sequential)
- **Async**: Query 1, Query 2, Query 3 (parallel)

This can provide significant speedup when:
- Processing multiple user queries
- Handling batch requests
- Running in async web frameworks

### Example Performance

```python
# Sync: ~3 seconds for 3 queries
for q in queries:
    rag.query(q)  # Sequential

# Async: ~1 second for 3 queries
await asyncio.gather(*[rag.query_async(q) for q in queries])  # Parallel
```

## 🔧 Implementation Details

### Embedding Operations

- Uses `AsyncOpenAI` client for non-blocking API calls
- Multiple embeddings can be generated concurrently
- Thread-safe and efficient

### Vector Store Operations

- Milvus operations run in thread pool executor
- Non-blocking search operations
- Maintains compatibility with sync code

### Query Pipeline

The async query pipeline:
1. **Query Rewriting** (async) - Generate query variations
2. **Retrieval** (async) - Parallel embedding and search for all queries
3. **Re-ranking** (sync) - Currently sync, can be made async later
4. **Answer Generation** (async) - Generate final answer

## 📝 Notes

- **Backward Compatibility**: All sync methods remain available
- **Re-ranking**: Currently sync, but doesn't block significantly
- **Error Handling**: Same error handling as sync methods
- **Observability**: Langfuse tracing works with async methods

## 🎯 When to Use Async

Use async methods when:
- ✅ Processing multiple queries concurrently
- ✅ Integrating with async web frameworks (FastAPI, Quart, etc.)
- ✅ Building high-throughput APIs
- ✅ Handling batch operations

Use sync methods when:
- ✅ Simple single queries
- ✅ Scripts or notebooks
- ✅ Synchronous codebases

## 🔄 Migration Guide

### From Sync to Async

**Before:**
```python
response = rag.query("What is the budget?")
```

**After:**
```python
response = await rag.query_async("What is the budget?")
```

### Batch Processing

**Before:**
```python
responses = []
for query in queries:
    responses.append(rag.query(query))
```

**After:**
```python
responses = await asyncio.gather(*[rag.query_async(q) for q in queries])
```

## 🐛 Troubleshooting

### RuntimeError: no running event loop

If you see this error, make sure you're running async code in an async context:

```python
# ❌ Wrong
response = await rag.query_async("query")  # Not in async function

# ✅ Correct
async def main():
    response = await rag.query_async("query")

asyncio.run(main())
```

### Using in Jupyter Notebooks

Jupyter notebooks support async natively:

```python
# In Jupyter, you can use await directly
response = await rag.query_async("What is the budget?")
```

## 📚 See Also

- `examples/async_demo.py` - Complete async examples
- `mini/rag.py` - Implementation details
- `mini/embedding.py` - Async embedding methods
- `mini/store.py` - Async vector store methods

---

*Async support added in version 0.1.3*

