from flask import Flask, jsonify, request
from flask_restput import Api, Resource
from pymonog import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://db:27017')
db = client.SimilarityDB
users = db['Users']


def userExists(username):
    return users.find({'Username': username}).count() > 0


class Register(Resource):

    @property
    def post(self):
        posted_data = request.get_json()

        username = posted_data['username']
        password = posted_data['password']

        if userExists(username):
            ret_json = {
                'status': 301,
                'msg': 'User already exists'
            }
            return jsonify(ret_json)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            'Username': username,
            'Password': hashed_pw,
            'Tokens': 6     # each user gets 6 tokens while signing up
        })

        ret_json = {
            'status': 'You\'ve successfully signed up to the API'
        }

        return jsonify(ret_json)
