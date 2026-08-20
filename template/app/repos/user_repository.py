from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update
from sqlmodel import Session, select
from app.models.models import User


class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_user_by_id(self, user_id):
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data):
        new_user = User(**user_data)
        self.db.add(new_user)
        self.db.commit()
        return new_user

    def update_user(self, user_id, user_data):
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            self.db.commit()
            return user
        return None

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False