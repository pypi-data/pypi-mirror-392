from . import Api, CrudApi


class ContentHubApi(CrudApi):

    def __init__(self, api: Api):
        super().__init__(api, "/content-hub")

    def get_content(self, id: int, path: str):
        res = self.api.session.get(
            self._with_base_url(f"/{id}/content/{path.strip('/')}"), stream=True
        )
        self.api._raise_error(res)
        return res

    def put_content(self, id: int, path: str, file):
        return self.api.put(
            self._with_base_path(f"/{id}/content/{path.strip('/')}"),
            files={"file": file},
        )

    def delete_content(self, id: int, path: str):
        return self.api.delete(self._with_base_path(f"/{id}/content/{path.strip('/')}"))
