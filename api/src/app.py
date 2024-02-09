from src.repositories.task_repository.task_repository_mongo import TaskRepositoryMongo
from src.repositories.task_repository.task_repository_maria import TaskRepositoryMaria
from src.models.task import Task
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
if DB_TYPE == "mongodb":
    task_repo = TaskRepositoryMongo("tasks")
elif DB_TYPE == "mariadb":
    task_repo = TaskRepositoryMaria("tasks")

@app.route('/')
def index():
    response = {
        'urls': [
            {'/': 'Index'},
            {'/tasks': 'Get all tasks'},
            {'/tasks/<id>': 'Get task by id'},
            {'/tasks': 'Create a task'},
            {'/tasks/<id>': 'Update a task'},
            {'/tasks/<id>': 'Delete a task'}
        ],
        'db_type': f'{DB_TYPE}'
    }
    return jsonify(response)

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