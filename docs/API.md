## API DOCS

This document provide the instruction to use the mns RESR API, this reduce the time for running the command each time from the cli.
The API is very simple and easy to use, just make sure you have curl installed on your machine.

### Status Code
* 200: Success
* 201: Created
* 404: Not found
* 409: Dupliacted document
* 500: Internal Server Error

## Ping Test Endpoint

### GET `/api/v1/ping`
Endpoint for testing the API.

**Response:**
- Success (200 OK):
    ```json
    {
        "success": true,
        "code": 200,
        "message": "pong"
    }

## GET All the domains
### GET `/api/v1/domains`
Endpoint to retrive all the domains.

**Response:**
- Success (200 OK):
    ```json
        {
            "success":true,
            "code":200,
            "message":
                [
                    "google.com",
                    "facebook.com",
                    "hackerone.com"
                ]
        }



## GET All subdomains for domain
### GET `/api/v1/subdomains/hackerone.com`
Endpoint to retrive all subdomain for a domain.

**Response:**
- Success (200 OK):
    ```json
        {
            "success":true,
            "code":200,
            "message":
                {
                    "domain":"hackerone.com",
                    "subdomains":[
                        "support.hackerone.com",
                        "design.hackerone.com",
                        "events.hackerone.com"
                    ],
                    "id":"64d69318a9d46d3123329cf5"
                }
        }

## Add new domain to the Monitoring Process
### GET `api/v1/domain?domain=hackerone.com`
Add new domain to the database

**Response:**
- Success (200 OK):
    ```json
        {
            "success":true,
            "code":200,
            "message":
                {
                    "domain":"hackerone.com",
                    "subdomains":[
                        "support.hackerone.com",
                        "design.hackerone.com",
                        "events.hackerone.com"
                    ],
                    "id":"64d69318a9d46d3123329cf5"
                }
        }

```
in case the domain is already in database
```json
{
    "success":false,
    "code":409,
    "message":"Domain already exists"}

```


#### Delet target
```bash
curl "http://127.0.0.1:1337/domain/facebook.com" -X DELETE
```

```json
{
    "success": true,
    "code": 200,
    "message": "domain deleted successfully"
}

{
    "success": false,
    "code": 404,
    "message": "Domain not found"
}
```


#### Delet target
```bash
curl "http://127.0.0.1:1337/monitor"
```

```json
{
    "success": true,
    "code": 200,
    "message": "start Monitoring"
}
```
