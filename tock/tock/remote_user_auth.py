from django.contrib.auth.middleware import RemoteUserMiddleware

class EmailHeaderMiddleware(RemoteUserMiddleware):
    header = 'X-Forwarded-Email'