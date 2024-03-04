from http import HTTPStatus

from flask_restful import Resource

from models.matches import MatchesModel


class Match(Resource):

    def get(self, id):
        match = MatchesModel.get_by_id(id)
        return {'match': match.json()}, HTTPStatus.OK if match else HTTPStatus.NOT_FOUND

    def post(self, id=None):
        match = MatchesModel.post_by_id(id)
        if type(match) is tuple:
            return match
        return {'match': match.json()}, HTTPStatus.OK if match else HTTPStatus.NOT_FOUND

    def delete(self, id):
        match = MatchesModel.delete_by_id(id)
        # delete team if it exists
        if match:
            if type(match) is tuple:
                return match
            return {'message': "match with id [{}] deleted successfully".format(id)}, HTTPStatus.OK
        # else return error 404 not found
        return {'message': "match with id [{}] does not exist, therefore not deleted".format(id)}, HTTPStatus.NOT_FOUND

    def put(self, id):
        match = MatchesModel.put_by_id(id)
        if type(match) is tuple:
            return match
        return {'match': match.json()}, HTTPStatus.OK if match else HTTPStatus.NOT_FOUND


class MatchesList(Resource):
    def get(self):
        matches_list = list()
        if MatchesModel.query.all() == 0:
            return {'message': "There are no matches"}, HTTPStatus.NOT_FOUND
        for match in MatchesModel.query.all():
            matches_list.append(match.json())

        return {'matches': matches_list}, HTTPStatus.OK if matches_list else HTTPStatus.NOT_FOUND


class MatchTeamsList(Resource):
    def get(self, id):
        match = MatchesModel.get_by_id(id)
        teams = dict()
        teams["Local Team"] = match.local.json()
        teams["Visitor Team"] = match.visitor.json()
        return teams, HTTPStatus.OK
