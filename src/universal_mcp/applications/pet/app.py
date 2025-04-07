from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration
from typing import Any, Dict, List

class SwaggerPetstoreOpenapi30App(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        """
        Initialize an instance of a class with optional integration object and additional keyword arguments.
        
        Args:
            integration: An optional Integration object to be used for the class instance.
            **kwargs: Additional keyword arguments to be passed to the parent class during initialization.
        
        Returns:
            None. The function does not return any value.
        """
        super().__init__(name='swaggerpetstoreopenapi30app', integration=integration, **kwargs)
        self.base_url = "/api/v3"

    def petstore_update_pet(self, request_body) -> Dict[str, Any]:
        """
        Updates a pet resource in a pet store API by sending a PUT request with the updated pet data.
        
        Args:
            self: The instance of the class containing this method.
            request_body: A dictionary or object containing the updated pet data to be sent in the PUT request body.
        
        Returns:
            A dictionary containing the response data from the API after successfully updating the pet resource.
        """
        if request_body is None:
            raise ValueError("Missing required request body")
        path_params = {}
        url = f"{self.base_url}/pet".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._put(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_add_pet(self, request_body) -> Dict[str, Any]:
        """
        Adds a new pet to the pet store API.
        
        Args:
            self: The instance of the class that this method belongs to.
            request_body: A JSON object representing the new pet to be added, containing details such as name, species, age, etc.
        
        Returns:
            A dictionary containing the response from the API after adding the new pet, which may include details like the ID of the new pet, status codes, etc.
        """
        if request_body is None:
            raise ValueError("Missing required request body")
        path_params = {}
        url = f"{self.base_url}/pet".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_find_pets_by_status(self, status=None) -> List[Any]:
        """
        Retrieves a list of pets from the pet store API filtered by their status.
        
        Args:
            self: The instance of the class containing this method.
            status: The status value to filter pets by. If None, no filtering is applied.
        
        Returns:
            A list of dictionaries representing the pet objects matching the specified status filter.
        """
        path_params = {}
        url = f"{self.base_url}/pet/findByStatus".format_map(path_params)
        query_params = {k: v for k, v in [('status', status)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_find_pets_by_tags(self, tags=None) -> List[Any]:
        """
        Finds pets by their tags in a pet store API.
        
        Args:
            self: An instance of the class containing this method.
            tags: A list of tags to filter pets by. If None, all pets are returned.
        
        Returns:
            A list of dictionaries representing the pets matching the given tags.
        """
        path_params = {}
        url = f"{self.base_url}/pet/findByTags".format_map(path_params)
        query_params = {k: v for k, v in [('tags', tags)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_get_pet_by_id(self, petId) -> Dict[str, Any]:
        """
        Get a pet by its ID from the pet store.
        
        Args:
            self: An instance of the class containing this method.
            petId: The ID of the pet to retrieve.
        
        Returns:
            A dictionary containing the pet details, or raises an exception if the pet ID is not provided or if the request fails.
        """
        if petId is None:
            raise ValueError("Missing required parameter 'petId'")
        path_params = {'petId': petId}
        url = f"{self.base_url}/pet/{petId}".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_update_pet_with_form(self, petId, name=None, status=None) -> Dict[str, Any]:
        """
        Updates an existing pet in the pet store using a form request.
        
        Args:
            self: The instance of the class containing this method.
            petId: The ID of the pet to be updated.
            name: (Optional) The new name for the pet.
            status: (Optional) The new status for the pet.
        
        Returns:
            A dictionary containing the updated pet data.
        """
        if petId is None:
            raise ValueError("Missing required parameter 'petId'")
        path_params = {'petId': petId}
        url = f"{self.base_url}/pet/{petId}".format_map(path_params)
        query_params = {k: v for k, v in [('name', name), ('status', status)] if v is not None}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_delete_pet(self, petId, api_key=None) -> Any:
        """
        Deletes a pet from the pet store by ID.
        
        Args:
            self: The object instance
            petId: The ID of the pet to be deleted
            api_key: Optional API key for authentication (default is None)
        
        Returns:
            A JSON response from the server indicating the success or failure of the deletion operation
        """
        if petId is None:
            raise ValueError("Missing required parameter 'petId'")
        path_params = {'petId': petId}
        url = f"{self.base_url}/pet/{petId}".format_map(path_params)
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_upload_file(self, petId, additionalMetadata=None, request_body=None) -> Dict[str, Any]:
        """
        Uploads a file to the pet store for a specific pet identified by its ID.
        
        Args:
            self: The instance of the class containing this method.
            petId: The ID of the pet for which the file is being uploaded.
            additionalMetadata: Optional additional metadata related to the file being uploaded.
            request_body: Optional data to be included in the request body.
        
        Returns:
            A dictionary containing the response from the server after successfully uploading the file.
        """
        if petId is None:
            raise ValueError("Missing required parameter 'petId'")
        path_params = {'petId': petId}
        url = f"{self.base_url}/pet/{petId}/uploadImage".format_map(path_params)
        query_params = {k: v for k, v in [('additionalMetadata', additionalMetadata)] if v is not None}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_get_inventory(self, ) -> Dict[str, Any]:
        """
        Retrieves the inventory of pets available in the pet store.
        
        Args:
            self: The instance of the class containing this method.
        
        Returns:
            A dictionary containing the inventory of pets available in the pet store, where the keys are pet IDs and the values are the number of pets available for that ID.
        """
        path_params = {}
        url = f"{self.base_url}/store/inventory".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_place_order(self, request_body=None) -> Dict[str, Any]:
        """
        Places a new order at the petstore.
        
        Args:
            self: An instance of the class containing this method.
            request_body: The request body containing the details of the order to be placed. This is an optional parameter and can be None.
        
        Returns:
            A dictionary containing the response from the server after placing the order. The keys and values in the dictionary will depend on the response structure from the server.
        """
        path_params = {}
        url = f"{self.base_url}/store/order".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_get_order_by_id(self, orderId) -> Dict[str, Any]:
        """
        Retrieves order details from the pet store API by order ID.
        
        Args:
            self: The class instance object.
            orderId: The unique identifier of the order to retrieve.
        
        Returns:
            A dictionary containing the order details in JSON format, with keys representing different attributes of the order.
        """
        if orderId is None:
            raise ValueError("Missing required parameter 'orderId'")
        path_params = {'orderId': orderId}
        url = f"{self.base_url}/store/order/{orderId}".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_delete_order(self, orderId) -> Any:
        """
        Deletes a pet store order by its ID.
        
        Args:
            self: The instance of the class containing this method.
            orderId: The ID of the order to be deleted.
        
        Returns:
            A JSON response from the API indicating the success or failure of the operation.
        """
        if orderId is None:
            raise ValueError("Missing required parameter 'orderId'")
        path_params = {'orderId': orderId}
        url = f"{self.base_url}/store/order/{orderId}".format_map(path_params)
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_create_user(self, request_body=None) -> Dict[str, Any]:
        """
        Creates a new user in the petstore API.
        
        Args:
            self: The instance of the API client class.
            request_body: A dictionary or JSON-serializable object containing the details of the new user to be created. If omitted, the new user will be created with default values.
        
        Returns:
            A dictionary containing the response data from the API, which should include the details of the newly created user.
        """
        path_params = {}
        url = f"{self.base_url}/user".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_create_users_with_list_input(self, request_body=None) -> Dict[str, Any]:
        """
        Creates a batch of user objects in the petstore.
        
        Args:
            self: The instance of the API client class.
            request_body: A list of user objects to be created in the petstore.
        
        Returns:
            A dictionary containing the server's response, which may include details about the created users or any errors that occurred.
        """
        path_params = {}
        url = f"{self.base_url}/user/createWithList".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._post(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_login_user(self, username=None, password=None) -> Any:
        """
        Authenticates a user with the provided username and password in a pet store API.
        
        Args:
            self: An instance of the class containing this method.
            username: The username of the user to authenticate (optional).
            password: The password of the user to authenticate (optional).
        
        Returns:
            A JSON response from the API containing the authentication status and any additional data.
        """
        path_params = {}
        url = f"{self.base_url}/user/login".format_map(path_params)
        query_params = {k: v for k, v in [('username', username), ('password', password)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_logout_user(self, ) -> Any:
        """
        Logs out the current user from the pet store application.
        
        Args:
            self: The instance of the class the method belongs to.
        
        Returns:
            A JSON response from the server indicating the success or failure of the logout operation.
        """
        path_params = {}
        url = f"{self.base_url}/user/logout".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_get_user_by_name(self, username) -> Dict[str, Any]:
        """
        Retrieves information about a user from a pet store by their username.
        
        Args:
            self: The instance object for the class containing this method.
            username: The username of the user whose information needs to be retrieved. This is a required parameter.
        
        Returns:
            A dictionary containing the user information retrieved from the pet store API. The keys and values in the dictionary depend on the API response format.
        """
        if username is None:
            raise ValueError("Missing required parameter 'username'")
        path_params = {'username': username}
        url = f"{self.base_url}/user/{username}".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_update_user(self, username, request_body=None) -> Any:
        """
        Updates an existing user in a pet store system.
        
        Args:
            self: The instance of the class containing this method.
            username: The username of the user to be updated.
            request_body: An optional request body containing the updated user data. If not provided, the existing user data will be used.
        
        Returns:
            A JSON response containing the updated user data.
        """
        if username is None:
            raise ValueError("Missing required parameter 'username'")
        path_params = {'username': username}
        url = f"{self.base_url}/user/{username}".format_map(path_params)
        query_params = {}
        json_body = request_body if request_body is not None else None
        response = self._put(url, data=json_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_delete_user(self, username) -> Any:
        """
        Deletes a user from the petstore API by their username.
        
        Args:
            self: An instance of the API client class.
            username: The username of the user to be deleted.
        
        Returns:
            A JSON response from the API indicating the success or failure of the delete operation.
        """
        if username is None:
            raise ValueError("Missing required parameter 'username'")
        path_params = {'username': username}
        url = f"{self.base_url}/user/{username}".format_map(path_params)
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        """
        Returns a list of functions related to managing pets, orders, and users in a pet store API.
        
        Args:
            self: An instance of the class containing the listed functions
        
        Returns:
            A list of function references related to managing pets, orders, and users in the pet store API.
        """
        return [
            self.petstore_update_pet,
            self.petstore_add_pet,
            self.petstore_find_pets_by_status,
            self.petstore_find_pets_by_tags,
            self.petstore_get_pet_by_id,
            self.petstore_update_pet_with_form,
            self.petstore_delete_pet,
            self.petstore_upload_file,
            self.petstore_get_inventory,
            self.petstore_place_order,
            self.petstore_get_order_by_id,
            self.petstore_delete_order,
            self.petstore_create_user,
            self.petstore_create_users_with_list_input,
            self.petstore_login_user,
            self.petstore_logout_user,
            self.petstore_get_user_by_name,
            self.petstore_update_user,
            self.petstore_delete_user
        ]
