import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional
import logging
from supabase import create_client, Client
import os
import requests
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_PUBLIC_URL")
SUPABASE_KEY = os.getenv("ANON_KEY")
OLLAMA_URL = os.getenv("OLLAMA_URL")

def gerar_resposta_ollama(prompt):
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": "llama3.2",
            "messages": [{"role": "user", "content": prompt}],
            "options": {"temperature": 0.7, "max_tokens": 500}
        }
    )
    response.raise_for_status()
    return response.json()["message"]["content"]

class SupabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
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
            return str(uuid.uuid4())
    
    async def save_message(self, conversation_id: str, phone_number: str, message: str, message_type: str, message_id: str = None, metadata: dict = None):
        try:
            message_data = {
                "id": str(uuid.uuid4()),
                "conversation_id": conversation_id,
                "phone_number": phone_number,
                "message": message,
                "message_type": message_type,
                "external_message_id": message_id,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            result = self.supabase.table("messages").insert(message_data).execute()
            logger.info(f"Mensagem salva: {result.data[0]['id']}")
            return result.data[0]["id"]
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {e}")
            return None
    
    async def get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        try:
            result = self.supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=True).limit(limit).execute()
            return list(reversed(result.data))
        except Exception as e:
            logger.error(f"Erro ao recuperar histórico: {e}")
            return []
    
    async def update_conversation(self, conversation_id: str, updates: dict):
        try:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            result = self.supabase.table("conversations").update(updates).eq("id", conversation_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"Erro ao atualizar conversa: {e}")
            return None 