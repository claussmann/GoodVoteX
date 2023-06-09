from flask import Blueprint

goodvotex_cli = Blueprint('goodvotex_cli', __name__, cli_group='goodvotex')

from . import cli
