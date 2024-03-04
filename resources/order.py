from http import HTTPStatus

from flask_restful import Resource, reqparse

from db import db
from models.accounts import AccountsModel, auth
from models.matches import MatchesModel
from models.orders import OrdersModel
from flask import g


class Orders(Resource):
    def get(self, username):
        order = OrdersModel.get_by_username(username)
        return {'order': order.json()}, HTTPStatus.OK if order else HTTPStatus.NOT_FOUND


    def post(self, username):
        if username != g.user.username:
            return {'message': "username [{}] is not the same associated with the token"}.format(
                username), HTTPStatus.BAD_REQUEST

        order = OrdersModel.post_by_username(username)
        if type(order) is tuple:
            return order
        return {'order': order.json()}, HTTPStatus.OK if order else HTTPStatus.NOT_FOUND


class OrdersList(Resource):

    def get(self):
        if OrdersModel.query.all() == 0:
            return {'message': "There are no orders"}, HTTPStatus.NOT_FOUND
        orders_list = list()
        for order in OrdersModel.query.all():
            orders_list.append(order.json())

        return {'orders': orders_list}, HTTPStatus.OK if orders_list else HTTPStatus.NOT_FOUND


    def get(self, username):
        orders_list = list()
        orders = OrdersModel.query.filter_by(username=username).all()
        if len(orders) == 0:
            return {'message': "There are no orders"}, HTTPStatus.NOT_FOUND
        for order in orders:
            orders_list.append(order.json())

        return {'orders': orders_list}, HTTPStatus.OK if orders_list else HTTPStatus.NOT_FOUND


    @auth.login_required(role='user')
    def post(self, username):
        if username != g.user.username:
            return {'message': "username [{}] is not the same associated with the token"}.format(
                username), HTTPStatus.BAD_REQUEST

        total = 0
        parser = reqparse.RequestParser()  # create parameters parser from request
        # define all input parameters need and its type
        parser.add_argument('orders', type=dict, action='append', required=True, help="This field cannot be left blank")
        data = parser.parse_args()

        # Consulteu l'usuari actual: filtreu per nom d'usuari
        account = AccountsModel.get_by_username(username)
        if not account:
            return {'message': "account with username [{}] does not exists".format(
                username)}, HTTPStatus.NOT_FOUND

        for order in data["orders"]:
            # Consulteu el partit actual: filtreu per match_id
            match = MatchesModel.get_by_id(order["match_id"])
            if not match:
                return {'message': "match with id [{}] does not exists".format(order["match_id"])}, HTTPStatus.NOT_FOUND
            total += round((match.price * order["tickets_bought"]), 2)

        if account.available_money < total:
            return {
                       'message': "account with username [{}] does not have enough money to buy all these tickets"
                                  "with total price of [{}]. Account has [{}] euros left".format(
                           username, total, account.available_money)}, HTTPStatus.NOT_FOUND

        for order in data["orders"]:
            # Consulteu el partit actual: filtreu per match_id
            match = MatchesModel.get_by_id(order["match_id"])
            tickets_bought = order["tickets_bought"]
            if not match:
                return {'message': "match with id [{}] does not exists".format(order["match_id"])}, HTTPStatus.NOT_FOUND

            # Comproveu si l'usuari té prou diners per comprar el bitllet
            money_spent = round((match.price * tickets_bought), 2)
            if account.available_money < money_spent:
                return {
                           'message': "account with username [{}] does not have enough money to buy [{}] ticket(s) from match "
                                      "with id [{}], the price is [{}], account has [{}] euros left".format(
                               username, order["tickets_bought"], order["match_id"], money_spent,
                               account.available_money)}, HTTPStatus.NOT_FOUND

            # Comproveu si hi ha entrades disponibles
            if match.total_available_tickets < tickets_bought:
                return {
                           'message': "match with id [{}] only has [{}] tickets available, you were trying to buy [{}]".format(
                               order["match_id"], match.total_available_tickets,
                               order["tickets_bought"])}, HTTPStatus.NOT_FOUND

            # Actualitzeu les entrades disponibles (- entrades comprades)
            match.total_available_tickets -= tickets_bought

            # Actualitzeu els diners de l'usuari després de comprar els bitllets (-preu * bitllets comprat)
            account.available_money -= (match.price * tickets_bought)

            # Inicialitzar OrdersModel(match_id, tickets_bought)
            new_order = OrdersModel(order["match_id"], tickets_bought)

            # Afegiu la comanda a la relació d'usuari user.orders.append(new_order)
            account.orders.append(new_order)

            # Deseu la comanda, l'espectacle i l'usuari a la BD.
            try:
                db.session.add(new_order)
                db.session.add(match)
                db.session.add(account)
            except:
                db.rollback()
                return {'message': "error afegint comanda, match i user a db"}, HTTPStatus.NOT_FOUND
            try:
                db.session.commit()
            except:
                db.rollback()
                return {'message': "error afegint comanda, match i user a db (commit)"}, HTTPStatus.NOT_FOUND

        return {'orders': [order for order in data["orders"]]}, HTTPStatus.OK if data["orders"] \
            else HTTPStatus.NOT_FOUND
