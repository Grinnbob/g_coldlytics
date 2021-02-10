from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator, AnyUrl, Schema

class GetPrfole(BaseModel):
    emailAddress: str
    messagesTotal: Optional[int] = None
    threadsTotal: Optional[int] = None
    historyId: Optional[str] = None

class ListLabels(BaseModel):
    id: str
    name: str
    messageListVisibility: Optional[str] = None
    labelListVisibility: Optional[str] = None
    type: Optional[str] = None

class MessagesListResponse(BaseModel):
    messages: Optional[list] = None
    next_page_token: Optional[str] = None
    error: Optional[bool] = False
    response: Optional[dict] = None


class MessagesListRequest(BaseModel):
    userId: str
    labelIds: List[str]
    pageToken: Optional[str] = None

class MessagesGetRequest(BaseModel):
    userId: str
    msg_ids: List[str]
    format: str
