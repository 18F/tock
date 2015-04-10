from django.contrib.auth.middleware import RemoteUserMiddleware


class EmailHeaderMiddleware(RemoteUserMiddleware):
  header = 'HTTP_X_FORWARDED_EMAIL'
