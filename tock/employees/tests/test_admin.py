import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from employees.admin import UserDataForm
from organizations.models import Organization
from projects.models import ProfitLossAccount


class TestUserDataForm(TestCase):
    fixtures = [
        'employees/fixtures/user_data.json',
        'tock/fixtures/prod_user.json',
        'organizations/fixtures/organizations.json'
    ]

    def setUp(self):
        ProfitLossAccount.objects.create(
            name='PL',
            accounting_string='1234',
            as_start_date=datetime.date.today() + datetime.timedelta(
                days=10
            ),
            as_end_date=datetime.date.today() + datetime.timedelta(days=20),
            account_type='Expense'
        )
        # Organization.objects.create(name="18F")
        self.form_data = {
            'user': User.objects.first().id,
            'start_date': datetime.date.today(),
            'end_date': '',
            'current_employee': '',
            'organization': Organization.objects.first().id,
            'unit': '',
            'profit_loss_account': ProfitLossAccount.objects.first().id,
            'expected_billable_hours': settings.DEFAULT_EXPECTED_BILLABLE_HOURS
        }

    def test_user_data_form(self):
        """Tests custom admin form validation."""

        # Checks that a ProfitLossAccount object with a start date that is
        # after the employee's start date is accepted.
        form = UserDataForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_user_data_form_too_many_expected_billable_hours(self):
        self.form_data.update(
            {
                'expected_billable_hours': settings.HOURS_IN_A_REGULAR_WORK_WEEK + 1
            }
        )
        form = UserDataForm(data=self.form_data)
        self.assertFalse(form.is_valid())

    def test_user_data_form_bad_start_date(self):
        # Checks that changing the start date to a date that is after the
        # end date of the ProfitLossAccount object results in a rejection.
        self.form_data.update(
            {
                'start_date': ProfitLossAccount.objects.first().as_end_date \
                    + datetime.timedelta(days=1)
            }
        )
        form = UserDataForm(data=self.form_data)
        self.assertFalse(form.is_valid())

    def test_user_data_form_wrong_account_type(self):
        # Checks that a ProfitLossAccount object with the wrong account type is
        # rejected.
        pl_update = ProfitLossAccount.objects.first()
        pl_update.account_type = 'Revenue'
        pl_update.save()
        form = UserDataForm(data=self.form_data)
        self.assertFalse(form.is_valid())
