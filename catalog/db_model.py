#!/usr/bin/env python
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime

Base = declarative_base()


class User(Base):
    """Class representing a user in the database."""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    picture = Column(String(250))


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
