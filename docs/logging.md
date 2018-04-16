# Tock logging

[:arrow_left: Back to Tock Documentation](../docs)

Tock leverages the cloud.gov logging system, which runs on the Elastic Logsearch
Kibana (ELK) software stack. 

Logs for the Tock system are available to
Tock developers who have cloud.gov access. For more information about cloud.gov's
logging system, [please read the documentation][cg-logs].

[cg-logs]: https://cloud.gov/docs/apps/logs/

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
- `Targets`
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
