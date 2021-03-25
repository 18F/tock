**Timecard Summary info**
----
Fetch a list of timecard and associated summary information. Does not include
project level tock data.

* **URL**

  /timecard_summary.json

* **Method:**

  `GET`

*  **URL params**

   **Required:**
   None.

   **Optional:**
   - `date=YYYY-MM-DD` — Returns timecards for the reporting period in which the YYYY-MM-DD value falls
   - `before=YYYY-MM-DD` — Returns timecards for the reporting periods before the YYYY-MM-DD value
   - `after=YYYY-MM-DD` — Returns timecards for the reporting periods after the YYYY-MM-DD value
   - `user=firstname.lastname` — Returns timecards for the specified user
   - `org=18F` - Returns timecards associated with the provided organization

* **Success response:**

  * **Code:** `200` <br />
    **Content:**
```
[
    {
        "id": <int>,
        "user": "first.last",
        "reporting_start_date": YYYY-MM-DD,
        "reporting_end_date": YYYY-MM-DD,
        "unit": "<string>",
        "organization": "<string>",
        "submitted": <boolean>,
        "billable_expectation": "<decimal>",
        "target_hours": "<decimal>",
        "billable_hours": "<decimal>",
        "non_billable_hours": "<decimal>",
        "excluded_hours": "<decimal>",
        "utilization": "<decimal>"
    },...
```

* **Error response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample call:**

```
$ curl https://tock.18f.gov/api/timecard_summary.json\?date\=2020-01-01\&user\=tock.user -H 'Authorization: Token <auth_token>'
```
