from typing import Iterable, Optional
from abc import abstractmethod
from src.repositories.repository_abc import RepositoryABC
from src.models.user import User
from pymongo import MongoClient
import datetime

class UserRepositoryMongo(RepositoryABC[User, str, str]):
    def __init__(self, collection: str):
        self.collection = collection
        print("Connecting to MongoDB...")
        client = MongoClient("mongodb://root:example@mongodb:27017/")

        self.db = client.testdb
        self.user_collection = self.db[self.collection]

        try: self.db.command("serverStatus")

        except Exception as e: print(e)

        else: print("Connected to MongoDB users!")  

    async def find_all(self, idc: str) -> Iterable[User]:
        cursor = self.user_collection.find({"idc": idc})

        users = [User(name=get_user.get('name', ''), email=get_user.get('email', ''), password=get_user.get('password', ''), id=get_user.get('id', ''), update_date=get_user.get('update_date', ''), create_date=get_user.get('create_date', ''), is_active=get_user.get('is_active', False)) for get_user in cursor]
        return users

    async def find_by_id(self, id: str, idc: str) -> Optional[User]:
        cursor = self.user_collection.find_one({"email": id, "idc": idc})
        if cursor is None:
            return None
        get_user = User(name=cursor.get('name', ''), email=cursor.get('email', ''), password=cursor.get('password', ''), id=cursor.get('id', ''), update_date=cursor.get('update_date', ''), create_date=cursor.get('create_date', ''), is_active=cursor.get('is_active', False))
        return get_user


    async def save(self, t: User, idc: str, id: str) -> Optional[User]:
        t.update_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        find = await self.find_by_id(idc, idc)
        if find != None:
            t.create_date = find.create_date
            filter_query = {"idc": idc, "email": id}           
            update_data = {"$set": t.__dict__} 

            # Actualizar el documento existente
            result = self.user_collection.update_one(filter_query, update_data)
            print(f"Matched {result.matched_count} documents")

            # Verificar si se actualizó con éxito
            if result.modified_count > 0:
                return t
        else:
            # Agregar el campo "idc" al documento
            document_data = t.__dict__
            document_data["idc"] = idc

            result = self.user_collection.insert_one(document_data)
            if result.inserted_id:
                return t

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

    async def count(self, idc: str) -> int:
        return await self.user_collection.count_documents({"idc": idc})

    def close(self) -> None:
        self.db.close()