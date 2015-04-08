from django import template

from hours.models import Timecard
register = template.Library()

@register.filter(name='has_submitted_timesheet')
def has_submitted_timesheet(user, reporting_period):
	if not Timecard.objects.filter(reporting_period=reporting_period, user=user).exists():
		return False
	else:
		return True