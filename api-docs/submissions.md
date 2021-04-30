**Submissions by range**
----
Fetches a list of users and a count of punctual timecard submission by past reporting periods

* **URL**

  /submissions/[X].json

  *The value [X] represents the number of recent reporting periods from which timecard counts will be pulled.*

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
        "user": 77,
        "username": "john.smith",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@abc"
        "on_time_submissions": 21
    },...
```

* **Error response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample call:**

```
$ curl https://tock.18f.gov/api/submissions/10.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

* **Notes:** None.

