from decouple import config as config_decouple
from flask import Flask
from flask import render_template
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api

from config import config
from db import db, secret_key
from resources.account import Accounts, AccountsList
from resources.competition import Competition, CompetitionsList, CompetitionTeamsList, CompetitionMatch
from resources.login import Login
from resources.match import Match, MatchesList, MatchTeamsList
from resources.order import Orders, OrdersList
from resources.team import Team, TeamsList, TeamMatchesList

# modificat sessió 6
app = Flask(__name__)
environment = config['development']

if config_decouple('PRODUCTION', cast=bool, default=False):
    environment = config['production']

app.config.from_object(environment)


api = Api(app)
CORS(app, resources={r'/*': {'origins': '*'}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key

migrate = Migrate(app, db)
db.init_app(app)

api.add_resource(Team, '/team/<int:id>', '/team')
api.add_resource(TeamsList, '/teams')
api.add_resource(TeamMatchesList, '/team/<int:id>/matches')

api.add_resource(Competition, '/competition/<int:id>', '/competition')
api.add_resource(CompetitionsList, '/competitions')
api.add_resource(CompetitionTeamsList, '/competition/<int:id>/teams')
api.add_resource(CompetitionMatch, '/competition/<int:competition_id>/match',
                 '/competition/<int:competition_id>/match/<int:match_id>')

api.add_resource(Match, '/match/<int:id>', '/match')
api.add_resource(MatchesList, '/matches')
api.add_resource(MatchTeamsList, '/match/<int:id>/teams')

api.add_resource(Orders, '/order/<string:username>')
api.add_resource(OrdersList, '/orders/<string:username>', '/orders')

api.add_resource(Accounts, '/account/<string:username>', '/account')
api.add_resource(AccountsList, '/accounts')

api.add_resource(Login, '/login')


@app.route('/')
def render_vue():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(port=5000, debug=True)
