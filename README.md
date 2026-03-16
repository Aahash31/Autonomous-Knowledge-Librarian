# Autonomous-Knowledge-Librarian
RAG personal knowledge management system. Provides verifiable answers based on a private document database.

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
