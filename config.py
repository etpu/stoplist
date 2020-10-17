from os import environ
import bleach

DB_PASS = environ.get('DB_PASS')


class BasicConfig():
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = environ.get('SECRET_KEY') or "?%tRx7PpAu3F?fjq0~4V#ZW||JxtAf"
    API_KEY = environ.get('API_KEY') or "eL*wuZmbeWcf9{$pLKCp9ZCk~O$CZr"
    SECURITY_PASSWORD_SALT = environ.get('SECURITY_PASSWORD_SALT') or "Q|~FvB}NK3z6L~stN69#InK@$C}H2f"
    SECURITY_PASSWORD_HASH = environ.get('SECURITY_PASSWORD_HASH') or "~n90V0zdzT0XfXI7@eWex7?s8jAnyT"
    BABEL_DEFAULT_LOCALE = 'ru'
    FLASK_ADMIN_SWATCH = 'cosmo'
    SECURITY_USER_IDENTITY_ATTRIBUTES = [
        {
            'login': {
                'mapper': lambda i: bleach.clean(i, strip=True),
                'case_insensitive': False
            }
        }
    ]


class DevelopmentConfig(BasicConfig):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    # SQLALCHEMY_DATABASE_URI = f'sqlite:///{path.join(path.dirname(__file__), "db.sqlite3")}'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}/{}".format(
        environ.get('DB_USER'), environ.get('DB_PASS'),
        environ.get('DB_HOST'), environ.get('DB_NAME')
    )


class ProductionConfig(BasicConfig):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}/{}".format(
        environ.get('DB_USER'), environ.get('DB_PASS'),
        environ.get('DB_HOST'), environ.get('DB_NAME')
    )


class TestingConfig(BasicConfig):
    pass


configurations = {
    'prod': ProductionConfig,
    'dev': DevelopmentConfig,
    'test': TestingConfig
}
