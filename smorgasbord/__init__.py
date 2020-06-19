from flask import Flask
from flask_assets import Environment

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    assets = Environment()
    assets.init_app(app)

    with app.app_context():
        #import core flask app
        from . import routes
        from . import db
        from .assets import compile_static_assets

        #import dash application
        from .plotlydash.dashboard import create_dashboard
        app = create_dashboard(app)

        #compile static assets
        compile_static_assets(assets)

        return app
