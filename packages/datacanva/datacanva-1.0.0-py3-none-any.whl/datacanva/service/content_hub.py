from logging import Logger

from ..api.content_hub import ContentHubApi
from . import Service


class ContentHub:

    def __init__(self, service: "ContentHubService", data: dict):
        self.service = service
        self.id = data["id"]
        self.name = data["name"]
        self.creator = data["creatorUsername"]

    def __str__(self):
        return f"ContentHub/{self.creator}/{self.name}({self.id})"

    def get_content(self, path: str):
        return self.service.api.get_content(self.id, path=path)

    def put_content(self, path: str, file):
        return self.service.api.put_content(self.id, path=path, file=file)

    def delete_content(self, path: str):
        return self.service.api.delete_content(self.id, path=path)


class ContentHubService(Service[ContentHub]):

    def __init__(self, logger: Logger, api: ContentHubApi):
        super().__init__(logger, api, ContentHub)
        self.api = api
