from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_model import Base, User, Category, Item
import datetime

# Setup database. 
engine = create_engine("sqlite:///catalog.db")
Base.metadata.bind = engine
dbSession = sessionmaker(bind=engine)
session = dbSession()

# Create user.
user = User(name="Juan Camaney", email="rr@email.com")
session.add (user)
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

# Create items.
item1 = Item(name="God of War", description="It is a new beginning for Kratos."
"Living as a man outside the shadow of the gods, he ventures into the brutal"
"Norse wilds with his son Atreus, fighting to fulfill a deeply personal quest.",
category_id=1, user_id=1)
session.add(item1)
session.commit()

item2 = Item(name="Red Dead Redemption 2", description="Developed by the creators of"
"Grand Theft Auto V and Red Dead Redemption, Red Dead Redemption 2 is an epic tale"
"of life in America's unforgiving heartland. ",
category_id=1, user_id=1)
session.add(item2)
session.commit()

item3 = Item(name="NBA2K18", description="The highest rated* annual sports title"
"of this console generation returns with NBA 2K18, featuring unparalleled authenticity"
"and improvements on the court. *According to 2008 - 2016 Metacritic.com",
category_id=3, user_id=1)
session.add(item3)
session.commit()

item4 = Item(name="Mortal Kombat XL", description="One of the best-selling titles of 2015"
"has gone XL! Komplete The Mortal Kombat X Experience with new and existing content",
category_id=2, user_id=1)
session.add(item4)
session.commit()

print("Added items.")