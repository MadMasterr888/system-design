# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from pymongo import MongoClient
from passlib.context import CryptContext
import os

# Настройки
SECRET_KEY = "secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/my_service")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://root:example@localhost:27017")
mongo_client = MongoClient(MONGODB_URL)
mongo_db = mongo_client.my_service_db

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Модели Pydantic
class OrderCreate(BaseModel):
    order_number: int
    description: str
    amount: float

class Order(BaseModel):
    id: str
    order_number: int
    description: str
    amount: float

    class Config:
        orm_mode = True

# Эндпоинты MongoDB
@app.post("/orders", response_model=dict)
def create_order(order: OrderCreate):
    if mongo_db.orders.find_one({"order_number": order.order_number}):
        raise HTTPException(status_code=400, detail="Order with this number already exists")
    
    order_data = order.dict()
    mongo_db.orders.insert_one(order_data)
    
    return {"status": "Order created successfully", "order_number": order.order_number}

@app.get("/orders/{order_number}", response_model=Order)
def get_order(order_number: int):
    order = mongo_db.orders.find_one({"order_number": order_number})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order["_id"] = str(order["_id"])  # Преобразуем ObjectId в строку
    return Order(**order)
