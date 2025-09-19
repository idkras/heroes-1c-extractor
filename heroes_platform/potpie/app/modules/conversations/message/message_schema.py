from datetime import datetime
from typing import Optional

from app.modules.conversations.message.message_model import MessageStatus, MessageType
from app.modules.media.media_schema import AttachmentInfo
from pydantic import BaseModel


class NodeContext(BaseModel):
    node_id: str
    name: str


class MessageRequest(BaseModel):
    content: str
    node_ids: Optional[list[NodeContext]] = None
    attachment_ids: Optional[list[str]] = None  # IDs of uploaded attachments


class DirectMessageRequest(BaseModel):
    content: str
    node_ids: Optional[list[NodeContext]] = None
    agent_id: str | None = None
    attachment_ids: Optional[list[str]] = None  # IDs of uploaded attachments


class RegenerateRequest(BaseModel):
    node_ids: Optional[list[NodeContext]] = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    content: str
    sender_id: Optional[str] = None
    type: MessageType
    reason: Optional[str] = None
    created_at: datetime
    status: MessageStatus
    citations: Optional[list[str]] = None
    has_attachments: bool = False
    attachments: Optional[list[AttachmentInfo]] = None

    class Config:
        from_attributes = True
