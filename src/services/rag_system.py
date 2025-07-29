import hashlib
import json
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import logging
import httpx
import warnings

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self, ollama_url, ollama_model, qdrant_host, qdrant_port):
        self.ollama_url = ollama_url
        self.ollama_model = ollama_model
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.qdrant = None
        self.collection_name = "knowledge_base"
        # Removida a inicialização lazy do construtor
    
    async def initialize_qdrant(self) -> bool:
        """Inicializa conexão com Qdrant de forma assíncrona"""
        
        warnings.filterwarnings("ignore", category=FutureWarning, module="torch.nn.modules.module")

        try:
            logger.info("🔍 Inicializando Qdrant...")
            logger.info(f"Host: {self.qdrant_host}, Port: {self.qdrant_port}")
            
            self.qdrant = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
            
            # Testar conexão
            collections = self.qdrant.get_collections()
            logger.info(f"Conexão com Qdrant estabelecida. Coleções: {[c.name for c in collections.collections]}")
            
            # Verificar se a coleção existe
            if self.collection_name not in [c.name for c in collections.collections]:
                logger.info(f"Criando coleção '{self.collection_name}'...")
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                logger.info(f"Coleção '{self.collection_name}' criada com sucesso")
            else:
                logger.info(f"Coleção '{self.collection_name}' já existe")
                
            logger.info("✅ Qdrant inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Qdrant: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.qdrant = None
            return False

    async def test_ollama_connection(self) -> bool:
        """Testa a conexão com o Ollama"""
        try:
            logger.info("🧠 Testando conexão com Ollama...")
            logger.info(f"URL do Ollama: {self.ollama_url}")
            
            # Testar se o Ollama está respondendo
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    logger.info("📡 Testando conectividade básica...")
                    response = await client.get(f"{self.ollama_url}/api/tags")
                    response.raise_for_status()
                    logger.info("✅ Ollama está respondendo!")
                except Exception as e:
                    logger.error(f"❌ Ollama não está respondendo em {self.ollama_url}: {e}")
                    logger.error("💡 Verifique se o Ollama está rodando: ollama serve")
                    return False
                    
                logger.info("✅ Ollama conectado e funcionando!")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro geral ao conectar com Ollama: {e}")
            return False

    async def add_documents_to_rag(self, documents: List[str], metadatas: List[Dict] = None):
        try:
            if not self.qdrant:
                logger.error("Qdrant não foi inicializado. Chame initialize_qdrant() primeiro.")
                return
            
            embeddings = self.embedding_model.encode(documents).tolist()
            points = [
                PointStruct(
                    id=hashlib.md5(doc.encode()).hexdigest(),
                    vector=embedding,
                    payload={**(metadatas[i] if metadatas else {"source": "manual"}), "document": doc}
                )
                for i, (doc, embedding) in enumerate(zip(documents, embeddings))
            ]
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Adicionados {len(documents)} documentos ao RAG")
        except Exception as e:
            logger.error(f"Erro ao adicionar documentos: {e}")

    async def retrieve_context(self, query: str, conversation_history: List[Dict] = None, n_results: int = 3) -> List[str]:
        try:
            logger.info(f"Iniciando retrieve_context para query: '{query}'")
            
            # Verificar se o Qdrant está disponível
            if not self.qdrant:
                logger.error("Qdrant não foi inicializado. Chame initialize_qdrant() primeiro.")
                return []
            
            # Verificar se a coleção existe
            try:
                collections = self.qdrant.get_collections()
                collection_names = [c.name for c in collections.collections]
                logger.info(f"Coleções disponíveis: {collection_names}")
                
                if self.collection_name not in collection_names:
                    logger.warning(f"Coleção '{self.collection_name}' não encontrada. Criando...")
                    self.qdrant.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                    )
                    logger.info(f"Coleção '{self.collection_name}' criada com sucesso")
            except Exception as e:
                logger.error(f"Erro ao verificar/criar coleção: {e}")
                return []
            
            # Preparar query de busca
            search_query = query
            if conversation_history:
                recent_messages = [msg["content"] for msg in conversation_history[-3:]]
                search_query = f"{query} {' '.join(recent_messages)}"
                logger.info(f"Query expandida com histórico: '{search_query}'")
            
            # Gerar embedding
            try:
                query_embedding = self.embedding_model.encode([search_query])[0].tolist()
                logger.info(f"Embedding gerado com sucesso (dimensão: {len(query_embedding)})")
            except Exception as e:
                logger.error(f"Erro ao gerar embedding: {e}")
                return []
            
            # Buscar no Qdrant
            try:
                search_result = self.qdrant.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=n_results
                )
                logger.info(f"Busca realizada com sucesso. Resultados encontrados: {len(search_result)}")
                
                # Extrair documentos dos resultados
                documents = []
                for hit in search_result:
                    if "document" in hit.payload:
                        documents.append(hit.payload["document"])
                    else:
                        logger.warning(f"Resultado sem campo 'document': {hit.payload}")
                
                logger.info(f"Documentos recuperados: {len(documents)}")
                return documents
                
            except Exception as e:
                logger.error(f"\nErro na busca no Qdrant: {e}\n")
                return []
                
        except Exception as e:
            logger.error(f"Erro geral na recuperação de contexto: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    async def generate_response(self, user_message: str, context: List[str], conversation_history: List[Dict] = None) -> str:
        try:
            context_text = "\n".join(context) if context else ""
            history_text = ""
            if conversation_history:
                for msg in conversation_history[-5:]:
                    role = "Cliente" if msg["direction"] == "incoming" else "outgoing"
                    history_text += f"{role}: {msg['content']}\n"
            prompt = f"""
            Você é um assistente virtual prestativo e amigável que responde mensagens de WhatsApp.
            
            Base de Conhecimento:
            {context_text}
            
            Histórico da Conversa:
            {history_text}
            
            Mensagem atual do cliente: {user_message}
            
            Instruções:
            - Responda de forma útil, amigável e concisa
            - Use o conhecimento fornecido quando relevante
            - Mantenha o contexto da conversa
            - Se não souber algo, seja honesto
            - Não cumprimente o cliente, não diga "olá", "olá novamente" ou qualquer outra forma de cumprimento
            - Responda em português brasileiro
            - Mantenha o tom conversacional e profissional
            
            Resposta:
            """

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.ollama_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "options": {"temperature": 0.7}
                    }
                )
                response.raise_for_status()
                
                # Processar resposta streaming do Ollama
                try:
                    # O Ollama retorna Newline Delimited JSON (NDJSON)
                    # Cada linha é um JSON separado
                    lines = response.text.strip().split('\n')
                    full_content = ""
                    
                    for line in lines:
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                if 'message' in chunk and 'content' in chunk['message']:
                                    full_content += chunk['message']['content']
                            except json.JSONDecodeError:
                                logger.warning(f"Linha inválida ignorada: {line}")
                                continue
                    
                    if full_content:
                        return full_content.strip()
                    else:
                        logger.warning("Nenhum conteúdo extraído da resposta do Ollama")
                        return "Desculpe, não foi possível gerar uma resposta."
                        
                except Exception as e:
                    logger.error(f"Erro ao processar resposta streaming do Ollama: {e}")
                    logger.error(f"Resposta bruta: {response.text[:500]}...")
                    return "Desculpe, houve um erro ao processar sua mensagem."
                
        except Exception as e:
            logger.error(f"Erro na geração de resposta: {e}")
            return "Desculpe, houve um erro ao processar sua mensagem. Tente novamente em alguns instantes." 