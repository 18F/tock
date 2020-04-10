from django.contrib.auth import get_user_model
from django.views.generic import ListView
from hours.models import ReportingPeriod
from organizations.models import Unit
from tock.utils import PermissionMixin

from .org import org_billing_context
from .unit import unit_billing_context
from .utils import utilization_users_queryset

User = get_user_model()

class GroupUtilizationView(PermissionMixin, ListView):
    template_name = 'utilization/group_utilization.html'
    requested_periods = 4

    def dispatch(self, *args, **kwargs):
        """
        Resolve recent reporting periods.

        Although recent_rps is set to the last four reporting periods,
        we could accept a form response that allows the user or app to
        dynamically customize number of periods to include in the queryset.
        """
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()
        self.available_periods = ReportingPeriod.objects.count()
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        """
        Gets submitted timecards for billable staff
        limited to the reporting periods in question.
        """
        # Start stubbing a dict for our units, using a quick list comprehension
        units = [{
            'id': unit.id,
            'name': unit.name,
            'slug': unit.slug
         } for unit in Unit.objects.filter(active=True)]

        # Iterate through each unit, calculating utilization for each
        # employee therein as well as overall

        for unit in units:
            unit_users = User.objects.filter(user_data__unit=unit['id'])
            active_unit_users = utilization_users_queryset(unit_users)
            if active_unit_users.exists():
                unit['utilization'] = unit_billing_context(unit['id'])
            else:
                unit['utilization'] = []
        return units

    def get_context_data(self, **kwargs):
        context = super(GroupUtilizationView, self).get_context_data(**kwargs)
        context.update({'org_totals': org_billing_context()}
        )
        return context
