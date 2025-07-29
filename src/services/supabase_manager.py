import os
import uuid
import logging
import requests
from models.schemas import Message
from datetime import datetime, timezone
from typing import List, Dict, Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class SupabaseManager:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self._client = None
    
    async def initialize(self):
        """Inicializa conexão com Supabase"""
        if self._client is not None:
            return True
            
        try:
            self._client = create_client(self.url, self.key)
            # Testar conexão
            self._client.table("conversations").select("id").limit(1).execute()
            logger.info("Conexão com Supabase estabelecida com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar com Supabase: {e}")
            raise ConnectionError(f"Não foi possível conectar ao Supabase: {e}")
    
    async def health_check(self) -> bool:
        """Verifica se a conexão com Supabase está saudável"""
        try:
            if self._client is None:
                return False
            self._client.table("conversations").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Health check falhou: {e}")
            return False
    
    @property
    def supabase(self) -> Client:
        """Retorna o cliente Supabase"""
        if self._client is None:
            raise ConnectionError("Supabase não foi inicializado. Chame initialize() primeiro.")
        return self._client
    
    async def get_or_create_conversation(self, phone_number: str, user_name: str = None) -> str:
        try:
            result = self.supabase.table("conversations").select("*").eq("phone_number", phone_number).order("created_at", desc=True).limit(1).execute()
            if result.data:
                conversation_id = result.data[0]["id"]
                logger.info(f"Conversa existente encontrada: {conversation_id}")
                return conversation_id
            conversation_data = {
                "id": str(uuid.uuid4()),
                "phone_number": phone_number,
                "user_name": user_name,
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            result = self.supabase.table("conversations").insert(conversation_data).execute()
            conversation_id = result.data[0]["id"]
            logger.info(f"Nova conversa criada: {conversation_id}")
            return conversation_id
        except Exception as e:
            logger.error(f"Erro ao gerenciar conversa: {e}")
            raise ConnectionError(f"Erro ao gerenciar conversa no Supabase: {e}")
    
    def message_to_json(self, message: Message):
        return {
            "id": str(uuid.uuid4()),
            "conversation_id": message.conversation_id,
            "platform": message.platform,
            "sender": message.sender,
            "receiver": message.receiver,
            "message_type": message.message_type,
            "external_message_id": message.id,
            "content": message.content,
            "metadata": message.metadata or {},
            "direction": message.direction,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

    async def save_message(self, message: Message):
        message_data = self.message_to_json(message)
        
        try:
            result = self.supabase.table("messages").insert(message_data).execute()
            logger.info(f"Mensagem salva: {result.data[0]['id']}")
            return result.data[0]["id"]
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {e}")
            raise ConnectionError(f"Erro ao salvar mensagem no Supabase: {e}")
    
    async def get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        try:
            result = self.supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=True).limit(limit).execute()
            return list(reversed(result.data))
        except Exception as e:
            logger.error(f"Erro ao recuperar histórico: {e}")
            raise ConnectionError(f"Erro ao recuperar histórico do Supabase: {e}")
    
    async def update_conversation(self, conversation_id: str, updates: dict):
        try:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            result = self.supabase.table("conversations").update(updates).eq("id", conversation_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"Erro ao atualizar conversa: {e}")
            return None 