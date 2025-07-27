#!/usr/bin/env python3
"""
Script de diagnóstico para verificar o status do Ollama
"""
import asyncio
import httpx
import subprocess
import sys
from config import OLLAMA_MODEL, OLLAMA_HOST, OLLAMA_PORT, OLLAMA_URL

async def check_ollama_installation():
    """Verifica se o Ollama está instalado"""
    print("🔍 Verificando instalação do Ollama...")
    
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama instalado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama não está instalado ou não está no PATH")
            return False
    except FileNotFoundError:
        print("❌ Ollama não encontrado no sistema")
        print("💡 Instale em: https://ollama.ai")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar instalação: {e}")
        return False

async def check_ollama_service():
    """Verifica se o serviço Ollama está rodando"""
    print(f"🔍 Verificando se Ollama está rodando em {OLLAMA_URL}...")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                print("✅ Ollama está respondendo!")
                return True
            else:
                print(f"❌ Ollama respondeu com status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Ollama não está respondendo: {e}")
        print("💡 Inicie o Ollama com: ollama serve")
        return False

async def check_models():
    """Verifica modelos disponíveis"""
    print("🔍 Verificando modelos disponíveis...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            models_data = response.json()
            
            available_models = [model["name"] for model in models_data.get("models", [])]
            print(f"📋 Modelos disponíveis: {available_models}")
            
            if not available_models:
                print("⚠️ Nenhum modelo encontrado")
                print("💡 Baixe um modelo: ollama pull llama3.2")
                return False
            
            if OLLAMA_MODEL in available_models:
                print(f"✅ Modelo {OLLAMA_MODEL} encontrado!")
                return True
            else:
                print(f"❌ Modelo {OLLAMA_MODEL} não encontrado")
                print(f"💡 Baixe o modelo: ollama pull {OLLAMA_MODEL}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao verificar modelos: {e}")
        return False

async def test_model_generation():
    """Testa geração de resposta"""
    print("🔍 Testando geração de resposta...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [{"role": "user", "content": "Responda apenas 'OK'"}],
                    "options": {"temperature": 0.1, "max_tokens": 5}
                }
            )
            
            if response.status_code == 200:
                print("✅ Geração de resposta funcionando!")
                return True
            else:
                print(f"❌ Erro na geração: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao testar geração: {e}")
        return False

async def main():
    """Executa todos os diagnósticos"""
    print("🚀 Diagnóstico do Ollama")
    print("=" * 50)
    
    # Verificar instalação
    installed = await check_ollama_installation()
    if not installed:
        print("\n❌ Ollama não está instalado. Instale em: https://ollama.ai")
        return
    
    # Verificar serviço
    service_ok = await check_ollama_service()
    if not service_ok:
        print("\n❌ Ollama não está rodando. Execute: ollama serve")
        return
    
    # Verificar modelos
    models_ok = await check_models()
    if not models_ok:
        print(f"\n❌ Modelo {OLLAMA_MODEL} não encontrado. Execute: ollama pull {OLLAMA_MODEL}")
        return
    
    # Testar geração
    generation_ok = await test_model_generation()
    if not generation_ok:
        print("\n❌ Geração de resposta falhou")
        return
    
    print("\n🎉 Ollama está funcionando perfeitamente!")
    print("✅ Você pode iniciar o servidor agora!")

if __name__ == "__main__":
    asyncio.run(main()) 