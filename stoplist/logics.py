from .models import db, Stoplist, Log
import requests


def send_to_log_and_asterisk(current_user, type, id: int, data: dict):
    """Выполняет действия при Создании/Редактировании/Удалении записи в базе данных

    :param current_user:
    :param id: id записи в которой произвелись изменения
    :param data: Передаются данные формы
    """
    # code, number = data["code"], data["number"]
    # reason1, reason2, reason3, reason4, = data["reason1"], data["reason2"], data["reason3"], data["reason4"]
    # text = f"{code=}, {number=}, {reason1=}, {reason2=}, {reason3=}, {reason4=}"

    log = Log(stoplist_id=id, user=current_user.id, type=type, data=str(data))
    db.session.add(log)
    db.session.commit()
    send_to_asterisk()


def after_delete():
    pass


def send_to_asterisk():
    pass
