**Reporting period info**
----
To fetch a list of all available reporting periods and basic information about them.

* **URL**

  /reporting_period_audit.json

* **Method:**

  `GET`
  
*  **URL params**

   **Required:**
   None.
   
   **Optional:**
   None.

* **Success response:**

  * **Code:** `200` <br />
    **Content:** 
```
[
    {
        "start_date": "2016-09-25",
        "end_date": "2016-10-01",
        "exact_working_hours": 40,
        "min_working_hours": 40,
        "max_working_hours": 40
    },...
```
 
* **Error response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample call:**

```
$ curl https://tock.18f.gov/api/reporting_period_audit.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

* **Notes:** None.
 
