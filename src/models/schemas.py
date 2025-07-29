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
    
    class Config:
        extra = "ignore"

class WtsChannel(BaseModel):
    id: str
    key: str
    platform: str  # Pode vir como "WhatsApp", "whatsapp", etc.
    displayName: str
    
    class Config:
        extra = "ignore"

class WtsContact(BaseModel):
    id: str
    name: str
    first_name: Optional[str] = Field(None, alias="first-name")
    phonenumber: str
    display_phonenumber: str = Field(alias="display-phonenumber")
    email: Optional[str] = None
    instagram: Optional[str] = None
    tags: Optional[list] = None
    annotation: Optional[str] = None
    metadata: Dict[str, Any]
    
    class Config:
        extra = "ignore"

class WtsLastMessage(BaseModel):
    id: str
    createdAt: str
    type: str
    text: str
    fileId: Optional[str] = None
    file: Optional[Any] = None
    
    class Config:
        extra = "ignore"

class WtsLastMessagesAggregated(BaseModel):
    text: str
    files: list
    
    class Config:
        extra = "ignore"

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
    
    class Config:
        extra = "ignore"

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
    
    class Config:
        extra = "ignore"