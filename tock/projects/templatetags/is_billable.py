from django import template

from projects.models import Project
register = template.Library()


@register.simple_tag(name='is_billable')
def is_billable(pk):
  project = Project.objects.get(pk=pk)
  if project.accounting_code.billable is True:
    return "billable"
  else:
    return "non-billable"
