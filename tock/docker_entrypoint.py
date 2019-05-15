#! /usr/bin/env python

"""
    This is a Docker entrypoint that configures the container to run
    as the same uid of the user on the host container, rather than
    the Docker default of root. Aside from following security best
    practices, this makes it so that any files created by the Docker
    container are also owned by the same user on the host system.
"""

import sys
import os
import pwd
import subprocess # nosec

from tock.settings.env import env

HOST_UID = os.stat('/tock').st_uid
HOST_USER = env.get_credential('HOST_USER', 'tock_user')


def does_username_exist(username):
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False


def does_uid_exist(uid):
    try:
        pwd.getpwuid(uid)
        return True
    except KeyError:
        return False

if __name__ == '__main__':
    if HOST_UID != os.geteuid():
        if not does_uid_exist(HOST_UID):
            username = HOST_USER
            while does_username_exist(username):
                username += '0'
            home_dir = '/home/%s' % username
            subprocess.check_call([ # nosec
                'useradd',
                '-d', home_dir,
                '-m', username,
                '-u', str(HOST_UID)
            ])
        os.environ['HOME'] = '/home/%s' % pwd.getpwuid(HOST_UID).pw_name
        os.setuid(HOST_UID)
    os.execvp(sys.argv[1], sys.argv[1:])  # nosec
