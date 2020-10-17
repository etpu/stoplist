Данное приложение показывает возможности интеграции Flask-Admin и Flask-Security-Too
с использованием не адреса электронной почты в качестве основного идентификационного
параметра пользователя.

Для развертывания приложения необходимо выполнить несколько простых действий.
В первую очередь собрать зависимости с помощью `pipenv`:

.. code:: shell

   pipenv install


Затем, произвести генерацию базы данных:

.. code::

   pipenv run flask db init
   pipenv run flask db migrate
   pipenv run flask db upgrade


После необходимо создать роли пользователей и суперпользователя:

.. code::

   pipenv run flask stoplist generateroles
   pipenv run flask stoplist createsuperuser admin


После этого можно запустить приложения и авторизоваться под пользователем admin,
который был создан ранее. Для запуска приложения необходимо выполнить следующую
команду:

.. code::

   pipenv run flask run
