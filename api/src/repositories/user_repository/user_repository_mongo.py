from typing import Iterable, Optional
from abc import abstractmethod
from src.repositories.user_repository.user_repository_abc import UserRepositoryABC
from src.models.user import User
from pymongo import MongoClient
import datetime

class UserRepositoryMongo(UserRepositoryABC):
    def __init__(self, collection: str):
        self.collection = collection
        print("Connecting to MongoDB...")
        client = MongoClient("mongodb://root:example@mongodb:27017/")

        self.db = client.testdb
        self.user_collection = self.db[self.collection]

        try: self.db.command("serverStatus")

        except Exception as e: print(e)

        else: print("Connected to MongoDB users!")  

    def find_all(self, idc: str) -> Iterable[User]:
        cursor = self.user_collection.find({"idc": idc})

        users = [User(name=get_user.get('name', ''), email=get_user.get('email', ''), password=get_user.get('password', ''), id=get_user.get('id', ''), update_date=get_user.get('update_date', ''), create_date=get_user.get('create_date', ''), is_verified=get_user.get('is_verified', False), verify_code=get_user.get('verify_code', '')) for get_user in cursor]
        return users

    def find_by_id(self, id: str, idc: str) -> Optional[User]:
        cursor = self.user_collection.find_one({"email": id, "idc": idc})
        if cursor is None:
            return None
        get_user = User(name=cursor.get('name', ''), email=cursor.get('email', ''), password=cursor.get('password', ''), id=cursor.get('id', ''), update_date=cursor.get('update_date', ''), create_date=cursor.get('create_date', ''), is_verified=cursor.get('is_verified', False), verify_code=cursor.get('verify_code', ''))
        return get_user


    def save(self, t: User, idc: str, id: str) -> Optional[User]:
        t.update_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        find = self.find_by_id(id, idc)
        if find != None:
            t.create_date = find.create_date
            t.is_verified = find.is_verified
            t.verify_code = find.verify_code
        
        filter_query = {"idc": idc, "email": id}
        update_data = {"$set": t.__dict__}

        result = self.user_collection.update_one(filter_query, update_data, upsert=True)

        if result.matched_count > 0 or result.upserted_id:
            return t
        else:
            return None

    def delete_by_id(self, id: str, idc: str) -> None:
        self.user_collection.delete_one({"email": id, "idc": idc})

    def delete(self, t: User, idc: str) -> None:
        self.delete_by_id(t.email, idc)

    def delete_all(self, idc: str) -> None:
        self.user_collection.delete_many({"idc": idc})
        
    def exists_by_id(self, id: str, idc: str) -> bool:
        return self.user_collection.find_one({"email": id, "idc": idc}) is not None
        
    def exists(self, t: User, idc: str) -> bool:
        return self.exists_by_id(t.email, idc)

    def count(self, idc: str) -> int:
        return self.user_collection.count_documents({"idc": idc})

    def validate_user(self, email: str, password: str) -> bool:
        user = self.find_by_id(email, email)
        if user is None or user.is_verified == False:
            return False
        return user.password == password

    def verify_user(self, email: str, code: str) -> bool:
        user = self.find_by_id(email, email)
        if user is None:
            return False
        if user.is_verified:
            return True
        if user.verify_code == code:
            user.is_verified = True
            # No llamo a save porque hay que cambiar si esta verificado 
            # y save este hecho para no editar el ese campo
            filter_query = {"idc": email, "email": email}
            update_data = {"$set": user.__dict__}
            response = self.user_collection.update_one(filter_query, update_data, upsert=True)
            if response.matched_count > 0 or response.upserted_id:
                return True
        return False

    def close(self) -> None:
        self.db.close()