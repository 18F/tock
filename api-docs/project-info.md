**Project Info**
----
To fetch information about a specific project.

* **URL**

  /projects/[integer].json
  
  *[integer] is the project's `id` or `pk` value. To get a list of these values, see [/projects.json documentation](https://github.com/18F/blob/master/tock/api-docs/projects.md).*

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
    "id": 1,
    "client": "Ministry of Coin",
    "name": "Big Project",
    "description": "Updating Ministry of Coin website to U.S. Web Design Standards.",
    "billable": true,
    "start_date": "2016-01-01",
    "end_date": "2016-09-30",
    "active": false
},...
```
 
* **Error Response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample Call:**

```
$ curl https://tock.18f.gov/api/projects/100.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

* **Notes:** None.
 
