from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

import os

BASE_API = '/api'

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://db:27017')
db = client.SimilarityDB
users = db['Users']


def userExists(username):
    return users.count_documents({'Username': username}) > 0


class Register(Resource):

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

        users.insert_one({
            'Username': username,
            'Password': hashed_pw,
            'Tokens': 6  # each user gets 6 tokens while signing up
        })

        ret_json = {
            'status': 'You\'ve successfully signed up to the API'
        }

        return jsonify(ret_json)


def verifyPw(username, password):
    if not userExists(username):
        return False

    hashed_pw = users.find_one({
        'Username': username
    })['Password']

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True

    return False


def countTokens(username):
    return users.find_one({
        'Username': username
    })['Tokens']


class Detect(Resource):

    def post(self):
        posted_data = request.get_json()

        username = posted_data['username']
        password = posted_data['password']
        text1 = posted_data['text1']
        text2 = posted_data['text2']

        correct_pw = verifyPw(username, password)

        if not correct_pw or not userExists(username):
            ret_json = {
                'status': 302,
                'msg': 'Invalid username or password'
            }
            return jsonify(ret_json)

        num_tokens = countTokens(username)

        if num_tokens <= 0:
            ret_json = {
                'status': 303,
                'msg': 'You\re out of tokens please purchase more'
            }
            return jsonify(ret_json)

        # Calculate the edit distance
        nlp = spacy.load('en_core_web_sm')

        text1 = nlp(text1)
        text2 = nlp(text2)

        # Ratio is the degree of similarity between the texts
        ratio = text1.similarity(text2)

        ret_json = {
            'status': 200,
            'similarity': ratio,
            'msg': 'Similarity score generated successfully'
        }

        users.update_one({
            'Username': username,
        }, {
            '$set': {
                'Tokens': num_tokens - 1
            }
        })

        return jsonify(ret_json)


class Refill(Resource):

    def post(self):
        posted_data = request.get_json()

        username = posted_data['username']
        password = posted_data['admin_pw']
        refill_amount = posted_data['refill']

        if not userExists(username):
            ret_json = {
                'status': 301,
                'msg': 'Invalid username'
            }
            return jsonify(ret_json)

        admin_password = os.environ['ADMIN_PW']

        if not password == admin_password:
            ret_json = {
                'status': 304,
                'msg': 'Invalid admin password'
            }
            return jsonify(ret_json)

        current_tokens = countTokens(username)
        new_amount = current_tokens + refill_amount
        users.update_one({
            'Username': username
        }, {
            '$set': {
                'Tokens': new_amount
            }
        })

        ret_json = {
            'status': 200,
            'refill': new_amount,
            'msg': 'User refilled'
        }
        return jsonify(ret_json)


api.add_resource(Register, BASE_API + '/register')
api.add_resource(Detect, BASE_API + '/detect')
api.add_resource(Refill, BASE_API + '/refill')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
