# Tock Logging

[:arrow_left: Back to Tock
Documentation](https://github.com/18F/tock/tree/master/docs)

Tock leverages cloud.gov logging system which runs on the Elastic Logsearch
Kibana (ELK) software stack. Logs for the Tock system are available to
Tock Developers with cloud.gov access. For more information about cloud.gov's
logging system, [please read the documentation][cg-logs].

[cg-logs]: https://cloud.gov/docs/apps/logs/

## Kibana Queries

The following logging events (LE) are documented below for developers to easily
access using [cloud.gov's logging system][cg-log-sys].

[cg-log-sys]: https://logs.fr.cloud.gov

| Description                | Kibana Query                                                   |
| -------------------------- | -------------------------------------------------------------- |
| Deployments                | `@cf.app:"tock" AND @message:"Recording deployment of"`        |
| Authorization checks       | `@cf.app:"tock" AND @message:"tock-auth"`                      |
| Authentication checks      | `@cf.app:"tock" AND @message:"Authenticating user"`            |
| Successful login events    | `@cf.app:"tock" AND @message:"Successful login"`               |
| Unsuccessful login events  | `@cf.app:"tock" AND @message:"Unsuccessful login"`             |
| Object access *            | `@cf.app:"tock" AND <TABLE_NAME>`                              |
| Account management events  | `@cf.app:"tock" AND ((versions AND User) OR user_roles)`       |
| All administrator activity | `@cf.app:"tock" AND admin`                                     |
| Data deletions **          | `@cf.app:"tock" AND DELETE`                                    |
| Data access **             | `@cf.app:"tock" AND SELECT`                                    |
| Data changes **            | `@cf.app:"tock" AND (UPDATE OR INSERT)`                        |
| Permission Changes         | `@cf.app:"tock" AND user_roles AND INSERT`                     |

\* For "object access" search by database table name or Model name

\** For these queries, consider including a table name like `@cf.app:"tock" AND SELECT AND employees_employeegrade`

Some table names:
- `employees_employeegrade`
- `employees_userdata`
- `hours_holidayprefills`
- `hours_reportingperiod`
- `hours_reportingperiod_holiday_prefills`
- `hours_targets`
- `hours_timecard`
- `hours_timecardnote`
- `hours_timecardobject`
- `hours_timecardprefilldata`
- `organizations_organization`
- `projects_accountingcode`
- `projects_agency`
- `projects_profitlossaccount`
- `projects_project`
- `projects_project_alerts`
- `projects_projectalert`

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
