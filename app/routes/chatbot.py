from fastapi import APIRouter
from app.schemas.chatbot import ChatRequest, ChatResponse
from app.services.chatbot_service import ChatbotService

router = APIRouter(
    prefix="/chat",
    tags=["AI Chatbot"]
)


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Chat with Student Management AI",
    description="Submits a query to the LangGraph agent which dynamically routes to SQLite or ChromaDB vector store."
)
def chat(request: ChatRequest):
    return ChatbotService.process_message(request.message)
