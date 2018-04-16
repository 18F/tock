**Hours by quarter**
----
To fetch an hourly summary, by year and quarter, of all submitted timecards.

* **URL**

  hours/by_quarter.json

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
        "year": 2010,
        "quarter": 3,
        "billable": 16,869.0,
        "nonbillable": 1001.0,
        "total": 17870.0
    },...
```
 
* **Error response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample call:**

```
$ curl https://tock.18f.gov/api/hours/by_quarter.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

* **Notes:** None.
 
