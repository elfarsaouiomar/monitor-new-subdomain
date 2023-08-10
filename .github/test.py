from http.client import responses

status_code = 401
phrase = responses.get(status_code, '')
print(phrase)