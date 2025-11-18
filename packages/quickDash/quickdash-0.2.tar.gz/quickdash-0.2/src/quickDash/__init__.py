import flask
from typing import Callable
import os
import math

request = flask.request

class Dashboard():
    def __init__(self, module_name, title="Dashboard") -> None:
        self.app = flask.Flask(module_name, static_folder=os.path.join(__file__, "..", "static"), template_folder=os.path.join(__file__, "..", "templates"))
        self.title = title
        self.theme = "light"
        self.run = self.app.run
    
    def route(self, rule: str, **kwargs):
        def decorator(f: Callable):
            def mkPage():
                request = flask.request
                return flask.render_template("master.html", title=f"{self.title} | "+f.__name__, content=f"<h1>{f.__name__}</h1>"+f(), theme=self.theme)
            self.app.add_url_rule(rule, f.__name__, mkPage, None, **kwargs)
            return f
        return decorator