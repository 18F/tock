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

if __name__ == '__main__':
    if os.environ.get('RUNNING_IN_DOCKER') == 'yup':
        setup_docker_sigterm_handler()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tock.settings.dev')

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
