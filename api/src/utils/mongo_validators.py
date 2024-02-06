from pymongo import MongoClient

# class MongoValidators(metaclass=SingletonMeta):
#     def __init__(self):
#         client = MongoClient("mongodb://root:example@mongodb:27017/")
#         self.db = client.testdb

#     def apply_mongo_shema(self, schema: dict, collection: str):
#         validate = self.db.command({"collStats": collection, "scale": 1})["validator"]
#         if validate != None:
#             self.db.command({
#                 "collMod": collection,
#                 "validator": {
#                     "$jsonSchema": schema
#                 }
#             })

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