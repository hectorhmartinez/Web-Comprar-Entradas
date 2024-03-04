from http import HTTPStatus

from flask_restful import reqparse

from db import db
from lock import lock
from models.teams import TeamsModel

teams_in_competitions = db.Table("teams_in_competitions",
                                 db.Column("id", db.Integer, primary_key=True),
                                 db.Column("team_id", db.Integer, db.ForeignKey("teams.id")),
                                 db.Column("competition_id", db.Integer, db.ForeignKey("competitions.id")))


class CompetitionsModel(db.Model):
    # TODO comprovar a l'hora d'afegir el category o sport si esta o no a la llista
    __tablename__ = 'competitions'  # This is table name
    __table_args__ = (db.UniqueConstraint('name', 'category', 'sport'),)

    categories_list = ("Senior", "Junior", "fifa", "puto", "senior")
    sports_list = ("Volleyball", "Football", "Basketball", "Futsal", "furbo", "lol")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    #category = db.Column(db.Enum(*categories_list), name='categories_types', nullable=False)
    #sport = db.Column(db.Enum(*sports_list), name='sports_types', nullable=False)
    category = db.Column(db.Enum(*categories_list), nullable=False)
    sport = db.Column(db.Enum(*sports_list), nullable=False)
    teams = db.relationship("TeamsModel", secondary=teams_in_competitions, backref=db.backref("competition"))

    matches = db.relationship("MatchesModel", back_populates="competition")

    def __init__(self, name, category, sport):
        self.name = name
        self.category = category
        self.sport = sport

    def json(self):
        return {'id': self.id, 'name': self.name, 'category': self.category, 'sport': self.sport,
                'teams': [{"Team " + str(i + 1): team.json()} for i, team in enumerate(self.teams) if team],
                'matches': [{"Match " + str(i + 1): match.json()} for i, match in enumerate(self.matches) if match]}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(self, id):
        competition = self.query.get(id)
        if not competition:
            return None
        return competition

    @classmethod
    def get_by_name(self, given_name):
        competition = CompetitionsModel.query.filter_by(name=given_name).first()
        if not competition:
            return None
        return competition

    @classmethod
    def delete_by_id(self, id):
        with lock.lock:
            competition = self.query.get(id)
            # delete team if it exists
            if competition is not None:
                try:
                    competition.delete_from_db()
                except:
                    # TODO fer rollback?
                    return {"message": "An error occurred deleting the competition."}, HTTPStatus.INTERNAL_SERVER_ERROR
                return True
            return None

    @classmethod
    def post_by_id(self, id=None):
        if not id:
            id = max([competition.id for competition in CompetitionsModel.query.all()]) + 1
        # check if id exists
        competition = CompetitionsModel.get_by_id(id)
        if competition:
            return {'message': "match with id [{}] already exists".format(id)}, HTTPStatus.NOT_FOUND

        data = self.get_data(self, post=True)
        data["id"] = id
        with lock.lock:
            new_competition = CompetitionsModel(data["name"], data["category"], data["sport"])

            if data["teams"]:
                print("data teams: [{}]".format(data["teams"]))
                for team in data["teams"]:
                    if team["id"]:
                        team_by_id = TeamsModel.get_by_id(team["id"])
                        if not team_by_id:
                            return {"message": "Team in teams with id [{}] does not exist".format(
                                name)}, HTTPStatus.NOT_FOUND
                        new_competition.teams.append(team_by_id)
                    # Asumim que si et dona un nom correcte, la country també ho serà
                    elif team["name"]:
                        name = team["name"]
                        team_by_name = TeamsModel.get_by_name(name)
                        if not team_by_name:
                            return {"message": "Team in teams with name [{}] does not exist".format(
                                name)}, HTTPStatus.NOT_FOUND
                        new_competition.teams.append(team_by_name)
                    else:
                        return {"message": "Team in teams needs at least name or id"}, HTTPStatus.NOT_FOUND
            if data["matches"]:
                for match in data["matches"]:
                    if match["id"]:
                        match_by_id = MatchesModel.get_by_id(match.id)
                        if not match_by_id:
                            return {'message': "Given match with id [{}] does not exist.".format(id)}, HTTPStatus.NOT_FOUND
                        new_competition.matches.append(match_by_id)
                    elif match["visitor_id"] and match["local_id"] and match["competition_id"]:
                        visitor_id = match["visitor_id"]
                        local_id = match["local_id"]
                        comp_id = match["competition_id"]
                        match_by_multiple_ids = MatchesModel.get_by_visitor_local_comp_ids(visitor_id, local_id, comp_id)
                        if not match_by_multiple_ids:
                            return {'message': "Given match with local_id [{}], visitor_id [{}] and competition_id [{}] "
                                               "does not exist.".format(local_id, visitor_id,
                                                                        comp_id)}, HTTPStatus.NOT_FOUND
                        self.add_match_and_teams(self, new_competition, match_by_multiple_ids, local_id, visitor_id)
            new_competition.id = data["id"]
            new_competition.save_to_db()
            return new_competition

    @classmethod
    def put_by_id(self, id):
        data = self.get_data(self)
        data["id"] = id
        with lock.lock:
            competition = CompetitionsModel.get_by_id(id)
            if competition:
                # Comprovem si ens ha pasat dades noves i les sobreescribim
                if data["name"]:
                    competition.name = data["name"]

                if data["category"]:
                    if data["category"] not in CompetitionsModel.categories_list:
                        return {"message": "Category [{}] not found in sports list, try one of the following: [{}]".format(
                            data["category"], CompetitionsModel.categories_list)}, HTTPStatus.NOT_FOUND
                    competition.category = data["category"]

                if data["sport"]:
                    if data["sport"] not in CompetitionsModel.sports_list:
                        return {"message": "Sport [{}] not found in sports list, try one of the following: [{}]".format(
                            data["sport"], CompetitionsModel.sports_list)}, HTTPStatus.NOT_FOUND
                    competition.sport = data["sport"]

                if data["teams"]:
                    for team in data["teams"]:
                        if team["id"]:
                            team_by_id = TeamsModel.get_by_id(team["id"])
                            if not team_by_id:
                                return {"message": "Team in teams with id [{}] does not exist".format(
                                    name)}, HTTPStatus.NOT_FOUND
                            team_by_id.name = data["name"]
                            team_by_id.country = data["contry"]
                        # Asumim que si et dona un nom correcte, la country també ho serà
                        elif team["name"]:
                            name = team["name"]
                            team_by_name = TeamsModel.get_by_name(name)
                            if not team_by_name:
                                return {"message": "Team in teams with name [{}] does not exist".format(
                                    name)}, HTTPStatus.NOT_FOUND
                            team_by_name.name = data["name"]
                            team_by_name.country = data["country"]
                        else:
                            return {"message": "Team in teams needs at least name or id"}, HTTPStatus.NOT_FOUND
                if data["matches"]:
                    for match in data["matches"]:
                        if match["id"]:
                            match_by_id = MatchesModel.get_by_id(match.id)
                            if not match_by_id:
                                return {'message': "Given match with id [{}] does not exist.".format(
                                    id)}, HTTPStatus.NOT_FOUND
                            competition.matches.append(match_by_id)
                            match_by_id.date = data["date"]
                            match_by_id.price = data["price"]
                            match_by_id.save_to_db()
                        elif match["visitor_id"] and match["local_id"] and match["competition_id"]:
                            visitor_id = match["visitor_id"]
                            local_id = match["local_id"]
                            comp_id = match["competition_id"]
                            match_by_multiple_ids = MatchesModel.get_by_visitor_local_comp_ids(visitor_id, local_id,
                                                                                               comp_id)
                            if not match_by_multiple_ids:
                                return {
                                           'message': "Given match with local_id [{}], visitor_id [{}] and competition_id [{}] "
                                                      "does not exist.".format(local_id, visitor_id,
                                                                               comp_id)}, HTTPStatus.NOT_FOUND
                            competition.matches.append(match_by_multiple_ids)
                            match_by_multiple_ids.date = data["date"]
                            match_by_multiple_ids.price = data["price"]
                            match_by_multiple_ids.save_to_db()
                        else:
                            return {"message": "Match in Matches needs at least match_id or local_id + visitor_id +"
                                               " competition_id"}, HTTPStatus.NOT_FOUND
                competition.save_to_db()
            else:
                new_competition = CompetitionsModel(data["name"], data["category"], data["sport"])
                if data["teams"]:
                    for team in data["teams"]:
                        if team["id"]:
                            team_by_id = TeamsModel.get_by_id(team["id"])
                            if not team_by_id:
                                return {"message": "Team in teams with id [{}] does not exist".format(
                                    name)}, HTTPStatus.NOT_FOUND
                            new_competition.teams.append(team_by_id)
                        # Asumim que si et dona un nom correcte, la country també ho serà
                        elif team["name"]:
                            name = team["name"]
                            team_by_name = TeamsModel.get_by_name(name)
                            if not team_by_name:
                                return {"message": "Team in teams with name [{}] does not exist".format(
                                    name)}, HTTPStatus.NOT_FOUND
                            new_competition.teams.append(team_by_name)
                        else:
                            return {"message": "Team in teams needs at least name or id"}, HTTPStatus.NOT_FOUND
                if data["matches"]:
                    for match in data["matches"]:
                        if match["id"]:
                            match_by_id = MatchesModel.get_by_id(match.id)
                            if not match_by_id:
                                return {'message': "Given match with id [{}] does not exist.".format(
                                    id)}, HTTPStatus.NOT_FOUND
                            new_competition.matches.append(match_by_id)
                        elif match["visitor_id"] and match["local_id"] and match["competition_id"]:
                            visitor_id = match["visitor_id"]
                            local_id = match["local_id"]
                            comp_id = match["competition_id"]
                            match_by_multiple_ids = MatchesModel.get_by_visitor_local_comp_ids(visitor_id, local_id,
                                                                                               comp_id)
                            if not match_by_multiple_ids:
                                return {
                                           'message': "Given match with local_id [{}], visitor_id [{}] and competition_id [{}] "
                                                      "does not exist.".format(local_id, visitor_id,
                                                                               comp_id)}, HTTPStatus.NOT_FOUND
                            self.add_match_and_teams(self, new_competition, match_by_multiple_ids, local_id, visitor_id)
                new_competition.save_to_db()
            competition = self.query.get(id)
            return competition

    def get_data(self, post=False):
        parser = reqparse.RequestParser()  # create parameters parser from request
        # define all input parameters need and its type
        if post:
            parser.add_argument('name', type=str, required=True, help="This parameter cannot be empty")
        else:
            parser.add_argument('name', type=str, help="This parameter cannot be empty")
        parser.add_argument('category', type=str)
        parser.add_argument('sport', type=str)
        parser.add_argument('teams', type=dict, action='append', required=False)
        parser.add_argument('matches', type=dict, action='append', required=False)
        data = parser.parse_args()
        return data

    def add_match_and_teams(self, competition, match, local_id, visitor_id):
        competition.matches.append(match)
        local_team = TeamsModel.get_by_id(local_id)
        visitor_team = TeamsModel.get_by_id(visitor_id)
        if local_team not in competition.teams:
            competition.teams.append(local_team)
        if visitor_team not in competition.teams:
            competition.teams.append(visitor_team)

    def add_competition(self, match, competition):
        print(competition)
        match.competition = competition
        competition.matches.append(match)


# Posem els imports aquests aqui abaix per a solucionar el problema del circular import
from models.matches import MatchesModel
