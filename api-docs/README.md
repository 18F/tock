# Tock API documentation

[:arrow_left: Back to Tock Documentation](../docs)


## Before you start
You'll need to have an API authorization token. Contact a Tock developer 
or ping the [`#tock-dev`](https://gsa-tts.slack.com/messages/tock-dev/) Slack channel for help.


## Usage
You may issue GET requests to the various endpoints via the `/api/` path; 
your results will be returned as JSON objects. 
We use Django REST Framework's TokenAuthentication library, 
which requires all requests to include a token value in the request header using the following format:

```sh
$ curl https://tock.18f.gov/api/projects.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```
This example uses a cURL command-line-based request for getting project data from our Tock deployment.

To access similar data in CSV format within Tock, please visit the
[/reports](https://tock.18f.gov/reports) page.


## Available Endpoints

- [Hours by quarter by user](hours-by-quarter-by-user.md): Fetches an hourly summary of all submitted timecards by year, by quarter, and by user.
- [Hours by quarter](hours-by-quarter.md): Fetches an hourly summary, by year and quarter, of all submitted timecards.
- [Project info](project-info.md): Fetches information about a specific project.
- [Projects](projects.md): Fetches information about various projects.
- [Reporting period (audit specific time period)](reporting-period-audit-specific.md): Fetches a list of all users who have not submitted a timecard for the specified period.
- [Reporting periods](reporting-period-audit.md): Fetches a list of all available reporting periods and basic information about them.
- [Submissions by range](submissions.md): Fetches a list of users and a count of timecards submitted on or before the last day of each timecard's reporting period.
- [Timecards](timecards.md): Fetches a list of all submitted timecard objects and related information. Note that a "timecard object" here represents time a person spent on a given project. It's a more granular view of what someone worked on (compared to the "full timecards" endpoint, documented below).
- [Full timecards](full-timecards.md): Fetches a list of all timecards and related information. Note that a "timecard" here is different from a "timecard object" - a "timecard" is a higher level representation of what a person worked on during a reporting period, which could include many projects for varying periods of time, but that level of granularity is not captured here. If you want project-level data, don't use this endpoint - use the "Timecards" one above.
- [User data](user-data.md): Fetches a list of all users, along with organizational information for each.
- [Users](users.md): Fetches a list of all users, along with basic information about them.


## Examples 

Tock administrators and users use the Tock API in various ways.
Here are two common examples of Tock API usage:

- [AngryTock Slack Bot](https://github.com/18F/angrytock)
- [Google App Script](https://github.com/18F/tock-gas-ts)

--------

The Tock API documentation is written in
[GitHub-flavored markdown][gh-md] and is best read using the GitHub interface.

[gh-md]: https://guides.github.com/features/mastering-markdown/#GitHub-flavored-markdown
