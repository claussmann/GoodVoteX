from flask import Blueprint

goodvotes_cli = Blueprint('goodvotes_cli', __name__, cli_group='goodvotes')

from . import cli
