from pymongo import MongoClient

class MongoValidators:
    def __init__(self, db_user, db_pass):
        client = MongoClient(f"mongodb://{db_user}:{db_pass}@mongodb:27017/")
        self.db = client.testdb

        self.date_regex = "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6}$"
        self.id_regex = "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[4][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
        self.email_regex = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$"
        self.password_regex = "^.{5,}$"

    def collection_exists(self, collection: str) -> bool:
        return collection in self.db.list_collection_names()

    def apply_mongo_shema(self, schema: dict, collection: str):
        try:
            if not self.collection_exists(collection):
                self.db.create_collection(collection)
            self.db.command({
                "collMod": collection,
                "validator": {"$jsonSchema": schema},
                "validationLevel": "moderate",
                "validationAction": "error"
            })
            print(f"Schema applied to {collection}")
        except Exception as e:
            print(f"Error: {e}")
            print(f"Schema not applied to {collection}")

    # def __init__(self, title: str, description: str, done: bool, end_date: str, update_date: str = str(time.time()), create_date: str = str(time.time()), id: str = str(uuid.uuid4()), ):
    def apply_task_mongo_shema(self, collection: str):
        
        schema = {
            "bsonType": "object",
            "required": ["id", "title", "description", "done", "is_important", "end_date", "create_date", "update_date"],
            "properties": {
                "id": {
                    "bsonType": "string",
                    "pattern": self.id_regex
                },
                "title": {"bsonType": "string", "maxLength": 50},
                "description": {"bsonType": "string", "maxLength": 200},
                "done": {"bsonType": "bool"},
                "is_important": {"bsonType": "bool"},
                "end_date": {"bsonType": "string", "pattern": self.date_regex},
                "create_date": {"bsonType": "string", "pattern": self.date_regex},
                "update_date": {"bsonType": "string", "pattern": self.date_regex}
            }
        }
        self.apply_mongo_shema(schema, collection)

    def apply_user_mongo_shema(self, collection: str):
        schema = {
            "bsonType": "object",
            "required": ["id", "name", "email", "password", "create_date", "update_date",],
            "properties": {
                "id": {"bsonType": "string", "pattern": self.id_regex},
                "name": {"bsonType": "string", "maxLength": 50},
                "email": {"bsonType": "string", "pattern": self.email_regex},
                "password": {"bsonType": "string", "pattern": self.password_regex},
                "create_date": {"bsonType": "string", "pattern": self.date_regex},
                "update_date": {"bsonType": "string", "pattern": self.date_regex}
            }
        }
        self.apply_mongo_shema(schema, collection)