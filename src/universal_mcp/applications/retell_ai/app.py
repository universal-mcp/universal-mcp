from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class RetellAiApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="retell-ai", integration=integration, **kwargs)
        self.base_url = "https://api.retellai.com"

    def get_v2_get_call_by_call_id(self, call_id) -> dict[str, Any]:
        """
        Retrieve detailed information about a specific call using its call ID.

        Args:
            call_id: The unique identifier of the call to retrieve. Must not be None.

        Returns:
            A dictionary containing the details of the requested call as returned by the API.

        Raises:
            ValueError: If the 'call_id' parameter is None.
            HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            get, call, api, important
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call_id'")
        url = f"{self.base_url}/v2/get-call/{call_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_v2_create_phone_call(
        self,
        from_number,
        to_number,
        override_agent_id=None,
        metadata=None,
        retell_llm_dynamic_variables=None,
    ) -> dict[str, Any]:
        """
        Initiates a phone call using a JSON payload with specified parameters.

        Args:
            from_number: The source number for the call.
            to_number: The destination number for the call.
            override_agent_id: Optional ID for overriding the default agent.
            metadata: Optional metadata to be included with the call request.
            retell_llm_dynamic_variables: Optional dynamic variables for LLM (Large Language Model) processing.

        Returns:
            A dictionary containing the response data for the created phone call.

        Raises:
            ValueError: Raised if either 'from_number' or 'to_number' is missing.

        Tags:
            initiate, create-call, async_job, management, important
        """
        if from_number is None:
            raise ValueError("Missing required parameter 'from_number'")
        if to_number is None:
            raise ValueError("Missing required parameter 'to_number'")
        request_body = {
            "from_number": from_number,
            "to_number": to_number,
            "override_agent_id": override_agent_id,
            "metadata": metadata,
            "retell_llm_dynamic_variables": retell_llm_dynamic_variables,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/create-phone-call"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_v2_create_web_call(
        self, agent_id, metadata=None, retell_llm_dynamic_variables=None
    ) -> dict[str, Any]:
        """
        Creates a web call via a POST request to the v2 endpoint with specified agent ID and optional metadata or dynamic variables.

        Args:
            agent_id: Required identifier of the agent initiating the web call.
            metadata: Optional metadata to include in the web call request.
            retell_llm_dynamic_variables: Optional dynamic variables for LLN model customization.

        Returns:
            A dictionary containing the response details from the web call creation request.

        Raises:
            ValueError: Raised when the required 'agent_id' parameter is missing.

        Tags:
            create, web-calls, api-call, important
        """
        if agent_id is None:
            raise ValueError("Missing required parameter 'agent_id'")
        request_body = {
            "agent_id": agent_id,
            "metadata": metadata,
            "retell_llm_dynamic_variables": retell_llm_dynamic_variables,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/create-web-call"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_get_voice_by_voice_id(self, voice_id) -> dict[str, Any]:
        """
        Fetches voice details based on the provided voice ID.

        Args:
            voice_id: The unique identifier of the voice to retrieve.

        Returns:
            A dictionary containing voice details.

        Raises:
            ValueError: Raised when the 'voice_id' parameter is missing or None.

        Tags:
            retrieve, voice, important, data-fetched
        """
        if voice_id is None:
            raise ValueError("Missing required parameter 'voice_id'")
        url = f"{self.base_url}/get-voice/{voice_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_v2_list_calls(
        self, filter_criteria=None, sort_order=None, limit=None, pagination_key=None
    ) -> list[Any]:
        """
        Sends a POST request to list call records with optional filtering, sorting, pagination, and limits.

        Args:
            filter_criteria: Optional dictionary specifying filter conditions for returned call records.
            sort_order: Optional sorting instructions (e.g., by date or status) for the call records.
            limit: Optional integer specifying the maximum number of call records to return.
            pagination_key: Optional key indicating where to continue fetching records for paginated results.

        Returns:
            A list of call record objects returned from the API.

        Raises:
            HTTPError: If the HTTP request to the remote service fails or returns an error status code.

        Tags:
            list, calls, api, batch, management, important
        """
        request_body = {
            "filter_criteria": filter_criteria,
            "sort_order": sort_order,
            "limit": limit,
            "pagination_key": pagination_key,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/list-calls"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_create_phone_number(
        self, area_code, inbound_agent_id=None, outbound_agent_id=None, nickname=None
    ) -> dict[str, Any]:
        """
        Creates a phone number with the specified area code and optional parameters.

        Args:
            area_code: The area code for the phone number (required).
            inbound_agent_id: The ID of the agent to handle inbound calls (optional).
            outbound_agent_id: The ID of the agent to handle outbound calls (optional).
            nickname: A user-friendly name for the phone number (optional).

        Returns:
            A dictionary containing the created phone number details and any associated metadata.

        Raises:
            ValueError: When the required parameter 'area_code' is None or not provided.
            HTTPError: When the API request fails with an error status code.

        Tags:
            create, phone, post, communication, important
        """
        if area_code is None:
            raise ValueError("Missing required parameter 'area_code'")
        request_body = {
            "inbound_agent_id": inbound_agent_id,
            "outbound_agent_id": outbound_agent_id,
            "area_code": area_code,
            "nickname": nickname,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/create-phone-number"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_get_phone_number_by_phone_number(self, phone_number) -> dict[str, Any]:
        """
        Retrieves phone number details by making a GET request to the API endpoint using the provided phone number.

        Args:
            phone_number: str. The phone number to look up. Must not be None.

        Returns:
            dict[str, Any]: A dictionary containing the details associated with the given phone number as returned by the API.

        Raises:
            ValueError: If the 'phone_number' parameter is None.
            requests.HTTPError: If the HTTP request fails or an error response is returned from the API.

        Tags:
            get, phone-number, api, lookup, important
        """
        if phone_number is None:
            raise ValueError("Missing required parameter 'phone_number'")
        url = f"{self.base_url}/get-phone-number/{phone_number}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_list_phone_numbers(
        self,
    ) -> list[Any]:
        """
        Retrieves a list of phone numbers from the remote API.

        Args:
            None: This function takes no arguments

        Returns:
            A list containing the phone numbers returned by the API.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            get, list, phone-numbers, api, synchronous, important
        """
        url = f"{self.base_url}/list-phone-numbers"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def patch_update_phone_number_by_phone_number(
        self, phone_number, inbound_agent_id=None, outbound_agent_id=None, nickname=None
    ) -> dict[str, Any]:
        """
        Updates the information of a phone number by its number, allowing optional modification of inbound and outbound agent IDs and nickname.

        Args:
            phone_number: str. The phone number to update. This parameter is required.
            inbound_agent_id: Optional[str]. The ID of the inbound agent to associate with the phone number. If None, this field will not be updated.
            outbound_agent_id: Optional[str]. The ID of the outbound agent to associate with the phone number. If None, this field will not be updated.
            nickname: Optional[str]. The nickname to assign to the phone number. If None, this field will not be updated.

        Returns:
            dict[str, Any]: A dictionary containing the updated phone number information as returned by the API.

        Raises:
            ValueError: If the required parameter 'phone_number' is not provided.
            requests.HTTPError: If the HTTP PATCH request fails or the response has an error status.

        Tags:
            update, phone-number, api, patch, management
        """
        if phone_number is None:
            raise ValueError("Missing required parameter 'phone_number'")
        request_body = {
            "inbound_agent_id": inbound_agent_id,
            "outbound_agent_id": outbound_agent_id,
            "nickname": nickname,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/update-phone-number/{phone_number}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_delete_phone_number_by_phone_number(self, phone_number) -> Any:
        """
        Deletes a phone number resource by its phone number identifier via an HTTP DELETE request.

        Args:
            phone_number: The phone number (str or compatible type) identifying the resource to be deleted.

        Returns:
            The server's JSON response as a Python object upon successful deletion.

        Raises:
            ValueError: If 'phone_number' is None.
            requests.HTTPError: If the HTTP DELETE request results in an error status code.

        Tags:
            delete, phone-number, api, management, important
        """
        if phone_number is None:
            raise ValueError("Missing required parameter 'phone_number'")
        url = f"{self.base_url}/delete-phone-number/{phone_number}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.get_v2_get_call_by_call_id,
            self.post_v2_create_phone_call,
            self.post_v2_create_web_call,
            self.get_get_voice_by_voice_id,
            self.post_v2_list_calls,
            self.post_create_phone_number,
            self.get_get_phone_number_by_phone_number,
            self.get_list_phone_numbers,
            self.patch_update_phone_number_by_phone_number,
            self.delete_delete_phone_number_by_phone_number,
        ]
