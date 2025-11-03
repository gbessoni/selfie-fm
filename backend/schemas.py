"""
Pydantic schemas for request/response validation
GitHub Issue #1: Build VoiceTree MVP - Core Features
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserCreateFromLinktree(BaseModel):
    username: str
    display_name: str
    bio: Optional[str] = None
    links: List[dict] = []

class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_published: bool = False
    imported_from_linktree: bool = False
    
    class Config:
        from_attributes = True

# Link Schemas
class LinkBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., max_length=1000)
    description: Optional[str] = None

class LinkCreate(LinkBase):
    pass

class LinkResponse(LinkBase):
    id: int
    user_id: int
    is_active: bool
    order: int
    created_at: datetime
    platform: Optional[str] = None
    click_count: Optional[int] = 0
    voice_message_audio: Optional[str] = None
    voice_message_text: Optional[str] = None
    
    class Config:
        from_attributes = True

# Scraper Schemas
class ScrapeRequest(BaseModel):
    linktree_url: str

class ScrapeResponse(BaseModel):
    username: str
    display_name: str
    bio: str
    links: List[dict]

# Voice AI Schemas
class VoiceCloneResponse(BaseModel):
    voice_id: str
    sample_path: str
    message: str

class GenerateVoiceRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=200)
    link_id: Optional[int] = None

class GenerateWelcomeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    message_type: str = Field(default="static")  # "static" or "daily_ai"

class VoiceMessageResponse(BaseModel):
    audio_path: str
    text: str
    message: str

# Authentication Schemas
class SignupRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)

class UserCreateWithPassword(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    email: Optional[str] = Field(None, max_length=255)

class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    display_name: str

class UserMeResponse(BaseModel):
    id: int
    username: str
    display_name: str
    email: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    is_published: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
