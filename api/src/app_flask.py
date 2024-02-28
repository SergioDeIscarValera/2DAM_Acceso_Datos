from src.repositories.task_repository.task_repository_mongo import TaskRepositoryMongo
from src.repositories.task_repository.task_repository_maria import TaskRepositoryMaria
from src.repositories.task_repository.user_repository_mongo import UserRepositoryMongo
from src.models.task import Task
from src.models.user import User
from src.utils.mongo_validators import MongoValidators
import datetime
import asyncio
from flask import Flask, jsonify, request, abort
from pymongo.errors import PyMongoError
from bson import ObjectId
import os
from dotenv import dotenv_values

# Load environment variables
env = dotenv_values()
# Create a Flask app
app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

DB_TYPE = env["DB_TYPE"]
print(f"DB_TYPE: {DB_TYPE}")
user_repo = UserRepositoryMongo("users")
if DB_TYPE == "mongodb":
    task_repo = TaskRepositoryMongo("tasks")
    #MongoValidators.apply_task_mongo_shema("tasks")
elif DB_TYPE == "mariadb":
    task_repo = TaskRepositoryMaria("tasks")

@app.route('/')
def index():
    response = {
        'urls': [
            {'/': 'Index'},
            {'/tasks?idc=<email>': 'Get all tasks (GET)'},
            {'/tasks/<id>?idc=<email>': 'Get task by id (GET)'},
            {'/tasks?idc=<email>': 'Create a task (POST)'},
            {'/tasks/<id>?idc=<email>': 'Update a task (PUT)'},
            {'/tasks/<id>?idc=<email>': 'Delete a task (DELETE)'},

            {'/users/<email>?pass=<password>': 'Get user by email and password (GET)'},
            {'/users': 'Create a user (POST)'},
            {'/users/<email>?pass=<password>': 'Update a user (PUT)'},
            {'/users/<email>?pass=<password>': 'Delete a user (DELETE)'}
        ],
        'db_type': f'{DB_TYPE}'
    }
    return jsonify(response)
#region Tasks
@app.route('/tasks', methods=['GET'])
async def get_tasks():
    try:
        idc = request.args.get('idc')  # Obtener el parámetro 'idc' de la consulta
        tasks = await task_repo.find_all(idc)
        if not tasks:
            return jsonify({"message": "[]"})
        serialized_tasks = [task.__dict__ for task in tasks]
        return jsonify(serialized_tasks)
    except PyMongoError as e:
        return jsonify({"Error": f"{e}"})

@app.route('/tasks/<id>', methods=['GET'])
async def get_task(id):
    try:
        idc = request.args.get('idc')  # Obtener el parámetro 'idc' de la consulta
        task = await task_repo.find_by_id(id, idc)
        if task is None:
            return jsonify({"message": "Task not found"})
        serialized_task = task.__dict__
        return jsonify(serialized_task)
    except PyMongoError as e:
        return jsonify({"Error": f"{e}"})

@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        idc = request.args.get('idc')  # Obtener el parámetro 'idc' de la consulta
        data = request.get_json()
        return _save_task(idc, data)
    except PyMongoError as e:
        return jsonify({"Error": f"{e}"})
    except KeyError as e:
        abort(400, description=f"Missing key: {e}")

@app.route('/tasks/<id>', methods=['PUT'])
def update_task(id):
    try:
        idc = request.args.get('idc')  # Obtener el parámetro 'idc' de la consulta
        data = request.get_json()
        return _save_task(idc, data, id)
    except PyMongoError as e:
        return jsonify({"Error": f"{e}"})
    except KeyError as e:
        abort(400, description=f"Missing key: {e}")

@app.route('/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    try:
        idc = request.args.get('idc')  # Obtener el parámetro 'idc' de la consulta
        task_repo.delete_by_id(id, idc)
        return jsonify({"message": "Task deleted successfully"})
        return jsonify(serialized_task)
    except PyMongoError as e:
        return jsonify({"Error": f"{e}"})
#endregion

#region Users
@app.route('/users/<email>', methods=['GET'])
async def get_user(email):
    try:
        passw = request.args.get('pass')  # Obtener el parámetro 'pass' de la consulta
        user = await user_repo.find_by_id(email, email)
        if user is None:
            return jsonify({"message": "User not found"})
        elif user.password != passw:
            return jsonify({"message": "Invalid password"})
        serialized_user = user.__dict__
        return jsonify(serialized_user)
    except PyMongoError as e:
        return jsonify({"Error": f"{e}"})

@app.route('/users', methods=['POST'])
async def create_user():
    try:
        data = request.get_json()
        return await _save_user(data['email'], data, data['email'])
    except PyMongoError as e:
        return jsonify({"Error": f"{e}"})
    except KeyError as e:
        abort(400, description=f"Missing key: {e}")

@app.route('/users/<email>', methods=['PUT'])
async def update_user(email):
    try:
        passw = request.args.get('pass')  # Obtener el parámetro 'pass' de la consulta
        data = request.get_json()
        get_user = await user_repo.find_by_id(email, email)
        if get_user is None:
            return jsonify({"message": "User not found"})
        elif get_user.password != passw:
            return jsonify({"message": "Invalid password"})
        return await _save_user(email, data, email)
    except PyMongoError as e:
        return jsonify({"Error": f"{e}"})

@app.route('/users/<email>', methods=['DELETE'])
def delete_user(email):
    try:
        passw = request.args.get('pass')  # Obtener el parámetro 'pass' de la consulta
        get_user = user_repo.find_by_id(email, email)
        if get_user is None:
            return jsonify({"message": "User not found"})
        elif get_user.password != passw:
            return jsonify({"message": "Invalid password"})
        user_repo.delete_by_id(email, email)
        return jsonify({"message": "User deleted successfully"})
    except PyMongoError as e:
        return jsonify({"Error": f"{e}"})
#endregion


if __name__ == '__main__':
    asyncio.run(debug=True)

def _save_task(idc, data, id = None):
    new_task = Task(title=data['title'], description=data['description'], done=data['done'], end_date=data['end_date'], id = id)
    saved_task = task_repo.save(new_task, idc, new_task.id)

    if saved_task is None:
        return jsonify({"message": "Failed to save task"})

    serialized_task = saved_task.__dict__

    # If serialized_task have '_id' cast to str
    if '_id' in serialized_task:
        serialized_task['_id'] = str(serialized_task['_id'])

    return jsonify(serialized_task)

async def _save_user(idc, data, email):
    new_user = User(name=data['name'], email=data['email'], password=data['password'])
    saved_user = await user_repo.save(new_user, idc, email)

    if saved_user is None:
        return jsonify({"message": "Failed to save user"})

    serialized_user = saved_user.__dict__

    # If serialized_user have '_id' cast to str
    if '_id' in serialized_user:
        serialized_user['_id'] = str(serialized_user['_id'])

    return jsonify(serialized_user)