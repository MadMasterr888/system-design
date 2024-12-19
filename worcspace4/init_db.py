# init_db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
from pymongo import MongoClient, ASCENDING
from passlib.context import CryptContext
import os

# URL подключения к PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/my_service")

# URL подключения к MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://root:example@localhost:27017")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_postgres():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Добавляем пользователя admin
    password_hash = pwd_context.hash("secret")
    admin_user = User(username="admin", password_hash=password_hash)
    db.add(admin_user)
    db.commit()
    db.close()

def init_mongo():
    client = MongoClient(MONGODB_URL)
    db = client.my_service_db
    # Создаём индекс на поле 'order_number' для 'orders'
    db.orders.create_index([("order_number", ASCENDING)], unique=True)

if __name__ == "__main__":
    
    init_postgres()
    
    init_mongo()