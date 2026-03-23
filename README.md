# Personalized Learning Path Generator

## Description
A production-ready FastAPI backend that generates personalized learning paths based on your experience, goals, and missing skills. It utilizes **Groq** for high-speed LLM generation (with HuggingFace fallback), features JWT authentication, semantic RAG matching with `sentence-transformers`, dependency enforcement graphs, and LLM structured prompt extraction. 

**Agentic Web Research:** The platform integrates the **Tavily API** to autonomously search the live internet. Instead of relying solely on static CSV datasets, it fetches the most recent, trending online courses and YouTube videos tailored perfectly to the user's missing skills.

## Requirements
- Python 3.9+
- Groq API Key (for fast LLM generation)
- Tavily API Key (for live Agentic Web Research)

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

### 2. Environment Variables
Create an `app/.env` file in your root project directory (or directly inside `app/`) and populate it:
```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
SECRET_KEY=super-secret-jwt-key
```

### 3. Start the Server
Start the FastAPI server through `uvicorn`:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The API runs on `http://localhost:8000`. 
Interactive Swagger UI Docs are found at `http://localhost:8000/docs`.

### 4. Provide Optional Datasets
The application dynamically initializes the `.csv` schemas in `dataset/` if they do not exist. To improve customized RAG matching alongside the live web search, you can populate `dataset/resources.csv` and `dataset/projects.csv` with proprietary data. 

## Testing Agentic Research
To verify that the Tavily web search integration is working successfully, you can run the test script included at the root:
```bash
python test_tavily.py
```
This simulates a search for missing skills and prints the top real-time courses and video links retrieved from the web.

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

### 3. Generate Personalized Roadmap
```bash
curl -X POST "http://localhost:8000/roadmap/generate-roadmap" \
 -H "Authorization: Bearer <access_token>"
```

### 4. Submit Feedback
```bash
curl -X POST "http://localhost:8000/roadmap/feedback" \
 -H "Authorization: Bearer <access_token>" \
 -H "Content-Type: application/json" \
 -d '{"content_id": "course-123", "content_type": "resource", "rating": 5, "comments": "Very helpful!"}'
```

## Structure
- `app/` -> the main FastAPI Application code.
  - `routes/` -> API Endpoint definitions using APIRouters.
  - `services/` -> Modular logic blocks including Auth, RAG retrieval, DB gap analysis, and the **Web Search Service** via Tavily.
  - `models/` -> Pydantic validations
  - `utils/` -> Thread-safe `pandas` CSV handler, Python-Jose Token verification, Settings manager.
- `app/data/` -> Auto-generated embeddings caching files and application logs.
- `dataset/` -> Auto-generated CSV files that act as the persistent data storage DB.
