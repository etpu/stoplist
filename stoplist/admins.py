import uuid

from flask import abort, redirect, request, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib import sqla
from flask_admin.menu import MenuLink
from flask_security import current_user

from .models import db, User, Role, Post, Stoplist, Log


class SecureAdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        if current_user.is_authenticated:
            return abort(403)
        return redirect(url_for('security.login', next=request.url))


class SecureStaffMixin(SecureAdminMixin):
    def is_accessible(self):
        return current_user.has_role('staff') or current_user.has_role('admin')


class AdminModelView(SecureAdminMixin, sqla.ModelView):
    pass


class StaffModelView(SecureStaffMixin, sqla.ModelView):
    pass


class SecureIndex(SecureStaffMixin, AdminIndexView):
    pass


class RoleView(AdminModelView):
    column_labels = {
        'name': 'Имя',
        'description': 'Описание'
    }
    form_excluded_columns = ('users',)


class UserView(AdminModelView):
    column_exclude_list = ('password',)
    column_searchable_list = ('login',)
    column_editable_list = ('active',)
    form_excluded_columns = ('fs_uniquifier',)
    column_labels = {
        'login': 'Логин',
        'active': 'Активирован',
        'password': 'Пароль',
        'roles': 'Роли',
    }

    def on_model_change(self, form, model, is_created):
        if not model.fs_uniquifier:
            model.fs_uniquifier = uuid.uuid4().hex
        return super().on_model_change(form, model, is_created)


class PostView(StaffModelView):
    column_exclude_list = ('text',)
    column_searchable_list = ('name',)
    column_labels = {
        'name': 'Имя',
        'text': 'Текст'
    }


class StoplistView(StaffModelView):
    column_exclude_list = ['reason5']
    can_create = True
    can_edit = True
    can_delete = True
    form_create_rules = ('code', 'number', 'reason1', 'reason2', 'reason3', 'reason4',)
    form_edit_rules = ('code', 'number', 'reason1', 'reason2', 'reason3', 'reason4',)
    can_view_details = True
    column_editable_list = ['reason1', 'reason2', 'reason3', 'reason4', 'number', 'code', ]
    create_modal = True
    edit_modal = True
    details_modal = True
    column_searchable_list = ['number', 'code']
    column_filters = ('number', 'code', 'reason1', 'reason2', 'reason3', 'reason4', 'number',)
    # column_labels = {
    #     'number': 'Numéro de téléphone',
    #     'reason1': 'Rendez-vous en Audiotel',
    #     'reason2': 'Rendez-vous en Privé',
    #     'reason3': 'Rendez-vous en Direct AOU',
    #     'reason4': 'Aucun appel',
    #     'modify': 'Date de la dernière modification',
    #     'user': 'Employé',
    # }

    def on_model_change(self, form, model, is_created):
        model.user = current_user.__str__()
        return super().on_model_change(form, model, is_created)


class LogView(AdminModelView):
    create_modal = True
    edit_modal = True
    details_modal = True


admin = Admin(
    name='stoplist', template_mode='bootstrap4',
    index_view=SecureIndex(name='Админка')
)
admin.add_link(MenuLink(name='На главную', url='/'))
admin.add_link(MenuLink(name='Выход', url='/logout'))

admin.add_view(UserView(User, db.session, name='Пользователи'))
admin.add_view(RoleView(Role, db.session, name='Роли'))
admin.add_view(PostView(Post, db.session, name='Посты'))
admin.add_view(StoplistView(Stoplist, db.session, name='Стоплист'))
admin.add_view(LogView(Log, db.session, name='Лог'))
