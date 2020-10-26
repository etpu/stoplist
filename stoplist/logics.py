from os import environ

import requests

from .models import db, Log


def send_to_log_and_asterisk(user, id: int, type, data: str):
    """Выполняет действия при Создании/Редактировании/Удалении записи в базе данных

    :param user: текущий пользователь
    :param id: запись в которой произвелись изменения
    :param data: Передаются данные об изменении в виде строки
    """
    log = Log(stoplist_id=id, user=user, type=type, data=str(data))
    db.session.add(log)
    db.session.commit()


def ami_string(cmd, types="action", data="") -> str:
    """Формирует строку с адресом для подключения к AMI"""
    return f"http://{environ.get('AMI_HOST')}/rawman?{types}={cmd}{'&' + data if data or cmd == 'login' else ''}"


def ami_login():
    """Авторизация с использованием ami_string для генерации адреса"""
    return requests.get(
        ami_string(cmd='login') + f"username={environ.get('AMI_USER')}&secret={environ.get('AMI_PASS')}")


def ami_cmd(cmd, data=None):
    """Выполняет нужную комманду через AMI. Запускает ami_login для получения Куки и используя его для авторизации."""
    return requests.get(ami_string(cmd, data=data), cookies=ami_login().cookies)
