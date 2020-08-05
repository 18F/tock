from datetime import date

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.views.generic import ListView, TemplateView
from hours.models import ReportingPeriod
from organizations.models import Unit
from tock.utils import PermissionMixin

import plotly.graph_objects as go
from plotly.offline import plot

from .org import org_billing_context
from .unit import unit_billing_context

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
            unit['utilization'] = unit_billing_context(unit['id'])

        return units

    def get_context_data(self, **kwargs):
        context = super(GroupUtilizationView, self).get_context_data(**kwargs)
        context.update({'org_totals': org_billing_context()}
        )
        return context


def _plot_utilization(dates, billable, nonbillable):
    """Make a stacked area plot of billable and nonbillable hours.

    dates, billable, and nonbillable should be sequences with the same length
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=billable,
        line_shape="hv",
        mode="lines",
        stackgroup="one",
        name="Billable",
    ))
    fig.add_trace(go.Scatter(
        x=dates,
        y=nonbillable,
        line_shape="hv",
        mode="lines",
        stackgroup="one",
        name="Non-Billable",
    ))

    fig.update_layout(
        # autosize=False,
        # width=900,
        # height=500,
        xaxis=dict(autorange=True),
        yaxis=dict(autorange=True),
        xaxis_title="Reporting Period Start Date",
        yaxis_title="Hours",
        title="Total Hours recorded vs. Time",
    )

    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div


def _utilization_data(start_date, end_date):
    Timecard = apps.get_model("hours", "Timecard")
    data = (Timecard.objects.filter(reporting_period__start_date__gte=start_date,
                                    reporting_period__end_date__lte=end_date,
                                    submitted=True,
        )
        .values("reporting_period__start_date")
        .annotate(billable=Sum("billable_hours"),
                  nonbillable=Sum("non_billable_hours"))
        .order_by("reporting_period__start_date")
    )
    dates = [item["reporting_period__start_date"] for item in data]
    billable_hours = [item["billable"] for item in data]
    nonbillable_hours = [item["nonbillable"] for item in data]
    return dates, billable_hours, nonbillable_hours


def utilization_plot(start_date, end_date):
    """Fetch data and make a plot for total utilization."""
    return _plot_utilization(*_utilization_data(start_date, end_date))


class UtilizationAnalyticsView(PermissionMixin, TemplateView):
    template_name = 'utilization/utilization_analytics.html'

    def get_context_data(self, **kwargs):
        context = super(UtilizationAnalyticsView, self).get_context_data(**kwargs)

        # use a date before Tock as the default start_date
        start_date = self.request.GET.get("start", "2000-01-01")
        end_date = self.request.GET.get("end", date.today().isoformat())

        # add the plot div to the context
        context.update({"plot": utilization_plot(start_date, end_date)})

        return context
