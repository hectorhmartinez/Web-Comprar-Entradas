from http import HTTPStatus

from flask_restful import reqparse

from db import db
from lock import lock

class TeamsModel(db.Model):
    __tablename__ = 'teams'  # This is table name
    __table_args__ = (db.UniqueConstraint('name'),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    country = db.Column(db.String(30), nullable=False)

    def __init__(self, name, country):
        self.name = name
        self.country = country

    def json(self):
        return {'id': self.id, 'name': self.name, 'country': self.country}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(self, id):
        team = self.query.get(id)
        if not team:
            return None
        return team

    @classmethod
    def get_by_name(self, given_name):
        team = TeamsModel.query.filter_by(name=given_name).first()
        if not team:
            return None
        return team

    @classmethod
    def delete_by_id(self, id):
        with lock.lock:
            team = self.query.get(id)
            # delete team if it exists
            if team is not None:
                try:
                    team.delete_from_db()
                except:
                    return {"message": "An error occurred deleting the teams."}, HTTPStatus.INTERNAL_SERVER_ERROR

                return True
            return None

    @classmethod
    def post_by_id(self, id=None):
        if id is None:
            id = max([x.id for x in TeamsModel.query.all()]) + 1
        team = TeamsModel.get_by_id(id)
        if team:
            return {'message': "team with id [{}] already exists".format(id)}, HTTPStatus.NOT_FOUND

        parser = reqparse.RequestParser()
        # define all input parameters need and its type
        parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('country', type=str)
        data = parser.parse_args()
        data["id"] = id
        with lock.lock:
            new_team = TeamsModel(data["name"], data["country"])
            new_team.id = data["id"]
            try:
                new_team.save_to_db()
            except:
                return {"message": "An error occurred inserting the teams."}, HTTPStatus.INTERNAL_SERVER_ERROR

            return new_team.json()

    @classmethod
    def put_by_id(self, id=None):
        parser = reqparse.RequestParser()  # create parameters parser from request

        # define all input parameters need and its type
        parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('country', type=str)
        data = parser.parse_args()
        data["id"] = id
        with lock.lock:
            team = self.query.get(id)
            if team:
                if data["name"]:
                    team.name = data["name"]
                if data["country"]:
                    team.country = data["country"]
                try:
                    team.save_to_db()
                except:
                    return {"message": "An error occurred inserting the teams."}, HTTPStatus.INTERNAL_SERVER_ERROR

            else:
                # if it does not exist, add it to teams
                new_team = TeamsModel(data["name"], data["country"])
                new_team.id = data["id"]
                try:
                    new_team.save_to_db()
                except:
                    return {"message": "An error occurred inserting the teams."}, HTTPStatus.INTERNAL_SERVER_ERROR

            team = self.query.get(id)
            return team
