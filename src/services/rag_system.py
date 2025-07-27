import hashlib
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import logging
import httpx
import asyncio

import os
from dotenv import load_dotenv
load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_PORT = os.getenv("OLLAMA_PORT")
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.qdrant = None
        self.collection_name = "knowledge_base"
        self._initialize_qdrant()
    
    def _initialize_qdrant(self):
        """Inicializa conexão com Qdrant de forma lazy"""
        try:
            self.qdrant = QdrantClient(host="localhost", port=6333)
            if self.collection_name not in [c.name for c in self.qdrant.get_collections().collections]:
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
            logger.info("Qdrant inicializado com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao inicializar Qdrant: {e}. Tentando novamente mais tarde...")
            self.qdrant = None

    async def add_documents_to_rag(self, documents: List[str], metadatas: List[Dict] = None):
        try:
            if not self.qdrant:
                self._initialize_qdrant()
                if not self.qdrant:
                    logger.error("Não foi possível conectar ao Qdrant")
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
            if not self.qdrant:
                self._initialize_qdrant()
                if not self.qdrant:
                    logger.error("Não foi possível conectar ao Qdrant")
                    return []
            
            search_query = query
            if conversation_history:
                recent_messages = [msg["message"] for msg in conversation_history[-3:]]
                search_query = f"{query} {' '.join(recent_messages)}"
            query_embedding = self.embedding_model.encode([search_query])[0].tolist()
            search_result = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=n_results
            )
            return [hit.payload["document"] for hit in search_result]
        except Exception as e:
            logger.error(f"Erro na recuperação de contexto: {e}")
            return []

    async def generate_response(self, user_message: str, context: List[str], conversation_history: List[Dict] = None) -> str:
        try:
            context_text = "\n".join(context) if context else ""
            history_text = ""
            if conversation_history:
                for msg in conversation_history[-5:]:
                    role = "Cliente" if msg["message_type"] == "incoming" else "Assistente"
                    history_text += f"{role}: {msg['message']}\n"
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
            - Responda em português brasileiro
            - Mantenha o tom conversacional e profissional
            
            Resposta:
            """
            
            # Chamada assíncrona ao Ollama via load balancer
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{OLLAMA_URL}/api/chat",
                    json={
                        "model": MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "options": {"temperature": 0.7}
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result['message']['content'].strip()
                
        except Exception as e:
            logger.error(f"Erro na geração de resposta: {e}")
            return "Desculpe, houve um erro ao processar sua mensagem. Tente novamente em alguns instantes." 