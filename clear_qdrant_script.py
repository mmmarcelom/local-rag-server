#!/usr/bin/env python3
"""
Script para Limpar Dados do Qdrant
==================================

Este script permite limpar todos os dados da base de conhecimento do Qdrant.
Pode ser executado diretamente ou usado como referência para outras implementações.

Uso:
    python clear_qdrant_script.py
    # ou no Jupyter:
    %run clear_qdrant_script.py
"""

import requests
import json
from typing import Optional
from datetime import datetime

# Configuração da API
BASE_URL = "http://localhost:8000"  # Ajuste conforme necessário

def test_connection():
    """Testa a conexão com o servidor"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Servidor está funcionando!")
            print(f"Status: {response.json()['status']}")
            return True
        else:
            print(f"❌ Erro na conexão: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

def clear_knowledge_base() -> Optional[dict]:
    """
    Limpa todos os dados da base de conhecimento via API
    
    Returns:
        dict: Resultado da operação ou None em caso de erro
    """
    try:
        url = f"{BASE_URL}/knowledge"
        
        print("🗑️ Iniciando limpeza da base de conhecimento...")
        
        response = requests.delete(url)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso! {result.get('message', 'Base limpa')}")
            return result
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao limpar base de conhecimento: {e}")
        return None

def get_knowledge_stats() -> Optional[dict]:
    """
    Obtém estatísticas da base de conhecimento (se disponível)
    
    Returns:
        dict: Estatísticas ou None em caso de erro
    """
    try:
        url = f"{BASE_URL}/health"
        
        print("📊 Verificando status dos serviços...")
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"🔍 Status Geral: {data.get('status', 'unknown')}")
            print(f"📋 Serviços: {data.get('services', {})}")
            return data
        else:
            print(f"❌ Erro ao obter estatísticas: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")
        return None

def clear_qdrant_direct(host: str = "localhost", port: int = 6333, collection_name: str = "knowledge_base"):
    """
    Limpa o Qdrant diretamente (sem usar a API)
    
    Args:
        host: Host do Qdrant
        port: Porta do Qdrant
        collection_name: Nome da coleção
    """
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.http.models import Distance, VectorParams
        
        print(f"🔗 Conectando diretamente ao Qdrant em {host}:{port}...")
        
        client = QdrantClient(host=host, port=port)
        
        # Verificar se a coleção existe
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if collection_name in collection_names:
            print(f"🗑️ Deletando coleção '{collection_name}'...")
            client.delete_collection(collection_name)
            print(f"✅ Coleção '{collection_name}' deletada")
        
        # Recriar a coleção vazia
        print(f"🔄 Recriando coleção '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"✅ Coleção '{collection_name}' recriada com sucesso!")
        return True
        
    except ImportError:
        print("❌ Biblioteca qdrant-client não encontrada")
        print("💡 Instale com: pip install qdrant-client")
        return False
    except Exception as e:
        print(f"❌ Erro ao limpar Qdrant diretamente: {e}")
        return False

def confirm_clear():
    """Solicita confirmação do usuário antes de limpar"""
    print("\n⚠️ ATENÇÃO: Esta operação irá deletar TODOS os dados da base de conhecimento!")
    print("📝 Esta ação não pode ser desfeita.")
    
    while True:
        response = input("\n🤔 Tem certeza que deseja continuar? (sim/não): ").lower().strip()
        
        if response in ['sim', 's', 'yes', 'y']:
            return True
        elif response in ['não', 'nao', 'n', 'no']:
            return False
        else:
            print("❌ Por favor, responda 'sim' ou 'não'")

def main():
    """Função principal do script"""
    print("=" * 60)
    print("SCRIPT PARA LIMPAR DADOS DO QDRANT")
    print("=" * 60)
    print()
    
    # Testar conexão
    print("1. Testando conexão com o servidor:")
    if not test_connection():
        print("❌ Não foi possível conectar ao servidor.")
        print("💡 Verifique se o servidor está rodando na porta 8000")
        return
    
    # Obter estatísticas
    print("\n2. Verificando status dos serviços:")
    stats = get_knowledge_stats()
    
    # Solicitar confirmação
    if not confirm_clear():
        print("❌ Operação cancelada pelo usuário")
        return
    
    # Limpar via API
    print("\n3. Limpando base de conhecimento via API:")
    result = clear_knowledge_base()
    
    if result and result.get('status') == 'success':
        print("✅ Base de conhecimento limpa com sucesso via API!")
    else:
        print("❌ Falha ao limpar via API. Tentando limpeza direta...")
        
        # Tentar limpeza direta
        print("\n4. Tentando limpeza direta do Qdrant:")
        if clear_qdrant_direct():
            print("✅ Base de conhecimento limpa com sucesso via conexão direta!")
        else:
            print("❌ Falha na limpeza direta também")
    
    print("\n" + "=" * 60)
    print("OPERAÇÃO CONCLUÍDA")
    print("=" * 60)

if __name__ == "__main__":
    main() 