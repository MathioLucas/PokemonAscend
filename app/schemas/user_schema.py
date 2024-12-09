from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=25, 
                          description="Create a unique username for the trainer")
    email: EmailStr
    password: str = Field(..., min_length=5, 
                          description="Password must be at least 5 characters")
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    trainer_level: int
    total_battles: int
    total_wins: int
    created_at: datetime
class Config:
        orm_mode = True
class UserLogin(BaseModel):
    username: str
    password: str