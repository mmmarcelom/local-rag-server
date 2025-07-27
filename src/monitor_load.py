#!/usr/bin/env python3
"""
Script para monitorar a distribuição de carga entre os containers Ollama
"""

import asyncio
import httpx
import time
import os
from collections import defaultdict

class OllamaLoadMonitor:
    def __init__(self):
        # Detectar modo baseado nas variáveis de ambiente
        self.ollama_host = os.getenv("OLLAMA_HOST", "localhost")
        self.ollama_port = os.getenv("OLLAMA_PORT", "11434")
        self.ollama_mode = os.getenv("OLLAMA_MODE", "single-ollama")
        
        # Configurar endpoints baseado no modo
        if self.ollama_mode == "multi-ollama":
            self.ollama_instances = [
                "http://localhost:11434",  # ollama-1
                "http://localhost:11435",  # ollama-2
                "http://localhost:11436",  # ollama-3
            ]
            self.load_balancer = f"http://{self.ollama_host}:{self.ollama_port}"
        else:
            # Modo single-ollama
            self.ollama_instances = [
                f"http://{self.ollama_host}:{self.ollama_port}"
            ]
            self.load_balancer = f"http://{self.ollama_host}:{self.ollama_port}"
        
        self.request_counts = defaultdict(int)
        
    async def test_single_instance(self, url: str, instance_name: str):
        """Testa uma instância individual do Ollama"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{url}/api/tags")
                if response.status_code == 200:
                    print(f"✅ {instance_name}: OK")
                    return True
                else:
                    print(f"❌ {instance_name}: Erro {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ {instance_name}: {e}")
            return False
    
    async def test_load_balancer(self):
        """Testa o load balancer ou Ollama único"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if self.ollama_mode == "multi-ollama":
                    response = await client.get(f"{self.load_balancer}/health")
                else:
                    response = await client.get(f"{self.load_balancer}/api/tags")
                
                if response.status_code == 200:
                    print(f"✅ {'Load Balancer' if self.ollama_mode == 'multi-ollama' else 'Ollama'}: OK")
                    return True
                else:
                    print(f"❌ {'Load Balancer' if self.ollama_mode == 'multi-ollama' else 'Ollama'}: Erro {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ {'Load Balancer' if self.ollama_mode == 'multi-ollama' else 'Ollama'}: {e}")
            return False
    
    async def send_test_request(self, request_id: int):
        """Envia uma request de teste via load balancer ou Ollama único"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                start_time = time.time()
                response = await client.post(
                    f"{self.load_balancer}/api/chat",
                    json={
                        "model": "llama3.2",
                        "messages": [{"role": "user", "content": f"Responda apenas: 'Request {request_id} processada'"}],
                        "options": {"temperature": 0.1}
                    }
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Request {request_id}: {result['message']['content']} ({(end_time - start_time):.2f}s)")
                    return True
                else:
                    print(f"❌ Request {request_id}: Erro {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Request {request_id}: {e}")
            return False
    
    async def run_health_check(self):
        """Executa verificação de saúde de todos os serviços"""
        print(f"🔍 Verificando saúde dos serviços (Modo: {self.ollama_mode})...")
        print("-" * 50)
        
        # Testar instâncias individuais
        for i, url in enumerate(self.ollama_instances, 1):
            instance_name = f"Ollama-{i}" if self.ollama_mode == "multi-ollama" else "Ollama"
            await self.test_single_instance(url, instance_name)
        
        print()
        await self.test_load_balancer()
        print("-" * 50)
    
    async def run_load_test(self, num_requests: int = 10):
        """Executa teste de carga"""
        print(f"🚀 Executando teste de carga com {num_requests} requests...")
        print("-" * 50)
        
        start_time = time.time()
        
        # Criar tasks para requests simultâneas
        tasks = []
        for i in range(num_requests):
            task = asyncio.create_task(self.send_test_request(i + 1))
            tasks.append(task)
        
        # Aguardar todas as requests
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        successful_requests = sum(1 for r in results if r is True)
        
        print("-" * 50)
        print(f"📊 Resultados do teste de carga:")
        print(f"   Modo: {self.ollama_mode}")
        print(f"   Requests enviadas: {num_requests}")
        print(f"   Requests bem-sucedidas: {successful_requests}")
        print(f"   Taxa de sucesso: {(successful_requests/num_requests)*100:.1f}%")
        print(f"   Tempo total: {total_time:.2f}s")
        print(f"   Requests por segundo: {num_requests/total_time:.2f}")
        print(f"   Tempo médio por request: {total_time/num_requests:.2f}s")

async def main():
    monitor = OllamaLoadMonitor()
    
    # Verificação de saúde
    await monitor.run_health_check()
    
    print()
    
    # Teste de carga
    await monitor.run_load_test(10)

if __name__ == "__main__":
    asyncio.run(main()) 