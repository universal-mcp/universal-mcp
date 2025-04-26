from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class ElevenlabsApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name='elevenlabs', integration=integration, **kwargs)
        self.base_url = "https://api.elevenlabs.io"

    def _get_headers(self) -> dict[str, Any]:
        api_key = self.integration.get_credentials().get("api_key")
        return {
            "xi-api-key": f"{api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get_generated_items_v1_history_get(self, page_size=None, start_after_history_item_id=None, voice_id=None) -> dict[str, Any]:
        """
        Retrieves a paginated history of generated items from the API, optionally filtered by page size, starting history item, or voice ID.
        
        Args:
            page_size: Optional; int. The maximum number of history items to return in one response.
            start_after_history_item_id: Optional; str. The ID of the history item after which to start retrieving results, used for pagination.
            voice_id: Optional; str. If specified, filters the history items to those generated using the given voice ID.
        
        Returns:
            dict[str, Any]: A dictionary representing the parsed JSON response containing the list of generated history items and associated metadata.
        
        Raises:
            requests.HTTPError: If the HTTP request to the API fails or an error status code is returned.
        
        Tags:
            get, history, list, api
        """
        url = f"{self.base_url}/v1/history"
        query_params = {k: v for k, v in [('page_size', page_size), ('start_after_history_item_id', start_after_history_item_id), ('voice_id', voice_id)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_history_item_by_id_v1_history__history_item_id__get(self, history_item_id) -> dict[str, Any]:
        """
        Retrieves a specific history item by its unique identifier.
        
        Args:
            history_item_id: str. The unique identifier of the history item to retrieve.
        
        Returns:
            dict. A dictionary containing the details of the requested history item.
        
        Raises:
            ValueError: Raised if 'history_item_id' is None.
            HTTPError: Raised if the HTTP request to retrieve the history item fails.
        
        Tags:
            get, history, item, fetch, api
        """
        if history_item_id is None:
            raise ValueError("Missing required parameter 'history_item_id'")
        url = f"{self.base_url}/v1/history/{history_item_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_history_item_v1_history__history_item_id__delete(self, history_item_id) -> Any:
        """
        Deletes a specific history item by its unique identifier.
        
        Args:
            history_item_id: str. The unique identifier of the history item to delete.
        
        Returns:
            dict. The JSON response from the API after deleting the history item.
        
        Raises:
            ValueError: If 'history_item_id' is None.
            requests.HTTPError: If the HTTP request to delete the history item fails.
        
        Tags:
            delete, history, management, v1
        """
        if history_item_id is None:
            raise ValueError("Missing required parameter 'history_item_id'")
        url = f"{self.base_url}/v1/history/{history_item_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_audio_from_history_item_v1_history__history_item_id__audio_get(self, history_item_id) -> Any:
        """
        Retrieves the audio data associated with a specific history item by its unique identifier.
        
        Args:
            history_item_id: str. The unique identifier of the history item whose audio data is to be retrieved.
        
        Returns:
            dict. The audio data for the specified history item, parsed from the JSON response.
        
        Raises:
            ValueError: If the 'history_item_id' parameter is None.
            requests.HTTPError: If the HTTP request to retrieve audio data fails (e.g., non-2xx status code).
        
        Tags:
            get, audio, history
        """
        if history_item_id is None:
            raise ValueError("Missing required parameter 'history_item_id'")
        url = f"{self.base_url}/v1/history/{history_item_id}/audio"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def download_history_items_v1_history_download_post(self, history_item_ids, output_format=None) -> Any:
        """
        Downloads specified history items in the given output format via a POST request.
        
        Args:
            history_item_ids: List of identifiers for the history items to download. Must not be None.
            output_format: Optional; specifies the desired output format for the downloaded data (e.g., 'json', 'csv'). If not provided, a default format is used.
        
        Returns:
            A JSON-decoded response containing the downloaded history items in the requested format.
        
        Raises:
            ValueError: If 'history_item_ids' is None.
            HTTPError: If the HTTP request to the API fails or returns an error response.
        
        Tags:
            download, history, post, api
        """
        if history_item_ids is None:
            raise ValueError("Missing required parameter 'history_item_ids'")
        request_body = {
            'history_item_ids': history_item_ids,
            'output_format': output_format,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/history/download"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_sample_v1_voices__voice_id__samples__sample_id__delete(self, voice_id, sample_id) -> Any:
        """
        Deletes a specific voice sample identified by voice_id and sample_id from the API.
        
        Args:
            voice_id: str. The unique identifier for the voice whose sample is to be deleted.
            sample_id: str. The unique identifier for the sample to be deleted.
        
        Returns:
            dict. The JSON response from the API after successful deletion of the sample.
        
        Raises:
            ValueError: Raised if either 'voice_id' or 'sample_id' is None.
            requests.HTTPError: Raised if the API response contains an HTTP error status.
        
        Tags:
            delete, voice, sample, api
        """
        if voice_id is None:
            raise ValueError("Missing required parameter 'voice_id'")
        if sample_id is None:
            raise ValueError("Missing required parameter 'sample_id'")
        url = f"{self.base_url}/v1/voices/{voice_id}/samples/{sample_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_audio_from_sample_v1_voices__voice_id__samples__sample_id__audio_get(self, voice_id, sample_id) -> Any:
        """
        Retrieves audio data for a specific sample from a given voice using provided identifiers.
        
        Args:
            voice_id: The unique identifier of the voice whose sample audio is to be retrieved.
            sample_id: The unique identifier of the sample whose audio data is requested.
        
        Returns:
            A JSON-decoded object containing the audio data and metadata for the specified sample.
        
        Raises:
            ValueError: Raised if 'voice_id' or 'sample_id' is None.
            requests.HTTPError: Raised if the HTTP request to fetch the audio fails with a non-2xx status code.
        
        Tags:
            get, audio, sample, voice, api
        """
        if voice_id is None:
            raise ValueError("Missing required parameter 'voice_id'")
        if sample_id is None:
            raise ValueError("Missing required parameter 'sample_id'")
        url = f"{self.base_url}/v1/voices/{voice_id}/samples/{sample_id}/audio"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def text_to_speech_v1_text_to_speech__voice_id__post(self, voice_id, text, optimize_streaming_latency=None, output_format=None, model_id=None, voice_settings=None, pronunciation_dictionary_locators=None, seed=None) -> Any:
        """
        Converts input text to speech using the specified voice configuration via a POST request to the text-to-speech API endpoint.
        
        Args:
            voice_id: str. The identifier of the voice to use for speech synthesis.
            text: str. The input text to be converted into speech.
            optimize_streaming_latency: Optional[int]. Controls streaming latency optimization; lower values may reduce initial playback delay.
            output_format: Optional[str]. Specifies the format of the returned audio (e.g., 'mp3', 'wav').
            model_id: Optional[str]. Identifier for the specific speech synthesis model to use.
            voice_settings: Optional[dict]. Additional settings for the selected voice, such as pitch or speed.
            pronunciation_dictionary_locators: Optional[list]. List of pronunciation dictionary locators to apply custom pronunciations.
            seed: Optional[int]. Seed value for deterministic speech synthesis output.
        
        Returns:
            dict. The JSON-decoded API response containing synthesized audio information or relevant metadata.
        
        Raises:
            ValueError: If 'voice_id' or 'text' is not provided.
            requests.HTTPError: If the HTTP request to the text-to-speech API fails or returns an unsuccessful status.
        
        Tags:
            text-to-speech, convert, api, voice, synthesis, ai, batch
        """
        if voice_id is None:
            raise ValueError("Missing required parameter 'voice_id'")
        if text is None:
            raise ValueError("Missing required parameter 'text'")
        request_body = {
            'text': text,
            'model_id': model_id,
            'voice_settings': voice_settings,
            'pronunciation_dictionary_locators': pronunciation_dictionary_locators,
            'seed': seed,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/text-to-speech/{voice_id}"
        query_params = {k: v for k, v in [('optimize_streaming_latency', optimize_streaming_latency), ('output_format', output_format)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def text_to_speech_v1_text_to_speech__voice_id__stream_post(self, voice_id, text, optimize_streaming_latency=None, output_format=None, model_id=None, voice_settings=None, pronunciation_dictionary_locators=None, seed=None) -> Any:
        """
        Streams synthesized speech audio for given text using a specified voice ID and customizable options.
        
        Args:
            voice_id: str. The unique identifier for the voice to synthesize speech with. Required.
            text: str. The input text to be converted to speech. Required.
            optimize_streaming_latency: Optional[int]. Optimization level for audio streaming latency. If provided, adjusts streaming performance.
            output_format: Optional[str]. Desired audio output format (e.g., 'mp3', 'wav').
            model_id: Optional[str]. Specific speech synthesis model ID to use.
            voice_settings: Optional[dict]. Additional settings for the selected voice (e.g., pitch, speed).
            pronunciation_dictionary_locators: Optional[List[str]]. List of pronunciation dictionary locators for custom pronunciations.
            seed: Optional[int]. Random seed for generating non-deterministic voice outputs.
        
        Returns:
            dict. The API's JSON response containing metadata about the speech synthesis stream and possibly streaming URLs or audio data.
        
        Raises:
            ValueError: Raised if 'voice_id' or 'text' is not provided.
            requests.HTTPError: Raised if the API request fails with an HTTP error response.
        
        Tags:
            text-to-speech, stream, ai, synthesize, voice, api
        """
        if voice_id is None:
            raise ValueError("Missing required parameter 'voice_id'")
        if text is None:
            raise ValueError("Missing required parameter 'text'")
        request_body = {
            'text': text,
            'model_id': model_id,
            'voice_settings': voice_settings,
            'pronunciation_dictionary_locators': pronunciation_dictionary_locators,
            'seed': seed,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/text-to-speech/{voice_id}/stream"
        query_params = {k: v for k, v in [('optimize_streaming_latency', optimize_streaming_latency), ('output_format', output_format)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def voice_generation_parameters_v1_voice_generation_generate_voice_parameters_get(self, ) -> dict[str, Any]:
        """
        Retrieves available parameter options for voice generation from the API.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A dictionary containing supported parameters and options for the voice generation endpoint.
        
        Raises:
            requests.HTTPError: If the HTTP request to the API fails or an error response is returned.
        
        Tags:
            fetch, parameters, voice-generation, api
        """
        url = f"{self.base_url}/v1/voice-generation/generate-voice/parameters"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def generate_a_random_voice_v1_voice_generation_generate_voice_post(self, gender, accent, age, accent_strength, text) -> Any:
        """
        Generates a synthetic voice audio based on specified demographics and text input by sending a POST request to the voice generation API.
        
        Args:
            gender: str. The gender for the generated voice (e.g., 'male', 'female'). Required.
            accent: str. The accent to apply to the synthesized voice (e.g., 'british', 'american'). Required.
            age: str or int. The age or age group for the generated voice. Required.
            accent_strength: str or float. The intensity of the accent in the output voice. Required.
            text: str. The text to be converted into synthetic speech. Required.
        
        Returns:
            dict. The JSON response containing the generated voice data and any related metadata.
        
        Raises:
            ValueError: If any of the required parameters ('gender', 'accent', 'age', 'accent_strength', or 'text') is None.
            requests.HTTPError: If the API request fails with an HTTP error status.
        
        Tags:
            generate, voice, ai, post
        """
        if gender is None:
            raise ValueError("Missing required parameter 'gender'")
        if accent is None:
            raise ValueError("Missing required parameter 'accent'")
        if age is None:
            raise ValueError("Missing required parameter 'age'")
        if accent_strength is None:
            raise ValueError("Missing required parameter 'accent_strength'")
        if text is None:
            raise ValueError("Missing required parameter 'text'")
        request_body = {
            'gender': gender,
            'accent': accent,
            'age': age,
            'accent_strength': accent_strength,
            'text': text,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/voice-generation/generate-voice"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_a_previously_generated_voice_v1_voice_generation_create_voice_post(self, voice_name, voice_description, generated_voice_id, labels=None) -> dict[str, Any]:
        """
        Creates a new voice entry using data from a previously generated voice.
        
        Args:
            voice_name: str. The display name for the new voice. Must not be None.
            voice_description: str. A textual description of the new voice. Must not be None.
            generated_voice_id: str. The unique identifier of the previously generated voice to use as a template. Must not be None.
            labels: Optional[dict]. Additional metadata or labels to associate with the voice. Defaults to None.
        
        Returns:
            dict. The server's JSON response containing information about the created voice.
        
        Raises:
            ValueError: Raised if any of the required parameters ('voice_name', 'voice_description', or 'generated_voice_id') are None.
            requests.HTTPError: Raised if the HTTP request to the voice-generation API fails (non-2xx response).
        
        Tags:
            create, voice, ai, api
        """
        if voice_name is None:
            raise ValueError("Missing required parameter 'voice_name'")
        if voice_description is None:
            raise ValueError("Missing required parameter 'voice_description'")
        if generated_voice_id is None:
            raise ValueError("Missing required parameter 'generated_voice_id'")
        request_body = {
            'voice_name': voice_name,
            'voice_description': voice_description,
            'generated_voice_id': generated_voice_id,
            'labels': labels,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/voice-generation/create-voice"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_user_subscription_info_v1_user_subscription_get(self, ) -> dict[str, Any]:
        """
        Retrieves the current user's subscription information from the API.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A dictionary containing the user's subscription details as returned by the API.
        
        Raises:
            requests.HTTPError: If the HTTP request to retrieve subscription information fails or returns an error status code.
        
        Tags:
            get, subscription, user, api
        """
        url = f"{self.base_url}/v1/user/subscription"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_user_info_v1_user_get(self, ) -> dict[str, Any]:
        """
        Retrieves information about the current authenticated user from the API.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A dictionary containing user details as returned by the API.
        
        Raises:
            requests.HTTPError: If the HTTP request to the user information endpoint fails or returns a non-success status code.
        
        Tags:
            get, user, info, api, important
        """
        url = f"{self.base_url}/v1/user"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_voices_v1_voices_get(self, ) -> dict[str, Any]:
        """
        Retrieves a list of available voices from the v1 API endpoint.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            dict: A dictionary containing information about the available voices as returned by the API.
        
        Raises:
            requests.HTTPError: Raised if the API response contains an HTTP error status.
        
        Tags:
            get, voices, api, list
        """
        url = f"{self.base_url}/v1/voices"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_default_voice_settings__v1_voices_settings_default_get(self, ) -> dict[str, Any]:
        """
        Retrieves the default voice settings from the API endpoint.
        
        Returns:
            A dictionary containing the default voice settings as returned by the API.
        
        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        
        Tags:
            get, voice-settings, api, fetch
        """
        url = f"{self.base_url}/v1/voices/settings/default"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_voice_settings_v1_voices__voice_id__settings_get(self, voice_id) -> dict[str, Any]:
        """
        Retrieves the settings for a specific voice using the provided voice ID.
        
        Args:
            voice_id: str. The unique identifier of the voice for which to fetch settings.
        
        Returns:
            dict. The settings of the specified voice, parsed from the service response.
        
        Raises:
            ValueError: If 'voice_id' is None.
            requests.exceptions.HTTPError: If the HTTP request to fetch settings fails (non-2xx response).
        
        Tags:
            get, voice-settings, ai
        """
        if voice_id is None:
            raise ValueError("Missing required parameter 'voice_id'")
        url = f"{self.base_url}/v1/voices/{voice_id}/settings"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_voice_v1_voices__voice_id__get(self, voice_id, with_settings=None) -> dict[str, Any]:
        """
        Retrieves details for a specific voice, optionally including voice settings, by making a GET request to the API.
        
        Args:
            voice_id: str. Unique identifier of the voice to retrieve. Must not be None.
            with_settings: Optional[bool]. If True, include voice settings in the response. Defaults to None, meaning settings are not included.
        
        Returns:
            dict[str, Any]: A dictionary containing voice details as returned by the API.
        
        Raises:
            ValueError: Raised if 'voice_id' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an error response.
        
        Tags:
            get, voice, api, management
        """
        if voice_id is None:
            raise ValueError("Missing required parameter 'voice_id'")
        url = f"{self.base_url}/v1/voices/{voice_id}"
        query_params = {k: v for k, v in [('with_settings', with_settings)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_voice_v1_voices__voice_id__delete(self, voice_id) -> Any:
        """
        Deletes a voice resource identified by the given voice ID using the v1 API endpoint.
        
        Args:
            voice_id: str. Unique identifier of the voice resource to be deleted.
        
        Returns:
            dict. Response data from the API after attempting to delete the voice resource.
        
        Raises:
            ValueError: Raised if the 'voice_id' parameter is None.
            requests.HTTPError: Raised if the HTTP request to delete the voice fails with an unsuccessful status code.
        
        Tags:
            delete, voice-management, api
        """
        if voice_id is None:
            raise ValueError("Missing required parameter 'voice_id'")
        url = f"{self.base_url}/v1/voices/{voice_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_sharing_voice_v1_voices_add__public_user_id___voice_id__post(self, public_user_id, voice_id, new_name) -> dict[str, Any]:
        """
        Adds a shared voice for a public user by sending a POST request with a new name for the specified voice.
        
        Args:
            public_user_id: str. The public user identifier to whom the voice will be shared.
            voice_id: str. The unique identifier of the voice to add.
            new_name: str. The new name to assign to the shared voice.
        
        Returns:
            dict[str, Any]: The JSON response from the server containing details about the shared voice addition.
        
        Raises:
            ValueError: Raised if any of the required parameters ('public_user_id', 'voice_id', or 'new_name') are None.
            requests.HTTPError: Raised if the HTTP request to the server returns an unsuccessful status code.
        
        Tags:
            add, sharing, voice, api, post, management
        """
        if public_user_id is None:
            raise ValueError("Missing required parameter 'public_user_id'")
        if voice_id is None:
            raise ValueError("Missing required parameter 'voice_id'")
        if new_name is None:
            raise ValueError("Missing required parameter 'new_name'")
        request_body = {
            'new_name': new_name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/voices/add/{public_user_id}/{voice_id}"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_projects_v1_projects_get(self, ) -> dict[str, Any]:
        """
        Retrieves a list of projects from the API using a GET request to the '/v1/projects' endpoint.
        
        Returns:
            A dictionary containing the JSON-decoded response from the API, typically representing a list of projects.
        
        Raises:
            requests.HTTPError: If the HTTP request to the projects API endpoint fails or returns an unsuccessful status code.
        
        Tags:
            get, list, projects, api, management
        """
        url = f"{self.base_url}/v1/projects"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project_by_id_v1_projects__project_id__get(self, project_id) -> dict[str, Any]:
        """
        Retrieve project details by project ID using the v1 projects API.
        
        Args:
            project_id: str. The unique identifier of the project to retrieve.
        
        Returns:
            dict[str, Any]: A dictionary containing the project's details as returned by the API.
        
        Raises:
            ValueError: If 'project_id' is None.
            HTTPError: If the HTTP request to the API fails with a non-success status code.
        
        Tags:
            get, project, management, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/v1/projects/{project_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_project_v1_projects__project_id__delete(self, project_id) -> Any:
        """
        Deletes a project by its ID using a DELETE HTTP request to the v1/projects endpoint.
        
        Args:
            project_id: The unique identifier of the project to be deleted. Must not be None.
        
        Returns:
            dict: The JSON response from the API after successful deletion of the project.
        
        Raises:
            ValueError: If 'project_id' is None.
            requests.HTTPError: If the API response contains an unsuccessful HTTP status code.
        
        Tags:
            delete, project, api, management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/v1/projects/{project_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def convert_project_v1_projects__project_id__convert_post(self, project_id) -> Any:
        """
        Converts the specified project by sending a POST request to the appropriate API endpoint.
        
        Args:
            project_id: The unique identifier of the project to convert. Must not be None.
        
        Returns:
            A dictionary containing the JSON response from the API after converting the project.
        
        Raises:
            ValueError: If 'project_id' is None.
            requests.HTTPError: If the API response contains an unsuccessful HTTP status code.
        
        Tags:
            convert, project, api, post
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/v1/projects/{project_id}/convert"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_project_snapshots_v1_projects__project_id__snapshots_get(self, project_id) -> dict[str, Any]:
        """
        Retrieves a list of snapshots for the specified project using the v1 projects API.
        
        Args:
            project_id: str. Unique identifier of the project for which snapshots are to be fetched.
        
        Returns:
            dict[str, Any]: The JSON response containing snapshot information for the given project.
        
        Raises:
            ValueError: If project_id is None.
            requests.HTTPError: If the HTTP request to the API endpoint results in an error status code.
        
        Tags:
            get, list, snapshots, project-management, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/v1/projects/{project_id}/snapshots"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def stream_project_audio_v1_projects__project_id__snapshots__project_snapshot_id__stream_post(self, project_id, project_snapshot_id, convert_to_mpeg=None) -> Any:
        """
        Streams audio data for a specific project snapshot, with optional conversion to MPEG format.
        
        Args:
            project_id: str. The unique identifier of the project whose audio snapshot is to be streamed.
            project_snapshot_id: str. The unique identifier of the project snapshot to stream audio from.
            convert_to_mpeg: Optional[bool]. If True, converts the audio stream to MPEG format before streaming. Defaults to None.
        
        Returns:
            dict. The JSON response containing the streamed audio data or relevant streaming metadata from the server.
        
        Raises:
            ValueError: Raised if 'project_id' or 'project_snapshot_id' is not provided.
            requests.HTTPError: Raised if the HTTP request to the streaming endpoint fails.
        
        Tags:
            stream, audio, project, snapshot, post
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if project_snapshot_id is None:
            raise ValueError("Missing required parameter 'project_snapshot_id'")
        request_body = {
            'convert_to_mpeg': convert_to_mpeg,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{project_id}/snapshots/{project_snapshot_id}/stream"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def streams_archive_with_project_audio_v1_projects__project_id__snapshots__project_snapshot_id__archive_post(self, project_id, project_snapshot_id) -> Any:
        """
        Creates an audio archive for the specified project snapshot by making a POST request to the project's archive endpoint.
        
        Args:
            project_id: The unique identifier of the project for which the snapshot archive is to be created.
            project_snapshot_id: The unique identifier of the project snapshot to archive.
        
        Returns:
            A dictionary containing the response data from the archive creation request.
        
        Raises:
            ValueError: Raised if 'project_id' or 'project_snapshot_id' is None.
            requests.HTTPError: Raised if the HTTP request to the archive endpoint returns an unsuccessful status code.
        
        Tags:
            archive, post, ai, management
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if project_snapshot_id is None:
            raise ValueError("Missing required parameter 'project_snapshot_id'")
        url = f"{self.base_url}/v1/projects/{project_id}/snapshots/{project_snapshot_id}/archive"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_chapters_v1_projects__project_id__chapters_get(self, project_id) -> dict[str, Any]:
        """
        Retrieves the list of chapters for a specific project by project ID.
        
        Args:
            project_id: The unique identifier of the project whose chapters are to be fetched.
        
        Returns:
            A dictionary representing the JSON response containing the project's chapters.
        
        Raises:
            ValueError: Raised if 'project_id' is None.
            requests.HTTPError: Raised if the HTTP request to the API endpoint fails.
        
        Tags:
            get, chapters, project, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        url = f"{self.base_url}/v1/projects/{project_id}/chapters"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_chapter_by_id_v1_projects__project_id__chapters__chapter_id__get(self, project_id, chapter_id) -> dict[str, Any]:
        """
        Retrieves a specific chapter resource by its ID from a given project using the API.
        
        Args:
            project_id: The unique identifier of the project containing the desired chapter.
            chapter_id: The unique identifier of the chapter to retrieve.
        
        Returns:
            A dictionary containing the chapter data as returned by the API.
        
        Raises:
            ValueError: Raised if either 'project_id' or 'chapter_id' is None.
            HTTPError: Raised if the HTTP request to the API fails or returns an error status.
        
        Tags:
            get, chapter, project, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if chapter_id is None:
            raise ValueError("Missing required parameter 'chapter_id'")
        url = f"{self.base_url}/v1/projects/{project_id}/chapters/{chapter_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_chapter_v1_projects__project_id__chapters__chapter_id__delete(self, project_id, chapter_id) -> Any:
        """
        Deletes a specific chapter from a project by its project and chapter IDs.
        
        Args:
            project_id: The unique identifier of the project containing the chapter to delete.
            chapter_id: The unique identifier of the chapter to delete from the project.
        
        Returns:
            The response body as a dictionary representing the result of the deletion operation.
        
        Raises:
            ValueError: If either 'project_id' or 'chapter_id' is None.
            requests.HTTPError: If the HTTP request fails or returns an unsuccessful status code.
        
        Tags:
            delete, chapter, project-management, api
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if chapter_id is None:
            raise ValueError("Missing required parameter 'chapter_id'")
        url = f"{self.base_url}/v1/projects/{project_id}/chapters/{chapter_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def convert_chapter_v1_projects__project_id__chapters__chapter_id__convert_post(self, project_id, chapter_id) -> Any:
        """
        Initiates a conversion operation for a specified chapter within a project and returns the result as JSON.
        
        Args:
            project_id: The unique identifier of the project containing the chapter to convert.
            chapter_id: The unique identifier of the chapter within the project to be converted.
        
        Returns:
            A JSON object containing the result of the chapter conversion operation.
        
        Raises:
            ValueError: Raised if 'project_id' or 'chapter_id' is not provided.
            requests.HTTPError: Raised if the POST request to the conversion endpoint fails.
        
        Tags:
            convert, chapter, post, api, async-job
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if chapter_id is None:
            raise ValueError("Missing required parameter 'chapter_id'")
        url = f"{self.base_url}/v1/projects/{project_id}/chapters/{chapter_id}/convert"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_chapter_snapshots_v1_projects__project_id__chapters__chapter_id__snapshots_get(self, project_id, chapter_id) -> dict[str, Any]:
        """
        Retrieves the list of chapter snapshots for a specific chapter within a project.
        
        Args:
            project_id: The unique identifier of the project containing the chapter.
            chapter_id: The unique identifier of the chapter whose snapshots are to be retrieved.
        
        Returns:
            A dictionary containing the snapshot data for the specified chapter.
        
        Raises:
            ValueError: Raised if either 'project_id' or 'chapter_id' is None.
            HTTPError: Raised if the HTTP request to retrieve snapshots fails.
        
        Tags:
            get, list, snapshots, project-management, chapter
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if chapter_id is None:
            raise ValueError("Missing required parameter 'chapter_id'")
        url = f"{self.base_url}/v1/projects/{project_id}/chapters/{chapter_id}/snapshots"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def stream_chapter_audio_v1_projects__project_id__chapters__chapter_id__snapshots__chapter_snapshot_id__stream_post(self, project_id, chapter_id, chapter_snapshot_id, convert_to_mpeg=None) -> Any:
        """
        Streams the audio for a specific chapter snapshot in a project, with optional conversion to MPEG format.
        
        Args:
            project_id: str. Unique identifier of the project containing the chapter.
            chapter_id: str. Identifier of the chapter whose audio is to be streamed.
            chapter_snapshot_id: str. Identifier of the chapter snapshot to stream audio from.
            convert_to_mpeg: bool, optional. If True, converts the audio stream to MPEG format before returning.
        
        Returns:
            dict. JSON response containing audio stream details or metadata.
        
        Raises:
            ValueError: If any of the required parameters ('project_id', 'chapter_id', or 'chapter_snapshot_id') are missing.
            requests.HTTPError: If the HTTP request to the audio streaming endpoint fails.
        
        Tags:
            stream, audio, chapter, project, ai
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if chapter_id is None:
            raise ValueError("Missing required parameter 'chapter_id'")
        if chapter_snapshot_id is None:
            raise ValueError("Missing required parameter 'chapter_snapshot_id'")
        request_body = {
            'convert_to_mpeg': convert_to_mpeg,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{project_id}/chapters/{chapter_id}/snapshots/{chapter_snapshot_id}/stream"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_pronunciation_dictionaries_v1_projects__project_id__update_pronunciation_dictionaries_post(self, project_id, pronunciation_dictionary_locators) -> Any:
        """
        Updates the pronunciation dictionaries for a specific project by sending the provided dictionary locators to the server.
        
        Args:
            project_id: str. The unique identifier of the project whose pronunciation dictionaries are to be updated.
            pronunciation_dictionary_locators: Any. The locators or references to the pronunciation dictionaries that should be updated for the project.
        
        Returns:
            Any. The JSON-decoded response from the server after updating the pronunciation dictionaries.
        
        Raises:
            ValueError: Raised if 'project_id' or 'pronunciation_dictionary_locators' is None.
            requests.HTTPError: Raised if the server responds with an unsuccessful HTTP status code.
        
        Tags:
            update, pronunciation-dictionaries, project-management, api-call
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if pronunciation_dictionary_locators is None:
            raise ValueError("Missing required parameter 'pronunciation_dictionary_locators'")
        request_body = {
            'pronunciation_dictionary_locators': pronunciation_dictionary_locators,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/projects/{project_id}/update-pronunciation-dictionaries"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_dubbing_project_metadata_v1_dubbing__dubbing_id__get(self, dubbing_id) -> dict[str, Any]:
        """
        Retrieves metadata for a dubbing project by its unique identifier.
        
        Args:
            dubbing_id: str. The unique identifier of the dubbing project to retrieve metadata for.
        
        Returns:
            dict[str, Any]: A dictionary containing metadata of the specified dubbing project.
        
        Raises:
            ValueError: If 'dubbing_id' is None.
            requests.HTTPError: If the HTTP request to fetch metadata fails.
        
        Tags:
            get, fetch, dubbing, metadata, api
        """
        if dubbing_id is None:
            raise ValueError("Missing required parameter 'dubbing_id'")
        url = f"{self.base_url}/v1/dubbing/{dubbing_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_dubbing_project_v1_dubbing__dubbing_id__delete(self, dubbing_id) -> Any:
        """
        Deletes a dubbing project identified by its ID via the v1 API endpoint.
        
        Args:
            dubbing_id: The unique identifier of the dubbing project to delete.
        
        Returns:
            A dictionary parsed from the JSON response indicating the result of the deletion operation.
        
        Raises:
            ValueError: If 'dubbing_id' is None.
            requests.HTTPError: If the HTTP request to delete the dubbing project fails (non-success status code).
        
        Tags:
            delete, dubbing, api, management
        """
        if dubbing_id is None:
            raise ValueError("Missing required parameter 'dubbing_id'")
        url = f"{self.base_url}/v1/dubbing/{dubbing_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_dubbed_file_v1_dubbing__dubbing_id__audio__language_code__get(self, dubbing_id, language_code) -> Any:
        """
        Retrieves the dubbed audio file for a given dubbing ID and language code from the API.
        
        Args:
            dubbing_id: The unique identifier of the dubbing resource to fetch. Must not be None.
            language_code: The language code (e.g., 'en', 'es') of the audio file to retrieve. Must not be None.
        
        Returns:
            dict: The JSON response containing the dubbed audio file metadata and/or download information.
        
        Raises:
            ValueError: Raised if either 'dubbing_id' or 'language_code' is None.
            HTTPError: Raised if the HTTP request to the API fails with an unsuccessful status code.
        
        Tags:
            get, audio, dubbing, api
        """
        if dubbing_id is None:
            raise ValueError("Missing required parameter 'dubbing_id'")
        if language_code is None:
            raise ValueError("Missing required parameter 'language_code'")
        url = f"{self.base_url}/v1/dubbing/{dubbing_id}/audio/{language_code}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_transcript_for_dub_v1_dubbing__dubbing_id__transcript__language_code__get(self, dubbing_id, language_code) -> Any:
        """
        Retrieves the transcript for a specific dubbing in the requested language.
        
        Args:
            dubbing_id: The unique identifier of the dubbing for which to fetch the transcript.
            language_code: The language code (e.g., 'en', 'es') for the desired transcript.
        
        Returns:
            The transcript data as parsed from the API response, typically a dictionary or list depending on the API.
        
        Raises:
            ValueError: If 'dubbing_id' or 'language_code' is not provided.
            requests.HTTPError: If the HTTP request to fetch the transcript fails.
        
        Tags:
            get, transcript, dubbing, api
        """
        if dubbing_id is None:
            raise ValueError("Missing required parameter 'dubbing_id'")
        if language_code is None:
            raise ValueError("Missing required parameter 'language_code'")
        url = f"{self.base_url}/v1/dubbing/{dubbing_id}/transcript/{language_code}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_sso_provider_admin_admin__admin_url_prefix__sso_provider_get(self, admin_url_prefix, workspace_id) -> dict[str, Any]:
        """
        Retrieves SSO provider information for a specific admin URL prefix and workspace.
        
        Args:
            admin_url_prefix: str. The URL prefix identifying the admin scope for the SSO provider.
            workspace_id: str. The ID of the workspace for which to retrieve SSO provider information.
        
        Returns:
            dict. A dictionary containing the SSO provider information for the specified workspace and admin URL prefix.
        
        Raises:
            ValueError: Raised if either 'admin_url_prefix' or 'workspace_id' is None.
            requests.HTTPError: Raised if the HTTP request to retrieve SSO provider information fails.
        
        Tags:
            get, sso-provider, admin, management
        """
        if admin_url_prefix is None:
            raise ValueError("Missing required parameter 'admin_url_prefix'")
        if workspace_id is None:
            raise ValueError("Missing required parameter 'workspace_id'")
        url = f"{self.base_url}/admin/{admin_url_prefix}/sso-provider"
        query_params = {k: v for k, v in [('workspace_id', workspace_id)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_models_v1_models_get(self, ) -> list[Any]:
        """
        Retrieves a list of available models from the v1 API endpoint.
        
        Args:
            None: This function takes no arguments
        
        Returns:
            A list containing model information retrieved from the API.
        
        Raises:
            requests.HTTPError: If the HTTP request to the models endpoint returns an unsuccessful status code.
        
        Tags:
            get, models, ai, api, list
        """
        url = f"{self.base_url}/v1/models"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_voices_v1_shared_voices_get(self, page_size=None, category=None, gender=None, age=None, accent=None, language=None, search=None, use_cases=None, descriptives=None, featured=None, reader_app_enabled=None, owner_id=None, sort=None, page=None) -> dict[str, Any]:
        """
        Retrieves a list of shared voice resources, filtered and paginated according to the specified criteria.
        
        Args:
            page_size: Optional; The number of voice results to return per page.
            category: Optional; Filter voices by category (e.g., audiobook, narration, commercial).
            gender: Optional; Filter voices by gender (e.g., male, female, neutral).
            age: Optional; Filter voices by age group (e.g., child, adult, senior).
            accent: Optional; Filter voices by accent or dialect.
            language: Optional; Filter voices by language code or name.
            search: Optional; Search query string to match against voice names or descriptions.
            use_cases: Optional; Filter voices by specific use cases.
            descriptives: Optional; Filter voices by descriptive attributes (e.g., warm, energetic).
            featured: Optional; Filter to only featured voices if True.
            reader_app_enabled: Optional; Filter voices available in the reader app.
            owner_id: Optional; Filter voices by the owner's identifier.
            sort: Optional; Sort order for returned voices (e.g., by relevance or name).
            page: Optional; The page number for paginated results.
        
        Returns:
            A dictionary containing metadata and a list of shared voice resources matching the provided filters.
        
        Raises:
            requests.HTTPError: If the HTTP request to fetch shared voices fails or returns a non-success status code.
        
        Tags:
            get, list, voices, filter, pagination, batch, ai
        """
        url = f"{self.base_url}/v1/shared-voices"
        query_params = {k: v for k, v in [('page_size', page_size), ('category', category), ('gender', gender), ('age', age), ('accent', accent), ('language', language), ('search', search), ('use_cases', use_cases), ('descriptives', descriptives), ('featured', featured), ('reader_app_enabled', reader_app_enabled), ('owner_id', owner_id), ('sort', sort), ('page', page)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_rules_to_the_pronunciation_dictionary_v1_pronunciation_dictionaries__pronunciation_dictionary_id__add_rules_post(self, pronunciation_dictionary_id, rules) -> dict[str, Any]:
        """
        Adds new pronunciation rules to a specified pronunciation dictionary by making a POST request to the backend service.
        
        Args:
            pronunciation_dictionary_id: The unique identifier of the pronunciation dictionary to which the rules will be added.
            rules: A list or collection of pronunciation rules to be added to the dictionary.
        
        Returns:
            A dictionary containing the server's response data after attempting to add the specified rules.
        
        Raises:
            ValueError: Raised if 'pronunciation_dictionary_id' or 'rules' is None.
            requests.HTTPError: Raised if the POST request to the backend service fails due to a bad HTTP response.
        
        Tags:
            add, rules, pronunciation-dictionary, post, api, management
        """
        if pronunciation_dictionary_id is None:
            raise ValueError("Missing required parameter 'pronunciation_dictionary_id'")
        if rules is None:
            raise ValueError("Missing required parameter 'rules'")
        request_body = {
            'rules': rules,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/pronunciation-dictionaries/{pronunciation_dictionary_id}/add-rules"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def remove_rules_from_the_pronunciation_dictionary_v1_pronunciation_dictionaries__pronunciation_dictionary_id__remove_rules_post(self, pronunciation_dictionary_id, rule_strings) -> dict[str, Any]:
        """
        Removes specified pronunciation rules from a pronunciation dictionary via a POST request to the API.
        
        Args:
            pronunciation_dictionary_id: str. The unique identifier of the pronunciation dictionary from which to remove rules.
            rule_strings: list[str]. A list of pronunciation rule strings to be removed from the dictionary.
        
        Returns:
            dict[str, Any]: A dictionary containing the API response data after removing the rules.
        
        Raises:
            ValueError: Raised when 'pronunciation_dictionary_id' or 'rule_strings' is None.
            requests.HTTPError: Raised if the API request fails or returns a non-success status code.
        
        Tags:
            remove, pronunciation, dictionary, rules, api, post, management
        """
        if pronunciation_dictionary_id is None:
            raise ValueError("Missing required parameter 'pronunciation_dictionary_id'")
        if rule_strings is None:
            raise ValueError("Missing required parameter 'rule_strings'")
        request_body = {
            'rule_strings': rule_strings,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/pronunciation-dictionaries/{pronunciation_dictionary_id}/remove-rules"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_pls_file_with_a_pronunciation_dictionary_version_rules_v1_pronunciation_dictionaries__dictionary_id___version_id__download_get(self, dictionary_id, version_id) -> Any:
        """
        Downloads a pronunciation lexicon (PLS) file for a specific pronunciation dictionary version.
        
        Args:
            dictionary_id: The unique identifier of the pronunciation dictionary to download.
            version_id: The specific version identifier of the pronunciation dictionary.
        
        Returns:
            A dictionary containing the JSON response data of the downloaded PLS file.
        
        Raises:
            ValueError: Raised if 'dictionary_id' or 'version_id' is None.
            HTTPError: Raised if the HTTP request for the PLS file results in a failed status code.
        
        Tags:
            download, pronunciation-dictionary, get, ai
        """
        if dictionary_id is None:
            raise ValueError("Missing required parameter 'dictionary_id'")
        if version_id is None:
            raise ValueError("Missing required parameter 'version_id'")
        url = f"{self.base_url}/v1/pronunciation-dictionaries/{dictionary_id}/{version_id}/download"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_metadata_for_a_pronunciation_dictionary_v1_pronunciation_dictionaries__pronunciation_dictionary_id___get(self, pronunciation_dictionary_id) -> dict[str, Any]:
        """
        Retrieves metadata for a specific pronunciation dictionary by its ID.
        
        Args:
            pronunciation_dictionary_id: The unique identifier of the pronunciation dictionary to retrieve metadata for.
        
        Returns:
            A dictionary containing the metadata of the specified pronunciation dictionary.
        
        Raises:
            ValueError: If 'pronunciation_dictionary_id' is None.
            requests.HTTPError: If the HTTP request to retrieve the metadata fails with a non-success status.
        
        Tags:
            get, pronunciation-dictionary, metadata, api
        """
        if pronunciation_dictionary_id is None:
            raise ValueError("Missing required parameter 'pronunciation_dictionary_id'")
        url = f"{self.base_url}/v1/pronunciation-dictionaries/{pronunciation_dictionary_id}/"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_pronunciation_dictionaries_v1_pronunciation_dictionaries__get(self, cursor=None, page_size=None) -> dict[str, Any]:
        """
        Retrieve a paginated list of pronunciation dictionaries from the v1 API endpoint.
        
        Args:
            cursor: Optional; a string used for pagination, indicating the position to continue retrieving results from.
            page_size: Optional; an integer specifying the maximum number of pronunciation dictionaries to return in one page.
        
        Returns:
            A dictionary containing the response data from the pronunciation dictionaries API, typically including results and pagination information.
        
        Raises:
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an error response status code.
        
        Tags:
            get, list, pronunciation-dictionaries, api, pagination
        """
        url = f"{self.base_url}/v1/pronunciation-dictionaries/"
        query_params = {k: v for k, v in [('cursor', cursor), ('page_size', page_size)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_a_profile_page_profile__handle__get(self, handle) -> dict[str, Any]:
        """
        Retrieves a user's profile data as a dictionary using their unique handle.
        
        Args:
            handle: str. The unique identifier for the user profile to retrieve.
        
        Returns:
            dict[str, Any]: A dictionary containing the user's profile data returned by the API.
        
        Raises:
            ValueError: If 'handle' is None.
            requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
        
        Tags:
            get, profile, api, user-data
        """
        if handle is None:
            raise ValueError("Missing required parameter 'handle'")
        url = f"{self.base_url}/profile/{handle}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def redirect_to_mintlify_docs_get(self, ) -> Any:
        """
        Fetches the Mintlify documentation by sending a GET request and returns the parsed JSON response.
        
        Returns:
            dict: Parsed JSON content from the Mintlify documentation endpoint.
        
        Raises:
            requests.HTTPError: If the HTTP request to the Mintlify documentation endpoint fails (i.e., a non-success status code is returned).
        
        Tags:
            get, docs, mintlify, api
        """
        url = f"{self.base_url}/docs"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.get_generated_items_v1_history_get,
            self.get_history_item_by_id_v1_history__history_item_id__get,
            self.delete_history_item_v1_history__history_item_id__delete,
            self.get_audio_from_history_item_v1_history__history_item_id__audio_get,
            self.download_history_items_v1_history_download_post,
            self.delete_sample_v1_voices__voice_id__samples__sample_id__delete,
            self.get_audio_from_sample_v1_voices__voice_id__samples__sample_id__audio_get,
            self.text_to_speech_v1_text_to_speech__voice_id__post,
            self.text_to_speech_v1_text_to_speech__voice_id__stream_post,
            self.voice_generation_parameters_v1_voice_generation_generate_voice_parameters_get,
            self.generate_a_random_voice_v1_voice_generation_generate_voice_post,
            self.create_a_previously_generated_voice_v1_voice_generation_create_voice_post,
            self.get_user_subscription_info_v1_user_subscription_get,
            self.get_user_info_v1_user_get,
            self.get_voices_v1_voices_get,
            self.get_default_voice_settings__v1_voices_settings_default_get,
            self.get_voice_settings_v1_voices__voice_id__settings_get,
            self.get_voice_v1_voices__voice_id__get,
            self.delete_voice_v1_voices__voice_id__delete,
            self.add_sharing_voice_v1_voices_add__public_user_id___voice_id__post,
            self.get_projects_v1_projects_get,
            self.get_project_by_id_v1_projects__project_id__get,
            self.delete_project_v1_projects__project_id__delete,
            self.convert_project_v1_projects__project_id__convert_post,
            self.get_project_snapshots_v1_projects__project_id__snapshots_get,
            self.stream_project_audio_v1_projects__project_id__snapshots__project_snapshot_id__stream_post,
            self.streams_archive_with_project_audio_v1_projects__project_id__snapshots__project_snapshot_id__archive_post,
            self.get_chapters_v1_projects__project_id__chapters_get,
            self.get_chapter_by_id_v1_projects__project_id__chapters__chapter_id__get,
            self.delete_chapter_v1_projects__project_id__chapters__chapter_id__delete,
            self.convert_chapter_v1_projects__project_id__chapters__chapter_id__convert_post,
            self.get_chapter_snapshots_v1_projects__project_id__chapters__chapter_id__snapshots_get,
            self.stream_chapter_audio_v1_projects__project_id__chapters__chapter_id__snapshots__chapter_snapshot_id__stream_post,
            self.update_pronunciation_dictionaries_v1_projects__project_id__update_pronunciation_dictionaries_post,
            self.get_dubbing_project_metadata_v1_dubbing__dubbing_id__get,
            self.delete_dubbing_project_v1_dubbing__dubbing_id__delete,
            self.get_dubbed_file_v1_dubbing__dubbing_id__audio__language_code__get,
            self.get_transcript_for_dub_v1_dubbing__dubbing_id__transcript__language_code__get,
            self.get_sso_provider_admin_admin__admin_url_prefix__sso_provider_get,
            self.get_models_v1_models_get,
            self.get_voices_v1_shared_voices_get,
            self.add_rules_to_the_pronunciation_dictionary_v1_pronunciation_dictionaries__pronunciation_dictionary_id__add_rules_post,
            self.remove_rules_from_the_pronunciation_dictionary_v1_pronunciation_dictionaries__pronunciation_dictionary_id__remove_rules_post,
            self.get_pls_file_with_a_pronunciation_dictionary_version_rules_v1_pronunciation_dictionaries__dictionary_id___version_id__download_get,
            self.get_metadata_for_a_pronunciation_dictionary_v1_pronunciation_dictionaries__pronunciation_dictionary_id___get,
            self.get_pronunciation_dictionaries_v1_pronunciation_dictionaries__get,
            self.get_a_profile_page_profile__handle__get,
            self.redirect_to_mintlify_docs_get
        ]
