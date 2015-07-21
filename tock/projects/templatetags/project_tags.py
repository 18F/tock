from django import template

register = template.Library()


def get(value, key):
    return value.get(key)


register.filter('get', get)
