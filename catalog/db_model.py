#!/usr/bin/env python
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import(TimedJSONWebSignatureSerializer as serializer, BadSignature, SignatureExpired)
import datetime
import random
import string

Base = declarative_base()


class User(Base):
    """Class representing a user in the database."""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    picture = Column(String(250))
    password_hash = Column(String(64))

    def hash_password(self, password):
        """Hashes user password."""
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        """Verifies password.
        
        Verifies password passed is the user's password. 
        
        Return: True if same password.         
        """
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, secret_key, expiration=600):
        """Generates new token.
        
        Return: Token.
        """
        s = serializer(secret_key, expires_in=expiration)
        return s.dumps({"id": self.id})

    @staticmethod
    def verify_auth_token(token, secret_key):
        """Verifies token.
        
        Return: User's id if token is valid. 
        """
        s = serializer(secret_key)

        try:
            data = s.loads(token)
        except SignatureExpired:
            # Expired token.
            return None
        except BadSignature:
            # Invalid token.
            return None
        return data["id"]


class Category(Base):
    """Class representing a category in the database."""
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    @property
    def serialize(self):
        """Returns Category info in JSON format."""
        return{
            "id": self.id,
            "category": self.category,
        }


class Item(Base):
    """Class representing an item in the database."""
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(250))
    date_created = Column(DateTime(), default=datetime.date.today)
    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    @property
    def serialize(self):
        """Returns Item info in JSON format."""
        return{
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "date": self.date_created,
            "category_id": self.category_id,
        }

# Connect to the database.
engine = create_engine("sqlite:///catalog.db")
# Create tables if they don't already exist.
Base.metadata.create_all(engine)
