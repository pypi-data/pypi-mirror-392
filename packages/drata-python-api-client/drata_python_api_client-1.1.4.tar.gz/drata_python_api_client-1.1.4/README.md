# drata-python-api-client
A client library for accessing The Drata public API 

## Usage
First, create a client:

```python
from drata_python_api_client.models import (
    UserResponsePublicDto, ExceptionResponsePublicDto
)
from drata_python_api_client import AuthenticatedClient

drata_client = AuthenticatedClient(region="EU", token="VeryMuchSecureToken")
```

Now call your endpoint and use your models:

```python
from drata_python_api_client.api.users import users_public_controller_get_user_by_email

user: UserResponsePublicDto = users_public_controller_get_user_by_email.sync(
    client=drata_client,
    email="some@email.com",
)
```

Or do the same thing with an async version:

```python
from drata_python_api_client.models import (
    UserResponsePublicDto, ExceptionResponsePublicDto
)
from drata_python_api_client.api.users import users_public_controller_get_user_by_email

async with client as client:
    Union[
        BackgroundCheckResponsePublicDto, 
        ExceptionResponsePublicDto
    ] = await users_public_controller_get_user_by_email.asyncio(client=client, email="some@email.com")
```

## Advanced customizations

There are more settings on the generated `AuthenticatedClient` class which let you control more runtime behavior, check out the docstring on that class for more info. You can also customize the underlying `httpx.Client` or `httpx.AsyncClient` (depending on your use-case):

```python
from drata_python_api_client import AuthenticatedClient

def log_request(request):
    print(f"Request event hook: {request.method} {request.url} - Waiting for response")

def log_response(response):
    request = response.request
    print(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")

client = AuthenticatedClient(
    region="EU",
    httpx_args={"event_hooks": {"request": [log_request], "response": [log_response]}},
)

```

## Building / publishing this package

If you want to install this client into another project without publishing it (e.g. for development) then:
1. If that project **is using Poetry**, you can simply do `poetry add <path-to-this-client>` from that project
1. If that project is not using Poetry:
    1. Build a wheel with `poetry build -f wheel`
    1. Install that wheel from the other project `pip install <path-to-wheel>`
