**User info**
----
To fetch a list of all users, along with basic information about them.

* **URL**

  /users.json

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
        "id": 42,
        "username": "john.smith",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@abc"
    },...
```
 
* **Error response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample call:**

```
$ curl https://tock.18f.gov/api/users.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

* **Notes:** None.
 
