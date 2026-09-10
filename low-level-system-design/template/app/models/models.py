from typing import Optional, List
import enum
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String
from sqlalchemy import Enum as SAEnum


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column("username", String, unique=True, nullable=False))
    email: str = Field(sa_column=Column("email", String, unique=True, nullable=False))
    password_hash: str = Field(sa_column=Column("password_hash", String, nullable=False))
    role: UserRole = Field(sa_column=Column(SAEnum(UserRole), nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)