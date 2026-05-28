from flask import Blueprint

bp = Blueprint('team', __name__, url_prefix='/equipe')

from app.team import routes
