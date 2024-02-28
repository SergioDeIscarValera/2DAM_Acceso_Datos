from flask import Flask, jsonify, request, abort
from graphene import ObjectType, String, Schema

class Query(ObjectType):
    hello = String(name=String(default_value="World"))
    def resolve_hello(self, info, name):
        return 'Hello ' + name

schema = Schema(query=Query)

query_string = '{ hello }'

@app.route('/hello')
def hello():
    result = schema.execute(query_string)
    return jsonify(result.data)

if __name__ == '__main__':
    app.run(debug=True)