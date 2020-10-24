from flask import current_app
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from flask_babelex import Babel

from .models import db, User, Role

migrate = Migrate()
security = Security()
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
babel = Babel(default_locale='fr')


@babel.localeselector
def get_locale():
    return current_app.config['BABEL_DEFAULT_LOCALE']
