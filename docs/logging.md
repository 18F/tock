# Tock Logging

[:arrow_left: Back to Tock Documentation](..)

Tock leverages cloud.gov logging system which runs on the Elastic Logsearch
Kibana (ELK) software stack. Logs for the Tock system are available to
Tock Developers with cloud.gov access. For more information about cloud.gov's
logging system, [please read the documentation][cg-logs].

[cg-logs]: https://cloud.gov/docs/apps/logs/

## Kibana Queries

The following logging events (LE) are documented below for developers to easily
access using [cloud.gov's logging system][cg-log-sys].

[cg-log-sys]: https://logs.fr.cloud.gov

| Description                | Kibana Query                                      |
| -------------------------- | ------------------------------------------------- |
| Deployments                | `@cf.app:"tock" AND @cf.message:"Recorded deployment"`               |
| Authorization checks       | `@cf.app:"tock" AND @cf.message:"Authorization check"`               |
| Authentication checks      | `@cf.app:"tock" AND @cf.message:"Authentication check"`              |
| Successful login events    | `@cf.app:"tock" AND @cf.message:"Successful login"`                  |
| Unsuccessful login events  | `@cf.app:"tock" AND @cf.message:"Unsuccessful login"`                |
| Object access *            | `@cf.app:"tock" AND gsa18f_procurements`                 |
| Account management events  | `@cf.app:"tock" AND ((versions AND User) OR user_roles)` |
| All administrator activity | `@cf.app:"tock" AND admin`                               |
| Data deletions **          | `@cf.app:"tock" AND DELETE`                              |
| Data access **             | `@cf.app:"tock" AND SELECT`                              |
| Data changes **            | `@cf.app:"tock" AND (UPDATE OR INSERT)`                  |
| Permission Changes         | `@cf.app:"tock" AND user_roles AND INSERT`               |

\* For "object access" search by database table name.

\** For these queries, consider including a table name like `@cf.app:"tock" AND SELECT AND proposals`


Some table names:
- `<TABLE_NAME>`

https://docs.djangoproject.com/en/dev/ref/contrib/auth/#module-django.contrib.auth.signals
