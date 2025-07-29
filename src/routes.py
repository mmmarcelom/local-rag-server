from typing import List, Dict, Any
from fastapi import APIRouter, BackgroundTasks
from datetime import datetime
from controllers.messages import receive_webhook
from models.schemas import WhatsappMessage, WtsWebhookData
from config import get_supabase_manager, get_rag_system, get_external_api
import asyncio

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
            "health": "/health",
            "test_services": "/test-services"
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

@router.get("/test-services")
async def test_all_services():
    """Testa todos os serviços de forma assíncrona e retorna resultados detalhados"""
    try:
        # Obter instâncias
        supabase_manager = get_supabase_manager()
        rag_system = get_rag_system()
        external_api = get_external_api()
        
        # Definir todas as tarefas de teste com timeouts
        tasks = {
            "supabase": asyncio.wait_for(supabase_manager.initialize(), timeout=30),
            "qdrant": asyncio.wait_for(rag_system.initialize_qdrant(), timeout=30),
            "ollama": asyncio.wait_for(rag_system.test_ollama_connection(), timeout=30),
            "wts_api": asyncio.wait_for(external_api.test_connection(), timeout=30)
        }
        
        # Executar todas as tarefas em paralelo
        task_results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Mapear resultados
        results = {}
        all_success = True
        
        for service_name, result in zip(tasks.keys(), task_results):
            if isinstance(result, asyncio.TimeoutError):
                results[service_name] = {
                    "status": "timeout",
                    "message": "Timeout após 30s",
                    "success": False
                }
                all_success = False
            elif isinstance(result, Exception):
                results[service_name] = {
                    "status": "error",
                    "message": str(result),
                    "success": False
                }
                all_success = False
            else:
                results[service_name] = {
                    "status": "success" if result else "failed",
                    "message": "Serviço funcionando" if result else "Serviço não respondeu",
                    "success": bool(result)
                }
                if not result:
                    all_success = False
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy" if all_success else "unhealthy",
            "services": results,
            "summary": {
                "total_services": len(results),
                "successful_services": sum(1 for r in results.values() if r["success"]),
                "failed_services": sum(1 for r in results.values() if not r["success"])
            }
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "error",
            "error": str(e),
            "services": {},
            "summary": {
                "total_services": 0,
                "successful_services": 0,
                "failed_services": 0
            }
        }

@router.post("/message")
async def receive_message_endpoint(message: WhatsappMessage, background_tasks: BackgroundTasks):
    return get_external_api().send_message(message)

@router.post("/webhook/wts")
async def receive_wts_webhook_endpoint(webhook_data: WtsWebhookData, background_tasks: BackgroundTasks):    
    return await receive_webhook(webhook_data, background_tasks)

@router.post("/knowledge")
async def add_knowledge_endpoint(documents: List[str], source: str = "manual"):
    print('inserindo doc na base de conhecimento', documents)
    from controllers.knowledge import add_knowledge
    result = await add_knowledge(documents, source)
    return result 