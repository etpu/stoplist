import uuid

from flask import abort, redirect, request, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin._backwards import ObsoleteAttr
from flask_admin.contrib import sqla
from flask_admin.menu import MenuLink
from flask_security import current_user

from .logics import send_to_log_and_asterisk, ami_cmd
from .models import db, User, Role, Stoplist, Log


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
        'name': 'Nom',
        'description': 'Description'
    }
    form_excluded_columns = ('users',)


class UserView(AdminModelView):
    column_exclude_list = ('password',)
    column_searchable_list = ('login',)
    column_editable_list = ('active',)
    form_excluded_columns = ('fs_uniquifier',)
    column_labels = {
        'login': 'Connexion',
        'active': 'Actif',
        'password': 'Mot de passe',
        'roles': 'Rôle',
    }

    def on_model_change(self, form, model, is_created):
        if not model.fs_uniquifier:
            model.fs_uniquifier = uuid.uuid4().hex
        return super().on_model_change(form, model, is_created)


class StoplistView(StaffModelView):
    column_exclude_list = ['created_on']
    can_create = True
    can_edit = False
    can_delete = True
    form_create_rules = ('code', 'number', 'reason1', 'reason2', 'reason3', 'reason4',)
    form_edit_rules = ('code', 'reason1', 'reason2', 'reason3', 'reason4',)
    can_view_details = True
    column_editable_list = ['reason1', 'reason2', 'reason3', 'reason4', 'code', ]
    create_modal = True
    edit_modal = True
    details_modal = True
    column_searchable_list = ['number', 'code']
    column_filters = ('id', 'number', 'code', 'reason1', 'reason2', 'reason3', 'reason4', 'number',)
    column_labels = {
        'id': 'id',
        'number': 'Numéro',
        'reason1': 'Audiotel',
        'reason2': 'Privé',
        'reason3': 'Direct AOU',
        'reason4': 'Aucun appel',
        'modify': 'Date de la dernière modification',
    }
    column_display_pk = ObsoleteAttr('column_display_pk',
                                     'list_display_pk',
                                     True)

    def on_model_change(self, form, model, is_created):
        model.user = current_user.__str__()
        if not model.reason1 and not model.reason2 and not model.reason3 and not model.reason4:
            raise Exception(ValueError)
        return super().on_model_change(form, model, is_created)

    def after_model_change(self, form, model, is_created):
        if is_created:
            send_to_log_and_asterisk(current_user.__str__(), model.id, "CREATE", self._model_data(model))
            ami_cmd("DBPut", f"family=ART&key={model.number}&val={self._create_playback(model)}")
        else:
            if form.reason1:
                data = f'Audiotel={"On" if model.reason1 else "Off"}'
            elif form.reason2:
                data = f'Prive={"On" if model.reason2 else "Off"}'
            elif form.reason3:
                data = f'Direct AUO={"On" if model.reason3 else "Off"}'
            elif form.reason4:
                data = f'All={"On" if model.reason4 else "Off"}'
            elif form.code:
                data = f'Code={model.code}'
            elif form.number:
                data = f'Number={model.number}'
            else:
                data = "None"
            send_to_log_and_asterisk(current_user.__str__(), model.id, "UPDATE", data)
            ami_cmd("DBPut", f"family=ART&key={model.number}&val={self._create_playback(model)}")
        return super().after_model_change(form, model, is_created)

    def after_model_delete(self, model):
        send_to_log_and_asterisk(current_user.__str__(), model.id, "DELETE", self._model_data(model))
        ami_cmd("DBDel", f"family=ART&key={model.number}")
        return super().after_model_delete(self)

    @staticmethod
    def _model_data(model):
        return "id={}, code={}, num={}, Audiotel={}, Prive={}, Direct AUO={}, All={}".format(
            model.id, model.code, model.number,
            'On' if model.reason1 else 'Off',
            'On' if model.reason2 else 'Off',
            'On' if model.reason3 else 'Off',
            'On' if model.reason4 else 'Off',
        )

    @staticmethod
    def _create_playback(model):
        pb_list = []
        if model.reason1:
            pb_list.append("stop%2Faudiotel")
        if model.reason2:
            pb_list.append("stop%2Fprive")
        if model.reason3:
            pb_list.append("stop%2Fauo")
        if model.reason4:
            pb_list = ["stop%2Fall"]
        return "%26".join(pb_list)


class LogView(AdminModelView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    column_searchable_list = ['stoplist_id', 'created_on', 'user', 'type', 'data']
    column_filters = ('stoplist_id', 'created_on', 'user', 'type', 'data')


admin = Admin(
    name='stoplist', template_mode='bootstrap4',
    index_view=SecureIndex(name='Aider')
)
admin.add_link(MenuLink(name='Logout', url='/logout'))

admin.add_view(UserView(User, db.session, name='Users'))
admin.add_view(RoleView(Role, db.session, name='Rôle'))
admin.add_view(StoplistView(Stoplist, db.session, name='Stoplist'))
admin.add_view(LogView(Log, db.session, name='Journal'))
