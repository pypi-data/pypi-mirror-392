from typing import TypeVar, Generic
from collections.abc import Callable
from logging import Logger

from ..api import CrudApi

ItemType = TypeVar("ItemType")


class Service(Generic[ItemType]):

    def __init__(
        self, logger: Logger, crud_api: CrudApi, item: Callable[..., ItemType]
    ):
        self.logger = logger
        self.crud_api = crud_api
        self.item = item

    def get_by_name(self, creator_username: str, entity_name: str):
        try:
            res = self.crud_api.get_list(
                {
                    "name.eq": entity_name,
                    "creatorUsername.eq": creator_username,
                }
            )
            items = res["items"]
            if len(items) == 0:
                self.logger.error(f"Item not found: {creator_username}/{entity_name}")
                return None

            return self.item(self, items[0])
        except Exception as e:
            self.logger.error(f"Failed to get item by name: {e}")
            return None
