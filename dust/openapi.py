from pydantic import BaseModel
from typing import Dict, List
import yaml

class OpenAPI:
    def __init__(self, title: str, version: str, description: str):
        self.title = title
        self.version = version
        self.description = description
        self.paths = {}

    def add_path(self, path: str, method: str, summary: str, description: str, responses: Dict, parameters: List = None, request_body: Dict = None):
        if path not in self.paths:
            self.paths[path] = {}
        self.paths[path][method.lower()] = {
            "summary": summary,
            "description": description,
            "responses": responses
        }
        if parameters:
            self.paths[path][method.lower()]["parameters"] = parameters
        if request_body:
            self.paths[path][method.lower()]["requestBody"] = request_body

    def generate(self):
        openapi_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": self.description
            },
            "paths": self.paths
        }
        return yaml.dump(openapi_schema)
