#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tock.settings.dev')
    from django.core.management import execute_from_command_line
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
