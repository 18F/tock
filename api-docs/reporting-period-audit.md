**Reporting Period Info**
----
To fetch a list of all available reporting periods and their related information.

* **URL**

  /reporting_period_audit.json

* **Method:**

  `GET`
  
*  **URL Params**

   **Required:**
   None.
   
   **Optional:**
   None.

* **Success Response:**

  * **Code:** `200` <br />
    **Content:** 
```
{
    "count": 105,
    "next": "http://tock.18f.gov/api/reporting_period_audit.json?page=2",
    "previous": null,
    "results": [
        {
            "start_date": "2016-09-18",
            "end_date": "2016-09-24",
            "exact_working_hours": 40,
            "min_working_hours": 40,
            "max_working_hours": 40
        },...
```
 
* **Error Response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample Call:**

```
$ curl https://tock.18f.gov/api/reporting_period_audit.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

* **Notes:** None.
 
