from flask import Blueprint
from .models import User

auth = Blueprint('auth', __name__, template_folder='templates')
auth_cli = Blueprint('auth_cli', __name__, cli_group='auth')


@auth.record
def record_params(setup_state):
    app = setup_state.app
    auth.config = dict([(key, value) for (key, value) in app.config.items()])

from . import cli
from . import views
