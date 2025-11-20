import json
import requests
from rb_commons.http.exceptions import BadRequestException, InternalException
from requests import RequestException

class BaseAPI:
    def __init__(self, base_url: str):
        self.BASE_URL = base_url

    def _make_request(self, method: str,
        path: str,  data: dict | list = None,
        params: dict = None, headers: dict = None,
        reset_base_url: bool = False, form_encoded: bool = False,
    ) -> requests.Response:
        url = self.BASE_URL + path
        if reset_base_url:
            url = path

        try:
            request_methods = {
                "POST": requests.post,
                "GET": requests.get,
                "PUT": requests.put,
                "DELETE": requests.delete,
            }

            if method not in request_methods:
                raise BadRequestException(f"Unsupported HTTP method: {method}")

            headers = dict(headers or {})

            if form_encoded:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                kwargs = {
                    "params": params,
                    "headers": headers,
                    "data": data,
                }
            else:
                headers["Content-Type"] = "application/json"
                kwargs = {
                    "params": params,
                    "headers": headers,
                    "json": data
                }

            response = request_methods[method](url, **kwargs)

            try:
                if response.text.strip():
                    data = response.json()
                else:
                    data = {}
            except ValueError:
                error_message = response.text
                raise BadRequestException(
                    "Invalid JSON response",
                    additional_info={"error_message": error_message},
                )

            if not (200 <= response.status_code < 300):
                error_message = data.get("message") or data.get("detail") or response.text
                raise BadRequestException(
                    "Unexpected error occured",
                    additional_info={"error_message": error_message},
                )

            return response

        except RequestException as e:
            raise BadRequestException(
                f"Request exception: {str(e)}",
                additional_info={"error_message": str(e)},
            )
        except BadRequestException:
            raise
        except (json.JSONDecodeError, ValueError) as e:
            raise InternalException(f"Failed to parse JSON: {str(e)}")
        except Exception as e:
            raise InternalException(f"Unhandled error: {str(e)}")

    def _post(self, path: str, data: dict | list, headers: dict = None, params: dict = None,
              reset_base_url: bool = False, form_encoded: bool = False) -> requests.Response:
        return self._make_request('POST', path, data=data, headers=headers, params=params,
                                  reset_base_url=reset_base_url, form_encoded=form_encoded)

    def _get(self, path: str, params: dict = None, headers: dict = None, reset_base_url: bool = False, form_encoded: bool = False) -> requests.Response:
        return self._make_request('GET', path, params=params, headers=headers, reset_base_url=reset_base_url, form_encoded=form_encoded)

    def _put(self, path: str, params: dict = None, data: dict = None, headers: dict = None, reset_base_url: bool = False, form_encoded: bool = False) -> requests.Response:
        return self._make_request('PUT', path, params=params, data=data, headers=headers, reset_base_url=reset_base_url, form_encoded=form_encoded)

    def _delete(self, path: str, headers: dict = None, reset_base_url: bool = False, form_encoded: bool = False) -> requests.Response:
        return self._make_request('DELETE', path, headers=headers, reset_base_url=reset_base_url, form_encoded=form_encoded)
