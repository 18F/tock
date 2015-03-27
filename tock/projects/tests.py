from django.test import SimpleTestCase
from projects.models import Agency, Project, AccountingCode

class AgencyTests(SimpleTestCase):

    def test_agency_save(self):
        agency = Agency(name='General Services Administration')
        agency.save()

        retrieved = Agency.objects.get(pk=agency.pk)
        self.assertEqual(
            'General Services Administration', str(retrieved))

class ProjectTest(SimpleTestCase):
    def test_project_save(self):
        agency = Agency(name='General Services Administration')
        agency.save()

        accounting_code = AccountingCode(agency=agency)
        accounting_code.save()

        project = Project(
            accounting_code=accounting_code,
            name="Test Project"
        )
        project.save()

        retrieved = Project.objects.get(pk=project.pk)
        self.assertEqual(retrieved.name, "Test Project")