from flask import Flask, jsonify, request, abort
from graphql_server.flask import GraphQLView
from graphene import ObjectType, String, Schema, ID, List, Field, Mutation, InputObjectType, Boolean
from dotenv import dotenv_values
from src.repositories.user_repository.user_repository_mongo import UserRepositoryMongo
from src.repositories.task_repository.task_repository_mongo import TaskRepositoryMongo
from src.repositories.task_repository.task_repository_maria import TaskRepositoryMaria
from src.utils.mongo_validators import MongoValidators
from src.models.user import User
from src.models.task import Task
from src.models.user_type import UserType
from src.models.task_type import TaskType
from src.services.mapper.user_mapper import UserMapperService
from src.services.mapper.task_mapper import TaskMapperService
from src.services.email.email_service_smtplib import EmailServiceSmtplib
# import asyncio

app = Flask(__name__)

env = dotenv_values()
DB_TYPE = env["DB_TYPE"]
DB_USER = env["DB_USER"]
DB_PASS = env["DB_PASS"]

# Set up the repositories
mongo_validators = MongoValidators(DB_USER, DB_PASS)
mongo_validators.apply_user_mongo_shema("my_users")
user_repo = UserRepositoryMongo("my_users", DB_USER, DB_PASS)

# Set up the email service
email_service = EmailServiceSmtplib(env)

if DB_TYPE == "mongodb":
    task_repo = TaskRepositoryMongo("tasks", DB_USER, DB_PASS)
    mongo_validators.apply_task_mongo_shema("tasks")
elif DB_TYPE == "mariadb":
    task_repo = TaskRepositoryMaria("tasks", DB_USER, DB_PASS)

#region Tasks
class TaskInput(InputObjectType):
    title = String(required=True)
    description = String(required=True)
    end_date = String(required=True)
    is_important = Boolean(default_value=False)
    is_done = Boolean(default_value=False)

class TaskInputEdit(InputObjectType):
    title = String(default_value=None)
    description = String(default_value=None)
    end_date = String(default_value=None)
    is_important = Boolean(default_value=None)
    is_done = Boolean(default_value=None)

class CreateTask(Mutation):
    class Arguments:
        email = String(required=True)
        password = String(required=True)
        input = TaskInput(required=True)

    task = Field(lambda: TaskType)
    def mutate(self, info, email, password, input):
        user = user_repo.find_by_id(email, email)
        if user is None or user.password != password:
            return Exception('Invalid user or password')
        if user.is_verified == False:
            return Exception('User not verified')
        new_task = Task(title=input.title, description=input.description, end_date=input.end_date, is_important=input.is_important, done=input.is_done)
        result = task_repo.save(new_task, email, new_task.id)
        if result is None:
            return Exception('Task not saved')
        return CreateTask(task=TaskMapperService.map_task_to_task_type(result))

class EditTask(Mutation):
    class Arguments:
        id = String(required=True)
        email = String(required=True)
        password = String(required=True)
        input = TaskInputEdit(required=True)

    task = Field(lambda: TaskType)
    def mutate(self, info, id, email, password, input):
        if input.title is None and input.description is None and input.end_date is None and input.is_important is None and input.is_done is None:
            return Exception('No changes to make')

        user = user_repo.find_by_id(email, email)
        if user is None or user.password != password:
            return Exception('Invalid user or password')
        if user.is_verified == False:
            return Exception('User not verified')
        task = task_repo.find_by_id(id, email)
        if task is None:
            return Exception('Task not found')

        task.title = input.title if input.title is not None else task.title
        task.description = input.description if input.description is not None else task.description
        task.end_date = input.end_date if input.end_date is not None else task.end_date
        task.is_important = input.is_important if input.is_important is not None else task.is_important
        task.done = input.is_done if input.is_done is not None else task.done

        result = task_repo.save(task, email, task.id)
        if result is None:
            return Exception('Task not saved')
        return EditTask(task=TaskMapperService.map_task_to_task_type(result))

class DeleteTask(Mutation):
    class Arguments:
        id = String(required=True)
        email = String(required=True)
        password = String(required=True)

    task = Field(lambda: TaskType)
    def mutate(self, info, id, email, password):
        user = user_repo.find_by_id(email, email)
        if user is None or user.password != password:
            return Exception('Invalid user or password')
        if user.is_verified == False:
            return Exception('User not verified')
        task = task_repo.find_by_id(id, email)
        if task is None:
            return Exception('Task not found')
        task_repo.delete_by_id(id, email)
        return DeleteTask(task=TaskMapperService.map_task_to_task_type(task))
#endregion
#region Users
class UserInput(InputObjectType):
    name = String(required=True)
    email = String(required=True)
    password = String(required=True)

class UserInputEdit(InputObjectType):
    name = String()
    password = String()

class CreateUser(Mutation):
    class Arguments:
        input = UserInput(required=True)

    user = Field(lambda: UserType)
    def mutate(self, info, input):
        new_user = User(name=input.name, email=input.email, password=input.password)
        result = user_repo.save(new_user, input.email, input.email)
        if result is None:
            return Exception('User not saved')
        # await email_service.send_verify_email(result.email, result.verify_code)
        return CreateUser(user=UserMapperService.map_user_to_user_type(result))

class EditUser(Mutation):
    class Arguments:
        email = String(required=True)
        old_password = String(required=True)
        input = UserInputEdit(required=True)

    user = Field(lambda: UserType)
    def mutate(self, info, email, old_password, input):
        user = user_repo.find_by_id(email, email)
        if user is None or user.password != old_password:
            return Exception('Invalid user or password')
        if input.name is None and input.password is None:
            return EditUser(user=UserMapperService.map_user_to_user_type(user))

        user.name = input.name if input.name is not None else user.name
        user.password = input.password if input.password is not None else user.password

        result = user_repo.save(user, email, email)
        if result is None:
            return Exception('User not saved')
        return EditUser(user=UserMapperService.map_user_to_user_type(result))

class DeleteUser(Mutation):
    class Arguments:
        email = String(required=True)
        password = String(required=True)

    user = Field(lambda: UserType)
    def mutate(self, info, email, password):
        user = user_repo.find_by_id(email, email)
        if user is None or user.password != password:
            return Exception('Invalid user or password')
        user_repo.delete_by_id(email, email)
        return DeleteUser(user=UserMapperService.map_user_to_user_type(user))
#endregion

class Mutation(ObjectType):
    create_user = CreateUser.Field()
    edit_user = EditUser.Field()
    delete_user = DeleteUser.Field()

    create_task = CreateTask.Field()
    edit_task = EditTask.Field()
    delete_task = DeleteTask.Field()

class Query(ObjectType):
    # Find one user by email and password
    user = Field(UserType, email=String(required=True), password=String(required=True))
    tasks = List(TaskType, email=String(required=True), password=String(required=True))
    task = Field(TaskType, id=String(required=True), email=String(required=True), password=String(required=True))

    def resolve_user(self, info, email, password):
        user = user_repo.find_by_id(email, email)
        if user is None or user.password != password:
            return Exception('Invalid user or password')
        return UserMapperService.map_user_to_user_type(user)

    def resolve_tasks(self, info, email, password):
        user = user_repo.find_by_id(email, email)
        if user is None or user.password != password:
            return Exception('Invalid user or password')
        if user.is_verified == False:
            return Exception('User not verified')
        tasks = task_repo.find_all(email)
        return [TaskMapperService.map_task_to_task_type(tem) for tem in tasks]

    def resolve_task(self, info, id, email, password):
        user = user_repo.find_by_id(email, email)
        if user is None or user.password != password:
            return Exception('Invalid user or password')
        if user.is_verified == False:
            return Exception('User not verified')
        task = task_repo.find_by_id(id, email)
        if task is None:
            return Exception('Task not found')
        return TaskMapperService.map_task_to_task_type(task)

schema = Schema(query=Query, mutation=Mutation)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)) # AsyncioExecutor¿?

if __name__ == '__main__':
    app.run(debug=True)