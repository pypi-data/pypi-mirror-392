from magu.core import router
import re

def request_mapping(uri: str = "/"):
    def wrapper(cls):
        cls._uri = uri
        return cls
    return wrapper

def parse_route(route: str):
    param_regex = r"{([a-zA-Z_][a-zA-Z0-9_]*)}"
    params = re.findall(param_regex, route)

    pattern = re.sub(param_regex, lambda m: f"(?P<{m.group(1)}>[^/]+)", route)
    pattern = "^" + pattern + "$"

    return re.compile(pattern), params


class PathVariable:
    def __init__(self):
        self.name = None
    
    def __set_name__(self, owner, name: str):
        self.name = name
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


def get_mapping(uri: str = "/"):
        def wrapper(func):
            func._http_method = 'GET'

            pattern = r"({(.*?)})"
            uri_initial = re.sub(pattern, "{ID_PLACEHOLDER}", uri)
            func._method_uri = uri_initial

            return func
        return wrapper
    
def post_mapping(uri: str = "/"):
    def wrapper(func):
        func._http_method = 'POST'

        pattern = r"({(.*?)})"
        uri_initial = re.sub(pattern, "{ID_PLACEHOLDER}", uri)
        func._method_uri = uri_initial

        return func
    return wrapper
    
def put_mapping(uri: str = "/"):
    def wrapper(func):
        func._http_method = 'PUT'

        pattern = r"({(.*?)})"
        uri_initial = re.sub(pattern, "{ID_PLACEHOLDER}", uri)
        func._method_uri = uri_initial
        
        return func
    return wrapper
    
def patch_mapping(uri: str = "/"):
    def wrapper(func):
        func._http_method = 'PATCH'

        pattern = r"({(.*?)})"
        uri_initial = re.sub(pattern, "{ID_PLACEHOLDER}", uri)
        func._method_uri = uri_initial

        return func
    return wrapper
    
def delete_mapping(uri: str = "/"):
    def wrapper(func):
        func._http_method = 'DELETE'

        pattern = r"({(.*?)})"
        uri_initial = re.sub(pattern, "{ID_PLACEHOLDER}", uri)
        func._method_uri = uri_initial
        
        return func
    return wrapper

class Controller:
    def __init__(self):
        self.uri = self._uri
        router.get_routes(self.__class__)

    def __str__(self):
        return f"Controller for {self.uri}"
