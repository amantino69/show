from flask import Blueprint

bp = Blueprint('devtools', __name__, url_prefix='/ferramentas')

from app.devtools import routes  # noqa: E402, F401
