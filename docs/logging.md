# Tock logging

[:arrow_left: Back to Tock Documentation](../docs)

Tock leverages the cloud.gov logging system, which runs on the Elastic Logsearch
Kibana (ELK) software stack.

Logs for the Tock system are available to
Tock developers who have cloud.gov access. For more information about cloud.gov's
logging system, [please read the documentation][cg-logs].

[cg-logs]: https://cloud.gov/docs/apps/logs/

## Admin Logs

The Admin Recent Actions logs are maintained by the Django Framework. Query this
database table to determine any of the following actions in the admin interface.

- Content Type ID
- User ID
- Action Time
- Object ID
- Object Representation
- Action Flag
  - This can have a value of any of the following:
    - Addition - `1`
    - Change - `2`
    - Deletion - `3`
- Change Message

Viewing these logs requires you to be connected to the database. Read more about
this [in the cloud.gov documentation around
RDS](https://cloud.gov/docs/services/relational-database/#manually-access-a-database).

Once you've connected to the database, running the following SQL Query will
retrieve all entries from the Admin Recent Actions logs.

```sql
SELECT * FROM django_admin_log ORDER BY django_admin_log DESC;
```

The results give you a log of recent activity with the most recent activity at
the top. The logs help Tock developers determine who made the changes and what
specific changes were made. They are less noisy than the Kibana logs described
before for Admin recent activity.

## Kibana queries

The following logging events (LE) are documented here so developers can easily
access them as they're using [cloud.gov's logging system][cg-log-sys].

[cg-log-sys]: https://logs.fr.cloud.gov

| Description                | Kibana query                                                     |
| -------------------------- | ---------------------------------------------------------------- |
| Deployments                | `@cf.app:"tock" AND @message:"Recording deployment of"`          |
| Authorization checks       | `@cf.app:"tock" AND @message:"tock-auth"`                        |
| Authentication checks      | `@cf.app:"tock" AND @message:"Authenticating user"`              |
| Successful login events    | `@cf.app:"tock" AND @message:"Successful login"`                 |
| Unsuccessful login events  | `@cf.app:"tock" AND @message:"Unsuccessful login"`               |
| Object access *            | `@cf.app:"tock" AND @message:"TimecardObject"`                   |
| Account management events  | `@cf.app:"tock" AND @message:"account-management"`               |
| All administrator activity | `@cf.app:"tock" AND @message:"admin-log"`                        |
| Data deletions             | `@cf.app:"tock" AND (@message:"removed" OR @message:"deleted")`  |
| Data access **             | `@cf.app:"tock" AND @message:"/api/reporting_period"`            |
| Data changes *             | `@cf.app:"tock" AND (@message:"create" OR @message:"change")`    |
| Permission changes         | `@cf.app:"tock" AND @message:"account-management"`               |

\* For "object access," search by Model name, `AND @message:"EmployeeGrade"`.

\** For "data access," search by Data URL.

Some Model names:
- `EmployeeGrade`
- `UserData`
- `HolidayPrefills`
- `ReportingPeriod`
- `Timecard`
- `TimecardNote`
- `TimecardObject`
- `TimecardPrefillData`
- `Organization`
- `AccountingCode`
- `Agency`
- `ProfitLossAccount`
- `Project`
- `ProjectAlerts`
- `ProjectAlert`

Some Data URLs:
- `/reporting_period`
- `/reports`
- `/employees`
- `/utilization`
- `/projects`
- `/admin`
- `/auth`
- `/api`
- `/api/projects`
- `/api/users`
- `/api/reporting_period_audit`
- `/api/timecards`
- `/api/hours/by_quarter`
- `/api/hours/by_quarter_by_user`
- `/api/user_data`


## Tock Log Auditing

To ensure that we are secure and that we are fulfilling our compliance duties, we
do continuous monitoring of the events coming from the tock system.  

If you 
are an admin who has been assigned this responsibility, you should have at least
one issue open in the [Tock Issues Page](https://github.com/18F/tock/issues/)
that is assigned to you.  The issues are titled something like
`Weekly Tock Logging Audit [20191004]` for the audit that is to be carried out
on 10/04/2019.  If not, create one now, using https://github.com/18F/tock/issues/913
as an example.  You may, as this example indicates, want to create a few
more for future weeks and assign them to yourself or other admins, if you are
going to be out of town, for example.

Once you have created the issue, follow the Audit Process.

### Audit Process

On a weekly
basis, we will log into [the cloud.gov logging system](https://logs.fr.cloud.gov/app/kibana#/discover) and
search for:
```
@cf.app:"tock" AND ((@message:"tock-auth" AND @message:"Creating User for") OR @message:"Unsuccessful login" OR @message:"account-management" OR @message:"admin-log" OR @message:"Updated app with guid")
```

Make sure you set your time range to the last 7 days or more.  This should get you a list
of events for the last week that you can review for signs of unusual activity.  The events are:

- **New Tock users being created:**  If these users are unusually named, or you see many of
  them created at once, it may be signs of enemy activity.
- **Unsuccessful logins:**  This probably shouldn't happen in production, given that it
  uses UAA for authentication.  If it does, perhaps that has been bypassed.
- **Account Management:**  These messages should reflect when permissions are granted to
  people.  It doesn't happen often, so if you see permissions being granted to random users,
  or with any great frequency, you should check to see that these are proper.
- **Admin Logs:**  This shows a log of administrator activities, like creating timecards
  for others, changing/creating projects and accounting codes, etc.  If there are unusual
  users doing these activities, or unusual amounts of these events, you might need to
  verify that the users and activities are authorized.
- **Deploy Logs:**  Unusually timed deployments should be investigated.  You should be
  able to correlate deployment events with [CircleCI deploys](https://circleci.com/gh/18F/workflows/tock/tree/master).
  If not, then somebody might be trying to push code out outside of the process.

You should scan over the events netted by this search, using the criteria given above.
It should not take more than a few minutes.

### Extra Credit

You should also take a quick look at this query too:
```
@cf.app:"tock" AND @source.type:"RTR" NOT (rtr.status:"200" OR rtr.status:"302" OR rtr.status:"304")
```
It will reveal the many people who are banging on the door of the application in
one way or another.  They are not in themselves incidents, but the kind of traffic
you see here might be unusually high in volume, indicating a Denial Of Service attack,
or they may have interesting data in the URLs that indicate that they are targeting
a specific user or feature of the application.  You might consider talking to the user
and seeing why they might be targeting them, or auditing the code of the endpoint/feature
they are attacking.

This part of the audit is not required, but is good to do because it is proactive
rather than reactive.  It may give you information on things that you might
need to deal with someday.

### Recording The Log Audit

If you see events that are bad/suspicious, initiate the
[Security Incident Process](https://handbook.18f.gov/security-incidents/).

Otherwise, record the log audit so that we can prove to auditors that we are
actually continuously monitoring the app:

- Open up the [Tock Issues Page](https://github.com/18F/tock/issues/) and find the issue
  for this week.
- Close the issue with a comment like
  `I have reviewed the logs using https://github.com/18F/tock/blob/master/docs/logging.md and found nothing unusual.`
- Create at least one issue for next week's audit and assign it to a tock admin
  who can carry the audit out (or yourself).
- Celebrate!  You have completed the audit.
