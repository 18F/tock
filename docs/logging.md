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
