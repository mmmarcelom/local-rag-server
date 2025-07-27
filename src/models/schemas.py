from pydantic import BaseModel
from typing import Optional

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