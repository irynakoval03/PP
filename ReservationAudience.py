from sqlalchemy import create_engine, or_, and_,Enum
from sqlalchemy.sql import exists
from sqlalchemy.orm import sessionmaker, Query, aliased
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse
from flask_marshmallow import Marshmallow
from typing import List, Any
from models import User, Audience, Reserve
import pandas as pd
import ast
from marshmallow import ValidationError, fields, post_load, EXCLUDE, INCLUDE
import json
from werkzeug.exceptions import HTTPException, NotFound, Conflict, BadRequest
import datetime
from flask_bcrypt import Bcrypt, check_password_hash
from datetime import timedelta
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.from_pyfile('settings.cfg')
db = SQLAlchemy(app)
#api = Api(app)
ma = Marshmallow(app)
auth = HTTPBasicAuth()

@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.errorhandler(ValidationError)
def handle_exception(e):
    return {
        "ValidationErrors": e.messages
    }, 400


@app.errorhandler(Exception)
def handle_exception(e):
    return {
        "Error": str(e)
    }, 500


class AuditoriumInputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Audience
        field = ('name')
        unknown = EXCLUDE

    @post_load
    def make_auditorium(self, data, **kwargs):
        return Audience(**data)

class AuditoriumOutputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ('audienceId', 'name')

@app.route("/auditorium", methods=['POST'])
@auth.login_required
def post_auditorium():
    schema = AuditoriumInputSchema()
    auditorium: Audience = schema.load(request.json)

    if db.session.query(Audience).filter(Audience.name == auditorium.name).one_or_none() != None:
        raise Conflict('Auditorium already exists with such name.')

    if auth.current_user().username != 'moderator':
        return 'Access error', 401

    db.session.add(auditorium)
    db.session.commit()
    return AuditoriumOutputSchema().dump(auditorium), 200

@app.route("/auditorium/<int:auditoriumId>", methods=['GET'])
def get_auditorium_by_id(auditoriumId: int):
    auditorium: Audience =  db.session.query(Audience).filter(Audience.audienceId == auditoriumId).one_or_none()
    if auditorium==None:
        raise NotFound('Auditorium does not exist with such id.')
    return AuditoriumOutputSchema().dump(auditorium), 200

@app.route("/auditorium/<int:audienceId>", methods=['PUT'])
@auth.login_required
def edit_auditorium(audienceId: int):
    auditorium_to_change: Audience = db.session.query(Audience).filter(Audience.audienceId == audienceId).one_or_none()
    if auditorium_to_change == None:
        raise NotFound('Auditorium does not exist with such id.')

    if auth.current_user().username != 'moderator':
        return 'Access error', 401
        
    schema = AuditoriumInputSchema()
    auditorium: Audience = schema.load(request.json)

    if db.session.query(Audience).filter(Audience.name == auditorium.name, Audience.audienceId != audienceId).one_or_none() != None:
        raise Conflict('Auditorium already exists with such name.')

    auditorium_to_change.name=auditorium.name
    db.session.commit()
    return AuditoriumOutputSchema().dump(auditorium_to_change), 200

@app.route("/auditorium/<audienceId>", methods=['DELETE'])
@auth.login_required
def delete_auditorium_by_id(audienceId):
    auditorium: Audience = db.session.query(Audience).filter(Audience.audienceId == audienceId).one_or_none()
    if auditorium == None:
        raise NotFound('Auditorium does not exist with such id.')

    if auth.current_user().username != 'moderator':
        return 'Access error', 401

    db.session.delete(auditorium)
    db.session.commit()

    return AuditoriumOutputSchema().dump(auditorium), 200


@app.route("/auditorium/findByStatus/<string:status>", methods=['GET'])
def get_auditorium_by_status(status: str):
    if status != 'available' and status != 'taken':
        raise ValidationError('Auditorium status is not valid')

    date  = datetime.datetime.utcnow()
    list = db.session.query(Audience).filter(
        Audience.audience.any(and_(Reserve.end > date, Reserve.begin < date)) == (status != 'available')
        ).all()
    return jsonify(AuditoriumOutputSchema().dump(list, many=True)), 200

class UserInputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ('username', 'firstName', 'lastName', 'email', 'password', 'phone')
        unknown = EXCLUDE

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)

class UserOutputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ('userId', 'username')

class GetUserOutputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ('userId', 'username', 'firstName', 'lastName', 'email', 'password', 'phone')

@app.route("/user", methods=['POST'])
def post_user():
    schema = UserInputSchema()
    user: User = schema.load(request.json)

    if db.session.query(User).filter(User.username == user.username).one_or_none() != None:
        raise Conflict('User already exists with such username.')
    
    user.password = bcrypt.generate_password_hash(user.password).decode("utf-8")
    db.session.add(user)
    db.session.commit()

    return GetUserOutputSchema().dump(user), 200

@auth.verify_password
def login(username, password):
    user = db.session.query(User).filter(User.username == username).one_or_none()
    if user is None:
        return False

    if not bcrypt.check_password_hash(user.password, password):
        return False

    return user

@app.route("/user/<username>", methods=['PUT'])
@auth.login_required
def edit_user(username):
    user_to_change: User = db.session.query(User).filter(User.username == username).one_or_none()
    if user_to_change == None:
        raise NotFound('User does not exist with such username.')
    if auth.username() != username:
        return 'Access error', 401
    schema = UserInputSchema()
    user: User = schema.load(request.json)
    if db.session.query(User).filter(User.username == user.username).one_or_none() !=None:
        raise Conflict('User already exists with such username.')
    user_to_change.username=user.username
    user_to_change.firstName=user.firstName
    user_to_change.lastName=user.lastName
    user_to_change.email=user.email
    user_to_change.password=bcrypt.generate_password_hash(user.password).decode("utf-8")
    user_to_change.phone=user.phone
    db.session.commit()
    return GetUserOutputSchema().dump(user_to_change), 200

@app.route("/user/<username>", methods=['GET'])
def get_user_by_id(username):
    user: User =  db.session.query(User).filter(User.username == username).one_or_none()
    if user == None:
        raise NotFound('User does not exist with such username.')
    return GetUserOutputSchema().dump(user), 200

@app.route("/user/<username>", methods=['DELETE'])
@auth.login_required
def delete_user_by_id(username):
    user: User = db.session.query(User).filter(User.username == username).one_or_none()
    if user == None:
        raise NotFound('Reservation does not exist with such id.')

    if auth.username() != username:
        return 'Access error', 401

    db.session.delete(user)
    db.session.commit()

    return GetUserOutputSchema().dump(user), 200

class ReserveInputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reserve
        fields = ('begin', 'end', 'userId', 'audienceId')
        unknown = EXCLUDE

    @post_load
    def make_reserve(self, data, **kwargs):
        return Reserve(**data)


class ReserveOutputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ('reserveId', 'userId', 'audienceId', 'begin', 'end')


@app.route("/reserve", methods=['POST'])
@auth.login_required
def post_reserve():
    schema = ReserveInputSchema()
    reserve: Reserve = schema.load(request.json)

    auditorium: Audience = db.session.query(Audience).filter(Audience.audienceId == reserve.audienceId).one_or_none()
    if auditorium is None:
        raise NotFound('Auditorium does not exist with such id.')

    user: User = db.session.query(User).filter(User.userId == reserve.userId).one_or_none()
    if user is None:
        raise NotFound('User does not exist with such username.')

    if auth.username() != user.username:
        return 'Access error', 401

    q = db.session.query(Reserve).filter(
        Reserve.audienceId == reserve.audienceId,
        Reserve.begin < reserve.end,
        Reserve.end > reserve.begin, reserve.end>reserve.begin)
    if (db.session.query(q.exists()).scalar()):
        raise Conflict('Auditorium is not available at that time.')

    dur= reserve.end-reserve.begin
    dur_in_s = dur.total_seconds()
    hours = divmod(dur_in_s, 3600)[0]
    days = dur.days
    days = divmod(dur_in_s, 86400)[0]
    if hours< 1 or days > 5:
        raise BadRequest('Time for reservation is incorrect.')

    db.session.add(reserve)
    db.session.commit()

    return ReserveOutputSchema().dump(reserve), 200

@app.route("/reserve/<reserveId>", methods=['PUT'])
@auth.login_required
def edit_reserve(reserveId):
    reserve_to_change: Reserve = db.session.query(Reserve).filter(Reserve.reserveId == reserveId).one_or_none()
    if reserve_to_change is None:
        raise NotFound('Reservation does not exist with such id.')

    schema = ReserveInputSchema()
    reserve: Reserve = schema.load(request.json)

    auditorium: Audience = db.session.query(Audience).filter(Audience.audienceId == reserve.audienceId).one_or_none()
    if auditorium is None:
        raise NotFound('Auditorium does not exist with such id.')

    user: User = db.session.query(User).filter(User.userId == reserve.userId).one_or_none()
    if user is None:
        raise NotFound('User does not exist with such username.')

    if auth.username() != user.username:
        return 'Access error', 401

    q = db.session.query(Reserve).filter(
        Reserve.audienceId == reserve.audienceId,
        Reserve.reserveId != reserve.reserveId,
        Reserve.begin < reserve.end,
        Reserve.end > reserve.begin)
    if (db.session.query(q.exists()).scalar()):
        raise Conflict('Auditorium is not available at that time.')

    dur = reserve.end - reserve.begin
    dur_in_s = dur.total_seconds()
    hours = divmod(dur_in_s, 3600)[0]
    days = dur.days
    days = divmod(dur_in_s, 86400)[0]
    if hours < 1 or days > 5:
        raise BadRequest('Time for reservation is incorrect.')

    if int(reserve_to_change.userId) != int(reserve.userId):
        return 'You can reserve auditorium only for yourself', 401
    reserve_to_change.userId = reserve.userId
    reserve_to_change.audienceId = reserve.audienceId
    reserve_to_change.begin = reserve.begin
    reserve_to_change.end = reserve.end
    db.session.commit()

    return ReserveOutputSchema().dump(reserve_to_change), 200

@app.route("/reserve/<reserveId>", methods=['GET'])
@auth.login_required
def get_reservation_by_id(reserveId):
    reserve: Reserve =  db.session.query(Reserve).filter(Reserve.reserveId == reserveId).one_or_none()
    if reserve == None:
        raise NotFound('Reservation does not exist with such id.')

    user: User = db.session.query(User).filter(User.userId == reserve.userId).one_or_none()
    if user is None:
        raise NotFound('User does not exist with such username.')

    if auth.username() != user.username:
        return 'Access error', 401

    return ReserveOutputSchema().dump(reserve), 200

@app.route("/reserve/<reserveId>", methods=['DELETE'])
@auth.login_required
def delete_reservation_by_id(reserveId):
    reserve: Reserve = db.session.query(Reserve).filter(Reserve.reserveId == reserveId).one_or_none()
    if reserve == None:
        raise NotFound('Reservation does not exist with such id.')

    user: User = db.session.query(User).filter(User.userId == reserve.userId).one_or_none()
    if user is None:
        raise NotFound('User does not exist with such username.')

    if auth.username() != user.username:
        return 'Access error', 401

    db.session.delete(reserve)
    db.session.commit()

    return ReserveOutputSchema().dump(reserve), 200


if __name__ == "__main__":
    app.run(debug=True)


#create_user
#curl -X POST http://127.0.0.1:5000/user -H "Content-Type: application/json" --data "{\"username\": \"user1\", \"firstName\": \"Bohdana\", \"lastName\": \"Honserovska\", \"email\": \"someemail@gmail.com\", \"password\": \"1111\", \"phone\": \"0992341122\"}"
#curl -X POST http://127.0.0.1:5000/user -H "Content-Type: application/json" --data "{\"username\": \"moderator\", \"firstName\": \"Bohdana\", \"lastName\": \"Honserovska\", \"email\": \"someemail@gmail.com\", \"password\": \"1111\", \"phone\": \"0992341122\"}"
#curl -X POST http://127.0.0.1:5000/user -H "Content-Type: application/json" --data "{\"username\": \"to_delete\", \"firstName\": \"Bohdana\", \"lastName\": \"Honserovska\", \"email\": \"someemail@gmail.com\", \"password\": \"1111\", \"phone\": \"0992341122\"}"

#edit_user
#curl -X PUT http://127.0.0.1:5000/user/user1 -H "Content-Type: application/json" --data "{\"username\": \"new_user\", \"firstName\": \"Bohdana\", \"lastName\": \"Honserovska\", \"email\": \"newemail@gmail.com\", \"password\": \"1234\"}"
#curl --user to_delete:1111 --request PUT http://127.0.0.1:5000/user/to_delete -H "Content-Type: application/json" --data "{\"username\": \"new_user\", \"firstName\": \"Bohdana\", \"lastName\": \"Honserovska\",\"email\": \"newemail@gmail.com\", \"password\": \"1234\"}"

#get_user
#curl -X GET http://127.0.0.1:5000/user/new_user

#delete_user
#curl -X DELETE http://127.0.0.1:5000/user/to_delete
#curl --user user1:1 --request DELETE http://127.0.0.1:5000/user/new_user

#create_auditorium
#curl -X POST http://127.0.0.1:5000/auditorium -H "Content-Type: application/json" --data "{\"name\": \"101\"}"
#curl --user moderator:1111 --request POST http://127.0.0.1:5000/auditorium -H "Content-Type: application/json" --data "{\"name\": \"101\"}"

#edit_auditorium
#curl -X PUT http://127.0.0.1:5000/auditorium -H "Content-Type: application/json" --data "{\"name\": \"102\"}"
#curl --user moderator:1111 --request PUT http://127.0.0.1:5000/auditorium/1 -H "Content-Type: application/json" --data "{\"name\": \"103\"}"

#delete_auditorium
#curl -X DELETE http://127.0.0.1:5000/auditorium/1
#curl --user moderator:1111 --request DELETE http://127.0.0.1:5000/auditorium/1

#get_auditorium
#curl -X GET http://127.0.0.1:5000/auditorium/1

#reserve_auditorium
#curl -X POST http://127.0.0.1:5000/reserve -H "Content-Type: application/json" --data "{\"begin\": \"2021-11-24 11:00\", \"end\": \"2021-11-24 13:00\", \"userId\": \"2\", \"audienceId\": \"1\"}"
#curl --user user1:1111 --request POST http://127.0.0.1:5000/reserve -H "Content-Type: application/json" --data "{\"begin\": \"2021-11-27 11:00\", \"end\": \"2021-11-27 13:00\", \"userId\": \"4\", \"audienceId\": \"2\"}"

#edit_reserve
#curl -X PUT http://127.0.0.1:5000/reserve/1 -H "Content-Type: application/json" --data "{\"begin\": \"2021-11-23 18:00\", \"end\": \"2021-11-24 19:30\", \"userId\": \"2\", \"audienceId\": \"1\"}"
#curl --user user1:1111 --request PUT http://127.0.0.1:5000/reserve/2 -H "Content-Type: application/json" --data "{\"begin\": \"2021-11-23 11:00\", \"end\": \"2021-11-23 12:30\", \"userId\": \"4\", \"audienceId\": \"2\"}"

#get_reserve
#curl -X GET http://127.0.0.1:5000/reserve/4
#curl --user user2:1111 --request GET http://127.0.0.1:5000/reserve/2

#delete_reserve
#curl -X DELETE http://127.0.0.1:5000/reserve/4
#curl --user user1:1111 --request DELETE http://127.0.0.1:5000/reserve/1