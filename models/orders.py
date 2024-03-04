from http import HTTPStatus

from flask_restful import reqparse
from lock import lock
from db import db
from models.accounts import AccountsModel
from models.matches import MatchesModel


class OrdersModel(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), db.ForeignKey('accounts.username'), nullable=False)
    match_id = db.Column(db.Integer, nullable=False)
    tickets_bought = db.Column(db.Integer, nullable=False)

    def __init__(self, match_id, tickets_bought):
        self.match_id = match_id
        self.tickets_bought = tickets_bought

    def json(self):
        return {'match_id': self.match_id, 'tickets_bought': self.tickets_bought, 'username': self.username}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_username(self, given_username):
        order = OrdersModel.query.filter_by(username=given_username).first()
        if not order:
            return None
        return order

    """orders = OrdersModel.query.filter_by(username=given_username).all()
        orders_list = list()
        if not orders:
            return None
        for order in orders:
            orders_list.append(order.json())
        return {'orders': orders_list}, HTTPStatus.OK if orders_list else HTTPStatus.NOT_FOUND
    """

    @classmethod
    def post_by_username(self, given_username):
        parser = reqparse.RequestParser()  # create parameters parser from request
        # define all input parameters need and its type
        parser.add_argument('match_id', type=int, required=True, help="This field cannot be left blank")
        parser.add_argument('tickets_bought', type=int, required=True, help="This field cannot be left blank")
        data = parser.parse_args()
        data["username"] = given_username
        with lock.lock:
            # Consulteu l'usuari actual: filtreu per nom d'usuari
            account = AccountsModel.get_by_username(given_username)
            if not account:
                return {'message': "account with username [{}] does not exists".format(
                    given_username)}, HTTPStatus.NOT_FOUND

            # Consulteu el partit actual: filtreu per match_id
            match = MatchesModel.get_by_id(data["match_id"])
            if not match:
                return {'message': "match with id [{}] does not exists".format(data["match_id"])}, HTTPStatus.NOT_FOUND

            # Comproveu si l'usuari té prou diners per comprar el bitllet
            money_spent = round((match.price * data["tickets_bought"]), 2)
            if account.available_money < money_spent:
                return {'message': "account with username [{}] does not have enough money to buy [{}] ticket(s) from match "
                                   "with id [{}], the price is [{}], account has [{}] euros left".format(
                    given_username, data["tickets_bought"], data["match_id"], money_spent,
                    account.available_money)}, HTTPStatus.NOT_FOUND

            # Comproveu si hi ha entrades disponibles
            if match.total_available_tickets < data["tickets_bought"]:
                return {'message': "match with id [{}] only has [{}] tickets available, you were trying to buy [{}]".format(
                    data["match_id"], match.total_available_tickets, data["tickets_bought"])}, HTTPStatus.NOT_FOUND

            # Actualitzeu les entrades disponibles (- entrades comprades)
            match.total_available_tickets -= data["tickets_bought"]

            # Actualitzeu els diners de l'usuari després de comprar els bitllets (-preu * bitllets comprat)
            account.available_money -= (match.price * data["tickets_bought"])

            # Inicialitzar OrdersModel(match_id, tickets_bought)
            new_order = OrdersModel(data["match_id"], data["tickets_bought"])

            # Afegiu la comanda a la relació d'usuari user.orders.append(new_order)
            account.orders.append(new_order)

            # Deseu la comanda, l'espectacle i l'usuari a la BD.
            try:
                db.session.add(new_order)
                db.session.add(match)
                db.session.add(account)
                db.session.commit()
            except:
                db.rollback()
                return {'message': "error afegint comanda, match i user a db"}, HTTPStatus.NOT_FOUND
            return new_order
