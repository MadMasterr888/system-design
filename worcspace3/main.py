# main.py

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from jose import JWTError, jwt
from passlib.context import CryptContext
from models import Base, User, Item
import os

# Настройки
SECRET_KEY = "secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/my_service")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# Контексты для паролей и токенов
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Модели Pydantic
class UserCreate(BaseModel):
    username: str
    password: str

class ItemCreate(BaseModel):
    name: str
    description: str
    price: float

# Функция для создания пользователя
def create_user(db: Session, user: UserCreate):
    password_hash = pwd_context.hash(user.password)
    db_user = User(username=user.username, password_hash=password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Функция для аутентификации
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and pwd_context.verify(password, user.password_hash):
        return user
    return False

# Создание токена JWT
def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# Эндпоинты
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(SessionLocal)):
    return create_user(db, user)

@app.post("/token")
def login_for_access_token(user: UserCreate, db: Session = Depends(SessionLocal)):
    user = authenticate_user(db, user.username, user.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/items")
def get_items(db: Session = Depends(SessionLocal)):
    return db.query(Item).all()

@app.post("/items")
def create_item(item: ItemCreate, db: Session = Depends(SessionLocal)):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item