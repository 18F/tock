from django.apps import apps
from django.db.models import Count, F, Sum

import pandas as pd

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.offline import plot


def compute_utilization(data_frame):
    """Compute utilization percentage from a DataFrame with billable and non_billable columns."""
    return data_frame["billable"].astype(float) / (
        data_frame["non_billable"] + data_frame["billable"]
    ).astype(float)


def utilization_plot(data_frame):
    """Make a stacked area plot of billable and nonbillable hours.

    data_frame has start_date, billable, and non_billable columns
    """
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.3, 0.7],
    )

    fig.add_trace(
        go.Scatter(
            x=data_frame["start_date"],
            y=data_frame["billable"],
            line_shape="hv",
            stackgroup="only",
            name="Billable",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=data_frame["start_date"],
            y=data_frame["non_billable"],
            line_shape="hv",
            stackgroup="only",
            name="Non-Billable",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=data_frame["start_date"],
            y=data_frame["excluded"],
            line_shape="hv",
            stackgroup="only",
            name="OOO",
        ),
        row=2,
        col=1,
    )

    utilization_fraction = compute_utilization(data_frame)
    fig.add_trace(
        go.Scatter(
            x=data_frame["start_date"],
            y=utilization_fraction * 100,
            name="Utilization Rate",
            hovertext=(utilization_fraction * 100).map("{:,.1f}%".format),
        ),
        row=1,
        col=1,
    )

    fig.update_xaxes(title="Reporting Period Start Date", row=2, col=1)
    fig.update_yaxes(title="Hours", row=2, col=1)

    fig.update_layout(
        autosize=False,
        width=1000,
        height=700,
        xaxis=dict(autorange=True),
        yaxis=dict(autorange=True),
        title_text="Total Hours recorded vs. Time",
        hovermode="x",
    )

    plot_div = plot(fig, output_type="div", include_plotlyjs=False)
    return plot_div


def utilization_data(start_date, end_date):
    """Get a data frame of utilization data.

    Has start_date, billable, and nonbillable columns.
    """
    Timecard = apps.get_model("hours", "Timecard")
    data = (
        Timecard.objects.filter(
            reporting_period__start_date__gte=start_date,
            reporting_period__end_date__lte=end_date,
        )
        .values(start_date=F("reporting_period__start_date"))
        .annotate(
            billable=Sum("billable_hours"),
            non_billable=Sum("non_billable_hours"),
            excluded=Sum("excluded_hours"),
        )
        .filter(billable__isnull=False)
        .order_by("start_date")
    )
    frame = pd.DataFrame.from_records(data)
    return frame


def headcount_plot(data_frame):
    """Make a line plot of headcount.

    The data frame should have start_date and headcount columns
    """
    fig = px.area(
        data_frame, x="start_date", y="headcount", color="organization", line_shape="hv"
    )

    fig.update_layout(
        xaxis_title="Reporting Period Start Date",
        yaxis_title="",
        title_text="Number of Tockers by organization vs. Time",
        hovermode="x",
    )
    fig.update_traces(hovertemplate="%{y}")

    plot_div = plot(fig, output_type="div", include_plotlyjs=False)
    return plot_div


def headcount_data(start_date, end_date):
    """Get a data frame of Tock head count.

    Result has start_date, headcount and organization columns.
    """
    Timecard = apps.get_model("hours", "Timecard")
    data = (
        Timecard.objects.filter(
            reporting_period__start_date__gte=start_date,
            reporting_period__end_date__lte=end_date,
        )
        .values(
            start_date=F("reporting_period__start_date"),
            org=F(  # use "org" temporarily to avoid name collision
                "user__user_data__organization__name"
            ),
        )
        .annotate(headcount=Count("user__id", distinct=True))
        .order_by("start_date")
    )
    frame = pd.DataFrame.from_records(data)
    frame["organization"] = frame["org"].astype(str)
    frame.drop("org", axis=1, inplace=True)
    return frame
