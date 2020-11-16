from functools import wraps
from typing import List, Union, Dict, Callable


def parse_response(expected: str) -> Callable:
    """
    Decorator for a function that returns a requests.Response object.
    This decorator parses that response depending on the value of <expected>.

    If the response indicates the request failed (status >= 400) a dictionary
    containing the response status and message will be returned. Otherwise,
    the content will be parsed and a dictionary or list will be returned if
    expected == 'json', a string will be returned if expected == 'text' and
    a binary string will be returned if expected == 'content'.

    This also updates the return annotation for the wrapped function according
    to the expected return value type.
    """

    def _parser(f):
        @wraps(f)
        def _f(*args, **kwargs):
            response = f(*args, **kwargs)
            if not response.ok or expected == "json":
                return response.json()
            if expected == "content":
                return response.content
            if expected == "text":
                return response.text
            return response.json()

        f.__annotations__["return"] = _get_expected_return(expected)
        return _f

    return _parser


def _get_expected_return(expected: str) -> type:
    if expected == "json":
        return Union[Dict[str, str], List[Dict[str, str]]]
    elif expected == "content":
        return Union[Dict[str, str], bytes]
    elif expected == "text":
        return Union[Dict[str, str], bytes]
    return Dict[str, str]
