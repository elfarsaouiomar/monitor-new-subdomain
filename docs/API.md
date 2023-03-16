## API DOCS

This document provide the instruction to use the mns RESR API, this reduce the time for running the command each time from the cli.
The API is very simple and easy to use, just make sure you have curl installed on your machine.

### Status Code Errors
* 200: success
* 404: not found 
* 409: dupliacted document
* 500: Internal Server Error 


#### Get All domains
```bash
curl http://127.0.0.1:8000/domains
```

```json
{
    "success": true,
    "code": 200,
    "message":
        [
        "linkedin.com",
        "tesla.com",
        "facebook.com"
        ]
}
```

#### Get subdomains by domain name
```bash
curl http://127.0.0.1:8000/domain/linkedin.com
```

```json
"success": true,
"code": 200,
"message": {
"domain": "linkedin.com",
"subdomains": [
        "lva1-svn-ha-stg-dr.corp.linkedin.com",
        "do.linkedin.com",
        "ltx1-invipsapi.prod.linkedin.com",
        "gc.linkedin.com",
        "mgmtgw01.corp.linkedin.com",
        "rum9.linkedin.com",
        "content.linkedin.com"
    ]
}
```

#### Add new target
```bash
curl "http://127.0.0.1:8000/domain?domain=facebook.com" -X POST
```

```json
{
    "success": true,
    "code": 201, 
    "message": "facebook.com"
}
```

#### Delet target
```bash
curl "http://127.0.0.1:8000/domain/facebook.com" -X DELETE
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
curl "http://127.0.0.1:8000/monitor"
```

```json
{
    "success": true,
    "code": 200, 
    "message": "start Monitoring"
}
```
