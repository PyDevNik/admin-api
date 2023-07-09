from pydantic import BaseModel
from typing import List

class User(BaseModel):
    token: str
    username: str
    password: str
    folder: str 
    files: List[str] = []

class UserCreate(BaseModel):
    username: str
    password: str