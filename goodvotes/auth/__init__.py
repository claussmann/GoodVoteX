from flask import Blueprint
from .models import User

auth = Blueprint('auth', __name__, template_folder='templates')
auth_cli = Blueprint('auth_cli', __name__, cli_group='auth')

from . import cli
from . import views
