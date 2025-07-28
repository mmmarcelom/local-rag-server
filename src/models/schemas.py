from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Schema para o webhook real do WTS
class WtsSession(BaseModel):
    id: str
    createdAt: str
    departmentId: str
    userId: str
    number: str
    utm: Optional[str] = None

class WtsChannel(BaseModel):
    id: str
    key: str
    platform: str
    displayName: str

class WtsContact(BaseModel):
    id: str
    name: str
    first_name: Optional[str] = None
    phonenumber: str
    display_phonenumber: str
    email: Optional[str] = None
    instagram: Optional[str] = None
    tags: Optional[Any] = None
    annotation: str
    metadata: Dict[str, Any]
    rg: Optional[str] = None
    cep: Optional[str] = None
    pa_s: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    cpf_62: Optional[str] = None
    estado: Optional[str] = None
    profiss_o: Optional[str] = None
    complemento: Optional[str] = None
    endere_o_53: Optional[str] = None
    estado_civil: Optional[str] = None

class WtsLastMessage(BaseModel):
    id: str
    createdAt: str
    type: str
    text: str
    fileId: Optional[str] = None
    file: Optional[Any] = None

class WtsLastMessagesAggregated(BaseModel):
    text: str
    files: list

class WtsWebhookData(BaseModel):
    responseKeys: list
    sessionId: str
    session: WtsSession
    channel: WtsChannel
    contact: WtsContact
    questions: Dict[str, Any]
    menus: Dict[str, Any]
    templates: Dict[str, Any]
    metadata: Dict[str, Any]
    lastContactMessage: str
    lastMessage: WtsLastMessage
    lastMessagesAggregated: WtsLastMessagesAggregated

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
def convert_wts_webhook_to_incoming_message(webhook: WtsWebhookData) -> IncomingMessage:
    """Converte webhook do WTS para formato interno"""
    # Extrair número do telefone do contato
    phone_number = webhook.contact.phonenumber.replace("+55|", "")
    
    return IncomingMessage(
        phone_number=phone_number,
        message=webhook.lastContactMessage,
        message_id=webhook.lastMessage.id,
        timestamp=webhook.lastMessage.createdAt,
        user_name=webhook.contact.name
    ) 