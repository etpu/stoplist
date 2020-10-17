from flask_security import RoleMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)


class User(db.Model, UserMixin):  # type: ignore
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password = db.Column(db.String(256), unique=False, nullable=False)
    active = db.Column(db.Boolean, unique=False, nullable=False)
    fs_uniquifier = db.Column(db.String(256), unique=True, nullable=False)
    roles = db.relationship(
        'Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic')
    )

    def __repr__(self):
        return '<User {}>'.format(self.login)

    def __str__(self):
        return self.login


class Stoplist(db.Model):
    __tablename__ = 'stoplists'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, nullable=False)
    number = db.Column(db.BIGINT, nullable=False, unique=True)
    reason1 = db.Column(db.Boolean, nullable=True)
    reason2 = db.Column(db.Boolean, nullable=True)
    reason3 = db.Column(db.Boolean, nullable=True)
    reason4 = db.Column(db.Boolean, nullable=True)
    created_on = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), server_onupdate=db.func.now())
    user = db.Column(db.String(30), nullable=True)

    def __repr__(self):
        return f'<StopList {self.number}>'

    def __str__(self):
        return f'{self.number}'


class Log(db.Model):
    __tablename__ = 'stoplists_log'

    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    stoplist_id = db.Column(db.ForeignKey('stoplists.id'), nullable=False, index=True)
    user = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(30), nullable=False)
    data = db.Column(db.String(255), nullable=False)

    stoplist = db.relationship('Stoplist')

    def __repr__(self):
        return f'<Log {self.id} from {self.user}>'

    def __str__(self):
        return f'{self.id}'


class Role(db.Model, RoleMixin):  # type: ignore
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.Unicode(512), unique=False, nullable=True)

    def __repr__(self):
        return '<Role {}>'.format(self.name)

    def __str__(self):
        return self.description if self.description else self.name


class Post(db.Model):  # type: ignore
    __tabename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(1024), unique=True, nullable=False)
    text = db.Column(db.Text, unique=False, nullable=True)

    def __repr__(self):
        return '<Post {}>'.format(self.name)

    def __str__(self):
        return self.name
