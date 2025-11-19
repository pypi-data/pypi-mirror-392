from magu.controllers.controller import Controller
from magu.services.handler import Handler
import inspect
import re

routes: dict[str, tuple] = {}

def get_routes(controller: Controller.__class__):
     for _, func in inspect.getmembers(controller, inspect.isfunction):
          if hasattr(func, "_http_method"):
            if func._method_uri.find("{") != -1 and func._method_uri.find("}") != -1:
                route = f"{func._http_method} /{controller._uri.replace("/", "")}{func._method_uri}"
            elif func._method_uri.strip() != "/":
                route = f"{func._http_method} /{controller._uri.replace("/", "")}/{func._method_uri.replace("/", "")}"
            else:
                route = f"{func._http_method} /{controller._uri.replace("/", "")}"
            routes[route] = (func, controller)


def get_methods(uri: str, method: str, id: str = None):
        methods = []
        for name in routes:
            route_method = name.split(" ")[0]
            route_uri = name.split(" ")[1]

            if route_uri.find("{") != -1 and route_uri.find("}") != -1:
                route_uri = re.sub(r"({(.*?)})", id, route_uri)

            controller = routes[name]
            if route_method.strip() == method and route_uri.strip() == uri:
                methods.append((routes[name], controller))
             
        return methods


class Router:
    def route(self, handler: Handler, http_method: str, data: dict = {}):
        server_path = handler.path
        parse_path = handler.parse_path(server_path)
        
        pk = re.findall(r"(?<=/)\d+", parse_path["path"])[0] if re.findall(r"(?<=/)\d+", parse_path["path"]) else ""

        try:
            gets = get_methods(parse_path["path"], http_method, pk)[0]
        except IndexError:
            handler.send_json({"404": "Not Found"}, status=404)
            return

        for func, cont in gets:
            cont.pk = pk
            cont.data = data
            instance = cont()
            handler.send_json(func(instance))
            break
