# Personalized Learning Path Generator

## Description
A production-ready FastAPI backend that generates personalized learning paths based on your experience, goals, and missing skills. It natively runs Ollama (with HuggingFace fallback) fully locally. It features JWT authentication, semantic RAG matching with `sentence-transformers`, dependency enforcement graph, and LLM structured prompt extraction.

## Requirements
- Python 3.9+
- Ollama installed locally (https://ollama.ai)

## Setup & Run Instructions

### 1. Install Dependencies
Create a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup Ollama
Ensure you have pulled the correct model (default is mistral):
```bash
ollama run mistral
```
Keep the Ollama server running in the background. Note: The app defaults to calling `http://localhost:11434`, configurable via `OLLAMA_BASE_URL` in `.env`.

### 3. Start the Server
Start the FastAPI server through `uvicorn`:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The API runs on `http://localhost:8000`. 
Interactive Swagger UI Docs are found at `http://localhost:8000/docs`.

### 4. Provide Optional Datasets
The application dynamically initializes the `.csv` schemas in `dataset/` if they do not exist. To improve RAG matching, populate `dataset/resources.csv` and `dataset/projects.csv` with mock or real data. The `.csv` headers correspond exactly to what is read in `csv_handler.py`.

## Example Usage

### 1. Register a new user
```bash
curl -X POST "http://localhost:8000/auth/register" \
 -H "Content-Type: application/json" \
 -d '{"email": "user@example.com", "password": "password123", "experience_level": "beginner", "available_hours_per_week": 10, "learning_style": "visual"}'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
 -H "Content-Type: application/json" \
 -d '{"email": "user@example.com", "password": "password123"}'
```
*Save the `access_token` from the response.*

### 3. Extract Skills from Free Text
```bash
curl -X POST "http://localhost:8000/users/extract-skills" \
 -H "Authorization: Bearer <access_token>" \
 -H "Content-Type: application/json" \
 -d '{"free_text": "I really want to get good at Python and Machine Learning, maybe a little bit of Pandas for data cleaning."}'
```

### 4. Generate Personalized Roadmap
```bash
curl -X POST "http://localhost:8000/roadmap/generate-roadmap" \
 -H "Authorization: Bearer <access_token>"
```

### 5. Submit Feedback
```bash
curl -X POST "http://localhost:8000/roadmap/feedback" \
 -H "Authorization: Bearer <access_token>" \
 -H "Content-Type: application/json" \
 -d '{"content_id": "course-123", "content_type": "resource", "rating": 5, "comments": "Very helpful!"}'
```

## Structure
- `app/` -> the main Fast Api Application code.
  - `routes/` -> API Endpoint definitions using APIRouters.
  - `services/` -> Modular logic blocks including Auth, Embeddings caching, RAG retrieval, DB gap analysis.
  - `models/` -> Pydantic validations
  - `utils/` -> Thread-safe `pandas` CSV handler, Python-Jose Token verification, Settings manager.
- `app/data/` -> Auto-generated embeddings caching files and application logs.
- `dataset/` -> Auto-generated CSV files that act as the persistent data storage DB.

