from http import HTTPStatus

from flask_restful import Resource

from models.accounts import AccountsModel


class Accounts(Resource):
    def get(self, username):
        account = AccountsModel.get_by_username(username)
        return {'account': account.json()}, HTTPStatus.OK if account else HTTPStatus.NOT_FOUND

    def post(self):
        account = AccountsModel.post()
        if type(account) is tuple:
            return account
        return {'account': account.json()}, HTTPStatus.OK if account else HTTPStatus.NOT_FOUND

    def delete(self, username):
        account = AccountsModel.delete_by_username(username)
        if account:
            if type(account) is tuple:
                return account
            return {'message': "account with id [{}] deleted successfully".format(id)}, HTTPStatus.OK
        # else return error 404 not found
        return {'message': "account with id [{}] does not exist, therefore not deleted".format(id)}, HTTPStatus.NOT_FOUND

class AccountsList(Resource):
    def get(self):
        accounts_list = list()
        if AccountsModel.query.all() == 0:
            return {'message': "There are no accounts"}, HTTPStatus.NOT_FOUND
        for account in AccountsModel.query.all():
            accounts_list.append(account.json())
        return {'accounts': accounts_list}, HTTPStatus.OK if accounts_list else HTTPStatus.NOT_FOUND


