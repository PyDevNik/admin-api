from pymongo import MongoClient
from schemas import User, UserCreate
import random, string, os
from typing import List
from config import *

class DB:
    def __init__(self) -> None:
        self.__client = MongoClient(url)
        self._db = self.__client.get_default_database(default=db_name)
        self._users = self._db.get_collection(users_collection)

    def get_user(self, **kwargs) -> User:
        user_dict = self._users.find_one(kwargs)
        return User(**user_dict) if user_dict else None
    
    def generate_token(self) -> str:
        def generate():
            return "".join([random.choice(string.ascii_letters) for _ in range(20)])
        users = [user.token for user in self.get_all_users()]
        token = generate()
        while token in users:
            token = generate()
        return token
    
    def get_all_users(self) -> List[User]:
        return [User(**data) for data in list(self._users.find())]

    def add_user(self, user: UserCreate) -> None:
        token = self.generate_token()
        user_folder = user.username
        while user_folder in os.listdir(os.path.join(os.getcwd(), "files")):
            user_folder += random.choice(string.ascii_letters)
        folder = os.path.join(os.getcwd(), "files", user_folder)
        if not os.path.exists(folder):
            os.makedirs(folder)
        user = User(token=token, folder=folder,**user.dict())
        self._users.insert_one(user.dict())
    