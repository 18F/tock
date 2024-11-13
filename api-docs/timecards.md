**Timecard info**
----
To fetch a list of all submitted timecards and related information.

Each entry in the response represents timecard data for a user, project, and reporting period.

* **URL**

  /timecards.json

* **Method:**

  `GET`
  
*  **URL params**

   **Required:**
   None.
   
   **Optional:**
   - `date=YYYY-MM-DD` — Returns timecard data for the reporting period in which the YYYY-MM-DD value falls.
   - `user=firstname.lastname` — Returns timecard data for the specified user.
   - `project=id` or `project=name` — Returns timecard data for the specified project by either the project's database `pk` value or the project's `name` value.
   - `before=YYYY-MM-DD` - Returns timecard data that occurred before the provided date.
   - `after=YYYY-MM-DD` - Returns timecard data that occurred after the provided date.

* **Success response:**

  * **Code:** `200` <br />
    **Content:** 
```
[
    {
        "user": "brackish.okun",
        "project_id": "30",
        "project_name": "Big Project",
        "profit_loss_account": "FY15 Ministry of Coin Billable",
        "hours_spent": "16.80",
        "project_allocation": "0.000",
        "start_date": "2014-10-01",
        "end_date": "2014-10-04",
        "billable": true,
        "agency": "Ministry of Coin",
        "flat_rate": false,
        "notes": "",
        "billable_expectation": "0.80",
        "employee_organization": "Keepers of the Keys",
        "project_organization": "Keepers of the Keys",
        "grade": 15
    },...
```
 
* **Error response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample call:**

```
$ curl https://tock.18f.gov/api/timecards.json\?date\=2016-01-01\&user\=brackish.okun\&project\=1 -H 'Authorization: Token 08c25228c4be36f5e66f1148fb9d9bcabb9ef41e'
```

* **Notes:**
  * The sample call includes all optional parameters.
  * `hours_spent` and `project_allocation`
    * For a given timecard entry in the response, at least one of hours and allocation should contain a zero value.
    * An entry may contain a zero value for both hours and allocation. Tock does not prevent a user from including a project in a timecard but not reporting any time for it.
 