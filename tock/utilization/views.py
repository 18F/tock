from datetime import date

import pandas as pd
from api.views import filter_timecards, get_timecardobjects
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, TemplateView
from hours.models import ReportingPeriod, Timecard, TimecardObject
from organizations.models import Organization, Unit
from projects.models import Project

from .analytics import (compute_utilization, headcount_data, headcount_plot,
                        utilization_data, utilization_plot, project_plot)
from .org import org_billing_context
from .unit import unit_billing_context

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



class FilteredAnalyticsView(LoginRequiredMixin):

    def get_filter_params(self):
        # we need a mutable copy of the request parameters so we can add
        # defaults that might not be set
        params = self.request.GET.copy()

        # use one year ago as the default start date
        d = date.today()

        # use setdefault here because if these parameters aren't sent, then we
        # want to add them with these default values so that they will get
        # used later in filter_timecards
        params.setdefault("after", d.replace(year=d.year - 1).isoformat())
        params.setdefault("before", d.isoformat())

        return params

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        params = self.get_filter_params()

        context.update({"start_date": params['after'], "end_date": params['before']})

        # get organization ID from the URL and put it in the context
        org_parameter = params.get("org", 0)
        if org_parameter == "None":
            org_id = None
        else:
            org_id = int(org_parameter)
        context.update({"current_org": org_id})

        # Make a name too for the template
        if org_id is None:
            context.update({"current_org_name": "NULL Organization"})
        elif org_id == 0:
            context.update({"current_org_name": "All Organizations"})
        else:
            name = Organization.objects.get(id=org_id).name
            context.update({"current_org_name": name + " Organization"})

        # give a tip about the oldest possible date
        min_date_result = ReportingPeriod.objects.order_by("start_date").values("start_date").first()
        min_date = min_date_result.pop("start_date").isoformat()
        context.update({"min_date": min_date})

        # organization choices
        org_choices = [
            (item["org_id"], item["name"])
            for item in Timecard.objects.values(
                org_id=F("user__user_data__organization__id"),
                name=F("user__user_data__organization__name")
            ).distinct("org_id")
        ]
        # add a 0 for everything
        org_choices = [(0, 'All')] + org_choices
        context.update({"org_choices": org_choices})
        return context


class UtilizationAnalyticsView(FilteredAnalyticsView, TemplateView):
    template_name = "utilization/utilization_analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        params = self.get_filter_params()

        # Use our common timecard query handling of parameters
        timecard_queryset = filter_timecards(Timecard.objects, params=params)

        # add the utilization plot to the context
        utilization_data_frame = utilization_data(timecard_queryset)
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
        headcount_data_frame = headcount_data(timecard_queryset)
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


class ProjectAnalyticsView(FilteredAnalyticsView, TemplateView):
    template_name = "utilization/project_analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # we need a mutable copy of the request parameters so we can add
        # defaults that might not be set
        params = self.get_filter_params()
        project = get_object_or_404(Project, id=self.kwargs['project_id'])

        # Use our common timecard query handling of parameters
        project_timecardobjects = get_timecardobjects(TimecardObject.objects.filter(project_id=project.id), params)

        data = (
            project_timecardobjects
            .values(
                'hours_spent',
                start_date=F("timecard__reporting_period__start_date"),
                user=F(
                    "timecard__user__username"
                ),
            )
            .order_by("start_date")
        )
        project_dataframe = pd.DataFrame.from_records(data)

        context.update(
            {
                "project": project,
                "project_data": project_dataframe.pivot(
                    index="start_date", values="hours_spent", columns="user"
                )
                .applymap("{:.0f}".format)
                .replace("nan", ""),
                "project_plot": project_plot(project_dataframe),
            }
        )

        return context


