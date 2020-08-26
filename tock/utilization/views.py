from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView
from hours.models import ReportingPeriod
from organizations.models import Unit

from .org import org_billing_context
from .unit import unit_billing_context
from .analytics import (
    compute_utilization,
    headcount_data,
    headcount_plot,
    utilization_data,
    utilization_plot,
)

User = get_user_model()

class GroupUtilizationView(LoginRequiredMixin, ListView):
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


class UtilizationAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = "utilization/utilization_analytics.html"

    def get_context_data(self, **kwargs):
        context = super(UtilizationAnalyticsView, self).get_context_data(**kwargs)

        # use one year ago as the default start date
        d = date.today()
        start_date = self.request.GET.get("start", d.replace(year=d.year - 1).isoformat())
        end_date = self.request.GET.get("end", d.isoformat())
        context.update({"start_date": start_date, "end_date": end_date})

        # give a tip about the oldest possible date
        min_date_result = ReportingPeriod.objects.order_by("start_date").values("start_date").first()
        min_date = min_date_result.pop("start_date").isoformat()
        context.update({"min_date": min_date})

        # add the utilization plot to the context
        utilization_data_frame = utilization_data(start_date, end_date)
        utilization_data_frame["utilization_rate"] = (
            100 * compute_utilization(utilization_data_frame)
        ).map("{:,.1f}%".format)
        context.update(
            {
                "utilization_data": utilization_data_frame.set_index("start_date"),
                "utilization_plot": utilization_plot(utilization_data_frame),
            }
        )

        # add the headcount plot to the context
        headcount_data_frame = headcount_data(start_date, end_date)
        context.update(
            {
                "headcount_data": headcount_data_frame.pivot(
                    index="start_date", values="headcount", columns="organization"
                )
                .applymap("{:.0f}".format)
                .replace("nan", ""),
                "headcount_plot": headcount_plot(headcount_data_frame),
            }
        )

        return context
