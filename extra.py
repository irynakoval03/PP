from sqlalchemy import create_engine, or_, and_
from sqlalchemy.sql import exists
from sqlalchemy.orm import sessionmaker, Query, aliased
from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api, reqparse
from typing import List, Any
from models import User, Audience, Reserve
import pandas as pd
import ast
from marshmallow import ValidationError,fields
import json

app = Flask(__name__)
api = Api(app)
ma = Marshmallow(app)
#@app.route('/')
#def index():
#    return "bkbcm"

class RestApi(Resource):
    def __init__(self):
        mysql_engine = create_engine("mysql+pymysql://root:Ira.ko03@127.0.0.1:3306/auditorium_reservation", encoding="utf-8",
                                     echo=True, future=True)
        Session = sessionmaker(bind=mysql_engine)
        self.session = Session()

class UserSchema(ma.Schema):
    class Meta:
        fields =('userId', 'username', 'firstName','lastName','email','password', 'phone')


user_schema =  UserSchema()
users_schemas = UserSchema(many=True)

class Users(RestApi):
    def post(self):

        username = request.json['username']
        firstName = request.json['firstName']
        lastName = request.json['lastName']
        email = request.json['email']
        password= request.json['password']
        phone = request.json['phone']

        if self.session.query(User).filter(User.username == username).one_or_none() != None:
            return 'User already exists with a such username.'

        user : User =User(username = username,
                  firstName = firstName,
                  lastName = lastName,
                  email = email,
                  password = password,
                  phone = phone
                   )

        self.session.add(user)
        self.session.commit()

        return {
                    'id': user.userId,
                    'username': user.username
               }, 200

    def get(self,username):
        user = self.session.query(User).get(username)
        return user_schema.jsonify(user)

api.add_resource(Users,'/user')
api.add_resource(Users,'/user/<username>')
#api.add_resource(Users,'/user/{username}')

#def post()
#    return jsonify({''})

if __name__=="__main__":
    app.run(debug=True)
