from typing import Iterable, Optional
from abc import abstractmethod
from src.repositories.repository_abc import RepositoryABC
from src.models.task import Task
from mariadb import mariadb
import datetime

class TaskRepositoryMaria(RepositoryABC[Task, str, str]):
    def __init__(self, table: str):
        self.table = table
        print("Connecting to MariaDB...")
        try:
            self.conn = mariadb.connect(
                host="mariadb",
                port=3306,
                user="root",
                password="example",
                database="testdb"
            )
            self.cursor = self.conn.cursor()
            print("Connected to MariaDB!")
            self.create_table_if_not_exists()
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB: {e}")  

    def create_table_if_not_exists(self) -> None:
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table} (id VARCHAR(36) PRIMARY KEY, idc VARCHAR(36), title VARCHAR(255), description TEXT, done BOOLEAN, end_date DATETIME, is_important BOOLEAN, create_date DATETIME DEFAULT CURRENT_TIMESTAMP, update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)")
        self.conn.commit()

    def find_all(self, idc: str) -> Iterable[Task]:
        self.cursor.execute(f"SELECT * FROM {self.table} WHERE idc = '{idc}'")
        tasks = [Task(title=task[2], description=task[3], done=task[4], end_date=task[5], is_important=task[6], create_date=task[7], update_date=task[8], id=task[0]) for task in self.cursor]
        return tasks

    def find_by_id(self, id: str, idc: str) -> Optional[Task]:
        self.cursor.execute(f"SELECT * FROM {self.table} WHERE id = '{id}' AND idc = '{idc}'")
        task = self.cursor.fetchone()
        if task is not None:
            return Task(title=task[2], description=task[3], done=task[4], end_date=task[5], is_important=task[6], create_date=task[7], update_date=task[8], id=task[0])
        else:
            return None

    def save(self, t: Task, idc: str, id: str) -> Optional[Task]:
        t.update_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        find = self.find_by_id(t.id, idc)
        if find != None:
            t.create_date = find.create_date
            update_data = (t.title, t.description, t.done, t.end_date, t.is_important, t.update_date, id, idc)
            self.cursor.execute(f"UPDATE {self.table} SET title = ?, description = ?, done = ?, end_date = ?, is_important = ?, update_date = ? WHERE id = ? AND idc = ?", update_data)
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return t
        else:
            t.create_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            t.update_date = t.create_date
            insert_data = (id, idc, t.title, t.description, t.done, t.end_date, t.is_important, t.create_date, t.update_date)
            self.cursor.execute(f"INSERT INTO {self.table} (id, idc, title, description, done, end_date, is_important, create_date, update_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", insert_data)
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return t

    def delete_by_id(self, id: str, idc: str) -> None:
        self.cursor.execute(f"DELETE FROM {self.table} WHERE id = '{id}' AND idc = '{idc}'")
        self.conn.commit()

    def delete(self, t: Task, idc: str) -> None:
        self.delete_by_id(t.id, idc)

    def delete_all(self, idc: str) -> None:
        self.cursor.execute(f"DELETE FROM {self.table} WHERE idc = '{idc}'")
        self.conn.commit()
        
    def exists_by_id(self, id: str, idc: str) -> bool:
        self.cursor.execute(f"SELECT * FROM {self.table} WHERE id = '{id}' AND idc = '{idc}'")
        return self.cursor.fetchone() is not None
        
    def exists(self, t: Task, idc: str) -> bool:
        return self.exists_by_id(t.id, idc)

    def count(self, idc: str) -> int:
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.table} WHERE idc = '{idc}'")
        return self.cursor.fetchone()[0]

    def close(self) -> None:
        self.cursor.close()
        self.conn.close()