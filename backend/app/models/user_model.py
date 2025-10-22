from beanie import Document
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    NATIVE = "native"


class LanguagePreference(BaseModel):
    language: str = Field(..., description="Target language to learn")
    current_level: UserLevel = Field(default=UserLevel.BEGINNER)
    target_level: UserLevel = Field(default=UserLevel.INTERMEDIATE)


class User(Document):
    email: EmailStr = Field(..., unique=True, description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    full_name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    hashed_password: str = Field(..., description="Hashed password")
    language_preferences: List[LanguagePreference] = Field(default=[], description="Languages user wants to learn")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    is_verified: bool = Field(default=False, description="Whether the user email is verified")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Settings:
        name = "users"
        use_state_management = True

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    class Config:
        schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "language_preferences": [
                    {
                        "language": "english",
                        "current_level": "beginner",
                        "target_level": "intermediate"
                    }
                ]
            }
        }


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    language_preferences: List[LanguagePreference] = []

    class Config:
        schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "password": "supersecretpassword123",
                "language_preferences": [
                    {
                        "language": "english",
                        "current_level": "beginner",
                        "target_level": "intermediate"
                    }
                ]
            }
        }


class UserResponse(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    username: str
    full_name: str
    language_preferences: List[LanguagePreference]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "email": "usuario@ejemplo.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "language_preferences": [
                    {
                        "language": "english",
                        "current_level": "beginner",
                        "target_level": "intermediate"
                    }
                ],
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }