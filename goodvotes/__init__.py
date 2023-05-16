from pathlib import Path
import os

from flask import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.orm import *
from sqlalchemy import ForeignKey
from werkzeug.exceptions import HTTPException

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from . import service
from .cli import *
from .auth import *
from .models.auth import *
from .models.election import *