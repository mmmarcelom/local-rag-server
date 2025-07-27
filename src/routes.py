from typing import List
from fastapi import APIRouter, BackgroundTasks
from datetime import datetime

from controllers.messages import receive_message, get_conversation
from models.schemas import IncomingMessage, OutgoingMessage

router = APIRouter()

@router.get("/")
async def hello():
    return {
        "status": "online",
        "message": "Local RAG Server está funcionando!",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "message": "/message",
            "conversation": "/conversation/{phone_number}",
            "knowledge": "/knowledge"
        }
    }

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/message")
async def receive_message_endpoint(message: IncomingMessage, background_tasks: BackgroundTasks):
    print('mensagem recebida', message)
    result = await receive_message(message, background_tasks)
    return result

@router.get("/conversation/{phone_number}")
async def get_conversation_endpoint(phone_number: str):
    print('buscando conversa', phone_number)
    result = await get_conversation(phone_number)
    return result

@router.post("/knowledge")
async def add_knowledge_endpoint(documents: List[str], source: str = "manual"):
    print('inserindo doc na base de conhecimento', documents)
    from controllers.knowledge import add_knowledge
    result = await add_knowledge(documents, source)
    return result