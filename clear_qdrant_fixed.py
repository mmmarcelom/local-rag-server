#!/usr/bin/env python3
"""
Script Corrigido para Limpar Dados do Qdrant
===========================================

Este script corrige o problema com o seletor de pontos do Qdrant.
"""

def clear_qdrant(host: str = "localhost", port: int = 6333, collection_name: str = "knowledge_base"):
    """
    Limpa o Qdrant diretamente (sem usar a API)
    
    Args:
        host: Host do Qdrant
        port: Porta do Qdrant
        collection_name: Nome da coleção
    """
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.http.models import PointIdsList
        
        print(f"🔗 Conectando diretamente ao Qdrant em {host}:{port}...")
        
        client = QdrantClient(host=host, port=port)
        
        # Verificar se a coleção existe
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if collection_name not in collection_names:
            print(f"⚠️ Coleção '{collection_name}' não encontrada")
            print(f"📋 Coleções disponíveis: {collection_names}")
            return False
        
        # Obter informações da coleção
        collection_info = client.get_collection(collection_name)
        print(f"📊 Coleção '{collection_name}' tem {collection_info.points_count} pontos")
        
        if collection_info.points_count == 0:
            print(f"✅ Coleção '{collection_name}' já está vazia!")
            return True
        
        # Deletar todos os pontos da coleção
        print(f"🗑️ Deletando todos os pontos da coleção '{collection_name}'...")
        
        # Método 1: Tentar deletar com filtro vazio (deleta tudo)
        try:
            client.delete(
                collection_name=collection_name,
                points_selector=PointIdsList(points=[])  # Lista vazia deleta tudo
            )
            print(f"✅ Coleção '{collection_name}' limpa com sucesso!")
            return True
        except Exception as e1:
            print(f"⚠️ Método 1 falhou: {e1}")
            
            # Método 2: Recriar a coleção
            try:
                print(f"🔄 Tentando recriar a coleção '{collection_name}'...")
                
                # Deletar a coleção existente
                client.delete_collection(collection_name)
                print(f"🗑️ Coleção '{collection_name}' deletada")
                
                # Recriar a coleção vazia
                from qdrant_client.http.models import Distance, VectorParams
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                print(f"✅ Coleção '{collection_name}' recriada com sucesso!")
                return True
                
            except Exception as e2:
                print(f"❌ Método 2 também falhou: {e2}")
                return False
        
    except ImportError:
        print("❌ Biblioteca qdrant-client não encontrada")
        print("💡 Instale com: pip install qdrant-client")
        return False
    except Exception as e:
        print(f"❌ Erro ao limpar Qdrant diretamente: {e}")
        return False

def clear_qdrant_simple(host: str = "localhost", port: int = 6333, collection_name: str = "knowledge_base"):
    """
    Versão simplificada que apenas recria a coleção
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
        print(f"❌ Erro ao limpar Qdrant: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SCRIPT CORRIGIDO PARA LIMPAR QDRANT")
    print("=" * 60)
    print()
    
    # Usar a versão simplificada que é mais confiável
    success = clear_qdrant_simple()
    
    if success:
        print("\n✅ Qdrant limpo com sucesso!")
    else:
        print("\n❌ Falha ao limpar Qdrant")
    
    print("\n" + "=" * 60) 