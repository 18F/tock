**User Data**
----
To fetch a list of all users with organizational information for each.

* **URL**

  /users_data.json

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
    "count": 306,
    "next": null,
    "previous": null,
    "results": [
        {
            "user": "david.levinson",
            "current_employee": true,
            "is_18f_employee": true,
            "is_billable": true,
            "unit": "Chapters-SETI"
        },...
```
 
* **Error Response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample Call:**

```
$ curl https://tock.18f.gov/api/user_data.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

* **Notes:** None.
 
