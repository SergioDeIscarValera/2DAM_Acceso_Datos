from src.models.task import Task
from src.models.task_type import TaskType
from graphene.types import ObjectType
from datetime import datetime
from typing import Union

class TaskMapperService(ObjectType):
    @staticmethod
    def map_task_to_task_type(task: Task) -> TaskType:
        return TaskType(
            id=task.id,
            title=task.title,
            description=task.description,
            done=task.done,
            is_important=task.is_important,
            end_date=datetime.strptime(task.end_date, "%Y-%m-%d %H:%M:%S.%f"),
            create_date=datetime.strptime(task.create_date, "%Y-%m-%d %H:%M:%S.%f"),
            update_date=datetime.strptime(task.update_date, "%Y-%m-%d %H:%M:%S.%f")
        )

    @staticmethod
    def map_task_type_to_task(task_type: TaskType) -> Task:
        return Task(
            id=task_type.id,
            title=task_type.title,
            description=task_type.description,
            done=task_type.done,
            is_important=task_type.is_important,
            end_date=task_type.end_date.strftime("%Y-%m-%d %H:%M:%S.%f"),
            create_date=task_type.create_date.strftime("%Y-%m-%d %H:%M:%S.%f"),
            update_date=task_type.update_date.strftime("%Y-%m-%d %H:%M:%S.%f")
        )