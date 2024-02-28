from pymongo import MongoClient

class MongoValidators:
    def __init__(self):
        client = MongoClient("mongodb://root:example@mongodb:27017/")
        self.db = client.testdb

    def apply_mongo_shema(self, schema: dict, collection: str):
        try:
            validate = self.db.command({"collStats": collection, "scale": 1})["validator"]
        except KeyError:
            # La clave 'validator' no está presente, la colección no tiene validación de esquema
            validate = None

        if validate is not None:
            self.db.command({
                "collMod": collection,
                "validator": {
                    "$jsonSchema": schema
                }
            })

    # def __init__(self, title: str, description: str, done: bool, end_date: str, update_date: str = str(time.time()), create_date: str = str(time.time()), id: str = str(uuid.uuid4()), ):
    def apply_task_mongo_shema(self, collection: str):
        # Apply regex to validate the date format and the id format like a UUID
        date_regex = "^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}$"
        schema = {
            "bsonType": "object",
            "required": ["id", "title", "description", "done", "is_important", "end_date", "create_date", "update_date"],
            "properties": {
                "id": {
                    "bsonType": "string",
                    "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
                },
                "title": {
                    "bsonType": "string",
                    "maxLength": 50
                },
                "description": {
                    "bsonType": "string",
                    "maxLength": 200
                },
                "done": {
                    "bsonType": "bool"
                },
                "is_important": {
                    "bsonType": "bool"
                },
                "end_date": {
                    "bsonType": "string",
                    "pattern": date_regex
                },
                "create_date": {
                    "bsonType": "string",
                    "pattern": date_regex
                },
                "update_date": {
                    "bsonType": "string",
                    "pattern": date_regex
                }
            }
        }
        self.apply_mongo_shema(schema, collection)
