import os
import pyjson5
from pathlib import Path
from logging import Logger, getLogger

from .api import Api
from .api.warehouse import WarehouseApi
from .api.content_hub import ContentHubApi

from .service.warehouse import WarehouseService
from .service.content_hub import ContentHubService


def load_config(file_path: str):
    locations = [
        Path(file_path if file_path is not None else ".datacanva"),
        Path.cwd() / ".datacanva",
        Path.home() / ".datacanva",
    ]

    for location in locations:
        try:
            if os.path.exists(location):
                with open(location, "r") as file:
                    return pyjson5.decode(file.read())
        except Exception as e:
            print(e)

    return {}


class DataCanvaClient:

    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        config_file: str = None,
        logger: Logger = None,
    ):
        config = load_config(config_file)

        if not base_url:
            base_url = config.get("base_url")

        if not api_key:
            api_key = config.get("api_key")

        self.logger = logger if logger is not None else getLogger("DataCanvaClient")
        self.api = Api(base_url=base_url, api_key=api_key)
        self.warehouse = WarehouseService(self.logger, WarehouseApi(self.api))
        self.content_hub = ContentHubService(self.logger, ContentHubApi(self.api))
