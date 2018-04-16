**Hours by quarter and user info**
----
To fetch an hourly summary of all submitted timecards by year, by quarter, and by user.

* **URL**

  /hours/by_quarter_by_user.json

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
        "year": 2012,
        "quarter": 4,
        "username": "julius.levinson",
        "billable": 200.8,
        "nonbillable": 50.2,
        "total": 251.0
    },...
```
 
* **Error response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample call:**

```
$ curl https://tock.18f.gov/api/hours/by_quarter_by_user.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

* **Notes:** None.
 
