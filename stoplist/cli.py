import click
from flask.cli import AppGroup
from flask_security import hash_password

from .extensions import user_datastore
from .models import db

stoplist_cli = AppGroup('stoplist')


@stoplist_cli.command('createsuperuser')
@click.argument('login')
@click.password_option()
def create_superuser(login: str, password: str):
    admin_role = user_datastore.find_or_create_role('admin')
    user = user_datastore.create_user(
        login=login, password=hash_password(password), active=True, roles=[admin_role]
    )
    db.session.add(user)
    db.session.commit()
    click.echo("Superuser {} successfully created.".format(login))


@stoplist_cli.command('generateroles')
def generate_roles():
    roles = [
        user_datastore.find_or_create_role(name=name, description=description)
        for name, description in (('admin', 'Администратор'), ('staff', 'Сотрудник'))
    ]
    for role in roles:
        db.session.add(role)
    db.session.commit()
    click.echo('Roles successfully generated.')
