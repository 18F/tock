from django.template.defaultfilters import pluralize
from django.core.urlresolvers import reverse
from .models import ReportingPeriod, Timecard, TimecardObject, Project

class HoursAdder(object):
    """Service object in charge of adding hours to a timecard object"""

    def __init__(self, **kwargs):
        self.project_id = kwargs.get('project_id', None)
        self.hours = kwargs.get('hours', None)
        self.reporting_period_id = kwargs.get('reporting_period_id', None)
        self.message = "Unknown error"
        self.user_id = kwargs.get('user_id', None)
        self.operation_was_successful = False

    def generate_successful_message(self, hours, project):
        if hours > 0:
            plural_hours = pluralize(hours, 'hour,hours')
            has = pluralize(hours, 'has,have')
            undo_query = "?hours=-%s&project=%s" % (hours, project.id)
            undo_url = reverse('AddHours') + undo_query
            undo_tag = "<a href=\"%s\">Undo</a>" % (undo_url)
            return "%s %s %s been added to %s. %s" % (hours, plural_hours, has,
                    project.name, undo_tag)

        plural_hours = pluralize(-hours, 'hour,hours')
        has = pluralize(-hours, 'has,have')
        return "%s %s %s been removed from %s." % (-hours, plural_hours, has,
                project.name)

    def perform_operation(self):
        error_msg = "Oops. That command was not correct and no time was added to your timecard. Try again by entering a URL with this format: tock.gov/addHours?project=231&hours=1"
        try:
            project = Project.objects.get(id=self.project_id)
        except Project.DoesNotExist:
            self.message = error_msg
            self.operation_was_successful = False

        tc, created = Timecard.objects.get_or_create(
            reporting_period_id=self.reporting_period_id,
            user_id=self.user_id)

        if created:
            tc.save()

        tco, created = TimecardObject.objects.get_or_create(
            timecard_id=tc.id,
            project_id=project.id)

        if self.hours is None:
            self.message = error_msg
            self.operation_was_successful = False
            return

        if tco.hours_spent is None:
            tco.hours_spent = 0

        updated_hours = tco.hours_spent + self.hours
        updated_hours = max(0, updated_hours)
        tco.hours_spent = updated_hours
        tco.save()

        self.message = self.generate_successful_message(self.hours, project)
        self.operation_was_successful = True

    def successful(self):
        return self.operation_was_successful

    def message(self):
        return self.message
