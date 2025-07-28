import uvicorn
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from config import (
    get_supabase_manager, 
    get_rag_system, 
    get_external_api,
    validate_env,
    SERVER_HOST,
    SERVER_PORT
)

async def test_services():
    """Testa todos os serviços de forma assíncrona e paralela"""
        # Obter instâncias globais

    supabase_manager = get_supabase_manager()
    rag_system = get_rag_system()
    external_api = get_external_api()
    
    # Definir todas as tarefas de teste
    tasks = {
        "supabase": supabase_manager.initialize(),
        "qdrant": rag_system.initialize_qdrant(),
        "ollama": rag_system.test_ollama_connection(),
        "wts_api": external_api.test_connection()
    }
    
    # Executar todas as tarefas em paralelo
    results = {}
    
    try:
        # Executar todas as tarefas simultaneamente
        task_results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Mapear resultados para nomes dos serviços
        for service_name, result in zip(tasks.keys(), task_results):
            if isinstance(result, Exception):
                results[service_name] = {
                    "status": "error",
                    "message": str(result),
                    "success": False
                }
            else:
                results[service_name] = {
                    "status": "success" if result else "failed",
                    "message": "Serviço funcionando" if result else "Serviço não respondeu",
                    "success": bool(result)
                }
        
        return results
        
    except Exception as e:
        print(f"❌")
        print(f"Erro durante testes paralelos: {e}")
        return {
            "error": {
                "status": "error",
                "message": str(e),
                "success": False
            }
        }

def check_services(results):
    """Analisa e compara os resultados de todos os serviços"""
    
    all_success = True
    services = []
    
    for service_name, result in results.items():
        if result["success"]:
            services.append(f"   - {service_name.upper()}: ✅")
        else:
            all_success = False
            services.append(f"   - {service_name.upper()}: ❌")      
    
    if all_success:
        print("✅")
        print(f"{'\n'.join(services)}")
        return True
    else:
        print("⚠️")
        print(f"{'\n'.join(services)}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    try:
        print("\n🚀 Iniciando servidor...\n\n⚙️  Validando configurações: ", end="")
        
        # Validar configurações
        validate_env()
        print("✅\n⚙️  Verificando serviços: ", end="")
        
        results = await test_services()
        if not check_services(results):
            raise Exception("Um ou mais serviços não estão funcionando corretamente")
        
        print("\n🎉 Servidor iniciado com sucesso!\n")
        print("Ignorando warnings de torch.nn.modules.module, verificar isso depois")
        
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