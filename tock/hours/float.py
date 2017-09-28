import datetime as dt
import logging
import sys

from .models import ReportingPeriod

from employees.models import UserData
from tock.utils import get_float_data, flatten

logger = logging.getLogger(__name__)

# Variables.
BASE_HOURS_PER_WEEK = 32.5
BASE_HOURS_PER_DAY = 6.5
BASE_DAYS_PER_WEEK = 5

def float_tasks_for_view(user, rp):
    userdata = UserData.objects.get(user=user)
    float_people_id = get_float_people_id(userdata)
    error_state = False
    tasks = []

    if not float_people_id:
        return None

    try:
        float_tasks = get_float_tasks(
            start_date=rp.start_date,
            float_people_id=float_people_id,
            weeks=1
        )
    except:
        logger.error(sys.exc_info()[0])
        error_state = True

    try:
        float_holidays = get_float_holidays(
            start_date=rp.start_date,
            weeks=2
        )
    except:
        logger.error(sys.exc_info()[0])
        error_state = True

    try:
        float_timeoffs = get_float_timeoffs(
            end_date=rp.end_date,
            float_people_id=float_people_id,
            weeks=26
        )
    except:
        logger.error(sys.exc_info()[0])
        error_state = True

    try:
        work_days = get_work_days(
            holidays=float_holidays,
            start_date=rp.start_date,
            end_date=rp.end_date
        )
    except:
        logger.error(sys.exc_info()[0])
        error_state = True

    try:
        work_hours = get_work_hours(
            start_date=rp.start_date,
            end_date=rp.end_date,
            timeoffs=float_timeoffs,
            work_days=work_days
        )
    except:
        logger.error(sys.exc_info()[0])
        error_state = True

    if not error_state:
        try:
            tasks = get_tasks(
                start_date=rp.start_date,
                end_date=rp.end_date,
                tasks=float_tasks,
                work_days=work_days,
                work_hours=work_hours
            )
        except:
            logger.error(sys.exc_info()[0])

    return tasks


def get_tasks(start_date, end_date, tasks, work_days, work_hours):
    for i in tasks:
        t_start_date, t_end_date = \
            [ dt.datetime.strptime(i[k], '%Y-%m-%d').date() for \
            k in ['start_date', 'end_date'] ]
        task_days = len(find_common_weekdays(
            (start_date, end_date),
            (t_start_date, t_end_date)
        ))
        i['hours_wk'] = float(i['hours_pd']) * task_days

    # Prevent a divide by zero error in the case of work hours being 0.
    if work_hours > 0:
        all_task_hours = sum([ float(i['hours_wk']) for i in tasks ])
        tasks_to_hours = all_task_hours / work_hours

        if tasks_to_hours > 1.0:
            for i in tasks:
                week_hours = i['hours_wk'] * (work_hours / all_task_hours)
                i.update({'hours_wk': round(week_hours, 2)})

    return tasks

def get_work_hours(start_date, end_date, timeoffs, work_days):
    hours_off = 0
    for i in timeoffs:
        to_start_date, to_end_date = \
            [ dt.datetime.strptime(i[k], '%Y-%m-%d').date() for \
            k in ['start_date', 'end_date'] ]
        days_off = len(find_common_weekdays(
            (start_date, end_date),
            (to_start_date, to_end_date)
        ))
        hours_off += float(i['hours']) * days_off

    work_hours = (work_days * BASE_HOURS_PER_DAY) - hours_off
    return work_hours

def get_work_days(holidays, start_date, end_date):
    # Get holiday info from Float for last two weeks
    # and check for holidays in period.
    return BASE_DAYS_PER_WEEK - len([ i for i in holidays \
        if start_date <= \
        dt.datetime.strptime(i['date'], '%Y-%m-%d').date() <= \
        end_date ])

def get_float_timeoffs(end_date, float_people_id, weeks=26):
    # Get Float timeoff for the user data.
    # Defaults to 26 weeks to guard against a really, really long
    # absence.
    return [ i for i in get_float_data(
        endpoint='timeoffs',
        params={
            'weeks': weeks,
            'start_day': end_date - dt.timedelta(weeks=weeks)
        }
    ).json()['timeoffs'] if int(i['people_id']) == float_people_id ]

def get_float_holidays(start_date, weeks=2):
    return get_float_data(
        endpoint='holidays',
        params={'start_day': (start_date - dt.timedelta(
            weeks=weeks))
        }
    ).json()['holidays']

def get_float_people_id(userdata):
    if userdata.float_people_id:
        return userdata.float_people_id

    float_people_id = [ i['people_id'] for i in \
        get_float_data(endpoint='people').json()['people'] if \
        i['im'] == userdata.user.username ]

    if float_people_id:
        # Use most recent Float people_id in the rare case a
        # person has multiple people_ids.
        userdata.float_people_id = int(float_people_id[-1])
        return userdata.float_people_id

    return None

def get_float_tasks(start_date, float_people_id, weeks=1):
    # Get all of the tasks associated with a Float user if the
    # user's Float people_id matches their Tock float_people_id.
    # See https://github.com/floatschedule/api/blob/805663be98c9f48a275c9a13e824b0d6701df398/Sections/tasks.md.
    # Assumes a reporting period is 1 week.
    all_tasks = get_float_data(
        endpoint='tasks',
        params={'weeks': weeks, 'start_day': start_date}
    ).json()['people']

    return flatten(
        [ ii for ii in [i['tasks'] for i in all_tasks \
            if int(i['people_id']) == float_people_id ] ]
    )

def find_common_weekdays(range_one, range_two):
    # Takes start and end dates of two date ranges and returns list of
    # common weekdays.
    last_start = max(range_one[0], range_two[0])
    first_end = min(range_one[1], range_two[1])
    diff = (first_end - last_start).days + 1
    days = [ last_start + dt.timedelta(days=i) for i in \
        range(diff) ]

    return [ d for d in days if d.weekday() < 5 ]
