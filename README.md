# Markus API

Python interface to the api for a [MarkUs](https://github.com/MarkUsProject/Markus) instance.

## Installation

Install this package with pip:

```
$ pip install markusapi
```

## Requirements

* python 3.6+
* the `url` of a running [MarkUs website](https://github.com/MarkUsProject/Markus)
* your `api_key` (this can be obtained from the dashboard page of the MarkUs website)

## Usage Example

Create a new Markus Api object:

```
import markusapi

api_key = 'mysecretapikey='
url = 'https://localhost:3000'

api = markusapi.Markus(api_key, url)
```

Print all user information

```
user_info = api.get_all_users()
print(user_info)
```

## Additional Info

Check out the MarkUs API documentation for details on API calls:

[https://github.com/MarkUsProject/Markus/wiki/RESTfulApiDocumentation](https://github.com/MarkUsProject/Markus/wiki/RESTfulApiDocumentation)

