# 🎓 NexusEdu • Student Management AI System

> **A production-ready, modular FastAPI backend combining an SQLite structured database, ChromaDB vector store, and a Gemini-powered LangGraph multi-tool chatbot with an interactive campus dashboard.**

---

## 🌟 How This Project Stands Out

While standard assignments only offer raw Swagger `/docs` and basic CRUD scripts, **NexusEdu** introduces four key engineering differentiators:

1. **Embedded Campus Web Dashboard (`http://127.0.0.1:8000/`)**:
   - Clean, modern single-page dashboard alongside the official Swagger UI (`/docs`).
   - Live analytics cards (Total Enrolled, Average CGPA, Highest CGPA, Vector Index status).
   - Real-time search by name, email, or technical skills with instant department & CGPA filter pills.
   - Interactive **AI Campus Advisor Drawer** with instant one-click test prompts.
2. **Transparent Tool Execution Badges**:
   - The AI assistant visually indicates its source of truth for every answer:
     - 🔍 `[SQLite DB Tool]` for structured queries (*"What is Abhishek's CGPA?"*, *"Who has CGPA > 8.5?"*).
     - 🧠 `[ChromaDB Vector Tool]` for semantic talent search (*"Find students skilled in machine learning and Python"*).
     - ⚡ `[Hybrid]` for combined queries.
3. **Automated Vector Store Synchronization**:
   - SQLite and ChromaDB stay in sync in real time. Creating, updating, or deleting a student record via the REST API or UI automatically updates their embedding in ChromaDB.
4. **Enriched Student Domain Model (Day 5 & Day 9 Alignment)**:
   - Extends the core attributes with `gender` (directly implementing the **Day 5 Page 6 worked example**), as well as `skills`, `interests`, and `bio`.

---

## 📚 Direct Alignment with Coursework Notes

| Lecture Module | Core Concept | Implementation in NexusEdu |
| :--- | :--- | :--- |
| **Day 5: Production Backend** | • Request/Response Protocol<br>• Application Security & CORS<br>• Request Validation (Pydantic)<br>• 5 Production Areas<br>• Modularity & Worked Example (`gender`) | • `app/main.py` includes CORS origin control & request-timing observability middleware (`X-Process-Time`).<br>• Clean separation into `database/`, `schemas/`, `crud/`, `routes/`, `services/`, `ai/`, `vectorstore/`.<br>• Student model includes `gender` and `skills`. |
| **Day 6: Transformers & LangGraph** | • Difference between LLMs and Agents<br>• Prompt vs Context (Prompt = question, Context = retrieved data)<br>• Multi-tool Agent Workflow | • `app/ai/graph.py` implements a LangGraph `StateGraph` with a routing node, tool execution node, and synthesis node using `gemini-2.5-flash`. |
| **Day 7 & 8: Data Structures & Functions** | • Lists, Tuples, Dictionaries<br>• Reusable functions with parameters & explicit returns<br>• Local vs Global scope | • Clean CRUD functions in `app/crud/student.py` leveraging Python dicts and lists with typed return models. |
| **Day 9: Object-Oriented Programming (OOP)** | • Class (Blueprint) & Objects (Instances)<br>• Attributes (`name`, `age`, `cgpa`, `gender`, etc.)<br>• Constructor `__init__` and `self`<br>• Encapsulation (Service layer classes) | • `Student` class inheriting from SQLAlchemy `Base`.<br>• `StudentService` and `ChatbotService` classes encapsulating data access and business rules. |
| **Day 11: Linux Systemd Services** | • The Daemon Paradigm (no manual `Run` button)<br>• Persistent background execution<br>• Daemon reload, enable, start, status, journalctl | • Production unit file `deploy/student-api.service` configured for autonomous execution and automatic restart. |

---

## 🏛️ System Architecture

```
                    ┌───────────────────────────────┐
                    │          Client / User        │
                    │   Browser Dashboard / Swagger │
                    └───────────────┬───────────────┘
                                    │ HTTP Requests
                                    ▼
                    ┌───────────────────────────────┐
                    │     FastAPI Application       │
                    │  (CORS + Observability MW)    │
                    └───────────────┬───────────────┘
                                    │
             ┌──────────────────────┴──────────────────────┐
             ▼                                             ▼
    Student REST Routes                             AI Chatbot Route
    (/students/)                                    (/chat/)
             │                                             │
             ▼                                             ▼
    StudentService Layer                            ChatbotService Layer
             │                                             │
      ┌──────┴──────┐                                      ▼
      │             │                              LangGraph StateGraph
      ▼             ▼                                      │
   SQLite       ChromaDB                         ┌─────────┴─────────┐
 Structured    Vector Store                      ▼                   ▼
 Data Store    (Semantic)                   SQLite Tool         ChromaDB Tool
                                            (CGPA, IDs)        (Skills, Bio)
                                                 │                   │
                                                 └─────────┬─────────┘
                                                           ▼
                                                    Gemini 2.5 Flash
                                                   (Prompt + Context)
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.9+ installed.
- (Optional) Google Gemini API Key for LLM natural language generation.

### 2. Run with One Command
Execute the automated startup runner:
```bash
./run.sh
```

Or manually:
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run server with Uvicorn
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open in Browser
- **NexusEdu Interactive Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **FastAPI Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🔑 Configuring Your Gemini API Key

Open `.env` in the project root:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
> **Note**: Even if no API key is provided, the application includes a deterministic rule-based response engine so all features, tests, and database queries work seamlessly out of the box!

---

## 🧪 Running Automated Tests

Run the complete test suite:
```bash
./venv/bin/pytest -v tests/test_students.py
```

### Verified Test Cases:
- `test_health_check`: Verifies the observability and service health status.
- `test_crud_student_lifecycle`: Creates, reads, updates, and deletes a student record with 404 validation.
- `test_duplicate_email_error`: Asserts that duplicate student emails return HTTP 400.
- `test_student_stats`: Validates CGPA aggregations and department counts.
- `test_ai_chatbot_structured_query`: Validates LangGraph routing to SQLite DB.
- `test_ai_chatbot_semantic_query`: Validates LangGraph routing to ChromaDB vector search.

---

## 🐧 Production Deployment (Linux Systemd - Day 11)

To run the backend autonomously on a Linux server:

1. Copy the service unit file to systemd:
   ```bash
   sudo cp deploy/student-api.service /etc/systemd/system/
   ```
2. Reload systemd daemon:
   ```bash
   sudo systemctl daemon-reload
   ```
3. Enable and start the service:
   ```bash
   sudo systemctl enable student-api
   sudo systemctl start student-api
   ```
4. Verify runtime status:
   ```bash
   systemctl status student-api
   ```
5. Inspect real-time logs with `journalctl`:
   ```bash
   journalctl -u student-api -f
   ```

---

## 📁 Project Directory Layout

```
student-management-ai/
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app, CORS, Observability, Route Mounting
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py             # SQLite engine, SessionLocal, get_db()
│   │   ├── models.py               # Student SQLAlchemy Model (OOP, attributes, gender, skills)
│   │   └── seed.py                 # Pre-populated realistic student demo dataset
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── student.py              # Pydantic Schemas (Create, Update, Response, Stats)
│   │   └── chatbot.py              # ChatRequest and ChatResponse schemas
│   ├── crud/
│   │   ├── __init__.py
│   │   └── student.py              # Isolated CRUD functions (Create, Read, Update, Delete)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── students.py             # /students CRUD endpoints, stats & vector sync
│   │   └── chatbot.py              # /chat endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── student_service.py      # Business logic & automatic ChromaDB sync
│   │   └── chatbot_service.py      # LangGraph invocation wrapper
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── gemini.py               # Gemini 2.5 Flash LLM initializer
│   │   ├── tools.py                # SQLite tools & ChromaDB vector search tool
│   │   └── graph.py                # LangGraph workflow (Router -> Tools -> Synthesizer)
│   ├── vectorstore/
│   │   ├── __init__.py
│   │   └── chroma.py               # ChromaDB client & semantic embedding index
│   └── static/
│       ├── index.html              # Sleek interactive campus dashboard
│       └── app.js                  # Frontend client logic & live chat controller
│
├── data/
│   └── students.db                 # SQLite database storage
├── chroma_db/                      # ChromaDB vector persistence
├── deploy/
│   └── student-api.service         # Linux systemd production service file (Day 11)
├── tests/
│   ├── __init__.py
│   └── test_students.py            # Automated Pytest suite
├── run.sh                          # One-click startup runner
├── .env                            # Environment variables (Gemini API Key)
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
