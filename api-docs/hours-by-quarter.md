**Timecards by Quarter**
----
To fetch a summary of all submitted timecards, by year and quarter.

* **URL**

  hours/by_quarter.json

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
[
    {
        "year": 2010,
        "quarter": 3,
        "billable": 16,869.0,
        "nonbillable": 1001.0,
        "total": 17870.0
    },...
```
 
* **Error Response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample Call:**

```
$ curl https://tock.18f.gov/api/hours/by_quarter.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

* **Notes:** None.
 
