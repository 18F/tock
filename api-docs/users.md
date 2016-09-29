**User Info**
----
To fetch a list of all users and their related information.

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
[
    {
        "id": 42,
        "username": "john.smith",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@abc"
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
 
