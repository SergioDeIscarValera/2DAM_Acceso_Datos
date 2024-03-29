from typing import Iterable, Optional
from abc import abstractmethod
from src.repositories.repository_abc import RepositoryABC
from src.models.task import Task
from pymongo import MongoClient
import datetime

class TaskRepositoryMongo(RepositoryABC[Task, str, str]):
    def __init__(self, collection: str, db_user: str, db_password: str):
        self.collection = collection
        print("Connecting to MongoDB...")
        client = MongoClient(f"mongodb://{db_user}:{db_password}@mongodb:27017/")

        self.db = client.testdb
        self.task_collection = self.db[self.collection]

        try: self.db.command("serverStatus")
        except Exception as e: print(e)
        else: print("Connected to MongoDB tasks!")  

    def find_all(self, idc: str) -> Iterable[Task]:
        cursor = self.task_collection.find({"idc": idc})
        tasks = [Task(title=task.get('title', ''), description=task.get('description', ''), done=task.get('done', False), is_important=task.get('is_important', False), end_date=task.get('end_date', ''), update_date=task.get('update_date', None), create_date=task.get('create_date', None), id=task.get('id', None)) for task in cursor]
        return tasks

    def find_by_id(self, id: str, idc: str) -> Optional[Task]:
        cursor = self.task_collection.find_one({"id": id, "idc": idc})
        if cursor is None:
            return None
        return Task(title=cursor.get('title', ''), description=cursor.get('description', ''), done=cursor.get('done', False), is_important=cursor.get('is_important', False), end_date=cursor.get('end_date', ''), update_date=cursor.get('update_date', None), create_date=cursor.get('create_date', None), id=cursor.get('id', None))

    def save(self, t: Task, idc: str, id: str) -> Optional[Task]:
        t.update_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        find = self.find_by_id(t.id, idc)
        if find != None:
            t.create_date = find.create_date

        filter_query = {"idc": idc, "id": id}
        update_data = {"$set": t.__dict__}

        result = self.task_collection.update_one(filter_query, update_data, upsert=True)

        if result.matched_count > 0 or result.upserted_id:
            return t
        else:
            return None

    def delete_by_id(self, id: str, idc: str) -> None:
        self.task_collection.delete_one({"id": id, "idc": idc})

    def delete(self, t: Task, idc: str) -> None:
        self.delete_by_id(t.id, idc)

    def delete_all(self, idc: str) -> None:
        self.task_collection.delete_many({"idc": idc})
        
    def exists_by_id(self, id: str, idc: str) -> bool:
        return self.task_collection.find_one({"id": id, "idc": idc}) is not None
        
    def exists(self, t: Task, idc: str) -> bool:
        return self.exists_by_id(t.id, idc)

    def count(self, idc: str) -> int:
        return self.task_collection.count_documents({"idc": idc})

    def close(self) -> None:
        self.db.close()