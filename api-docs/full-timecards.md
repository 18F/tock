**Full timecard info**
----
To fetch a list of timecards and related info. By default, only timecards that have already been submitted are returned (see the `submitted` parameter below to change that behavior).

* **URL**

  /full_timecards.json

* **Method:**

  `GET`
  
*  **URL params**

   **Required:**
   None.
   
   **Optional:**
   - `submitted=` - By default, only timecards which have been submitted are returned. Pass `no` as the value for this argument to fetch timecards that have _not_ been submitted.
   - `date=YYYY-MM-DD` — Returns timecard data for the reporting period in which the YYYY-MM-DD value falls.
   - `after=YYYY-MM-DD` — Returns timecard data for reporting periods whose end date falls on or after YYYY-MM-DD.
   - `before=YYYY-MM-DD` — Returns timecard data for the reporting periods whose start date falls on or before YYYY-MM-DD.
   - `user=firstname.lastname` — Returns timecard data for the specified user. Accepts either a username or a user's numeric ID.
   - `project=id` or `project=name` — Returns timecard data for the specified project by either the project's database `pk` value or the project's `name` value.
   - `org=id` - Returns timecard data for users belonging to a specific organization ID. Options: 0 - include all organizations. "none" - include timecards from users who belong to no organizations. Any other number - only return timecards for users belonging to that organization.

* **Success response:**

  * **Code:** `200` <br />
    **Content:** 
```
[
   {
      "hours_spent" : 16,
      "submitted" : false,
      "billable_hours" : "16.00",
      "excluded_hours" : "0.00",
      "submitted_date" : null,
      "non_billable_hours" : "0.00",
      "reporting_period_start_date" : "2021-04-18",
      "target_hours" : "13.00",
      "billable_expectation" : "0.80",
      "id" : 4412,
      "reporting_period_end_date" : "2021-04-24",
      "user_name" : "nick.user",
      "utilization" : "1.23"
   },...
]
```
* **Sample call:**

```
$ curl localhost:8000/api/full_timecards.json\?earliest_reporting_period_start=2021-04-01 -H 'Authorization: Token N0TaR@elT0k3n'
```

* **Notes:** The sample call includes all optional parameters.
 
