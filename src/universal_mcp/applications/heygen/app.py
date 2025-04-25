from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class HeygenApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="heygen", integration=integration, **kwargs)
        self.base_url = "https://api.heygen.com"

    def _get_headers(self) -> dict[str, Any]:
        api_key = self.integration.get_credentials().get("api_key")
        return {
            "x-api-key": f"{api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get_v1_voice_list(
        self,
    ) -> Any:
        """
        Retrieves the list of available voices from the v1 voice API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            dict: A dictionary containing the JSON response with details about the available voices.

        Raises:
            HTTPError: If the HTTP request to the voice API endpoint results in an unsuccessful status code.

        Tags:
            get, list, voice, api
        """
        url = f"{self.base_url}/v1/voice.list"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v1_avatar_list(
        self,
    ) -> Any:
        """
        Retrieves a list of available avatars from the v1 API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            A JSON-decoded object containing the list of avatars returned by the API.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request to the avatar list endpoint fails, such as due to a non-2xx response.

        Tags:
            get, list, avatar, api, important
        """
        url = f"{self.base_url}/v1/avatar.list"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v2_voices(
        self,
    ) -> Any:
        """
        Retrieves the list of available v2 voices from the API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            A JSON-decoded object containing information about available v2 voices.

        Raises:
            requests.HTTPError: If the HTTP request to the voices endpoint returns an unsuccessful status code.

        Tags:
            get, list, voices, api, important
        """
        url = f"{self.base_url}/v2/voices"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v2_avatars(
        self,
    ) -> Any:
        """
        Retrieves a list of avatar objects from the /v2/avatars API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            A JSON-decoded object containing the list of avatars as returned by the API.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request to the /v2/avatars endpoint returns an unsuccessful status code.

        Tags:
            get, list, avatars, api
        """
        url = f"{self.base_url}/v2/avatars"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v1_video_list(
        self,
    ) -> Any:
        """
        Retrieves a list of videos from the v1 API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            A JSON-decoded object containing the list of videos as returned by the API.

        Raises:
            requests.HTTPError: If the HTTP request to the API endpoint fails or returns an unsuccessful status code.

        Tags:
            get, list, video, api
        """
        url = f"{self.base_url}/v1/video.list"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_v2_video_generate(
        self,
        video_inputs,
        title=None,
        test=None,
        callback_id=None,
        dimension=None,
        aspect_ratio=None,
    ) -> Any:
        """
        Submits a request to generate a video using specified input parameters via the v2 video generate API endpoint.

        Args:
            video_inputs: A required object or list containing the video inputs used for generation. Must not be None.
            title: Optional; a string specifying the title of the generated video.
            test: Optional; a flag or parameter used for testing purposes. Its type and effect depend on the API implementation.
            callback_id: Optional; a string or identifier for callback tracking after video generation.
            dimension: Optional; defines the desired dimensions for the generated video.
            aspect_ratio: Optional; defines the desired aspect ratio for the generated video.

        Returns:
            A dictionary containing the API response parsed from JSON, typically including information about the video generation job.

        Raises:
            ValueError: Raised if 'video_inputs' is None.
            requests.HTTPError: Raised if the HTTP request to the video generation endpoint fails (e.g., non-2xx response).

        Tags:
            create, video, generate, api, async-job
        """
        if video_inputs is None:
            raise ValueError("Missing required parameter 'video_inputs'")
        request_body = {
            "title": title,
            "video_inputs": video_inputs,
            "test": test,
            "callback_id": callback_id,
            "dimension": dimension,
            "aspect_ratio": aspect_ratio,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/video/generate"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_v1_video(self, video_id=None) -> Any:
        """
        Deletes a video using the v1 API endpoint with the specified video ID.

        Args:
            video_id: Optional; The unique identifier of the video to delete. If None, no video is specified in the request.

        Returns:
            Parsed JSON response from the API indicating the result of the delete operation.

        Raises:
            requests.HTTPError: If the HTTP request fails or the server returns an error response.

        Tags:
            delete, video, api, v1, management
        """
        url = f"{self.base_url}/v1/video.delete"
        query_params = {k: v for k, v in [("video_id", video_id)] if v is not None}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v2_templates(
        self,
    ) -> Any:
        """
        Retrieves the list of v2 templates from the API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            Parsed JSON data from the API response containing the v2 templates.

        Raises:
            HTTPError: If the HTTP request to the API endpoint fails or returns an error status.

        Tags:
            get, templates, api, http
        """
        url = f"{self.base_url}/v2/templates"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v2_template_by_id(self, id) -> Any:
        """
        Retrieves a v2 template resource by its unique identifier.

        Args:
            id: The unique identifier of the v2 template to retrieve.

        Returns:
            The parsed JSON response containing the template data.

        Raises:
            ValueError: Raised if the 'id' parameter is None.
            requests.HTTPError: Raised if the HTTP request to retrieve the template fails.

        Tags:
            get, template, id-lookup, api
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v2/template/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_v2_template_generate_by_id(
        self, id, title, variables, test=None, caption=None, dimension=None
    ) -> Any:
        """
        Generates content from a template specified by ID using the provided title and variables, and returns the generation result.

        Args:
            id: str. The unique identifier of the template to use for content generation. Required.
            title: str. The title associated with the generated content. Required.
            variables: dict. The variables to substitute into the template. Required.
            test: bool, optional. If set, indicates whether to perform a test generation without committing changes.
            caption: str, optional. Caption to include with the generated content.
            dimension: str or dict, optional. Specifies dimensions or formatting options for generation.

        Returns:
            dict. The JSON response containing the generated content and metadata from the API.

        Raises:
            ValueError: If 'id', 'title', or 'variables' are not provided.
            requests.HTTPError: If the API response contains an HTTP error status.

        Tags:
            generate, template, post, ai
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        if title is None:
            raise ValueError("Missing required parameter 'title'")
        if variables is None:
            raise ValueError("Missing required parameter 'variables'")
        request_body = {
            "title": title,
            "variables": variables,
            "test": test,
            "caption": caption,
            "dimension": dimension,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/template/{id}/generate"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v2_video_translate_target_languages(
        self,
    ) -> Any:
        """
        Retrieves the list of supported target languages for video translation via the v2 API.

        Args:
            None: This function takes no arguments

        Returns:
            dict: A JSON-decoded dictionary containing the available target languages for video translation.

        Raises:
            requests.HTTPError: If the HTTP response indicates an unsuccessful status code.

        Tags:
            get, list, api, video-translation, languages
        """
        url = f"{self.base_url}/v2/video_translate/target_languages"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_v2_video_translate(
        self,
        video_url,
        output_language,
        title=None,
        translate_audio_only=None,
        speaker_num=None,
    ) -> Any:
        """
        Submits a video translation request and returns the API response as JSON.

        Args:
            video_url: str. The URL of the source video to translate. Must not be None.
            output_language: str. The target language code for translation output. Must not be None.
            title: Optional[str]. The title to assign to the translated video. Defaults to None.
            translate_audio_only: Optional[bool]. If True, only translates audio (not on-screen text). Defaults to None.
            speaker_num: Optional[int]. Number of speakers in the video, if known. Defaults to None.

        Returns:
            dict. The JSON response from the translation API containing the translation job details or result.

        Raises:
            ValueError: If 'video_url' or 'output_language' is not provided.
            requests.HTTPError: If the HTTP request to the translation API fails (non-success status code).

        Tags:
            video, translate, ai, async-job, post
        """
        if video_url is None:
            raise ValueError("Missing required parameter 'video_url'")
        if output_language is None:
            raise ValueError("Missing required parameter 'output_language'")
        request_body = {
            "title": title,
            "video_url": video_url,
            "output_language": output_language,
            "translate_audio_only": translate_audio_only,
            "speaker_num": speaker_num,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/video_translate"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v2_video_translate_status_by_id(self, id) -> Any:
        """
        Retrieves the status of a video translation job by its unique identifier.

        Args:
            id: The unique identifier of the video translation job to check.

        Returns:
            A dictionary representing the status and details of the video translation job.

        Raises:
            ValueError: Raised if the 'id' parameter is None.
            HTTPError: Raised if the HTTP request to retrieve the job status fails.

        Tags:
            get, video-translate, status, ai
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v2/video_translate/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_streaming_new(self, quality=None) -> Any:
        """
        Initiates a new streaming session with optional quality parameter and returns the server's JSON response.

        Args:
            quality: Optional quality setting for the streaming session (type: Any). If None, the default server quality will be used.

        Returns:
            A JSON-decoded response (type: Any) from the server containing information about the newly created streaming session.

        Raises:
            requests.HTTPError: If the HTTP request to start the streaming session fails or returns a non-success status code.

        Tags:
            post, streaming, async-job, start, api
        """
        request_body = {
            "quality": quality,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/streaming.new"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_streaming_list(
        self,
    ) -> Any:
        """
        Retrieves the list of available streaming resources from the remote API.

        Args:
            None: This function takes no arguments

        Returns:
            The parsed JSON response containing the list of streaming resources.

        Raises:
            requests.HTTPError: If the HTTP request to the streaming list endpoint fails or returns an error status code.

        Tags:
            get, list, streaming, api
        """
        url = f"{self.base_url}/v1/streaming.list"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_streaming_ice(self, session_id, candidate) -> Any:
        """
        Sends an ICE candidate for a streaming session to the server and returns the JSON response.

        Args:
            session_id: Unique identifier for the streaming session. Must not be None.
            candidate: ICE candidate information to be sent to the server. Must not be None.

        Returns:
            Parsed JSON response from the server as a Python object.

        Raises:
            ValueError: Raised if 'session_id' or 'candidate' is None.
            requests.HTTPError: Raised if the HTTP request to the server fails.

        Tags:
            post, streaming, ice, async-job, ai
        """
        if session_id is None:
            raise ValueError("Missing required parameter 'session_id'")
        if candidate is None:
            raise ValueError("Missing required parameter 'candidate'")
        request_body = {
            "session_id": session_id,
            "candidate": candidate,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/streaming.ice"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_streaming_task(self, session_id, text) -> Any:
        """
        Submits a streaming task for the specified session and text input, returning the response from the remote API.

        Args:
            session_id: The unique identifier for the streaming session. Must not be None.
            text: The text content to be processed in the streaming task. Must not be None.

        Returns:
            The parsed JSON response from the streaming task API call.

        Raises:
            ValueError: If either 'session_id' or 'text' is None.
            requests.HTTPError: If the API request fails or returns an unsuccessful status code.

        Tags:
            post, streaming-task, api, start
        """
        if session_id is None:
            raise ValueError("Missing required parameter 'session_id'")
        if text is None:
            raise ValueError("Missing required parameter 'text'")
        request_body = {
            "session_id": session_id,
            "text": text,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/streaming.task"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_streaming_stop(self, session_id) -> Any:
        """
        Stops an ongoing streaming session by sending a stop request for the specified session ID.

        Args:
            session_id: The unique identifier of the streaming session to be stopped.

        Returns:
            The parsed JSON response from the stop request, typically containing the status or result of the streaming stop operation.

        Raises:
            ValueError: If 'session_id' is None.
            requests.HTTPError: If the HTTP request to stop the streaming session fails or returns an error response.

        Tags:
            stop, streaming, management, async-job
        """
        if session_id is None:
            raise ValueError("Missing required parameter 'session_id'")
        request_body = {
            "session_id": session_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/streaming.stop"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_streaming_interrupt(self, session_id) -> Any:
        """
        Sends a request to interrupt an active streaming session identified by the given session ID.

        Args:
            session_id: The unique identifier of the streaming session to be interrupted.

        Returns:
            A dictionary containing the server's response to the interrupt request.

        Raises:
            ValueError: Raised if 'session_id' is None.
            requests.HTTPError: Raised if the HTTP request to interrupt the session fails.

        Tags:
            interrupt, streaming, management
        """
        if session_id is None:
            raise ValueError("Missing required parameter 'session_id'")
        request_body = {
            "session_id": session_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/streaming.interrupt"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_streaming_create_token(self, expiry=None) -> Any:
        """
        Creates a new streaming token with an optional expiry time by sending a POST request to the streaming token API endpoint.

        Args:
            expiry: Optional expiry time for the token in seconds. If None, the token will not have an explicit expiration.

        Returns:
            dict: The JSON response from the API containing the new streaming token and related metadata.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.

        Tags:
            create, streaming, token, api
        """
        request_body = {
            "expiry": expiry,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/streaming.create_token"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_streaming_avatar_list(
        self,
    ) -> Any:
        """
        Retrieves a list of available streaming avatars from the API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            A JSON-decoded object representing the list of streaming avatars.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request to the streaming avatar endpoint returns an unsuccessful status code.

        Tags:
            list, streaming, avatar, api
        """
        url = f"{self.base_url}/v1/streaming/avatar.list"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v1_webhook_list(
        self,
    ) -> Any:
        """
        Retrieves a list of all registered webhooks via the v1 API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            The parsed JSON response containing webhook list data.

        Raises:
            requests.HTTPError: If the HTTP request fails or an error response is returned from the server.

        Tags:
            list, webhook, api, management
        """
        url = f"{self.base_url}/v1/webhook/webhook.list"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_v1_webhook_endpoint_add(self, url, events) -> Any:
        """
        Registers a new webhook endpoint with the specified URL and events.

        Args:
            url: str. The callback URL where webhook notifications will be sent. Must not be None.
            events: list. A list of event types to subscribe the webhook to. Must not be None.

        Returns:
            dict. The JSON response from the API containing details about the created webhook endpoint.

        Raises:
            ValueError: Raised if the 'url' or 'events' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the endpoint fails.

        Tags:
            add, webhook, endpoint, api
        """
        if url is None:
            raise ValueError("Missing required parameter 'url'")
        if events is None:
            raise ValueError("Missing required parameter 'events'")
        request_body = {
            "url": url,
            "events": events,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/webhook/endpoint.add"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_v1_webhook_endpoint_by_id(self, endpoint_id) -> Any:
        """
        Deletes a webhook endpoint identified by its ID via a DELETE request to the v1 API.

        Args:
            endpoint_id: The unique identifier of the webhook endpoint to delete. Must not be None.

        Returns:
            The response payload parsed as JSON from the DELETE request.

        Raises:
            ValueError: If the 'endpoint_id' parameter is None.
            requests.HTTPError: If the DELETE request returns an unsuccessful HTTP status code.

        Tags:
            delete, webhook, endpoint, api
        """
        if endpoint_id is None:
            raise ValueError("Missing required parameter 'endpoint_id'")
        url = f"{self.base_url}/v1/webhook/endpoint.delete/{endpoint_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v1_webhook_endpoint_list(
        self,
    ) -> Any:
        """
        Retrieves a list of webhook endpoints from the v1 API.

        Args:
            None: This function takes no arguments

        Returns:
            A JSON-compatible object containing the list of webhook endpoints.

        Raises:
            requests.HTTPError: If the HTTP request to the webhook endpoint API fails or returns an unsuccessful status code.

        Tags:
            get, list, webhook, endpoint, api
        """
        url = f"{self.base_url}/v1/webhook/endpoint.list"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v1_talking_photo_list(
        self,
    ) -> Any:
        """
        Retrieves the list of talking photos from the v1 API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            The JSON-decoded response containing the list of talking photos.

        Raises:
            requests.HTTPError: If the HTTP request to the API endpoint returns an unsuccessful status code.

        Tags:
            get, list, api, talking-photo
        """
        url = f"{self.base_url}/v1/talking_photo.list"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_v2_talking_photo_by_id(self, id) -> Any:
        """
        Deletes a v2 talking photo resource identified by its unique ID.

        Args:
            id: The unique identifier of the v2 talking photo to be deleted.

        Returns:
            The response data as a JSON object if the deletion is successful.

        Raises:
            ValueError: Raised if the 'id' parameter is None.
            HTTPError: Raised if the HTTP request fails with an error status code.

        Tags:
            delete, talking-photo, v2, api, management
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v2/talking_photo/{id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_personalized_video_add_contact(self, project_id, variables_list) -> Any:
        """
        Adds a new contact to a personalized video project by sending the contact variables to the server.

        Args:
            project_id: The unique identifier for the personalized video project. Must not be None.
            variables_list: A list containing variables for the new contact. Must not be None.

        Returns:
            A dictionary representing the JSON response from the server, usually containing details or status of the added contact.

        Raises:
            ValueError: Raised if either 'project_id' or 'variables_list' is None.
            requests.HTTPError: Raised if the HTTP request fails or returns an error status code.

        Tags:
            add, contact, personalized-video, api, async_job
        """
        if project_id is None:
            raise ValueError("Missing required parameter 'project_id'")
        if variables_list is None:
            raise ValueError("Missing required parameter 'variables_list'")
        request_body = {
            "project_id": project_id,
            "variables_list": variables_list,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v1/personalized_video/add_contact"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_personalized_video_audience_detail(self, id=None) -> Any:
        """
        Retrieves detailed information about a personalized video audience by ID.

        Args:
            id: Optional; The unique identifier of the personalized video audience to retrieve details for. If None, details for all audiences may be returned depending on API behavior.

        Returns:
            A JSON-decoded Python object containing the audience detail information provided by the API.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.

        Tags:
            get, detail, audience, video, api
        """
        url = f"{self.base_url}/v1/personalized_video/audience/detail"
        query_params = {k: v for k, v in [("id", id)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_personalized_video_project_detail(self, id=None) -> Any:
        """
        Retrieves the details of a personalized video project by its unique identifier.

        Args:
            id: Optional; The unique identifier of the personalized video project to retrieve. If None, no project ID is passed as a parameter.

        Returns:
            A JSON-decoded Python object containing the details of the personalized video project.

        Raises:
            requests.HTTPError: If the HTTP request fails or returns a non-success status code, an HTTPError is raised.

        Tags:
            get, personalized-video, project-detail, api
        """
        url = f"{self.base_url}/v1/personalized_video/project/detail"
        query_params = {k: v for k, v in [("id", id)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v2_user_remaining_quota(
        self,
    ) -> Any:
        """
        Retrieves the current remaining quota information for the user from the v2 API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            dict: A dictionary containing remaining quota details for the user as returned by the API.

        Raises:
            requests.HTTPError: If the HTTP request to the quota endpoint fails or returns a non-success status code.

        Tags:
            get, quota, user-management, api
        """
        url = f"{self.base_url}/v2/user/remaining_quota"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def post_v1_asset_upload(self, request_body=None) -> Any:
        """
        Uploads an asset to the server using a POST request to the '/v1/asset' endpoint.

        Args:
            request_body: Optional. The data to include in the POST request body, typically representing the asset to upload.

        Returns:
            The parsed JSON response from the server, containing information about the uploaded asset.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.

        Tags:
            upload, asset, post, api
        """
        url = f"{self.base_url}/v1/asset"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_v1_video_status(self, video_id=None) -> Any:
        """
        Retrieves the status of a video by making a GET request to the v1 video_status endpoint.

        Args:
            video_id: Optional; The unique identifier of the video whose status is to be retrieved. If not provided, the request may fail or return an error depending on the API.

        Returns:
            A JSON-decoded object containing the status information of the requested video.

        Raises:
            requests.HTTPError: Raised if the HTTP request fails or the server returns an unsuccessful status code.

        Tags:
            get, video, status, api
        """
        url = f"{self.base_url}/v1/video_status.get"
        query_params = {k: v for k, v in [("video_id", video_id)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.get_v1_voice_list,
            self.get_v1_avatar_list,
            self.get_v2_voices,
            self.get_v2_avatars,
            self.get_v1_video_list,
            self.post_v2_video_generate,
            self.delete_v1_video,
            self.get_v2_templates,
            self.get_v2_template_by_id,
            self.post_v2_template_generate_by_id,
            self.get_v2_video_translate_target_languages,
            self.post_v2_video_translate,
            self.get_v2_video_translate_status_by_id,
            self.post_streaming_new,
            self.get_streaming_list,
            self.post_streaming_ice,
            self.post_streaming_task,
            self.post_streaming_stop,
            self.post_streaming_interrupt,
            self.post_streaming_create_token,
            self.get_streaming_avatar_list,
            self.get_v1_webhook_list,
            self.post_v1_webhook_endpoint_add,
            self.delete_v1_webhook_endpoint_by_id,
            self.get_v1_webhook_endpoint_list,
            self.get_v1_talking_photo_list,
            self.delete_v2_talking_photo_by_id,
            self.post_personalized_video_add_contact,
            self.get_personalized_video_audience_detail,
            self.get_personalized_video_project_detail,
            self.get_v2_user_remaining_quota,
            self.post_v1_asset_upload,
            self.get_v1_video_status,
        ]
