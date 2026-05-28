from flask import Blueprint

bp = Blueprint('marketing', __name__)

from app.marketing import routes
