from django.test import SimpleTestCase
from projects.models import Agency, Project, AccountingCode


class AgencyTests(SimpleTestCase):

    def test_agency_save(self):
        """ Test that agency model works correctly """
        agency = Agency(name='General Services Administration')
        agency.save()
        retrieved = Agency.objects.get(pk=agency.pk)
        self.assertEqual('General Services Administration', str(retrieved))


class ProjectAndAccountingCodeTest(SimpleTestCase):

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
