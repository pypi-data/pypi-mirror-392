import requests
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder as FormData

class DeepJSONError(Exception):
    def __init__(self, message, status=None, details=None):
        super().__init__(message)
        self.status = status
        self.details = details

class DeepJSONConnector:
    def __init__(self, config):
        self.base_url = config.get('base_url')
        self.token = config.get('token')
        self.storage = config.get('storage', 'memory')
        
        # Transmission options
        self.binary = False
        self.overwrite_key = False
        self.get_body = False
        
        # Configure session
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'DeepJSONConnector/1.0'
        })
        self.timeout = config.get('timeout', 10.0)

    # Authentication methods
    def login(self, username, password):
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={'username': username, 'password': password},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            self.token = data.get('token')
            return data
        except requests.RequestException as error:
            self._handle_error(error)

    def get_token(self):
        return self.token

    def is_binary(self):
        return self.binary

    def set_binary(self, true_or_false):
        self.binary = true_or_false
        return self

    def is_overwrite_key(self):
        return self.overwrite_key

    def set_overwrite_key(self, true_or_false):
        self.overwrite_key = true_or_false
        return self

    def has_get_body(self):
        return self.get_body

    def set_get_body(self, true_or_false):
        self.get_body = true_or_false
        return self

    # Core CRUD operations
    def get(self, key, value = '', script = None):
        headers = {}
        params = {}
        http_method = "GET"
        if self.get_body:
            headers['X-Method-Override'] = "GET"
            http_method = "POST"
        if self.binary:
            params['binary'] = True
            # params['token'] = self.token
        return self._request(http_method, f"/keys/{key}", params=params, data=value, headers=headers, script=script)

    def post(self, key, value, script = None):
        headers = {}
        if self.overwrite_key:
            headers['X-Override-Existing'] = 'true'
        return self._request('POST', f"/keys/{key}", data=value, headers=headers, script=script)

    def put(self, key, value, script = None):
        headers = {}
        return self._request('PUT', f"/keys/{key}", data=value, headers=headers, script=script)

    def delete(self, key):
        headers = {}
        return self._request('DELETE', f"/keys/{key}", headers=headers)

    def move(self, old_key, new_key):
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        data = json.dumps({
            "from": old_key,
            "to": new_key
        })
        return self._request('POST', "/cmd/move", data=data, headers=headers)

    # Universal file upload
    def upload_file(self, key, file, options={}):
        form = FormData(fields={
            'file': (file.name, file, 'application/octet-stream')
        })
        headers = {
            'Content-Type': form.content_type,
            'X-Override-Existing': 'true' if options.get('overwrite') else 'false'
        }
        return self._request('POST', f"/keys/{key}", data=form, headers=headers)

    # Admin methods
    def list_keys(self, filters):
        return self._request('GET', '/admin/keys', params=filters)

    # Private methods
    def _request(self, method, path, params=None, data=None, headers=None, script=None):
        try:
            headers = headers or {}
            if script and len(script) > 0:                
                data_json = ""
                if data:
                    data_json = data if isinstance(data, str) else json.dumps(data, indent=2)
                data = f"javascript:\n{script.strip()}\n\njavascript!\n\n{data_json}"
                headers["Content-Type"] = "text/plain; charset=utf-8"
            else:
                if data is not None and not isinstance(data, str):
                    data = json.dumps(data)
                headers["Content-Type"] = headers.get("Content-Type", "text/plain")

            request_headers = {
                **headers,
                **({'Authorization': f"Bearer {self.token}"} if self.token else {})
            }

            response = self.session.request(
                method=method,
                url=f"{self.base_url}{path}",
                params=params or {},
                data=data,
                headers=request_headers,
                timeout=self.timeout
            )

            response.raise_for_status()

            result = response.content if self.binary else response.json()
            self._reset_flags()
            return result

        except requests.RequestException as error:
            self._handle_error(error)

    def _reset_flags(self):
        self.binary = False
        self.overwrite_key = False
        self.get_body = False

    def _handle_error(self, error: requests.RequestException):
        status = None
        details = None
        message = str(error)

        if hasattr(error, 'response') and error.response is not None:
            try:
                status = error.response.status_code
                response_text = error.response.text

                try:
                    details = error.response.json()
                except ValueError:
                    details = response_text

                message = (f"API Error: {status} {error.response.reason}\n"
                            f"Response: {response_text[:500]}")
            except Exception as nested:
                message = f"Error processing response: {nested}\nOriginal: {message}"

        raise DeepJSONError(message, status, details)