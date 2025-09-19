from typing import Optional

from app.modules.conversations.conversation.conversation_model import Visibility
from pydantic import BaseModel, EmailStr


class ShareChatRequest(BaseModel):
    conversation_id: str
    recipientEmails: Optional[list[EmailStr]] = None
    visibility: Visibility


class ShareChatResponse(BaseModel):
    message: str
    sharedID: str


class SharedChatResponse(BaseModel):
    chat: dict


class RemoveAccessRequest(BaseModel):
    emails: list[EmailStr]
