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
from flask_bcrypt import Bcrypt
from datetime import timedelta

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.from_pyfile('settings.cfg')
db = SQLAlchemy(app)
#api = Api(app)
ma = Marshmallow(app)


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
def post_auditorium():
    schema = AuditoriumInputSchema()
    auditorium: Audience = schema.load(request.json)

    if db.session.query(Audience).filter(Audience.name == auditorium.name).one_or_none() != None:
        raise Conflict('Auditorium already exists with such name.')

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
def edit_auditorium(audienceId: int):
    auditorium_to_change: Audience = db.session.query(Audience).filter(Audience.audienceId == audienceId).one_or_none()
    if auditorium_to_change == None:
        raise NotFound('Auditorium does not exist with such id.')
        
    schema = AuditoriumInputSchema()
    auditorium: Audience = schema.load(request.json)

    if db.session.query(Audience).filter(Audience.name == auditorium.name, Audience.audienceId != audienceId).one_or_none() != None:
        raise Conflict('Auditorium already exists with such name.')

    auditorium_to_change.name=auditorium.name;
    db.session.commit()
    return AuditoriumOutputSchema().dump(auditorium_to_change), 200

@app.route("/auditorium/<audienceId>", methods=['DELETE'])
def delete_auditorium_by_id(audienceId):
    auditorium: Audience = db.session.query(Audience).filter(Audience.audienceId == audienceId).one_or_none()
    if auditorium == None:
        raise NotFound('Auditorium does not exist with such id.')

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

@app.route("/user/<username>", methods=['PUT'])
def edit_user(username):
    user_to_change: User = db.session.query(User).filter(User.username == username).one_or_none()
    if user_to_change == None:
        raise NotFound('User does not exist with such username.')
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
def delete_user_by_id(username):
    user: User = db.session.query(User).filter(User.username == username).one_or_none()
    if user == None:
        raise NotFound('Reservation does not exist with such id.')

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
def post_reserve():
    schema = ReserveInputSchema()
    reserve: Reserve = schema.load(request.json)

    auditorium: Audience = db.session.query(Audience).filter(Audience.audienceId == reserve.audienceId).one_or_none()
    if auditorium is None:
        raise NotFound('Auditorium does not exist with such id.')

    user: User = db.session.query(User).filter(User.userId == reserve.userId).one_or_none()
    if user is None:
        raise NotFound('User does not exist with such username.')

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

    reserve_to_change.userId = reserve.userId
    reserve_to_change.audienceId = reserve.reserveId
    reserve_to_change.begin = reserve.begin
    reserve_to_change.end = reserve.end
    db.session.commit()

    return ReserveOutputSchema().dump(reserve_to_change), 200

@app.route("/reserve/<reserveId>", methods=['GET'])
def get_reservation_by_id(reserveId):
    reserve: Reserve =  db.session.query(Reserve).filter(Reserve.reserveId == reserveId).one_or_none()
    if reserve == None:
        raise NotFound('Reservation does not exist with such id.')

    return ReserveOutputSchema().dump(reserve), 200

@app.route("/reserve/<reserveId>", methods=['DELETE'])
def delete_reservation_by_id(reserveId):
    reserve: Reserve = db.session.query(Reserve).filter(Reserve.reserveId == reserveId).one_or_none()
    if reserve == None:
        raise NotFound('Reservation does not exist with such id.')

    db.session.delete(reserve)
    db.session.commit()

    return ReserveOutputSchema().dump(reserve), 200


if __name__ == "__main__":
    app.run(debug=True)
