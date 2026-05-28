from flask import Blueprint

bp = Blueprint('p7', __name__, url_prefix='/artists')

from app.p7 import routes
