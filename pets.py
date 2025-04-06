from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration
from typing import Any, Dict, List

class SwaggerPetstoreOpenapi30App(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name='swaggerpetstoreopenapi30app', integration=integration, **kwargs)
        self.base_url = "/api/v3"

    def update_pet(self, request_body) -> Dict[str, Any]:
        if request_body is None:
            raise ValueError("Missing required request body")
        path_params = {}
        url = f"{self.base_url}/pet".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._put(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_pet(self, request_body) -> Dict[str, Any]:
        if request_body is None:
            raise ValueError("Missing required request body")
        path_params = {}
        url = f"{self.base_url}/pet".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def find_pets_by_status(self, status=None) -> List[Any]:
        path_params = {}
        url = f"{self.base_url}/pet/findByStatus".format_map(path_params)
        query_params = {k: v for k, v in [('status', status)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def find_pets_by_tags(self, tags=None) -> List[Any]:
        path_params = {}
        url = f"{self.base_url}/pet/findByTags".format_map(path_params)
        query_params = {k: v for k, v in [('tags', tags)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_pet_by_id(self, petId) -> Dict[str, Any]:
        if petId is None:
            raise ValueError("Missing required parameter 'petId'")
        path_params = {'petId': petId}
        url = f"{self.base_url}/pet/{petId}".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_pet_with_form(self, petId, name=None, status=None) -> Dict[str, Any]:
        if petId is None:
            raise ValueError("Missing required parameter 'petId'")
        path_params = {'petId': petId}
        url = f"{self.base_url}/pet/{petId}".format_map(path_params)
        query_params = {k: v for k, v in [('name', name), ('status', status)] if v is not None}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_pet(self, petId, api_key=None) -> Any:
        if petId is None:
            raise ValueError("Missing required parameter 'petId'")
        path_params = {'petId': petId}
        url = f"{self.base_url}/pet/{petId}".format_map(path_params)
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def upload_file(self, petId, additionalMetadata=None, request_body=None) -> Dict[str, Any]:
        if petId is None:
            raise ValueError("Missing required parameter 'petId'")
        path_params = {'petId': petId}
        url = f"{self.base_url}/pet/{petId}/uploadImage".format_map(path_params)
        query_params = {k: v for k, v in [('additionalMetadata', additionalMetadata)] if v is not None}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_inventory(self, ) -> Dict[str, Any]:
        path_params = {}
        url = f"{self.base_url}/store/inventory".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def place_order(self, request_body=None) -> Dict[str, Any]:
        path_params = {}
        url = f"{self.base_url}/store/order".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_order_by_id(self, orderId) -> Dict[str, Any]:
        if orderId is None:
            raise ValueError("Missing required parameter 'orderId'")
        path_params = {'orderId': orderId}
        url = f"{self.base_url}/store/order/{orderId}".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_order(self, orderId) -> Any:
        if orderId is None:
            raise ValueError("Missing required parameter 'orderId'")
        path_params = {'orderId': orderId}
        url = f"{self.base_url}/store/order/{orderId}".format_map(path_params)
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_user(self, request_body=None) -> Dict[str, Any]:
        path_params = {}
        url = f"{self.base_url}/user".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_users_with_list_input(self, request_body=None) -> Dict[str, Any]:
        path_params = {}
        url = f"{self.base_url}/user/createWithList".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def login_user(self, username=None, password=None) -> Any:
        path_params = {}
        url = f"{self.base_url}/user/login".format_map(path_params)
        query_params = {k: v for k, v in [('username', username), ('password', password)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def logout_user(self, ) -> Any:
        path_params = {}
        url = f"{self.base_url}/user/logout".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_user_by_name(self, username) -> Dict[str, Any]:
        if username is None:
            raise ValueError("Missing required parameter 'username'")
        path_params = {'username': username}
        url = f"{self.base_url}/user/{username}".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_user(self, username, request_body=None) -> Any:
        if username is None:
            raise ValueError("Missing required parameter 'username'")
        path_params = {'username': username}
        url = f"{self.base_url}/user/{username}".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._put(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_user(self, username) -> Any:
        if username is None:
            raise ValueError("Missing required parameter 'username'")
        path_params = {'username': username}
        url = f"{self.base_url}/user/{username}".format_map(path_params)
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.update_pet,
            self.add_pet,
            self.find_pets_by_status,
            self.find_pets_by_tags,
            self.get_pet_by_id,
            self.update_pet_with_form,
            self.delete_pet,
            self.upload_file,
            self.get_inventory,
            self.place_order,
            self.get_order_by_id,
            self.delete_order,
            self.create_user,
            self.create_users_with_list_input,
            self.login_user,
            self.logout_user,
            self.get_user_by_name,
            self.update_user,
            self.delete_user
        ]

