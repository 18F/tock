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
{
    "count": 280,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 120,
            "client": "Ministry of Coin",
            "name": "Big Project",
            "description": "Updating Ministry of Coin website to U.S. Web Design Standards.",
            "billable": True,
            "start_date": "2016-01-01",
            "end_date": "2016-09-30",
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

* **Notes:** None.
 
