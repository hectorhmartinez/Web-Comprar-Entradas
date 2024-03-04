import time
from http import HTTPStatus
from lock import lock

from flask_httpauth import HTTPBasicAuth
from flask import g, current_app
from flask_restful import reqparse
from jwt import encode, decode, ExpiredSignatureError, InvalidSignatureError
from passlib.apps import custom_app_context as pwd_context

from db import db

auth = HTTPBasicAuth()


class AccountsModel(db.Model):
    __tablename__ = 'accounts'

    username = db.Column(db.String(30), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    # 0 not admin/ 1 is admin
    is_admin = db.Column(db.Integer, nullable=False)
    available_money = db.Column(db.Integer)
    orders = db.relationship('OrdersModel', backref='orders', lazy=True)

    def __init__(self, username, available_money=500, is_admin=0):
        self.username = username
        self.available_money = available_money
        self.is_admin = is_admin

    def json(self):
        return {'username': self.username,
                'is_admin': self.is_admin, 'available_money': self.available_money}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_username(self, username):
        account = self.query.get(username)
        if not account:
            return None
        return account

    @classmethod
    def delete_by_username(self, username):
        with lock.lock:
            account = self.query.get(username)
            # delete account if it exists
            if account is not None:
                try:
                    account.delete_from_db()
                except:
                    return {"message": "An error occurred deleting the accounts."}, HTTPStatus.INTERNAL_SERVER_ERROR
                return True
            return None

    @classmethod
    def post(self):
        parser = reqparse.RequestParser()
        # define all input parameters need and its type
        parser.add_argument('username', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('password', type=str, required=True)
        data = parser.parse_args()
        with lock.lock:
            account = AccountsModel.get_by_username(data['username'])
            if account:
                return {'message': "account with username [{}] already exists".format(
                    data['username'])}, HTTPStatus.NOT_FOUND

            new_account = AccountsModel(data["username"])
            new_account.hash_password(data["password"])
            try:
                new_account.save_to_db()
            except:
                return {"message": "An error occurred inserting the teams."}, HTTPStatus.INTERNAL_SERVER_ERROR

            return new_account

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        a = pwd_context.verify(password, self.password)
        print("VerifyPWD ACCOUNTSMODEL: " + str(a))
        return a

    def generate_auth_token(self, expiration=600):
        return encode(
            {"username": self.username, "exp": int(time.time()) + expiration},
            current_app.secret_key,
            algorithm="HS256"
        )

    @classmethod
    def verify_auth_token(cls, token):
        try:
            data = decode(token, current_app.secret_key, algorithms=["HS256"])
        except ExpiredSignatureError:
            print('expiredToken')
            return None  # expired token
        except InvalidSignatureError:
            print('invalidToken')
            return None  # invalid token

        user = cls.query.filter_by(username=data['username']).first()

        return user


@auth.verify_password
def verify_password(token, password):
    usuari = AccountsModel.verify_auth_token(token)

    if usuari:
        g.user = usuari
        return usuari


@auth.get_user_roles
def get_user_roles(user):
    print(user)
    return 'admin' if user.is_admin == 1 else 'user'
