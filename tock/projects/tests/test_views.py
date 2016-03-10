from django.db.models import Sum
from django.core.urlresolvers import reverse
from django_webtest import WebTest

from hours.models import TimecardObject
from projects.models import Project


class ProjectViewTests(WebTest):
    fixtures = [
        'projects/fixtures/projects.json',
        'hours/fixtures/timecards.json',
        'tock/fixtures/prod_user.json'
    ]
    csrf_checks = False

    def test_total_hours_billed(self):
        """
        For a given project, ensure that the view displays the correct total.

        (Note that this project is the only test project for which timecards have been saved.)

        :return:
        """
        project = Project.objects.get(id__exact=1)
        timecard_objects = TimecardObject.objects.filter(
            project=project.id
        )

        total = timecard_objects.aggregate(Sum('hours_spent'))['hours_spent__sum']

        response = self.app.get(
            reverse('ProjectView', kwargs={'pk': project.id}),
            headers={'X-FORWARDED-EMAIL': 'aaron.snow@gsa.gov'}
        )

        self.assertEqual(float(response.html.select('#totalHours')[0].string), total)
