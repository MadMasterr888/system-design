# init_db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
from passlib.context import CryptContext
import os

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/my_service")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Инициализация базы данных
def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Добавляем пользователя admin
    password_hash = pwd_context.hash("$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW")
    admin_user = User(username="admin", password_hash=password_hash)
    db.add(admin_user)
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
