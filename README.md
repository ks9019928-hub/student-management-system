# Student Management System

A modular backend application built with FastAPI, SQLite, ChromaDB, and Gemini AI using LangGraph.

## Features
- **Modular Architecture**: Separate modules for database, schemas, CRUD operations, routes, services, and AI logic.
- **SQLite Database**: Relational storage for student records.
- **CRUD Operations**: Full Create, Read, Update, and Delete endpoints for student records.
- **FastAPI Swagger Documentation**: Interactive API documentation available at `/docs`.
- **ChromaDB Vector Store**: Vector database for storing and querying student skills and profile embeddings.
- **Gemini AI + LangGraph Chatbot**: An AI chatbot that reads and queries student data using a LangGraph workflow.
- **Production Deployment**: Configured to run as a persistent background service using Linux systemd.

---

## Project Structure

```text
student-management-ai/
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI entrypoint, middleware, routers
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py             # SQLite engine, SessionLocal, get_db
│   │   ├── models.py               # Student SQLAlchemy model
│   │   └── seed.py                 # Sample student data
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── student.py              # Pydantic schemas (StudentCreate, StudentUpdate, StudentResponse)
│   │   └── chatbot.py              # ChatRequest and ChatResponse schemas
│   ├── crud/
│   │   ├── __init__.py
│   │   └── student.py              # CRUD database operations
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── students.py             # Student API routes
│   │   └── chatbot.py              # Chatbot route
│   ├── services/
│   │   ├── __init__.py
│   │   ├── student_service.py      # Business logic & ChromaDB sync
│   │   └── chatbot_service.py      # LangGraph execution service
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── gemini.py               # Gemini LLM configuration
│   │   ├── tools.py                # Database and vector query tools
│   │   └── graph.py                # LangGraph workflow
│   └── vectorstore/
│       ├── __init__.py
│       └── chroma.py               # ChromaDB client and embedding storage
│
├── data/
│   └── students.db                 # SQLite database file
├── chroma_db/                      # ChromaDB persistent directory
├── deploy/
│   └── student-api.service         # Linux systemd service unit
├── tests/
│   ├── __init__.py
│   └── test_students.py            # Automated tests
├── run.sh                          # Startup script
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## System Architecture

```text
                    User / Client
                         │
                         ▼
                      FastAPI
                    REST Backend
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
       Student CRUD              AI Chatbot
        (/students)               (/chat)
             │                       │
             ▼                       ▼
          SQLite                 LangGraph
      (students.db)                  │
                              ┌──────┴──────┐
                              │             │
                              ▼             ▼
                           SQLite       ChromaDB
                          DB Tool      Vector Tool
                              │             │
                              └──────┬──────┘
                                     ▼
                                 Gemini AI
                                     │
                                     ▼
                                Final Answer
```

---

## Getting Started

### 1. Prerequisites
- Python 3.9 or higher
- Git

### 2. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and add your Google Gemini API key:
```ini
GEMINI_API_KEY=your_gemini_api_key
```

### 5. Run the Server
Using Uvicorn:
```bash
uvicorn app.main:app --reload
```
Or with the runner script:
```bash
./run.sh
```

The server will start at `http://127.0.0.1:8000`.

---

## API Documentation

FastAPI provides automatic interactive Swagger documentation:
- **Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/students/` | Create a new student record |
| `GET` | `/students/` | Get all students (supports filtering by course and CGPA) |
| `GET` | `/students/{id}` | Get student by ID |
| `PUT` | `/students/{id}` | Update student details |
| `DELETE` | `/students/{id}` | Delete student record |
| `POST` | `/chat/` | Ask questions to the Gemini + LangGraph chatbot |
| `GET` | `/health` | Health check endpoint |

---

## Linux Systemd Service Deployment

To deploy this backend as a persistent Linux service:

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

4. Check service status:
   ```bash
   systemctl status student-api
   ```

5. View logs using journalctl:
   ```bash
   journalctl -u student-api -f
   ```

---

## Running Tests

Run the test suite with pytest:
```bash
pytest -v
```
