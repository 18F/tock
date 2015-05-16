from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.middleware import RemoteUserMiddleware


class TockUserBackend(RemoteUserBackend):
    def clean_username(self, email_address):
        """
        Performs any cleaning on the "username" prior to using it to get or
        create the user object.  Returns the cleaned username.

        By default, returns the username unchanged.
        """
        username = email_address.split('@')[0]
        return username

class EmailHeaderMiddleware(RemoteUserMiddleware):
  header = 'HTTP_X_FORWARDED_EMAIL'
