#!/usr/bin/env python
import os
import sys


def wait_for_db(max_attempts=15, seconds_between_attempts=1):
    '''
    Some manage.py commands interact with the database, and we want
    them to be directly callable from `docker-compose run`. However,
    because docker may start the database container at the same time
    as it runs `manage.py`, we potentially face a race condition, and
    the manage.py command may attempt to connect to a database that
    isn't yet ready for connections.

    To alleviate this, we'll just wait for the database before calling
    the manage.py command.
    '''

    import time
    from django.db import DEFAULT_DB_ALIAS, connections
    from django.db.utils import OperationalError

    connection = connections[DEFAULT_DB_ALIAS]
    attempts = 0

    while True:
        try:
            connection.ensure_connection()
            break
        except OperationalError as e:
            if attempts >= max_attempts:
                raise e
            attempts += 1
            time.sleep(seconds_between_attempts)
            print("Attempting to connect to database.")

    print("Connection to database established.")

if __name__ == '__main__':
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'tock.settings.production'
    )

    if os.environ.get('RUNNING_IN_DOCKER') == 'yup':
        wait_for_db()

    from django.core.management import execute_from_command_line

    testing = 'test' in sys.argv

    if testing:
        import coverage
        cov = coverage.coverage(
            source=['tock', 'employees', 'projects', 'hours', 'api', 'utilization'],
            omit=['*/tests*', '*/migrations/*', '*/settings/*'],
        )
        cov.erase()
        cov.start()

    execute_from_command_line(sys.argv)

    if testing:
        cov.stop()
        cov.save()
        cov.report()
