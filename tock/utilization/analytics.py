from django.db.models import Count, F, Q, Sum
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.offline import plot


def compute_utilization(data_frame):
    """Compute utilization percentage from a DataFrame with billable and non_billable columns."""
    return ( data_frame["billable"] + data_frame["allocation_hours"] ).astype(float) / (
        data_frame["non_billable"] + data_frame["billable"] + data_frame["allocation_hours"]
    ).astype(float)


def _get_org_query(org_id):
    # short circuit this one first
    if org_id is None:
        return Q(user__user_data__organization__id__isnull=True)
    if org_id > 0:
        return Q(user__user_data__organization__id=org_id)
    # org_id = 0 gives all results
    return Q()


def utilization_plot(data_frame):
    """Make a stacked area plot of billable and nonbillable hours.

    data_frame has start_date, billable, non_billable, and allocation_hours columns
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
            name="Hourly Billable",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=data_frame["start_date"],
            y=data_frame["allocation_hours"],
            line_shape="hv",
            stackgroup="only",
            name="Weekly Allocation",
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
        width=960,
        height=720,
        xaxis=dict(autorange=True),
        yaxis=dict(autorange=True),
        title_text="Total Hours recorded vs. Time",
        hovermode="x",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    return fig.to_html(include_plotlyjs=False)


def utilization_data(timecard_queryset):
    """Get a data frame of utilization data.

    Has start_date, billable, nonbillable, and allocation_hours columns.
    """
    data = (
        timecard_queryset
        .values(start_date=F("reporting_period__start_date"))
        .annotate(
            billable=Sum("billable_hours"),
            non_billable=Sum("non_billable_hours"),
            excluded=Sum("excluded_hours"),
            allocation_hours=Sum("total_allocation_hours")
        )
        .filter(billable__isnull=False)
        .order_by("start_date")
    )
    frame = pd.DataFrame.from_records(data)
    if len(frame) == 0:
        # data frame is empty, lets ensure it has the right columns
        frame = pd.DataFrame(columns=["start_date", "billable", "non_billable", "allocation_hours", "excluded"])
    return frame


def headcount_plot(data_frame):
    """Make a line plot of headcount.

    The data frame should have start_date and headcount columns
    """
    if len(data_frame) == 0:
        fig = go.Figure()
    else:
        fig = px.area(
            data_frame, x="start_date", y="headcount", color="organization", line_shape="hv"
        )

    fig.update_layout(
        xaxis_title="Reporting Period Start Date",
        yaxis_title="",
        title_text="Number of Tockers vs. Time",
        hovermode="x",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    fig.update_traces(hovertemplate="%{y}")

    return fig.to_html(include_plotlyjs=False)


def headcount_data(timecard_queryset):
    """Get a data frame of Tock head count.

    Result has start_date, headcount and organization columns.
    """
    data = (
        timecard_queryset
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
    if len(frame) == 0:
        # data frame is empty, lets ensure it has the right columns
        frame = pd.DataFrame(columns=["start_date", "org", "headcount"])
    frame["organization"] = frame["org"].astype(str)
    frame.drop("org", axis=1, inplace=True)
    return frame


def project_dataframe(timecardobject_queryset):
    data = timecardobject_queryset.values(
                'hours_spent',
                start_date=F("timecard__reporting_period__start_date"),
                user=F(
                    "timecard__user__username"
                ),
            ).order_by("start_date")
    return pd.DataFrame.from_records(data)

def project_chart_and_table(timecardobject_queryset):
    """Make a line plot of headcount AND a table of the data

    The data frame should have start_date and headcount columns
    """
    data_frame = project_dataframe(timecardobject_queryset)

    # plot
    if len(data_frame) == 0:
        fig = go.Figure()
    else:
        fig = px.area(
            data_frame, x="start_date", y="hours_spent", color="user", line_shape="hv"
        )

    fig.update_layout(
        xaxis_title="Reporting Period Start Date",
        yaxis_title="",
        title_text="Hours tocked by user and week",
        hovermode="x"
    )
    fig.update_traces(hovertemplate="%{y}")

    plot_div = plot(fig, output_type="div", include_plotlyjs=False)

    # datatable
    datatable = data_frame.pivot(
                    index="start_date", values="hours_spent", columns="user"
                )
    # there can be some None in "hours_spent" rather than 0 which
    # is more typical, so let's replace the NaNs with zeroes before we
    # format the numbers
    datatable = datatable.fillna(0)
    datatable = datatable.map("{:.2f}".format)
    return plot_div, datatable
