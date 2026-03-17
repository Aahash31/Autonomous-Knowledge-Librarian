# Autonomous-Knowledge-Librarian
RAG personal knowledge management system. Provides verifiable answers based on a private document database.

The system follows a modern RAG (Retrieval-Augmented Generation) pipeline:
1.  **Ingestion:** Documents are chunked and embedded into MongoDB Atlas.
2.  **Routing:** LangGraph analyzes the user's message intent.
3.  **Retrieval:** Relevant context is fetched from the vector store.
4.  **Generation:** The LLM synthesizes an answer strictly from the provided context.

# Backend
FastAPI, Python, LangGraph, LangChain, MongoDB Atlas
```bash
├── data/                 # Raw source documents for RAG
│   ├── reminders.txt
│   ├── test_note.txt
├── .env                  # Private environment variables
├── agent.py              # FastAPI server, LangGraph workflow, LangChain library supports (llama 3.2 or gpt-4o-mini)
├── ingest.py             # Reads files, converts embeddings, saves into MongoDB Atlas
├── test_eval.py          # Runs automated tests against agent.py logic for intent validation
└── .gitignore            # Ensures sensitive files (.env, venv) are not tracked
```

## Tests
`python test_eval.py`
This validates:
* **Fact Retrieval:** Correct keyword identification from private notes.
* **Intent Recognition:** Content focused and minimizes irrelevant data.
* **Constraint Adherence:** Ensuring the agent admits when it "doesn't know" rather than hallucinating.
