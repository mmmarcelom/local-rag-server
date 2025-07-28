from typing import List, Dict, Any
from fastapi import APIRouter, BackgroundTasks
from datetime import datetime
from controllers.messages import receive_message
from models.schemas import IncomingMessage
from config import get_supabase_manager, get_rag_system, get_external_api

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
    result = await receive_message(message, background_tasks)
    return result

@router.post("/webhook/wts")
async def receive_wts_webhook_endpoint(webhook_data: Dict[str, Any], background_tasks: BackgroundTasks):    
    try:
        # Extrair dados do webhook
        contact = webhook_data.get("contact", {})
        last_message = webhook_data.get("lastMessage", {})
        
        # Extrair número do telefone
        phone_number = contact.get("phonenumber", "").replace("+55|", "")
        
        # Extrair mensagem
        message_text = webhook_data.get("lastContactMessage", "")
        
        # Extrair ID da mensagem
        message_id = last_message.get("id", "")
        
        # Extrair nome do usuário
        user_name = contact.get("name", "")
        
        # Criar IncomingMessage
        message_data = IncomingMessage(
            phone_number=phone_number,
            message=message_text,
            message_id=message_id,
            user_name=user_name
        )
        
        # Processar mensagem
        result = await receive_message(message_data, background_tasks)
        return result
        
    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        return {"status": "error", "message": f"Erro ao processar webhook: {str(e)}"}

@router.post("/knowledge")
async def add_knowledge_endpoint(documents: List[str], source: str = "manual"):
    print('inserindo doc na base de conhecimento', documents)
    from controllers.knowledge import add_knowledge
    result = await add_knowledge(documents, source)
    return result 