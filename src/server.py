import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from config import (
    get_supabase_manager, 
    get_rag_system, 
    get_external_api,
    validate_config,
    SERVER_HOST,
    SERVER_PORT
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    try:
        print("\n🚀 Iniciando servidor...")
        
        # Validar configurações
        print("⚙️  Validando configurações...", end="")
        validate_config()
        print("OK")
        
        # Obter instâncias globais
        supabase_manager = get_supabase_manager()
        rag_system = get_rag_system()
        external_api = get_external_api()
        
        # Inicializar Supabase
        print("📊 Conectando ao Supabase...", end="")
        await supabase_manager.initialize()
        print("OK")
        
        # Inicializar RAG System
        print("🧠 Inicializando RAG System... OK")
        
        # Testar conexão com Ollama
        print("🤖 Testando conexão com Ollama...", end="")
        ollama_ok = await rag_system.test_ollama_connection()
        if not ollama_ok:
            raise Exception("Ollama não está funcionando corretamente")
        print("OK")
        
        # Inicializar WTS API
        print("📱 Verificando WTS API...", end="")
        await external_api.test_connection()
        print("OK")
        
        print("\n🎉 Servidor iniciado com sucesso!\n")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar servidor: {e}")
        raise e
    
    yield
    
    # Shutdown
    print("🛑 Desligando servidor...")
    # Aqui você pode adicionar cleanup se necessário
    print("✅ Servidor desligado!")

app = FastAPI(title="WhatsApp RAG Bot com Supabase", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("server:app", host=SERVER_HOST, port=SERVER_PORT, reload=True) 