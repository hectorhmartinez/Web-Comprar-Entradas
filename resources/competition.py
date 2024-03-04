from datetime import datetime
from http import HTTPStatus

from flask_restful import Resource, reqparse

from models.competitions import CompetitionsModel
from models.matches import MatchesModel
from models.teams import TeamsModel


class Competition(Resource):

    def get(self, id):
        competition = CompetitionsModel.get_by_id(id)
        return {'competition': competition.json()}, HTTPStatus.OK if competition else HTTPStatus.NOT_FOUND

    def post(self, id=None):
        competition = CompetitionsModel.post_by_id(id)
        if type(competition) is tuple:
            return competition
        return {'competition': competition.json()}, HTTPStatus.OK if competition else HTTPStatus.NOT_FOUND

    def delete(self, id):
        competition = CompetitionsModel.delete_by_id(id)
        # delete team if it exists
        if competition:
            if type(competition) is tuple:
                return competition
            return {'message': "match with id [{}] deleted successfully".format(id)}, HTTPStatus.OK
        # else return error 404 not found
        return {'message': "match with id [{}] does not exist, therefore not deleted".format(id)}, HTTPStatus.NOT_FOUND

    def put(self, id):
        competition = CompetitionsModel.put_by_id(id)
        if type(competition) is tuple:
            return competition
        return {'competition': competition.json()}, HTTPStatus.OK if competition else HTTPStatus.NOT_FOUND


class CompetitionsList(Resource):
    def get(self):
        competitions_list = list()
        idx = 0
        if CompetitionsModel.query.all() == 0:
            return {'message': "There are no competitions"}, HTTPStatus.NOT_FOUND

        for competition in CompetitionsModel.query.all():
            idx += 1
            competitions_list.append(competition.json())
        return {'competitions': competitions_list}, HTTPStatus.OK if competitions_list else HTTPStatus.NOT_FOUND


class CompetitionTeamsList(Resource):
    def get(self, id):
        competition = CompetitionsModel.get_by_id(id)
        teams = list()
        for team in competition.teams:
            teams.append(team.json())
        return {'teams': teams}, HTTPStatus.OK if teams else HTTPStatus.NOT_FOUND


class CompetitionMatch(Resource):
    def get(self, competition_id, match_id):
        competition = CompetitionsModel.get_by_id(competition_id)
        if not competition:
            return {'message': "There is no competition with id [{}]".format(competition_id)}, HTTPStatus.NOT_FOUND

        match = MatchesModel.get_by_id(match_id)
        if not match:
            return {'message': "There is no match with id [{}]".format(match_id)}, HTTPStatus.NOT_FOUND

        if match not in competition.matches:
            return {'message': "There is no match with id [{}] in competition with id [{}]".format(match_id,
                                                                                                   competition_id)}, HTTPStatus.NOT_FOUND
        return {"match": match.json()}, HTTPStatus.OK

    def delete_by_id(self, competition_id, match_id):
        competition = CompetitionsModel.get_by_id(competition_id)
        if not competition:
            return {'message': "There is no competition with id [{}]".format(competition_id)}, HTTPStatus.NOT_FOUND

        match = MatchesModel.get_by_id(match_id)
        if not match:
            return {'message': "There is no match with id [{}]".format(match_id)}, HTTPStatus.NOT_FOUND

        if match not in competition.matches:
            return {'message': "There is no match with id [{}] in competition with id [{}]".format(match_id,
                                                                                                   competition_id)}, HTTPStatus.NOT_FOUND
        competition.matches.remove(match)
        return {"competition": competition.json()}, HTTPStatus.OK

    def post_by_id(self, competition_id, match_id=None):
        competition = CompetitionsModel.get_by_id(competition_id)
        if not competition:
            return {'message': "There is no competition with id [{}]".format(competition_id)}, HTTPStatus.NOT_FOUND

        # Mirem si ens pasa match_id o no
        if match_id:
            match = MatchesModel.get_by_id(match_id)
            if not match:
                return {'message': "There is no match with id [{}]".format(match_id)}, HTTPStatus.NOT_FOUND

            if match not in competition.matches:
                competition.matches.append(match)
                match.competition = competition
                competition.teams.append(match.local)
                competition.teams.append(match.visitor)

        else:
            data = self.get_data()

            data["id"] = id
            try:
                new_match = MatchesModel(datetime.strptime(data["date"], "%Y-%m-%d"), data["price"])
            except:
                return {"message": "Match already exists"}, HTTPStatus.NOT_FOUND
            # comprovem si ens pasan visitor/local id
            if data["visitor_id"] and data["local_id"]:
                # Create add_teams() method in MatchesModel
                visitor_team = TeamsModel.get_by_id(data["visitor_id"])
                local_team = TeamsModel.get_by_id(data["local_id"])
                if not visitor_team:
                    return {'message': "visitor with id [{}] does not exist".format(id)}, HTTPStatus.NOT_FOUND
                if not local_team:
                    return {'message': "local with id [{}] does not exist".format(id)}, HTTPStatus.NOT_FOUND
                self.add_teams(new_match, visitor_team, local_team)
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

            new_match.id = data["id"]
            new_match.save_to_db()
        return {"competition": competition.json()}, HTTPStatus.OK

    def add_teams(self, match, visitor_team, local_team):
        match.local = local_team
        match.visitor = visitor_team

    def add_competition(self, match, new_competition, visitor_team, local_team):
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
        parser.add_argument('local_id', type=int, required=False)
        parser.add_argument('visitor_id', type=int, required=False)
        parser.add_argument('competition', type=dict, required=False)
        parser.add_argument('competition_id', type=int, required=False)
        data = parser.parse_args()
        return data
