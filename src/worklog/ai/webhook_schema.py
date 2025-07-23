from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union


class TextContent(BaseModel):
    body: str


class LinkPreviewContent(BaseModel):
    body: str
    url: str
    title: str
    id: str
    sha256: str
    description: str
    preview: str  # Base64 encoded image data


class DocumentContent(BaseModel):
    id: str
    mime_type: str
    file_size: int
    sha256: str
    file_name: str
    link: str
    caption: Optional[str] = None
    filename: str
    page_count: Optional[int] = None
    preview: Optional[str] = None  # Base64 encoded image data


class VoiceContent(BaseModel):
    id: str
    mime_type: str
    file_size: int
    sha256: str
    link: str
    seconds: int


class StickerContent(BaseModel):
    id: str
    mime_type: str
    file_size: int
    sha256: str
    link: str
    width: int
    height: int
    animated: bool


class ActionContent(BaseModel):
    target: str
    type: str  # Можно заменить на Literal если известны все возможные значения
    emoji: Optional[str] = None


class Message(BaseModel):
    id: str
    from_me: bool
    type: str  # Можно использовать Literal["text", "link_preview", "document", "voice", "sticker", "action", ...]
    chat_id: str
    timestamp: int
    source: str
    text: Optional[TextContent] = None
    link_preview: Optional[LinkPreviewContent] = None
    document: Optional[DocumentContent] = None
    voice: Optional[VoiceContent] = None
    sticker: Optional[StickerContent] = None
    action: Optional[ActionContent] = None
    from_: str = Field(..., alias="from")
    from_name: Optional[str] = None


class EventInfo(BaseModel):
    type: str
    event: str


class WebhookPayload(BaseModel):
    messages: List[Message]
    event: EventInfo
    channel_id: str
