**Project Info**
----
To fetch information about a specific project.

* **URL**

  /users.json

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
    "count": 308,
    "next": "http://tock.18f.gov/api/users.json?page=2",
    "previous": null,
    "results": [
        {
            "id": 42,
            "username": "sarah.allen",
            "first_name": "Sarah",
            "last_name": "Allen",
            "email": "sarah.allen@gsa.gov"
        },...
```
 
* **Error Response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample Call:**

```
$ curl https://tock.18f.gov/api/users.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

* **Notes:** None.
 
