from typing import List
from fastapi import APIRouter, BackgroundTasks
from datetime import datetime
from controllers.messages import receive_message, receive_wts_webhook
from models.schemas import IncomingMessage, OutgoingMessage, WtsWebhookMessage
from config import get_supabase_manager, get_rag_system

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
            "webhook": "/webhook/wts",
            "conversation": "/conversation/{phone_number}",
            "knowledge": "/knowledge",
            "health": "/health"
        }
    }

@router.get("/health")
async def health_check():
    """Health check completo do sistema"""
    try:
        # Obter instâncias
        supabase_manager = get_supabase_manager()
        rag_system = get_rag_system()
        
        # Verificar Supabase
        supabase_healthy = await supabase_manager.health_check()
        
        # Verificar Ollama
        ollama_healthy = await rag_system.test_ollama_connection()
        
        # Determinar status geral
        all_healthy = supabase_healthy and ollama_healthy
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "supabase": "healthy" if supabase_healthy else "unhealthy",
                "ollama": "healthy" if ollama_healthy else "unhealthy"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "services": {
                "supabase": "unknown",
                "ollama": "unknown"
            }
        }

@router.post("/message")
async def receive_message_endpoint(message: IncomingMessage, background_tasks: BackgroundTasks):
    print('mensagem recebida no endpoint')
    result = await receive_message(message, background_tasks)
    return result

@router.post("/webhook/wts")
async def receive_wts_webhook_endpoint(webhook: WtsWebhookMessage, background_tasks: BackgroundTasks):
    """Endpoint para receber webhooks do WTS"""
    print('Webhook do WTS recebido no endpoint')
    result = await receive_wts_webhook(webhook, background_tasks)
    return result

@router.post("/knowledge")
async def add_knowledge_endpoint(documents: List[str], source: str = "manual"):
    print('inserindo doc na base de conhecimento', documents)
    from controllers.knowledge import add_knowledge
    result = await add_knowledge(documents, source)
    return result 