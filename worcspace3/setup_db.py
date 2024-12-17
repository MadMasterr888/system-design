from sqlalchemy.orm import Session
from models import User, Folder, Message

def init_db(db: Session):
    if db.query(User).count() == 0:
        user1 = User(username="user1", hashed_password="hashed_password1", email="user1@example.com")
        user2 = User(username="user2", hashed_password="hashed_password2", email="user2@example.com")
        db.add(user1)
        db.add(user2)
        db.commit()
    
    if db.query(Folder).count() == 0:
        folder1 = Folder(name="Inbox", user_id=1)
        folder2 = Folder(name="Sent", user_id=1)
        db.add(folder1)
        db.add(folder2)
        db.commit()

    if db.query(Message).count() == 0:
        message1 = Message(content="Hello from user1!", folder_id=1)
        message2 = Message(content="Hello from user2!", folder_id=2)
        db.add(message1)
        db.add(message2)
        db.commit()
