from datetime import datetime
import random

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import resources.data as data
from models.competitions import CompetitionsModel
from models.matches import MatchesModel
from models.teams import TeamsModel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)

teams = []
matches = []
competitions = []

for competition in data.competitions:
    competitionModel = CompetitionsModel(name=competition["name"], category=competition["category"],
                                         sport=competition["sport"])
    competitions.append(competitionModel)

for team in data.teams:
    teamModel = TeamsModel(name=team["name"], country=team["country"])
    teams.append(teamModel)

for match in data.matches:
    matchModel = MatchesModel(date=datetime.strptime(match["date"], "%Y-%m-%d"), price=match["price"])
    matches.append(matchModel)

# Relationships
for match in matches:
    # Choose randomly two different teams from the teams list
    random_teams = random.sample(teams, 2)
    local = random_teams[0]
    visitor = random_teams[1]

    # Assign local and visitor for the current match
    match.local = local
    match.visitor = visitor

    # Choose a random competition
    random_competition = random.choice(competitions)
    # Assign the competition to the match
    match.competition = random_competition

    # Append the match to the competition
    random_competition.matches.append(match)
    # Append local and visitor to the competition list of teams
    random_competition.teams.append(local)
    random_competition.teams.append(visitor)

db.session.add_all(teams)
db.session.add_all(matches)
db.session.add_all(competitions)
db.session.commit()
