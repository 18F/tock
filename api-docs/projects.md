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
        "client": "General Services Administration - 18F (Non-Billable)",
        "name": "18F Branding",
        "description": "Working on branding for 18F\u2014internal branding",
        "billable": false,
        "start_date": null,
        "end_date": null,
        "active": true
    },

```
 
* **Error Response:**

  * **Code:** `401 UNAUTHORIZED` <br />
    **Content:** `{"detail":"Authentication credentials were not provided."}`

* **Sample Call:**

```
$ curl https://tock.18f.gov/api/projects.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

* **Notes:** None.
 
