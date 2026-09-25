import time
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine
from app.routes.students import router as student_router
from app.routes.chatbot import router as chatbot_router

# Initialize SQLite tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Management System",
    description=(
        "Backend Application built with FastAPI, SQLite, ChromaDB, and Gemini AI.\n\n"
        "### Features:\n"
        "- **Modular Architecture**: Separate database, schemas, CRUD, routes, services, and AI layers.\n"
        "- **SQLite Student Database**: Source of truth for student records.\n"
        "- **CRUD Operations**: Full Create, Read, Update, Delete APIs for students.\n"
        "- **ChromaDB Vector Database**: Embeddings for semantic skill & interest matching.\n"
        "- **Gemini AI + LangGraph Chatbot**: Reads from the student database using LangGraph workflow.\n"
        "- **Production Service**: Ready for deployment via Linux systemd."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "docExpansion": "full",         # Automatically expands all endpoints so input fields show directly!
        "defaultModelsExpandDepth": -1, # Keeps the page focused on API inputs
        "displayRequestDuration": True
    }
)

# Day 5: CORS Origin Control
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Day 5: Observability & Request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response

# Include Modular Routers
app.include_router(student_router)
app.include_router(chatbot_router)


@app.get("/", include_in_schema=False)
def root():
    """Redirect root directly to FastAPI Swagger Docs as required in the screenshot."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint for monitoring and systemd service verification."""
    return {
        "status": "healthy",
        "service": "student-management-system",
        "database": "SQLite (data/students.db)",
        "vectorstore": "ChromaDB (chroma_db/)",
        "ai_engine": "Gemini + LangGraph"
    }
