from flask_api import FlaskAPI
from flask_cors import CORS
from config import env, get_env
from app.utils import db, timedelta


def create_app(config_name):
	app = FlaskAPI(__name__, instance_relative_config=False)
	app.config.from_object(env.app_env[config_name])
	app.config.from_pyfile('../config/env.py')
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

	# CORS
	CORS(app)
	
	from . import models
	db.init_app(app)
	
	return app
