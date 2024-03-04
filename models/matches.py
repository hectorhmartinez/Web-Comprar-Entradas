from datetime import datetime
from http import HTTPStatus

from flask_restful import reqparse

from db import db
from lock import lock
from models.competitions import CompetitionsModel
from models.teams import TeamsModel


class MatchesModel(db.Model):
    __tablename__ = 'matches'  # This is table name
    __table_args__ = (db.UniqueConstraint('local_id', 'visitor_id', 'competition_id', 'date'),)

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_available_tickets = db.Column(db.Integer)

    local_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    visitor_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    local = db.relationship("TeamsModel", foreign_keys=[local_id])
    visitor = db.relationship("TeamsModel", foreign_keys=[visitor_id])

    competition_id = db.Column(db.Integer, db.ForeignKey("competitions.id"), nullable=False)
    competition = db.relationship("CompetitionsModel", foreign_keys=[competition_id], back_populates="matches")

    def __init__(self, date, price, total_available_tickets):
        self.date = date
        self.price = price
        self.total_available_tickets = total_available_tickets

    def json(self):
        return {'id': self.id, 'date': self.date.isoformat(), 'price': self.price,
                'total_available_tickets': self.total_available_tickets if self.total_available_tickets else None,
                'local': self.local.json() if self.local else None,
                'visitor': self.visitor.json() if self.visitor else None,
                'competition': self.competition.name if self.competition else None,
                'competition_id': self.competition_id if self.competition_id else None}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(self, id):
        match = self.query.get(id)
        if not match:
            return None
        return match

    @classmethod
    def delete_by_id(self, id):
        with lock.lock:
            match = self.query.get(id)
            # delete team if it exists
            if match is not None:
                # TODO: adaptar el codi per si retorna la tupla del error a tots esl try except
                try:
                    match.delete_from_db()
                except:
                    return {"message": "An error occurred deleting the match."}, HTTPStatus.INTERNAL_SERVER_ERROR
                return True
            return None

    @classmethod
    def post_by_id(self, id=None):

        if not id:
            id = max([x.id for x in MatchesModel.query.all()]) + 1
        # check if id exists
        match = MatchesModel.get_by_id(id)
        if match:
            return {'message': "match with id [{}] already exists".format(id)}, HTTPStatus.NOT_FOUND

        data = self.get_data(self)
        data["id"] = id
        with lock.lock:
            new_match = MatchesModel(datetime.strptime(data["date"], "%Y-%m-%d"), data["price"])

            # comprovem si ens pasan visitor/local id
            if data["visitor_id"] and data["local_id"]:
                # Create add_teams() method in MatchesModel
                visitor_team = TeamsModel.get_by_id(data["visitor_id"])
                local_team = TeamsModel.get_by_id(data["local_id"])
                if not visitor_team:
                    return {'message': "visitor with id [{}] does not exist".format(id)}, HTTPStatus.NOT_FOUND
                if not local_team:
                    return {'message': "local with id [{}] does not exist".format(id)}, HTTPStatus.NOT_FOUND
                self.add_teams(self, new_match, visitor_team, local_team)
            # O el team local o visitor existent
            elif data["visitor"] and data["local"]:
                visitor_team = TeamsModel.get_by_name(data["visitor"]["name"])
                local_team = TeamsModel.get_by_name(data["local"]["name"])
                if not visitor_team:
                    return {'message': "Given visitor team does not exist."}, HTTPStatus.NOT_FOUND
                if not local_team:
                    return {'message': "Given local team does not exist."}, HTTPStatus.NOT_FOUND
                self.add_teams(new_match, visitor_team, local_team)
            else:
                return {'message': "No local/visitors teams or ids were given."}, HTTPStatus.NOT_FOUND

            # Fem el mateix per competitions
            if data["competition_id"]:
                competition = CompetitionsModel.get_by_id(data["competition_id"])
                if not competition:
                    return {'message': "competition with id [{}] does not exist".format(id)}, HTTPStatus.NOT_FOUND
                self.add_competition(self, new_match, competition, visitor_team, local_team)

            elif data["competition"]:
                name = data["competition"]["name"]
                competition = CompetitionsModel.get_by_name(name)

                if not competition:
                    return {'message': "Competition with name [{}] does not exist".format(name)}, HTTPStatus.NOT_FOUND
                self.add_competition(self, new_match, competition, visitor_team, local_team)
            else:
                return {'message': "No competition or competition_id was given."}, HTTPStatus.NOT_FOUND

            new_match.id = data["id"]
            new_match.save_to_db()
            return new_match

    @classmethod
    def put_by_id(self, id):
        data = self.get_data(self)
        data["id"] = id
        with lock.lock:
            match = MatchesModel.get_by_id(id)
            if match:
                # Comprovem si ens ha pasat dades noves i les sobreescribim
                if data["date"]:
                    match.date = datetime.strptime(data["date"], "%Y-%m-%d")
                if data["price"]:
                    match.price = data["price"]
                if data["total_available_tickets"]:
                    match.total_available_tickets = data["total_available_tickets"]
                if data["local_id"] and data["local_id"] != match.local_id:
                    team = TeamsModel.get_by_id(data["local_id"])
                    if team:
                        match.local_id = data["local_id"]
                        match.local = team
                    else:
                        return {'message': "team with id [{}] not exists".format(id)}, HTTPStatus.NOT_FOUND
                if data["visitor_id"] and data["visitor_id"] != match.visitor_id:
                    team = TeamsModel.get_by_id(data["visitor_id"])
                    if team:
                        match.visitor_id = data["visitor_id"]
                        match.visitor = team
                    else:
                        return {'message': "team with id [{}] not exists".format(id)}, HTTPStatus.NOT_FOUND
                if data["competition_id"] and data["competition_id"] != match.competition_id:
                    competition = CompetitionsModel.get_by_id(data["competition_id"])
                    if competition:
                        match.competition_id = data["competition_id"]
                        match.competition = competition
                        competition.matches.append(match)
                        competition.teams.append(match.local)
                        competition.teams.append(match.visitor)
                    else:
                        return {'message': "competition with id [{}] not exists".format(id)}, HTTPStatus.NOT_FOUND
                if data["local"]:
                    local_team = TeamsModel.get_by_name(data["local"]["name"])
                    if not local_team:
                        return {'message': "Given local team does not exist."}, HTTPStatus.NOT_FOUND
                    match.local = local_team
                    match.local_id = local_team.id
                if data["visitor"]:
                    visitor_team = TeamsModel.get_by_name(data["visitor"]["name"])
                    if not visitor_team:
                        return {'message': "Given visitor team does not exist."}, HTTPStatus.NOT_FOUND
                    match.visitor = visitor_team
                    match.visitor_id = visitor_team.id
                if data["competition"]:
                    competition = CompetitionsModel.get_by_name(data["competition"]["name"])
                    if not competition:
                        return {'message': "Given competition does not exist."}, HTTPStatus.NOT_FOUND
                    match.competition = competition
                    match.competition_id = competition.id
                    competition.matches.append(match)
                    competition.teams.append(match.local)
                    competition.teams.append(match.visitor)
                match.save_to_db()
                # TODO guardar competitioon?
                # TODO fer que es borrin els equips de la competition igual q els matches
            else:
                # if it does not exist, add it to matches
                new_match = MatchesModel(datetime.strptime(data["date"], "%Y-%m-%d"), data["price"])

                # comprovem si ens pasan visitor/local id
                if data["visitor_id"] and data["local_id"]:
                    # Create add_teams() method in MatchesModel
                    visitor_team = TeamsModel.get_by_id(data["visitor_id"])
                    local_team = TeamsModel.get_by_id(data["local_id"])
                    if not visitor_team:
                        return {'message': "visitor with id [{}] does not exist".format(id)}, HTTPStatus.NOT_FOUND
                    if not local_team:
                        return {'message': "local with id [{}] does not exist".format(id)}, HTTPStatus.NOT_FOUND
                    self.add_teams(self, new_match, visitor_team, local_team)
                # O el team local o visitor existent
                elif data["visitor"] and data["local"]:
                    visitor_team = TeamsModel.get_by_name(data["visitor"]["name"])
                    local_team = TeamsModel.get_by_name(data["local"]["name"])
                    if not visitor_team:
                        return {'message': "Given visitor team does not exist."}, HTTPStatus.NOT_FOUND
                    if not local_team:
                        return {'message': "Given local team does not exist."}, HTTPStatus.NOT_FOUND
                    self.add_teams(new_match, visitor_team, local_team)
                else:
                    return {'message': "No local/visitors teams or ids were given."}, HTTPStatus.NOT_FOUND

                # Fem el mateix per competitions
                if data["competition_id"]:
                    competition = CompetitionsModel.get_by_id(data["competition_id"])
                    if not competition:
                        return {'message': "competition with id [{}] does not exist".format(id)}, HTTPStatus.NOT_FOUND
                    self.add_competition(self, new_match, competition, visitor_team, local_team)

                elif data["competition"]:
                    name = data["competition"]["name"]
                    competition = CompetitionsModel.get_by_name(name)

                    if not competition:
                        return {'message': "Competition with name [{}] does not exist".format(name)}, HTTPStatus.NOT_FOUND
                    self.add_competition(self, new_match, competition, visitor_team, local_team)
                else:
                    return {'message': "No competition or competition_id was given."}, HTTPStatus.NOT_FOUND

                new_match.id = data["id"]
                new_match.save_to_db()
            match = self.query.get(id)
            return match

    def add_teams(self, match, visitor_team, local_team):
        match.local = local_team
        match.visitor = visitor_team

    def add_competition(self, match, new_competition, visitor_team, local_team):
        print(new_competition)
        match.competition = new_competition
        new_competition.matches.append(match)
        new_competition.teams.append(local_team)
        new_competition.teams.append(visitor_team)

    def get_data(self):
        parser = reqparse.RequestParser()  # create parameters parser from request
        # define all input parameters need and its type
        parser.add_argument('local', type=dict, required=False)
        parser.add_argument('visitor', type=dict, required=False)
        parser.add_argument('date', type=str)
        parser.add_argument('price', type=float)
        parser.add_argument('total_available_tickets', type=int)
        parser.add_argument('local_id', type=int, required=False)
        parser.add_argument('visitor_id', type=int, required=False)
        parser.add_argument('competition', type=dict, required=False)
        parser.add_argument('competition_id', type=int, required=False)
        data = parser.parse_args()
        return data

    @classmethod
    def get_by_visitor_local_comp_ids(self, vis_id, loc_id, comp_id):
        match = MatchesModel.query.filter(MatchesModel.visitor_id.any(visitor_id=vis_id)).filter(
            MatchesModel.local_id.any(local_id=loc_id)).filter(
            MatchesModel.competition_id.any(competition_id=comp_id)).first()
        if not match:
            return None
        print(match.json())
        return match

    # Posem els imports aquests aqui abaix per a solucionar el problema del circular import
    from models.competitions import CompetitionsModel
