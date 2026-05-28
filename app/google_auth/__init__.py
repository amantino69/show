from flask import Blueprint, redirect, url_for, session, flash, request
from flask_login import login_required, current_user
from app.google_calendar import setup_google_auth
from app.models import User
from app import db
import json

bp = Blueprint('google_auth', __name__)

from . import routes
