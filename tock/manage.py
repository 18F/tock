#!/usr/bin/env python
import os
import sys

def setup_docker_sigterm_handler():
    '''
    'manage.py runserver' is not set up to deal with a SIGTERM signal,
    and instead expects a Ctrl-C to come to its child process. So we'll
    add a SIGTERM handler here that finds all our children and gracefully
    shuts them down, which provides a quick graceful exit from Docker.
    '''

    if not (len(sys.argv) > 1 and sys.argv[1] == 'runserver'):
        return

    import signal
    import subprocess

    def get_children():
        output = subprocess.check_output(
            "ps --ppid=%d -o pid | awk 'NR>1' | xargs echo" % os.getpid(),
            shell=True
        )
        return map(int, output.split())

    def handler(signum, frame):
        for child_pid in get_children():
            try:
                os.kill(child_pid, signal.SIGTERM)
                os.waitpid(child_pid, 0)
            except OSError:
                pass
        sys.exit(0)

    print("Setting up Docker SIGTERM handler for quick, graceful exit.")
    signal.signal(signal.SIGTERM, handler)

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
        setup_docker_sigterm_handler()
        wait_for_db()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as e:
        # Assume the user wants to run us in docker.
        try:
            os.execvp('docker-compose', [
                'docker-compose', 'run', 'app', 'python'
            ] + sys.argv)
        except OSError:
            # Apparently docker-compose isn't installed, so just raise
            # the original ImportError.
            raise e

    testing = 'test' in sys.argv

    if testing:
        import coverage
        cov = coverage.coverage(
            source=['tock', 'employees', 'projects', 'hours', 'api'],
            omit=['*/tests*', '*/migrations/*', '*/settings/*'],
        )
        cov.erase()
        cov.start()

    execute_from_command_line(sys.argv)

    if testing:
        cov.stop()
        cov.save()
        cov.report()
