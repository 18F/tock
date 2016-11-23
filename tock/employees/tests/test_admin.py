import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from employees.admin import UserDataForm
from projects.models import ProfitLossAccount

class TestUserDataForm(TestCase):
    fixtures = [
        'employees/fixtures/user_data.json',
        'tock/fixtures/prod_user.json'
    ]

    def test_user_data_form(self):
        """Tests custom admin form validation."""

        # Checks that a ProfitLossAccount object with a start date that is
        # after the employee's start date is accepted.
        ProfitLossAccount.objects.create(
            name='PL',
            accounting_string='1234',
            as_start_date=datetime.date.today() + datetime.timedelta(
                days=10
            ),
            as_end_date=datetime.date.today() + datetime.timedelta(days=20),
            account_type='Expense'
        )
        form_data = {
            'user': User.objects.first().id,
            'start_date': datetime.date.today(),
            'end_date': '',
            'current_employee': '',
            'is_18f_employee': '',
            'is_billable': '',
            'unit': '',
            'profit_loss_account': ProfitLossAccount.objects.first().id
        }
        form = UserDataForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Checks that changing the start date to a date that is after the
        # end date of the ProfitLossAccount object results in a rejection.
        form_data.update(
            {
                'start_date': ProfitLossAccount.objects.first().as_end_date \
                    + datetime.timedelta(days=1)
            }
        )
        form = UserDataForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Checks that a ProfitLossAccount object with the wrong account type is
        # rejected.
        pl_update = ProfitLossAccount.objects.first()
        pl_update.account_type = 'Revenue'
        pl_update.save()
        form = UserDataForm(data=form_data)
        self.assertFalse(form.is_valid())
