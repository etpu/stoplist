from flask import Flask, redirect, url_for

from config import configurations as cfgs
from .admins import admin
from .cli import stoplist_cli
from .exceptions import InvalidConfigurationType
from .extensions import migrate, security, babel, user_datastore
from .models import db


def create_app(mode='dev'):
    try:
        cfg = cfgs[mode]
    except KeyError:
        raise InvalidConfigurationType(
            'Unknown config type, try "prod", "dev" or "test".'
        )
    app = Flask(__name__)
    app.config.from_object(cfg)
    db.init_app(app)
    migrate.init_app(app, db)
    security.init_app(app, user_datastore)
    babel.init_app(app)
    admin.init_app(app)
    app.cli.add_command(stoplist_cli)

    @app.route('/')
    def index():
        return redirect(url_for('admin.index'))

    return app