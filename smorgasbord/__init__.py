from flask import Flask
#from flask_assets import Environment
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    #assets = Environment()
    #assets.init_app(app)

    db.init_app(app)

    with app.app_context():
        #import core flask app
        from . import routes
        from . import smorgasbord
        from . import message
        #from .assets import compile_static_assets

        # db.create_all()
        #import dash application
        from .plotlydash.dashboard import create_dashboard
        app = create_dashboard(app)

        #compile static assets
        #compile_static_assets(assets)

        return app
