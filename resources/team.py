from http import HTTPStatus

from flask_restful import Resource

from models.matches import MatchesModel
from models.teams import TeamsModel


class Team(Resource):
    def get(self, id):
        team = TeamsModel.get_by_id(id)
        return {'team': team.json()}, HTTPStatus.OK if team else HTTPStatus.NOT_FOUND

    def post(self, id=None):
        team = TeamsModel.post_by_id(id)
        if type(team) is tuple:
            return team
        return {'team': team.json()}, HTTPStatus.OK if team else HTTPStatus.NOT_FOUND

    def delete(self, id):
        team = TeamsModel.delete_by_id(id)
        if team:
            if type(team) is tuple:
                return team
            return {'message': "team with id [{}] deleted successfully".format(id)}, HTTPStatus.OK
        # else return error 404 not found
        return {'message': "team with id [{}] does not exist, therefore not deleted".format(id)}, HTTPStatus.NOT_FOUND

    def put(self, id):
        team = TeamsModel.put_by_id(id)
        if type(team) is tuple:
            return team
        return {'team': team.json()}, HTTPStatus.OK if team else HTTPStatus.NOT_FOUND


class TeamsList(Resource):
    def get(self):
        teams_list = list()
        if TeamsModel.query.all() == 0:
            return {'message': "There are no teams"}, HTTPStatus.NOT_FOUND
        for team in TeamsModel.query.all():
            teams_list.append(team.json())

        return {'teams': teams_list}, HTTPStatus.OK if teams_list else HTTPStatus.NOT_FOUND


class TeamMatchesList(Resource):
    def get(self, id):
        matches = list()
        team = TeamsModel.get_by_id(id)
        for i, match in enumerate(MatchesModel.query.all()):
            if match:
                if match.local is team or match.visitor is team:
                    matches.append(match.json())
        return {'Matches': matches}, HTTPStatus.OK if matches else HTTPStatus.NOT_FOUND
