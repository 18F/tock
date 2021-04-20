**Full timecard info**
----
To fetch a list of timecards and related info.

* **URL**

  /full_timecards.json

* **Method:**

  `GET`
  
*  **URL params**

   **Required:**
   None.
   
   **Optional:**
   - `only_submitted=true` - Returns only timecards that have been submitted.
   - `earliest_reporting_period_start=YYYY-MM-DD` - Returns only timecards whose reporting period start date was _after_ the provided date. 

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
 
