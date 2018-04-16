**User data**
----
To fetch a list of all users, along with organizational information for each.

* **URL**

  /user_data.json

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
        "user": "david.levinson",
        "current_employee": true,
        "is_18f_employee": true,
        "is_billable": true,
        "unit": "Chapters-SETI"
    },...
```
 
* **Error response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample call:**

```
$ curl https://tock.18f.gov/api/user_data.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

* **Notes:** None.
 
