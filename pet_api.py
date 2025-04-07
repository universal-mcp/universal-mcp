from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration
from typing import Any, Dict, List

class SwaggerPetstoreOpenapi30App(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        """
        Initializes a new instance of a class, likely related to an application or service involving the Swagger Petstore OpenAPI 3.0 specification, and sets up the base URL for the API.
        
        Args:
            integration: An optional Integration object that provides integration-specific functionality or configuration.
            **kwargs: Additional keyword arguments that may be used for configuration or passing data to the superclass initializer.
        
        Returns:
            None. This is an initializer method that sets up the instance, but does not return a value.
        """
        super().__init__(name='swaggerpetstoreopenapi30app', integration=integration, **kwargs)
        self.base_url = "/api/v3"

    def petstore_update_pet(self, request_body) -> Dict[str, Any]:
        """
        Updates an existing pet in the pet store by sending a PUT request with the updated pet data in the request body.
        
        Args:
            self: The instance of the class to which this method belongs.
            request_body: A dictionary or JSON-serializable object containing the updated data for the pet.
        
        Returns:
            A dictionary containing the response data from the server after successfully updating the pet.
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
        Adds a new pet to the pet store by sending a POST request with the provided request body.
        
        Args:
            self: The instance of the class containing this method.
            request_body: A dictionary or JSON-serializable object representing the pet to be added.
        
        Returns:
            A dictionary containing the response data from the server, typically the details of the newly added pet.
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
        Retrieves a list of pet objects from the PetStore API based on their status (available, pending, or sold).
        
        Args:
            self: The instance of the class that this method belongs to.
            status: The status of the pets to retrieve. If not provided, pets of all statuses will be returned.
        
        Returns:
            A list of JSON objects representing the pet data retrieved from the API.
        """
        path_params = {}
        url = f"{self.base_url}/pet/findByStatus".format_map(path_params)
        query_params = {k: v for k, v in [('status', status)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_find_pets_by_tags(self, tags=None) -> List[Any]:
        """
        Finds pets by their tags using the Petstore API.
        
        Args:
            self: The Petstore API client instance.
            tags: A list of tags to filter pets by. If None, all pets are returned.
        
        Returns:
            A list of dictionaries representing the pets that match the specified tags.
        """
        path_params = {}
        url = f"{self.base_url}/pet/findByTags".format_map(path_params)
        query_params = {k: v for k, v in [('tags', tags)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_get_pet_by_id(self, petId) -> Dict[str, Any]:
        """
        Retrieves a pet from the pet store by its ID.
        
        Args:
            self: The instance of the class that the method belongs to.
            petId: The ID of the pet to retrieve.
        
        Returns:
            A dictionary containing the pet's information, or raises an exception if the pet ID is not provided or if the request fails.
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
        Updates an existing pet in the pet store by ID using form data.
        
        Args:
            self: The instance of the class containing this method.
            petId: The ID of the pet to be updated.
            name: (Optional) The new name for the pet.
            status: (Optional) The new status for the pet.
        
        Returns:
            A dictionary containing the updated pet data, or an error if the request failed.
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
        Deletes a pet from the store by its ID.
        
        Args:
            self: The instance of the class containing this method.
            petId: The ID of the pet to be deleted.
            api_key: Optional API key for authentication.
        
        Returns:
            A JSON response from the API server indicating the success or failure of the deletion operation.
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
        Uploads a file to a pet's record in the pet store API.
        
        Args:
            self: The instance of the API client class.
            petId: The ID of the pet to associate the file with.
            additionalMetadata: Optional additional metadata about the file being uploaded.
            request_body: The file content to be uploaded.
        
        Returns:
            A dictionary containing the response from the API server after uploading the file.
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
        Get the current inventory of the pet store.
        
        Args:
            self: An instance of the class that this method belongs to.
        
        Returns:
            A dictionary where the keys are the pet IDs and the values are the corresponding available quantities.
        """
        path_params = {}
        url = f"{self.base_url}/store/inventory".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_place_order(self, request_body=None) -> Dict[str, Any]:
        """
        Places a new order at the pet store.
        
        Args:
            self: An instance of the API client class.
            request_body: The request body containing the details of the order to be placed. Optional, can be None.
        
        Returns:
            A dictionary containing the response data from the API, including the details of the newly placed order.
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
        Retrieves an order from the pet store by its order ID.
        
        Args:
            self: The instance of the class that this method belongs to.
            orderId: The ID of the order to retrieve from the pet store.
        
        Returns:
            A dictionary containing the details of the requested order. The dictionary keys and values will depend on the structure of the order data returned by the pet store API.
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
        Deletes a pet store order by its unique identifier.
        
        Args:
            self: The instance object that the method is called on.
            orderId: The unique identifier of the order to be deleted.
        
        Returns:
            A JSON response from the API server containing information about the deleted order, or an error if the request was unsuccessful.
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
        Create a new user in the pet store by sending a POST request with the user data.
        
        Args:
            self: The instance of the class containing the base URL and HTTP methods.
            request_body: A dictionary or JSON-serializable object containing the data for the new user. If None, no request body is sent.
        
        Returns:
            A dictionary containing the response data from the server after creating the new user.
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
        Creates a batch of new user objects in the petstore.
        
        Args:
            self: An instance of the class containing this method.
            request_body: A list of user objects to be created. Each object should have fields like 'username', 'firstName', 'lastName', etc.
        
        Returns:
            A JSON response containing details about the newly created users.
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
        Authenticates a user with the given username and password in a pet store application.
        
        Args:
            self: The instance of the class containing this method.
            username: The username for the user to authenticate. Optional, can be None.
            password: The password for the user to authenticate. Optional, can be None.
        
        Returns:
            A JSON response containing authentication details or an error message if authentication fails.
        """
        path_params = {}
        url = f"{self.base_url}/user/login".format_map(path_params)
        query_params = {k: v for k, v in [('username', username), ('password', password)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_logout_user(self, ) -> Any:
        """
        Log out the current user from the petstore.
        
        Args:
            self: An instance of the API client class.
        
        Returns:
            A JSON response from the server indicating the logout status.
        """
        path_params = {}
        url = f"{self.base_url}/user/logout".format_map(path_params)
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def petstore_get_user_by_name(self, username) -> Dict[str, Any]:
        """
        Retrieves user information by username from the pet store API.
        
        Args:
            self: The instance of the class that this method belongs to.
            username: The username of the user to retrieve information for.
        
        Returns:
            A dictionary containing the user information retrieved from the API, or raises an exception if the username is not provided or if the API request fails.
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
        Updates the information of a user in the petstore.
        
        Args:
            self: The instance of the petstore client
            username: The name of the user to be updated
            request_body: The updated user information in JSON format (optional)
        
        Returns:
            The updated user information in JSON format, or an empty response if no content is returned
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
        Deletes a user from the petstore based on the provided username.
        
        Args:
            self: The instance of the class that the method belongs to.
            username: The username of the user to be deleted. This is a required parameter.
        
        Returns:
            The response from the server as a JSON object after successfully deleting the user. If the username is not provided, it raises a ValueError.
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
        Returns a list of all available API endpoints (tools) for interacting with the Petstore API.
        
        Args:
            self: The instance of the class containing the function.
        
        Returns:
            A list of methods representing the available API endpoints.
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
