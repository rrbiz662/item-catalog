#!/usr/bin/env python2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_model import Base, User, Category, Item
import datetime
from passlib.apps import custom_app_context as pwd_context


# Setup database.
engine = create_engine("postgresql://catalog:!@#$qwer@localhost/catalog")
Base.metadata.bind = engine
dbSession = sessionmaker(bind=engine)
session = dbSession()

# Create users.
user1 = User(name="luffy123", email="luffy123@email.com", password_hash=pwd_context.encrypt("!@#$qwer"))
session.add (user1)
session.commit()

user2 = User(name="chopper123", email="chopper123@email.com", password_hash=pwd_context.encrypt("!@#$qwer"))
session.add (user2)
session.commit()

# Create categories.
category1 = Category(category="Action", user_id=1)
session.add(category1)
session.commit()

category2 = Category(category="Fighting", user_id=1)
session.add(category2)
session.commit()

category3 = Category(category="Sports", user_id=1)
session.add(category3)
session.commit()

category4 = Category(category="Role-Playing", user_id=2)
session.add(category4)
session.commit()

# Create items.
item1 = Item(name="God of War", description="It is a new beginning for Kratos."
" Living as a man outside the shadow of the gods, he ventures into the brutal"
" Norse wilds with his son Atreus, fighting to fulfill a deeply personal quest.",
category_id=1, user_id=1)
session.add(item1)
session.commit()

item2 = Item(name="Red Dead Redemption 2", description="Developed by the creators of"
" Grand Theft Auto V and Red Dead Redemption, Red Dead Redemption 2 is an epic tale"
" of life in America's unforgiving heartland. ",
category_id=1, user_id=1)
session.add(item2)
session.commit()

item3 = Item(name="NBA2K18", description="The highest rated* annual sports title"
" of this console generation returns with NBA 2K18, featuring unparalleled authenticity"
" and improvements on the court. *According to 2008 - 2016 Metacritic.com",
category_id=3, user_id=1)
session.add(item3)
session.commit()

item4 = Item(name="Mortal Kombat XL", description="One of the best-selling titles of 2015"
" has gone XL! Komplete The Mortal Kombat X Experience with new and existing content",
category_id=2, user_id=1)
session.add(item4)
session.commit()

item5 = Item(name="Yakuza 6", description="In Yakuza 6, Kazuma Kiryu will find out exactly"
" how much people are willing to sacrifice for family - be those ties through blood or bond"
" - when he investigates a series of shadowy events that involve the ones he holds closest"
" to his heart.",
category_id=1, user_id=2)
session.add(item5)
session.commit()

item6 = Item(name="MLB The Show 18", description="Your team. Your rivals. Your buddies."
" Your hometown. No matter why you play or why you love baseball, MLB The Show 18"
" is for a fan like you.", category_id=3, user_id=2)
session.add(item6)
session.commit()

item7 = Item(name="Kingdom Hearts 3", description="", category_id=4, user_id=2)
session.add(item7)
session.commit()

item8 = Item(name="Madden NFL 19", description="", category_id=3, user_id=1)
session.add(item8)
session.commit()

item9 = Item(name="Nights of Azure 2", description="The story unfolds in a fictional,"
" demon-ridden Western European city towards the end of the 19th century and follows"
" Alushe, a knight protector who was ambushed and killed while guarding her childhood"
" friend and Curia Priestess, Liliana.",
category_id=4, user_id=2)
session.add(item9)
session.commit()

item10 = Item(name="Tales of Berseria", description="In TALES OF BERSERIA, players"
" embark on a journey of self-discovery as they assume the role of Velvet, a young"
" woman whose once kind demeanor has been replaced and overcome with a festering anger"
" and hatred after a traumatic experience three years prior to the events within TALES"
" OF BERSERIA.",
category_id=4, user_id=1)
session.add(item10)
session.commit()


print("Added items.")