from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Schema para o webhook do WTS
class WtsWebhookContent(BaseModel):
    id: str
    senderId: Optional[str] = None
    createdAt: str
    updatedAt: str
    editedAt: Optional[str] = None
    type: str
    active: bool
    sessionId: str
    templateId: Optional[str] = None
    userId: Optional[str] = None
    timestamp: str
    text: str
    direction: str
    status: str
    origin: str
    readContactAt: Optional[str] = None
    fileId: Optional[str] = None
    refId: Optional[str] = None
    waitingOptIn: bool
    details: Dict[str, Any]

class WtsWebhookDetails(BaseModel):
    file: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    contact: Optional[Dict[str, Any]] = None
    errors: Optional[Dict[str, Any]] = None
    transcription: Optional[Dict[str, Any]] = None

class WtsWebhookMessage(BaseModel):
    eventType: str
    date: str
    content: WtsWebhookContent
    changeMetadata: Optional[Dict[str, Any]] = None

# Schema simplificado para uso interno (mantém compatibilidade)
class IncomingMessage(BaseModel):
    phone_number: str
    message: str
    message_id: str
    timestamp: Optional[str] = None
    user_name: Optional[str] = None

class OutgoingMessage(BaseModel):
    phone_number: str
    message: str
    conversation_id: Optional[str] = None

# Função utilitária para converter webhook do WTS para formato interno
def convert_wts_webhook_to_incoming_message(webhook: WtsWebhookMessage) -> IncomingMessage:
    """Converte webhook do WTS para formato interno"""
    # Extrair número do telefone do sessionId ou outros campos
    # Por enquanto, vamos usar o sessionId como identificador
    phone_number = webhook.content.sessionId
    
    return IncomingMessage(
        phone_number=phone_number,
        message=webhook.content.text,
        message_id=webhook.content.id,
        timestamp=webhook.content.timestamp,
        user_name=None  # Pode ser extraído de outros campos se disponível
    ) 