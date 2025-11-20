from ..type.criteria import *
from . import Api, CrudApi


class WriteDataRequest(TypedDict):
    writeMode: WriteMode
    schema: Schema
    data: list[dict]
    generateSchema: bool
    skipValidation: bool
    upsertBy: list[str]
    patchMode: bool
    deleteMode: bool
    description: str


class GetDataRequest(TypedDict):
    acquireReadLock: bool = True
    page: int = 0
    size: int = 1000
    sort: list[tuple[str, str]]
    criteria: Criteria
    description: str


class WarehouseApi(CrudApi):

    def __init__(self, api: Api):
        super().__init__(api, "/warehouse/entity")

    def write_data(self, id: int, request: WriteDataRequest):
        return self.api.post(self._with_base_path(f"/{id}/data"), json=request)

    def get_data(self, id: int, request: GetDataRequest):
        return self.api.post(
            self._with_base_path(f"/{id}/data/get"),
            json={
                **request,
                "criteria": (
                    request["criteria"].__dict__()
                    if request["criteria"] is not None
                    else None
                ),
            },
        )

    def clear_data(self, id: int):
        return self.api.delete(self._with_base_path(f"/{id}/data"))

    def generate_schema(self, id: int):
        return self.api.post(self._with_base_path(f"/{id}/schema/generate"))

    def validate_schema(self, id: int):
        return self.api.post(self._with_base_path(f"/{id}/schema/validate"))

    def get_lock_queue(self, id: int):
        return self.api.get(self._with_base_path(f"/{id}/lock"))
