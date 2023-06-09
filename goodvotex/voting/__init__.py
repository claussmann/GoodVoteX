import logging

from flask import Blueprint

logger = logging.getLogger(__name__)

voting = Blueprint('voting', __name__, template_folder='templates')
