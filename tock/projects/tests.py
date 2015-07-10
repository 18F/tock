from django_webtest import WebTest
from projects.models import Agency, Project, AccountingCode
from django.core.urlresolvers import reverse


class ProjectsTest(WebTest):

    def setUp(self):
        agency = Agency(name='General Services Administration')
        agency.save()
        accounting_code = AccountingCode(
            code='abc', agency=agency, office='18F', billable=True)
        accounting_code.save()
        self.project = Project(accounting_code=accounting_code,
                               name="Test Project")
        self.project.save()

    def test_model(self):
        """ Check that the project model stores data correctly and links to
        AccountingCode model properly"""
        retrieved = Project.objects.get(pk=self.project.pk)
        self.assertEqual(
            retrieved.accounting_code.agency.name,
            'General Services Administration')
        self.assertEqual(retrieved.accounting_code.office, '18F')
        self.assertTrue(retrieved.accounting_code.billable)

    def test_is_billable(self):
        """ Check that the is_billable method works """
        retrieved = Project.objects.get(name='Test Project')
        self.assertTrue(retrieved.is_billable())
        retrieved.accounting_code.billable = False
        retrieved.accounting_code.save()
        self.assertFalse(retrieved.is_billable())

    def test_projects_list_view(self):
        """ Check that the project list view is open and the saved project
        are listed """
        response = self.app.get(reverse('ProjectListView'))
        self.assertEqual(
            len(response.html.find('a', href='/projects/1')), 1)
        self.assertEqual(response.status_code, 200)

    def test_projects_details_view(self):
        """ Check that the project detail view is open and the saved project
        exists """
        response = self.app.get(reverse('ProjectView', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
