from typing import Optional, List
from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import (
    Column, Integer, String, Enum as SQLEnum, DateTime, ForeignKey, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

# ==========================================
# 1. ENUMS & SQLAlchemy BASE
# ==========================================

Base = declarative_base()

class Symbol(str, Enum):
    X = "X"
    O = "O"
    EMPTY = "-"

class GameState(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"
    DRAW = "DRAW"

class PlayerModel(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    symbol = Column(SQLEnum(Symbol), nullable=False)

class GameModel(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(SQLEnum(GameState), default=GameState.IN_PROGRESS, nullable=False)
    board_state = Column(String(200), nullable=False)  # JSON string of 3x3 board
    winner_id = Column(Integer, ForeignKey('players.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    winner = relationship("PlayerModel", foreign_keys=[winner_id])
    moves = relationship("MoveModel", back_populates="game", cascade="all, delete-orphan")

class MoveModel(Base):
    __tablename__ = 'moves'

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    row = Column(Integer, nullable=False)
    col = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    game = relationship("GameModel", back_populates="moves")
    player = relationship("PlayerModel")