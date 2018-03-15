**Projects**
----
To fetch a list of projects  information.

* **URL**

  /projects.json

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
        "id": 120,
        "client": "Ministry of Coin",
        "name": "Branding",
        "description": "Working on branding.",
        "billable": true,
        "start_date": null,
        "end_date": null,
        "grade": 16,
        "active": true
    },...

```
 
* **Error Response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample Call:**

```
$ curl https://tock.18f.gov/api/projects.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

* **Notes:**

Note that `grade` may be `null` if no grade information is
available. If it is non-null, it will be a number corresponding to a grade;
the mapping is defined by `GRADE_CHOICES` in `tock/employees/models.py`.
