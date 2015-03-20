from django.test import SimpleTestCase
from projects.models import Agency, Project

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

        project = Project(
            agency=agency,
            name="Test Project"
        )
        project.save()

        retrieved = Project.objects.get(pk=project.pk)
        self.assertEqual(retrieved.name, "Test Project")

    def test_project_is_billable(self):
        agency = Agency(name='General Services Administration')
        agency.save()

        billable_project = Project(
            agency=agency,
            name="Test Project",
            iaa="IAA 2015-01-02"
        )
        billable_project.save()

        non_billable_project = Project(
            agency=agency,
            name="Nonbillable Project"
        )
        non_billable_project.save()

        self.assertTrue(billable_project.is_billable())
        self.assertFalse(non_billable_project.is_billable())