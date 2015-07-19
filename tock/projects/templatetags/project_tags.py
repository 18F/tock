from django import template

register = template.Library()


def get(value, key):
    return value.get(key)


def default(value, default):
    return value or default


register.filter('get', get)
register.filter('default', default)
