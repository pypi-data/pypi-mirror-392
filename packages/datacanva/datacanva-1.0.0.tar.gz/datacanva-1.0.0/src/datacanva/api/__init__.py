import requests


class Api:

    def __init__(self, base_url: str, api_key: str):
        if not base_url:
            raise Exception("Required argument 'base_url' is not provided.")

        if not api_key:
            raise Exception("Required argument 'api_key' is not provided.")

        self.base_url = base_url
        self.api_key = api_key

        self.session = requests.Session()
        self.session.headers.update({"X-Api-Key": api_key})

    def get(self, path: str, **args):
        return self._handle_response(
            self.session.get(self._with_base_url(path), **args)
        )

    def put(self, path: str, **args):
        return self._handle_response(
            self.session.put(self._with_base_url(path), **args)
        )

    def post(self, path: str, **args):
        return self._handle_response(
            self.session.post(self._with_base_url(path), **args)
        )

    def delete(self, path: str):
        return self._handle_response(self.session.delete(self._with_base_url(path)))

    def _with_base_url(self, path: str):
        return f"{self.base_url}/{path.lstrip('/')}"

    def _handle_response(self, res: requests.Response):
        body: dict[str, any] | None = None
        try:
            if res.text:
                body = res.json()
        except:
            raise Exception(
                f"Response body is not a valid JSON value ({res.status_code}): {res.text}"
            )
        self._raise_error(res, body)
        return body

    def _raise_error(self, res: requests.Response, json: dict[str, any] = None):
        if res.status_code != 200:
            body = json if json is not None else res.json()
            raise Exception(f"({res.status_code}) {body['message']}")



class CrudApi:

    def __init__(self, api: Api, base_path: str):
        self.api = api
        self.base_path = base_path

    def get_list(self, params={}):
        return self.api.get(self._with_base_path(), params=params)

    def get(self, id: int):
        return self.api.get(self._with_base_path(f"{id}"))

    def post(self, item):
        return self.api.post(self._with_base_path(), json=item)

    def put(self, id: int, item):
        return self.api.put(self._with_base_path(f"{id}"), item)

    def delete(self, id: int):
        return self.api.delete(self._with_base_path(f"{id}"))

    def _with_base_path(self, path: str = ""):
        return f"{self.base_path}/{path.lstrip('/')}".rstrip("/")

    def _with_base_url(self, path: str = ""):
        return self.api._with_base_url(self._with_base_path(path))
