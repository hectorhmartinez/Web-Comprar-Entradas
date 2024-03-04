from http import HTTPStatus

from flask_restful import Resource, reqparse

from models.accounts import AccountsModel


class Login(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        # define all input parameters need and its type
        parser.add_argument('username', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('password', type=str, required=True)
        data = parser.parse_args()

        account = AccountsModel.get_by_username(data["username"])
        if not account:
            return {'message': "account with username [{}] does not exist".format(
                data["username"])}, HTTPStatus.NOT_FOUND
        print("login data_password -> " + data["password"])
        verified_password = account.verify_password(data["password"])
        if not verified_password:
            return {'message': "password is incorrect for account with username [{}] ".format(
                data["username"])}, HTTPStatus.NOT_FOUND

        token = account.generate_auth_token()
        print(token.decode('ascii'))
        return {'token': token.decode('ascii')}, HTTPStatus.OK if token else HTTPStatus.NOT_FOUND
