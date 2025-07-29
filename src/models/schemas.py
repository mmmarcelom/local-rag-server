from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
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
    platform: str  # Pode vir como "WhatsApp", "whatsapp", etc.
    displayName: str

class WtsContact(BaseModel):
    id: str
    name: str
    first_name: Optional[str] = Field(None, alias="first-name")
    phonenumber: str
    display_phonenumber: str = Field(alias="display-phonenumber")
    email: Optional[str] = None
    instagram: Optional[str] = None
    tags: Optional[Any] = None
    annotation: str
    metadata: Dict[str, Any]
    rg: Optional[str] = None
    cep: Optional[str] = None
    pa_s: Optional[str] = Field(None, alias="pa-s")
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

class Message(BaseModel):
    id: str
    conversation_id: str
    platform: str
    sender: str
    receiver: str
    content: str
    direction: Literal['incoming', 'outgoing']
    message_type: Literal['text', 'audio', 'video']
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None