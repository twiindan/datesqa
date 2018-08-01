import json

from flask import Flask, request, redirect, render_template, g, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

auth = HTTPBasicAuth()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dateqa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
db = SQLAlchemy(app)


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    surname = db.Column(db.String(80))
    gender = db.Column(db.String(6))
    age = db.Column(db.Integer)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(64))


    def __repr__(self):
        return '<name: {}\n surname: {}\n gender: {}\n age: {}\ username{}\n>'.format(self.name, self.surname, self.gender, self.age, self.username)

    def __str__(self):
        return '<name: {}\n surname: {}\n gender: {}\n age: {}\ username{}\n>'.format(self.name, self.surname, self.gender, self.age, self.username)

    def get_user(self):
        return {"name": self.name, 'surname': self.surname, 'age': self.age, 'gender': self.gender, 'username': self.username}

    def update_user(self, user):
        self.name = user['name']
        self.surname = user['surname']
        self.gender = user['gender']
        self.age = user['age']
        self.username = user['username']
        self.password = user['password']

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sports = db.Column(db.Boolean)
    games = db.Column(db.Boolean)
    dancing = db.Column(db.Boolean)
    travel = db.Column(db.Boolean)
    cinema = db.Column(db.Boolean)
    music = db.Column(db.Boolean)

    def __init__(self, user_id, interests):
        self.user_id = user_id
        self.sports = interests['sports']
        self.games = interests['games']
        self.dancing = interests['dancing']
        self.travel = interests['travel']
        self.cinema = interests['cinema']
        self.music = interests['music']

    def get_interests(self):
        return {"sports": self.sports,
                'games': self.games,
                'dancing': self.dancing,
                'travel': self.travel,
                'cinema': self.cinema,
                'music': self.music}


@app.route('/user', methods=['POST'])
def user():
    body = request.get_json()
    username = request.json.get('username')
    password = request.json.get('password')
    name = request.json.get('name')
    surname = request.json.get('surname')
    age = request.json.get('age')
    gender = request.json.get('gender')


    if username is None or password is None:
        abort(400)    # missing arguments

    if User.query.filter_by(username=username).first() is not None:
        abort(400)  # existing user

    user = User(username=username, name=name, surname=surname, age=age, gender=gender)
    user.hash_password(password)
    db.session.add(user)
    db.session.flush()
    db.session.commit()

    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/users/<int:id>', methods=['GET'])
@auth.login_required
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify(user.get_user())


@app.route('/users/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_user(id):
    User.query.filter(User.id == id).delete()
    db.session.commit()
    return 'user deleted'



@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@auth.login_required
@app.route('/user/<int:user_id>', methods=['DELETE', 'PUT'])
def user_data(user_id):

    user = User.query.get(user_id)
    if not user:
        redirect('/')

    if request.method == 'DELETE':
        User.query.filter(User.id == user_id).delete()
        db.session.commit()
        return 'user deleted'

    if request.method == 'PUT':
        body = request.get_json()
        user.update_user(body)
        db.session.commit()
        return jsonify(user.get_user())

@app.route('/user/<int:user_id>/interests', methods=['PUT', 'GET'])
def interest_data(user_id):

    user = User.query.get(user_id)
    if not user:
        redirect('/')

    if request.method == 'PUT':
        body = request.get_json()
        new_interest = Interest(user_id=user_id, interests=body)
        db.session.add(new_interest)
        db.session.flush()
        db.session.commit()
        return 'interests updated'

    if request.method == 'GET':
        interest_test = Interest.query.get(user_id)
        return jsonify(interest_test.get_interests())


if __name__ == '__main__':
    app.run(debug=True)
