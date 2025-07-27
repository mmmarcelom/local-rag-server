"""
Configurações globais e instâncias compartilhadas
"""
import os
from dotenv import load_dotenv
from services.supabase_manager import SupabaseManager
from services.rag_system import RAGSystem
from services.wts_api import WtsAPIService

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do ambiente
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_PUBLIC_URL")
SUPABASE_KEY = os.getenv("ANON_KEY")

# Configurações do Ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_PORT = os.getenv("OLLAMA_PORT")
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

# Configurações do WTS API
WTS_API_TOKEN = os.getenv("WTS_API_TOKEN")

# Configurações do Qdrant
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = os.getenv("QDRANT_PORT")

# Configurações do Redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

# Configurações do servidor
SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = os.getenv("SERVER_PORT")

_supabase_manager = None
_rag_system = None
_external_api = None

def get_supabase_manager() -> SupabaseManager:
    """Retorna instância global do SupabaseManager"""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseManager(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_manager

def get_rag_system() -> RAGSystem:
    """Retorna instância global do RAGSystem"""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem(
            ollama_url=OLLAMA_URL,
            ollama_model=OLLAMA_MODEL,
            qdrant_host=QDRANT_HOST,
            qdrant_port=QDRANT_PORT
        )
    return _rag_system

def get_external_api() -> WtsAPIService:
    """Retorna instância global do WtsAPIService"""
    global _external_api
    if _external_api is None:
        _external_api = WtsAPIService(WTS_API_TOKEN)
    return _external_api

def validate_config():
    """Valida se todas as configurações necessárias estão presentes"""
    errors = []
    
    if not SUPABASE_URL:
        errors.append("SUPABASE_PUBLIC_URL não configurado")
    
    if not SUPABASE_KEY:
        errors.append("ANON_KEY não configurado")
    
    if not WTS_API_TOKEN:
        errors.append("WTS_API_TOKEN não configurado")
    
    if errors:
        raise ValueError(f"Configurações inválidas: {'; '.join(errors)}")
    
    return True