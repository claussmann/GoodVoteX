from flask import Blueprint
from .models import User

auth = Blueprint('auth', __name__, template_folder='templates')

from . import views