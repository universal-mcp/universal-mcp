from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class MailchimpApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="mailchimp", integration=integration, **kwargs)
        self.base_url = "https://us6.api.mailchimp.com/3.0"

    def root_list_resources(self, fields=None, exclude_fields=None) -> dict[str, Any]:
        """
        Lists available resources by making a GET request to the base URL.

        Args:
            fields: Optional; specific fields to include in the response.
            exclude_fields: Optional; specific fields to exclude from the response.

        Returns:
            Dictionary containing the available resources from the API response.

        Raises:
            HTTPError: Raised when the HTTP request returns an unsuccessful status code.

        Tags:
            list, resources, api, get, root
        """
        url = f"{self.base_url}/"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def activity_feed_get_latest_chimp_chatter(
        self, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Fetches the latest Chimp Chatter from the activity feed.

        Args:
            count: Optional number of items to fetch.
            offset: Optional offset for pagination.

        Returns:
            A dictionary containing the latest Chimp Chatter data.

        Raises:
            requests.HTTPError: Raised if the HTTP request fails with a status code indicating an error.

        Tags:
            fetch, scrape, async-optional, feed-management
        """
        url = f"{self.base_url}/activity-feed/chimp-chatter"
        query_params = {
            k: v for k, v in [("count", count), ("offset", offset)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def account_exports_list_for_given_account(
        self, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of account export jobs for the current account, with optional filtering and pagination.

        Args:
            fields: Optional[list or str]. Specific fields to include in the response for each export job.
            exclude_fields: Optional[list or str]. Fields to exclude from the response for each export job.
            count: Optional[int]. Number of records to return per page.
            offset: Optional[int]. Number of records to skip for pagination.

        Returns:
            dict: A dictionary containing details of the account export jobs matching the query parameters.

        Raises:
            requests.HTTPError: If the HTTP request to the API endpoint fails or returns an error status code.

        Tags:
            list, account-exports, management, batch, api
        """
        url = f"{self.base_url}/account-exports"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def account_exports_create_new_export(
        self, include_stages, since_timestamp=None
    ) -> dict[str, Any]:
        """
        Creates a new account export job with configurable stages and an optional starting timestamp.

        Args:
            include_stages: list: List of stage names to include in the export. Required.
            since_timestamp: str or None: Optional ISO 8601 timestamp string. Only data updated since this timestamp will be included in the export. If None, all data will be exported.

        Returns:
            dict: JSON response from the server describing the newly created export job.

        Raises:
            ValueError: If the required parameter 'include_stages' is not provided (i.e., is None).
            requests.HTTPError: If the HTTP request fails or the server responds with an error status.

        Tags:
            create, account-exports, start, async-job, management
        """
        if include_stages is None:
            raise ValueError("Missing required parameter 'include_stages'")
        request_body = {
            "include_stages": include_stages,
            "since_timestamp": since_timestamp,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/account-exports"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def account_export_info(
        self, export_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific account export.

        Args:
            export_id: The unique identifier of the account export to retrieve information for.
            fields: Optional. A comma-separated list of fields to include in the response.
            exclude_fields: Optional. A comma-separated list of fields to exclude from the response.

        Returns:
            A dictionary containing the account export information.

        Raises:
            ValueError: Raised when the required parameter 'export_id' is None.
            HTTPError: Raised when the HTTP request fails or returns an error status code.

        Tags:
            retrieve, export, account, info, api
        """
        if export_id is None:
            raise ValueError("Missing required parameter 'export_id'")
        url = f"{self.base_url}/account-exports/{export_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def authorized_apps_list_connected_applications(
        self, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of connected authorized applications with optional filtering and pagination.

        Args:
            fields: Optional[str]. Comma-separated list of fields to include in the response for each authorized application.
            exclude_fields: Optional[str]. Comma-separated list of fields to exclude from the response.
            count: Optional[int]. Number of authorized applications to return in the response.
            offset: Optional[int]. Number of records to skip for pagination.

        Returns:
            dict[str, Any]: A dictionary representing the JSON response containing the list of connected authorized applications and related metadata.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.

        Tags:
            list, authorized-apps, management, pagination
        """
        url = f"{self.base_url}/authorized-apps"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def authorized_apps_get_info(
        self, app_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieve detailed information about an authorized application by its ID.

        Args:
            app_id: str. The unique identifier of the authorized application to retrieve information for.
            fields: Optional[str]. Comma-separated list of fields to include in the response. If None, all fields are included.
            exclude_fields: Optional[str]. Comma-separated list of fields to exclude from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: A dictionary containing information about the specified authorized application.

        Raises:
            ValueError: Raised if 'app_id' is None.
            requests.exceptions.HTTPError: Raised if the HTTP request to fetch application information fails.

        Tags:
            get-info, authorized-apps, management
        """
        if app_id is None:
            raise ValueError("Missing required parameter 'app_id'")
        url = f"{self.base_url}/authorized-apps/{app_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_list_summary(
        self,
        count=None,
        offset=None,
        fields=None,
        exclude_fields=None,
        before_create_time=None,
        since_create_time=None,
        before_start_time=None,
        since_start_time=None,
        status=None,
    ) -> dict[str, Any]:
        """
        Retrieves a summary list of automation workflows based on optional filtering, pagination, and field selection criteria.

        Args:
            count: Optional integer specifying the maximum number of automations to return.
            offset: Optional integer determining the number of items to skip before starting to collect the result set.
            fields: Optional comma-separated string specifying fields to include in the response.
            exclude_fields: Optional comma-separated string specifying fields to exclude from the response.
            before_create_time: Optional ISO 8601 date string; only automations created before this time are returned.
            since_create_time: Optional ISO 8601 date string; only automations created since this time are returned.
            before_start_time: Optional ISO 8601 date string; only automations that started before this time are returned.
            since_start_time: Optional ISO 8601 date string; only automations that started since this time are returned.
            status: Optional string filter to return automations with a specific status (e.g., 'running', 'paused', etc.).

        Returns:
            A dictionary containing the list of automation workflows and associated metadata, formatted as returned by the API.

        Raises:
            HTTPError: If the HTTP request to the automations endpoint returns an unsuccessful status code.

        Tags:
            list, summary, automations, management, filter
        """
        url = f"{self.base_url}/automations"
        query_params = {
            k: v
            for k, v in [
                ("count", count),
                ("offset", offset),
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("before_create_time", before_create_time),
                ("since_create_time", since_create_time),
                ("before_start_time", before_start_time),
                ("since_start_time", since_start_time),
                ("status", status),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_create_classic(
        self, recipients, trigger_settings, settings=None
    ) -> dict[str, Any]:
        """
        Creates a classic automation by sending a POST request with the specified recipients and trigger settings.

        Args:
            recipients: A list or object specifying the intended recipients for the automation. Required.
            trigger_settings: A dictionary or object defining the trigger configuration for the automation. Required.
            settings: Optional settings to further configure the automation; can be None if not needed.

        Returns:
            A dictionary representing the JSON response from the API after creating the automation.

        Raises:
            ValueError: Raised if 'recipients' or 'trigger_settings' is not provided.
            requests.HTTPError: Raised if the HTTP request to create the automation fails (non-2xx status code).

        Tags:
            create, automation, classic, api
        """
        if recipients is None:
            raise ValueError("Missing required parameter 'recipients'")
        if trigger_settings is None:
            raise ValueError("Missing required parameter 'trigger_settings'")
        request_body = {
            "recipients": recipients,
            "settings": settings,
            "trigger_settings": trigger_settings,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/automations"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_get_classic_workflow_info(
        self, workflow_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves information about a classic automation workflow by its unique workflow ID.

        Args:
            workflow_id: The unique identifier of the workflow to retrieve.
            fields: Optional; a comma-separated list of fields to include in the response. Defaults to None.
            exclude_fields: Optional; a comma-separated list of fields to exclude from the response. Defaults to None.

        Returns:
            A dictionary containing details of the specified automation workflow.

        Raises:
            ValueError: Raised if 'workflow_id' is None.
            HTTPError: Raised if the HTTP request to the API fails (non-2xx response).

        Tags:
            get, automation, workflow, management
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        url = f"{self.base_url}/automations/{workflow_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_pause_workflow_emails(self, workflow_id) -> Any:
        """
        Pauses all workflow emails for a specified automation workflow.

        Args:
            workflow_id: The unique identifier of the automation workflow whose emails should be paused.

        Returns:
            A dictionary containing the API response with the status or details of the pause action.

        Raises:
            ValueError: Raised if the 'workflow_id' parameter is None.
            requests.HTTPError: Raised if the HTTP request to pause emails fails.

        Tags:
            pause, workflow, emails, async-job, automations
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        url = f"{self.base_url}/automations/{workflow_id}/actions/pause-all-emails"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_start_all_emails(self, workflow_id) -> Any:
        """
        Starts all email actions within the specified automation workflow.

        Args:
            workflow_id: The unique identifier of the automation workflow whose emails should be started.

        Returns:
            A dictionary containing the server's JSON response to the start-all-emails action.

        Raises:
            ValueError: Raised if 'workflow_id' is None.
            requests.HTTPError: Raised if the HTTP request to start emails fails.

        Tags:
            start, automations, emails, management
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        url = f"{self.base_url}/automations/{workflow_id}/actions/start-all-emails"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_archive_action(self, workflow_id) -> Any:
        """
        Archives an automation workflow by sending a POST request to the specified API endpoint.

        Args:
            workflow_id: The unique identifier of the automation workflow to be archived.

        Returns:
            dict: The JSON response from the API containing the result of the archive action.

        Raises:
            ValueError: If 'workflow_id' is None.
            HTTPError: If the HTTP request to the API fails.

        Tags:
            archive, automation, management, api
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        url = f"{self.base_url}/automations/{workflow_id}/actions/archive"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_get_classic_workflow_emails(self, workflow_id) -> dict[str, Any]:
        """
        Retrieves the list of emails associated with a classic workflow for a given workflow ID.

        Args:
            workflow_id: The unique identifier of the workflow for which emails are to be fetched.

        Returns:
            A dictionary containing details of the emails linked to the specified workflow.

        Raises:
            ValueError: Raised if the 'workflow_id' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the API endpoint returns an unsuccessful status code.

        Tags:
            fetch, list, emails, workflow, api
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        url = f"{self.base_url}/automations/{workflow_id}/emails"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_get_email_info(
        self, workflow_id, workflow_email_id
    ) -> dict[str, Any]:
        """
        Retrieves information about a specific email within a workflow automation, given the workflow and email identifiers.

        Args:
            workflow_id: The unique identifier of the workflow containing the email.
            workflow_email_id: The unique identifier of the email within the specified workflow.

        Returns:
            A dictionary containing details about the specified workflow email.

        Raises:
            ValueError: Raised if either 'workflow_id' or 'workflow_email_id' is not provided (i.e., is None).
            requests.HTTPError: Raised if the HTTP request to the API fails.

        Tags:
            get, email, automation, management
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        if workflow_email_id is None:
            raise ValueError("Missing required parameter 'workflow_email_id'")
        url = f"{self.base_url}/automations/{workflow_id}/emails/{workflow_email_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_delete_workflow_email(self, workflow_id, workflow_email_id) -> Any:
        """
        Deletes a specific email from a workflow in the automations system.

        Args:
            workflow_id: The unique identifier of the workflow containing the email to be deleted.
            workflow_email_id: The unique identifier of the workflow email to delete.

        Returns:
            A dictionary containing the API response data after the workflow email is deleted.

        Raises:
            ValueError: If 'workflow_id' or 'workflow_email_id' is None.
            requests.HTTPError: If the HTTP request to delete the workflow email fails.

        Tags:
            delete, workflow, email, automations, api
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        if workflow_email_id is None:
            raise ValueError("Missing required parameter 'workflow_email_id'")
        url = f"{self.base_url}/automations/{workflow_id}/emails/{workflow_email_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_update_workflow_email(
        self, workflow_id, workflow_email_id, settings=None, delay=None
    ) -> dict[str, Any]:
        """
        Updates the settings and delay of a specific workflow email in an automation workflow.

        Args:
            workflow_id: str. Unique identifier of the automation workflow to update.
            workflow_email_id: str. Unique identifier of the workflow email to be updated.
            settings: dict or None. Optional settings to update for the workflow email.
            delay: int or None. Optional delay, in seconds, before sending the workflow email.

        Returns:
            dict[str, Any]: The JSON response from the API after updating the workflow email.

        Raises:
            ValueError: If 'workflow_id' or 'workflow_email_id' is not provided.
            HTTPError: If the API request fails or returns an unsuccessful status code.

        Tags:
            update, workflow, email, automation, management
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        if workflow_email_id is None:
            raise ValueError("Missing required parameter 'workflow_email_id'")
        request_body = {
            "settings": settings,
            "delay": delay,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/automations/{workflow_id}/emails/{workflow_email_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_list_queue_emails(
        self, workflow_id, workflow_email_id
    ) -> dict[str, Any]:
        """
        Retrieves the list of queued emails for a specific workflow email in an automation.

        Args:
            workflow_id: str. The unique identifier of the workflow containing the email queue.
            workflow_email_id: str. The unique identifier of the workflow email whose queue will be listed.

        Returns:
            dict[str, Any]: A dictionary containing the details of the queued emails for the specified workflow email.

        Raises:
            ValueError: Raised if either 'workflow_id' or 'workflow_email_id' is None.
            HTTPError: Raised if the HTTP GET request to the API fails or returns an unsuccessful status code.

        Tags:
            list, queue, emails, automation
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        if workflow_email_id is None:
            raise ValueError("Missing required parameter 'workflow_email_id'")
        url = f"{self.base_url}/automations/{workflow_id}/emails/{workflow_email_id}/queue"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_add_subscriber_to_workflow_email(
        self, workflow_id, workflow_email_id, request_body=None
    ) -> dict[str, Any]:
        """
        Adds a subscriber to a specific workflow email queue in the automations system by sending a POST request.

        Args:
            workflow_id: str. The unique identifier of the workflow to which the subscriber will be added.
            workflow_email_id: str. The unique identifier of the workflow email where the subscriber should be queued.
            request_body: dict or None. Optional data to include in the request payload, such as subscriber details.

        Returns:
            dict[str, Any]: The JSON response from the server containing the results of the add-subscriber operation.

        Raises:
            ValueError: Raised if 'workflow_id' or 'workflow_email_id' is None.
            requests.HTTPError: Raised if the HTTP request returns an unsuccessful status code.

        Tags:
            add, subscriber, automations, workflow, email, api
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        if workflow_email_id is None:
            raise ValueError("Missing required parameter 'workflow_email_id'")
        url = f"{self.base_url}/automations/{workflow_id}/emails/{workflow_email_id}/queue"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_classic_automation_subscriber_info(
        self, workflow_id, workflow_email_id, subscriber_hash
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific subscriber in a classic automation email workflow.

        Args:
            workflow_id: str. The unique identifier for the automation workflow.
            workflow_email_id: str. The unique identifier for the specific email within the automation workflow.
            subscriber_hash: str. The MD5 hash of the subscriber's lowercase email address.

        Returns:
            dict. A dictionary containing information about the subscriber's status and details within the specified automation email.

        Raises:
            ValueError: Raised if any of 'workflow_id', 'workflow_email_id', or 'subscriber_hash' is None.
            requests.HTTPError: Raised if the HTTP request to the automation API fails or returns a non-successful status code.

        Tags:
            retrieve, subscriber-info, automation, classic, api
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        if workflow_email_id is None:
            raise ValueError("Missing required parameter 'workflow_email_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/automations/{workflow_id}/emails/{workflow_email_id}/queue/{subscriber_hash}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_pause_automated_email(self, workflow_id, workflow_email_id) -> Any:
        """
        Pauses an automated email within a specified workflow by sending a POST request to the automation API.

        Args:
            workflow_id: The unique identifier of the workflow containing the automated email to be paused.
            workflow_email_id: The unique identifier of the automated email to pause within the specified workflow.

        Returns:
            A JSON object containing the response from the API after attempting to pause the automated email.

        Raises:
            ValueError: Raised if 'workflow_id' or 'workflow_email_id' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an error status.

        Tags:
            pause, automated-email, workflow, api, management
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        if workflow_email_id is None:
            raise ValueError("Missing required parameter 'workflow_email_id'")
        url = f"{self.base_url}/automations/{workflow_id}/emails/{workflow_email_id}/actions/pause"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_start_automated_email(self, workflow_id, workflow_email_id) -> Any:
        """
        Starts an automated email within a specified workflow using the provided workflow and email identifiers.

        Args:
            workflow_id: The unique identifier of the workflow containing the email to be started.
            workflow_email_id: The unique identifier of the email within the workflow to start.

        Returns:
            Parsed JSON response from the API indicating the status or result of the start email action.

        Raises:
            ValueError: Raised if 'workflow_id' or 'workflow_email_id' is not provided.
            requests.HTTPError: Raised if the API response indicates an unsuccessful HTTP status.

        Tags:
            start, automations, email, async-job, api
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        if workflow_email_id is None:
            raise ValueError("Missing required parameter 'workflow_email_id'")
        url = f"{self.base_url}/automations/{workflow_id}/emails/{workflow_email_id}/actions/start"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_get_removed_subscribers(self, workflow_id) -> dict[str, Any]:
        """
        Retrieves the list of subscribers who have been removed from a specified automation workflow.

        Args:
            workflow_id: The unique identifier of the automation workflow for which to retrieve removed subscribers.

        Returns:
            A dictionary containing data about the removed subscribers for the given workflow.

        Raises:
            ValueError: Raised if 'workflow_id' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            get, removed-subscribers, automation, api
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        url = f"{self.base_url}/automations/{workflow_id}/removed-subscribers"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_remove_subscriber_from_workflow(
        self, workflow_id, request_body=None
    ) -> dict[str, Any]:
        """
        Removes a subscriber from a specified automation workflow.

        Args:
            workflow_id: str. The unique identifier of the workflow from which the subscriber will be removed. Must not be None.
            request_body: Optional[dict]. The request payload with the details of the subscriber to remove. Defaults to None.

        Returns:
            dict: The API response as a dictionary containing the result of the removal operation.

        Raises:
            ValueError: Raised when the required parameter 'workflow_id' is None.
            requests.HTTPError: Raised if the HTTP request to the API results in an error response.

        Tags:
            automations, remove, subscriber-management, api
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        url = f"{self.base_url}/automations/{workflow_id}/removed-subscribers"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def automations_get_removed_subscriber_info(
        self, workflow_id, subscriber_hash
    ) -> dict[str, Any]:
        """
        Retrieves information about a subscriber who was removed from a specific automation workflow.

        Args:
            workflow_id: The unique identifier of the automation workflow from which the subscriber was removed.
            subscriber_hash: The unique hash identifying the removed subscriber within the workflow.

        Returns:
            A dictionary containing details about the removed subscriber and their removal status.

        Raises:
            ValueError: Raised if 'workflow_id' or 'subscriber_hash' is None.
            requests.HTTPError: Raised if the HTTP request to the server fails or returns an error status.

        Tags:
            get, subscriber, async-job, management
        """
        if workflow_id is None:
            raise ValueError("Missing required parameter 'workflow_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/automations/{workflow_id}/removed-subscribers/{subscriber_hash}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def batches_list_requests_summary(
        self, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a summary of existing batch requests with optional field selection, exclusion, pagination, and filtering.

        Args:
            fields: Optional list of specific fields to include in the response.
            exclude_fields: Optional list of specific fields to exclude from the response.
            count: Optional integer specifying the number of batch records to return.
            offset: Optional integer indicating the starting position for the batch list.

        Returns:
            A dictionary containing the JSON response with a summary of batch requests.

        Raises:
            HTTPError: If the HTTP request to the batch requests endpoint fails or returns an error status code.

        Tags:
            list, batches, requests, summary, api
        """
        url = f"{self.base_url}/batches"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def batches_start_operation_process(self, operations) -> dict[str, Any]:
        """
        Starts a batch operation by sending the given operations to the remote service and returns the operation response as a dictionary.

        Args:
            operations: A list or collection of operation specifications to be executed in the batch.

        Returns:
            dict[str, Any]: The response from the remote service as a dictionary containing batch operation details or status.

        Raises:
            ValueError: If the 'operations' parameter is None.
            HTTPError: If the HTTP request to the remote service fails or returns a non-success status code.

        Tags:
            batches, start, async-job, management
        """
        if operations is None:
            raise ValueError("Missing required parameter 'operations'")
        request_body = {
            "operations": operations,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/batches"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def batches_get_operation_status(
        self, batch_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves the status and details of a batch operation using its batch ID.

        Args:
            batch_id: The unique identifier for the batch operation to retrieve status for. Must not be None.
            fields: Optional comma-separated string of fields to include in the response.
            exclude_fields: Optional comma-separated string of fields to exclude from the response.

        Returns:
            A dictionary containing the batch operation status and related details as returned by the API.

        Raises:
            ValueError: If 'batch_id' is None.
            requests.HTTPError: If the HTTP request for batch status information fails.

        Tags:
            get, batch, status, ai, management
        """
        if batch_id is None:
            raise ValueError("Missing required parameter 'batch_id'")
        url = f"{self.base_url}/batches/{batch_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def batches_stop_request(self, batch_id) -> Any:
        """
        Stops a running batch job by sending a DELETE request to the batch endpoint.

        Args:
            batch_id: The unique identifier of the batch job to stop.

        Returns:
            The JSON response from the API indicating the result of the stop request.

        Raises:
            ValueError: If 'batch_id' is None.
            requests.HTTPError: If the HTTP request to stop the batch job fails.

        Tags:
            stop, batch, async-job, management
        """
        if batch_id is None:
            raise ValueError("Missing required parameter 'batch_id'")
        url = f"{self.base_url}/batches/{batch_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def batch_webhooks_list_webhooks(
        self, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of batch webhooks with optional filtering and pagination.

        Args:
            fields: Optional[str]. Comma-separated list of fields to include in the results. If None, all fields are included.
            exclude_fields: Optional[str]. Comma-separated list of fields to exclude from the results. If None, no fields are excluded.
            count: Optional[int]. The number of records to return. If None, the default count is used.
            offset: Optional[int]. The number of records to skip before starting to return results. Useful for pagination.

        Returns:
            dict[str, Any]: A dictionary representing the JSON response containing the list of batch webhooks.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request to the webhooks API fails or returns an unsuccessful status code.

        Tags:
            list, batch, webhooks, api, management
        """
        url = f"{self.base_url}/batch-webhooks"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def batch_webhooks_add_webhook(self, url, enabled=None) -> dict[str, Any]:
        """
        Adds a new webhook to the batch webhooks endpoint.

        Args:
            url: The URL for the webhook. This is a required parameter.
            enabled: A boolean indicating whether the webhook is enabled. If not provided, defaults to None.

        Returns:
            A dictionary containing details about the newly added webhook.

        Raises:
            ValueError: Raised if the required 'url' parameter is missing.
            HTTPError: Raised if the HTTP request encounters an error.

        Tags:
            add, webhook, batch
        """
        if url is None:
            raise ValueError("Missing required parameter 'url'")
        request_body = {
            "url": url,
            "enabled": enabled,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/batch-webhooks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def batch_webhooks_get_info(
        self, batch_webhook_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves information about a specific batch webhook.

        Args:
            batch_webhook_id: The unique identifier for the batch webhook to retrieve.
            fields: Optional. Comma-separated list of fields to include in the response.
            exclude_fields: Optional. Comma-separated list of fields to exclude from the response.

        Returns:
            A dictionary containing information about the requested batch webhook.

        Raises:
            ValueError: When the required 'batch_webhook_id' parameter is None.
            HTTPError: When the API request fails.

        Tags:
            get, retrieve, info, batch, webhook, api
        """
        if batch_webhook_id is None:
            raise ValueError("Missing required parameter 'batch_webhook_id'")
        url = f"{self.base_url}/batch-webhooks/{batch_webhook_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def batch_webhooks_update_webhook(
        self, batch_webhook_id, url=None, enabled=None
    ) -> dict[str, Any]:
        """
        Updates the configuration of a batch webhook by ID, modifying its URL and/or enabled status.

        Args:
            batch_webhook_id: str. Unique identifier of the batch webhook to update. Must not be None.
            url: str or None. The new URL to associate with the webhook. If omitted, the existing URL is unchanged.
            enabled: bool or None. If set, enables or disables the webhook. If omitted, the enabled state is unchanged.

        Returns:
            dict[str, Any]: The updated webhook configuration as returned by the server.

        Raises:
            ValueError: If 'batch_webhook_id' is None.
            requests.HTTPError: If the HTTP request fails or the server returns an error status code.

        Tags:
            update, webhook, batch, management
        """
        if batch_webhook_id is None:
            raise ValueError("Missing required parameter 'batch_webhook_id'")
        request_body = {
            "url": url,
            "enabled": enabled,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/batch-webhooks/{batch_webhook_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def batch_webhooks_remove_webhook(self, batch_webhook_id) -> Any:
        """
        Removes a webhook associated with a given batch webhook ID.

        Args:
            batch_webhook_id: The unique identifier of the batch webhook to be removed.

        Returns:
            A dictionary containing the server's response data from the webhook removal.

        Raises:
            ValueError: If 'batch_webhook_id' is None.
            requests.HTTPError: If the HTTP request to remove the webhook fails with a non-success status code.

        Tags:
            remove, webhook, batch, management
        """
        if batch_webhook_id is None:
            raise ValueError("Missing required parameter 'batch_webhook_id'")
        url = f"{self.base_url}/batch-webhooks/{batch_webhook_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def template_folders_list_folders(
        self, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of template folders with optional filtering and pagination parameters.

        Args:
            fields: Optional; A comma-separated string of fields to include in the response.
            exclude_fields: Optional; A comma-separated string of fields to exclude from the response.
            count: Optional; The number of records to return in the response.
            offset: Optional; The number of records to skip for pagination purposes.

        Returns:
            A dictionary containing the list of template folders and associated metadata as returned by the API.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails or returns a non-success status code.

        Tags:
            list, template-folders, api, management
        """
        url = f"{self.base_url}/template-folders"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def template_folders_add_new_folder(self, request_body=None) -> dict[str, Any]:
        """
        Creates a new template folder using the provided request body and returns the server's response.

        Args:
            request_body: Optional; dict containing the data to create the new template folder. Defaults to None.

        Returns:
            dict: The JSON response from the server representing the newly created template folder.

        Raises:
            requests.exceptions.HTTPError: If the server returns an unsuccessful status code.

        Tags:
            add, template-folder, api, post
        """
        url = f"{self.base_url}/template-folders"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def template_folders_get_info(
        self, folder_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves information about a specific template folder.

        Args:
            folder_id: The unique identifier of the template folder to retrieve information for.
            fields: Optional. A comma-separated list of fields to include in the response.
            exclude_fields: Optional. A comma-separated list of fields to exclude from the response.

        Returns:
            A dictionary containing information about the specified template folder.

        Raises:
            ValueError: Raised when the required 'folder_id' parameter is None.
            HTTPError: Raised when the API request fails.

        Tags:
            get, retrieve, template, folder, information
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/template-folders/{folder_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def template_folders_update_specific_folder(
        self, folder_id, request_body=None
    ) -> dict[str, Any]:
        """
        Updates a specific template folder with new data using a PATCH request.

        Args:
            folder_id: str. The unique identifier of the template folder to update.
            request_body: dict or None. The data payload to update the folder with. If None, no fields are updated.

        Returns:
            dict. The updated template folder data returned from the API.

        Raises:
            ValueError: Raised if 'folder_id' is None.
            requests.HTTPError: Raised if the PATCH request fails or the server returns an error status code.

        Tags:
            update, template-folder, api, patch, management
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/template-folders/{folder_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def template_folders_delete_specific_folder(self, folder_id) -> Any:
        """
        Deletes a specific template folder identified by its folder_id.

        Args:
            folder_id: The unique identifier of the template folder to be deleted.

        Returns:
            The parsed JSON response from the server after successful deletion of the folder.

        Raises:
            ValueError: Raised if 'folder_id' is None.
            requests.HTTPError: Raised if the HTTP request to delete the folder fails.

        Tags:
            delete, template-folder, api, management
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/template-folders/{folder_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaign_folders_list_campaign_folders(
        self, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of campaign folders with optional filtering and pagination.

        Args:
            fields: Optional[str]. Comma-separated list of fields to include in the response.
            exclude_fields: Optional[str]. Comma-separated list of fields to exclude from the response.
            count: Optional[int]. The number of records to return in the response.
            offset: Optional[int]. Number of records to skip for pagination.

        Returns:
            dict[str, Any]: A dictionary containing the API response with campaign folder data.

        Raises:
            requests.HTTPError: If the HTTP request fails or the response status code indicates an error.

        Tags:
            list, campaign-folders, api, management
        """
        url = f"{self.base_url}/campaign-folders"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaign_folders_add_new_folder(self, request_body=None) -> dict[str, Any]:
        """
        Creates a new campaign folder by sending a POST request with the provided data.

        Args:
            request_body: Optional; dict containing the data for the new campaign folder. Defaults to None.

        Returns:
            dict: The JSON response from the server containing details of the newly created campaign folder.

        Raises:
            HTTPError: If the HTTP request returned an unsuccessful status code.

        Tags:
            create, campaign-folder, api, post
        """
        url = f"{self.base_url}/campaign-folders"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaign_folders_get_folder_info(
        self, folder_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves information about a specific campaign folder by its unique identifier.

        Args:
            folder_id: The unique identifier of the campaign folder to retrieve information for. Must not be None.
            fields: Comma-separated list of fields to include in the response. Optional.
            exclude_fields: Comma-separated list of fields to exclude from the response. Optional.

        Returns:
            A dictionary containing the campaign folder's information as returned by the API.

        Raises:
            ValueError: If 'folder_id' is None.
            requests.HTTPError: If the API request returns an unsuccessful HTTP status code.

        Tags:
            get, campaign-folder, ai, management
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/campaign-folders/{folder_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaign_folders_update_specific_folder(
        self, folder_id, request_body=None
    ) -> dict[str, Any]:
        """
        Updates a specific campaign folder by ID.

        Args:
            folder_id: The unique identifier of the campaign folder to update.
            request_body: Optional dictionary containing the updated folder information.

        Returns:
            A dictionary containing the updated campaign folder data.

        Raises:
            ValueError: Raised when folder_id is None.
            HTTPError: Raised when the HTTP request fails.

        Tags:
            update, campaign, folder, management
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/campaign-folders/{folder_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaign_folders_delete_folder(self, folder_id) -> Any:
        """
        Deletes a campaign folder by its unique identifier.

        Args:
            folder_id: The unique identifier of the campaign folder to be deleted.

        Returns:
            A JSON object containing the response from the delete operation.

        Raises:
            ValueError: Raised when 'folder_id' is None.
            requests.HTTPError: Raised if the HTTP request to delete the folder fails.

        Tags:
            delete, campaign-folder, management
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/campaign-folders/{folder_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_get_all(
        self,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        type=None,
        status=None,
        before_send_time=None,
        since_send_time=None,
        before_create_time=None,
        since_create_time=None,
        list_id=None,
        folder_id=None,
        member_id=None,
        sort_field=None,
        sort_dir=None,
        include_resend_shortcut_eligibility=None,
    ) -> dict[str, Any]:
        """
        Retrieves all campaigns from the API with optional filtering and pagination.

        Args:
            fields: Comma-separated string of fields to include in the response.
            exclude_fields: Comma-separated string of fields to exclude from the response.
            count: Number of records to return.
            offset: Number of records to skip.
            type: Filter by campaign type.
            status: Filter by campaign status.
            before_send_time: Filter campaigns sent before this timestamp.
            since_send_time: Filter campaigns sent after this timestamp.
            before_create_time: Filter campaigns created before this timestamp.
            since_create_time: Filter campaigns created after this timestamp.
            list_id: Filter by the list ID.
            folder_id: Filter by the folder ID.
            member_id: Filter by the member ID.
            sort_field: Field to sort results by.
            sort_dir: Direction to sort results (asc or desc).
            include_resend_shortcut_eligibility: Include information about resend eligibility.

        Returns:
            A dictionary containing campaign data and metadata.

        Raises:
            HTTPError: Raised when the API request fails due to an HTTP error.

        Tags:
            get, list, campaigns, retrieve, filter, paginate, important
        """
        url = f"{self.base_url}/campaigns"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("type", type),
                ("status", status),
                ("before_send_time", before_send_time),
                ("since_send_time", since_send_time),
                ("before_create_time", before_create_time),
                ("since_create_time", since_create_time),
                ("list_id", list_id),
                ("folder_id", folder_id),
                ("member_id", member_id),
                ("sort_field", sort_field),
                ("sort_dir", sort_dir),
                (
                    "include_resend_shortcut_eligibility",
                    include_resend_shortcut_eligibility,
                ),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_create_new_mailchimp_campaign(
        self,
        type,
        recipients=None,
        settings=None,
        variate_settings=None,
        tracking=None,
        rss_opts=None,
        social_card=None,
        content_type=None,
    ) -> dict[str, Any]:
        """
        Creates a new Mailchimp campaign with the specified type and optional configuration settings.

        Args:
            type: str. The type of campaign to create. This parameter is required.
            recipients: Optional[dict]. A dictionary specifying the recipients for the campaign. Defaults to None.
            settings: Optional[dict]. A dictionary with settings for the campaign, such as subject line and sender details. Defaults to None.
            variate_settings: Optional[dict]. Additional settings for A/B or multivariate campaigns. Defaults to None.
            tracking: Optional[dict]. Tracking options for the campaign. Defaults to None.
            rss_opts: Optional[dict]. Options for RSS campaign content. Defaults to None.
            social_card: Optional[dict]. Social card configuration for campaign previews. Defaults to None.
            content_type: Optional[str]. The type of content for the campaign, such as 'template' or 'html'. Defaults to None.

        Returns:
            dict. The API response containing details of the created Mailchimp campaign.

        Raises:
            ValueError: If the required 'type' parameter is not provided.
            HTTPError: If the Mailchimp API request fails with a non-success response (triggered by response.raise_for_status()).

        Tags:
            create, campaign, mailchimp, api, management, important
        """
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        request_body = {
            "type": type,
            "recipients": recipients,
            "settings": settings,
            "variate_settings": variate_settings,
            "tracking": tracking,
            "rss_opts": rss_opts,
            "social_card": social_card,
            "content_type": content_type,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/campaigns"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_get_info(
        self,
        campaign_id,
        fields=None,
        exclude_fields=None,
        include_resend_shortcut_eligibility=None,
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific campaign, supporting optional field filtering and resend shortcut eligibility inclusion.

        Args:
            campaign_id: str. Unique identifier for the campaign to retrieve information for. Must not be None.
            fields: Optional[str]. Comma-separated list of campaign fields to include in the response. If not specified, all fields are returned.
            exclude_fields: Optional[str]. Comma-separated list of fields to exclude from the response.
            include_resend_shortcut_eligibility: Optional[bool]. If True, includes information about resend shortcut eligibility in the response.

        Returns:
            dict[str, Any]: A dictionary containing the campaign's information as returned by the API.

        Raises:
            ValueError: Raised if 'campaign_id' is None.
            requests.HTTPError: Raised if the underlying HTTP request to the API fails with an unsuccessful status code.

        Tags:
            get, campaign, info, api, management, important
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/campaigns/{campaign_id}"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                (
                    "include_resend_shortcut_eligibility",
                    include_resend_shortcut_eligibility,
                ),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_update_settings(
        self,
        campaign_id,
        settings,
        recipients=None,
        variate_settings=None,
        tracking=None,
        rss_opts=None,
        social_card=None,
    ) -> dict[str, Any]:
        """
        Updates the settings of an email campaign with the specified parameters.

        Args:
            campaign_id: str. The unique identifier for the campaign to update.
            settings: dict. A dictionary containing new settings for the campaign. Required.
            recipients: dict or None. Optional dictionary specifying recipient information for the campaign.
            variate_settings: dict or None. Optional dictionary specifying variate (A/B testing) settings.
            tracking: dict or None. Optional dictionary specifying tracking options.
            rss_opts: dict or None. Optional dictionary specifying RSS options.
            social_card: dict or None. Optional dictionary specifying social card parameters.

        Returns:
            dict. The JSON response containing details of the updated campaign.

        Raises:
            ValueError: Raised if 'campaign_id' or 'settings' is None.
            HTTPError: Raised if the HTTP request to update the campaign fails.

        Tags:
            update, campaign, settings, api, management
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if settings is None:
            raise ValueError("Missing required parameter 'settings'")
        request_body = {
            "recipients": recipients,
            "settings": settings,
            "variate_settings": variate_settings,
            "tracking": tracking,
            "rss_opts": rss_opts,
            "social_card": social_card,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/campaigns/{campaign_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_remove_campaign(self, campaign_id) -> Any:
        """
        Removes a campaign identified by the given campaign ID.

        Args:
            campaign_id: The unique identifier of the campaign to be removed. Must not be None.

        Returns:
            The response data as a JSON object if the campaign is successfully removed.

        Raises:
            ValueError: If 'campaign_id' is None.
            HTTPError: If the HTTP request to remove the campaign fails (non-2xx status code).

        Tags:
            remove, campaign, management, api
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/campaigns/{campaign_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_cancel_send_action(self, campaign_id) -> Any:
        """
        Cancels the scheduled sending of a campaign identified by its campaign ID.

        Args:
            campaign_id: The unique identifier of the campaign whose scheduled send action is to be canceled.

        Returns:
            A JSON-decoded response object containing the result of the cancel send action.

        Raises:
            ValueError: If campaign_id is None.
            requests.HTTPError: If the HTTP request to cancel the campaign send fails.

        Tags:
            cancel, campaigns, management
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/campaigns/{campaign_id}/actions/cancel-send"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_replicate_action(self, campaign_id) -> dict[str, Any]:
        """
        Replicates an existing campaign by sending a replicate action request to the API.

        Args:
            campaign_id: str. The unique identifier of the campaign to replicate. Must not be None.

        Returns:
            dict[str, Any]: The API response as a dictionary containing details of the replicated campaign.

        Raises:
            ValueError: Raised if 'campaign_id' is None.
            requests.HTTPError: Raised if the API request fails (e.g., network errors or non-successful HTTP response).

        Tags:
            replicate, campaign, api, action
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/campaigns/{campaign_id}/actions/replicate"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_send_action(self, campaign_id) -> Any:
        """
        Triggers the send action for a specified email campaign.

        Args:
            campaign_id: The unique identifier of the campaign to be sent.

        Returns:
            dict: The JSON response from the server containing the status or result of the send action.

        Raises:
            ValueError: Raised if the 'campaign_id' parameter is None.
            requests.HTTPError: Raised if the HTTP request to send the campaign fails with a bad status code.

        Tags:
            send, campaigns, actions, api
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/campaigns/{campaign_id}/actions/send"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_schedule_delivery(
        self, campaign_id, schedule_time, timewarp=None, batch_delivery=None
    ) -> Any:
        """
        Schedules the delivery of an email campaign at a specified time, with optional timewarp and batch delivery settings.

        Args:
            campaign_id: The unique identifier of the campaign to be scheduled.
            schedule_time: The scheduled delivery time for the campaign in the appropriate format required by the API (typically an ISO-formatted datetime string).
            timewarp: Optional; whether to use timewarp, aligning delivery to recipients' local times. Defaults to None.
            batch_delivery: Optional; enables batch delivery settings such as batch size or intervals. Defaults to None.

        Returns:
            dict: The API response as a dictionary containing details of the scheduled campaign delivery.

        Raises:
            ValueError: If 'campaign_id' or 'schedule_time' is None.
            HTTPError: If the API request fails or returns an error status code.

        Tags:
            schedule, campaign, delivery, async-job, email, management
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if schedule_time is None:
            raise ValueError("Missing required parameter 'schedule_time'")
        request_body = {
            "schedule_time": schedule_time,
            "timewarp": timewarp,
            "batch_delivery": batch_delivery,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/campaigns/{campaign_id}/actions/schedule"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_unschedule_action(self, campaign_id) -> Any:
        """
        Unschedules an active campaign by sending a POST request to the campaign's unschedule action endpoint.

        Args:
            campaign_id: The unique identifier of the campaign to be unscheduled.

        Returns:
            A dictionary containing the server's response to the unschedule action.

        Raises:
            ValueError: Raised when 'campaign_id' is None.
            requests.HTTPError: Raised if the HTTP request to the unschedule endpoint returns an unsuccessful status code.

        Tags:
            unschedule, campaign, action, api
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/campaigns/{campaign_id}/actions/unschedule"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_send_test_email(self, campaign_id, test_emails, send_type) -> Any:
        """
        Sends a test email for a specific campaign to a list of test email addresses.

        Args:
            campaign_id: The unique identifier for the campaign to send the test email from.
            test_emails: A list of email addresses to send the test email to.
            send_type: The type of test email to send (e.g., 'html', 'plain_text').

        Returns:
            The JSON response from the API with details about the test email operation.

        Raises:
            ValueError: Raised when any of the required parameters (campaign_id, test_emails, or send_type) is None.
            HTTPError: Raised when the API request fails (via raise_for_status()).

        Tags:
            send, test, email, campaign
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if test_emails is None:
            raise ValueError("Missing required parameter 'test_emails'")
        if send_type is None:
            raise ValueError("Missing required parameter 'send_type'")
        request_body = {
            "test_emails": test_emails,
            "send_type": send_type,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/campaigns/{campaign_id}/actions/test"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_pause_rss_campaign(self, campaign_id) -> Any:
        """
        Pauses an RSS campaign by sending a pause action request to the campaign API endpoint.

        Args:
            campaign_id: The unique identifier of the campaign to be paused.

        Returns:
            dict: The JSON response from the API containing the status and details of the pause action.

        Raises:
            ValueError: If 'campaign_id' is None.
            requests.HTTPError: If the HTTP request to pause the campaign fails with a non-success status code.

        Tags:
            pause, campaign, rss, api, management
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/campaigns/{campaign_id}/actions/pause"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_resume_rss_campaign(self, campaign_id) -> Any:
        """
        Resumes an RSS campaign with the specified ID.

        Args:
            campaign_id: The unique identifier of the RSS campaign to resume. Cannot be None.

        Returns:
            The JSON response from the API containing information about the resumed campaign.

        Raises:
            ValueError: Raised when campaign_id is None.
            HTTPError: Raised when the API request fails.

        Tags:
            resume, campaign, rss, action, management
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/campaigns/{campaign_id}/actions/resume"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_resend_action(
        self, campaign_id, shortcut_type=None
    ) -> dict[str, Any]:
        """
        Initiates a resend action for a specified campaign using the provided campaign ID and optional shortcut type.

        Args:
            campaign_id: str. Unique identifier of the campaign for which the resend action will be created. Must not be None.
            shortcut_type: Optional[str]. Type of shortcut action to use for resending, if applicable.

        Returns:
            dict[str, Any]: A dictionary containing the API response data for the resend action.

        Raises:
            ValueError: Raised if 'campaign_id' is None.
            requests.exceptions.HTTPError: Raised if the API response contains an HTTP error status.

        Tags:
            resend, campaign, action, async_job, api, management
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        request_body = {
            "shortcut_type": shortcut_type,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/campaigns/{campaign_id}/actions/create-resend"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_get_content(
        self, campaign_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves the content of a specific campaign, with optional field filtering.

        Args:
            campaign_id: str. The unique identifier for the campaign whose content is to be retrieved.
            fields: Optional[list[str]]. A list of specific fields to include in the response. If None, all fields are included.
            exclude_fields: Optional[list[str]]. A list of fields to exclude from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: The content data of the specified campaign as a dictionary.

        Raises:
            ValueError: Raised if 'campaign_id' is None.
            requests.HTTPError: Raised if the HTTP request to retrieve campaign content fails.

        Tags:
            get, campaign, content, api, management
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/campaigns/{campaign_id}/content"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_set_content(
        self,
        campaign_id,
        plain_text=None,
        html=None,
        url=None,
        template=None,
        archive=None,
        variate_contents=None,
    ) -> dict[str, Any]:
        """
        Updates the content of a specific campaign with provided data such as plain text, HTML, URL, template, archive, or variate content.

        Args:
            campaign_id: str. The unique identifier of the campaign whose content is to be set. Required.
            plain_text: str or None. Optional plain text version of the campaign content.
            html: str or None. Optional HTML content for the campaign.
            url: str or None. Optional URL pointing to the source of the campaign content.
            template: dict or None. Optional template details for the campaign.
            archive: str or None. Optional path or data for an archive to upload as content.
            variate_contents: dict or None. Optional content variations for A/B testing or similar purposes.

        Returns:
            dict. A JSON-decoded response from the API representing the updated campaign content.

        Raises:
            ValueError: If 'campaign_id' is not provided.
            requests.HTTPError: If the HTTP request fails or the API returns an error response.

        Tags:
            set-content, campaign-management, update, api, http
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        request_body = {
            "plain_text": plain_text,
            "html": html,
            "url": url,
            "template": template,
            "archive": archive,
            "variate_contents": variate_contents,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/campaigns/{campaign_id}/content"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_list_feedback(
        self, campaign_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves feedback information for a specific email campaign, with optional field filtering.

        Args:
            campaign_id: str. The unique identifier for the campaign whose feedback is to be retrieved.
            fields: Optional[list[str]]. A list of fields to include in the response. If specified, only these fields will be returned.
            exclude_fields: Optional[list[str]]. A list of fields to exclude from the response.

        Returns:
            dict[str, Any]: The API response containing the campaign's feedback information.

        Raises:
            ValueError: If 'campaign_id' is None.
            HTTPError: If the HTTP request to the feedback endpoint fails.

        Tags:
            list, feedback, campaign, ai
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/campaigns/{campaign_id}/feedback"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_add_feedback(
        self, campaign_id, message, block_id=None, is_complete=None
    ) -> dict[str, Any]:
        """
        Submit feedback for a specific campaign by sending a message and optional metadata.

        Args:
            campaign_id: str. The unique identifier of the campaign to which feedback is being added.
            message: str. The feedback message to submit for the campaign.
            block_id: Optional[str]. The identifier of a campaign block related to the feedback, if applicable.
            is_complete: Optional[bool]. Indicates whether this feedback marks the campaign as complete.

        Returns:
            dict[str, Any]: The JSON response from the API after submitting feedback.

        Raises:
            ValueError: If 'campaign_id' or 'message' is not provided.
            requests.HTTPError: If the API response contains an HTTP error status.

        Tags:
            feedback, campaign, submit, management, api
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if message is None:
            raise ValueError("Missing required parameter 'message'")
        request_body = {
            "block_id": block_id,
            "message": message,
            "is_complete": is_complete,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/campaigns/{campaign_id}/feedback"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_get_feedback_message(
        self, campaign_id, feedback_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves a specific feedback message for a given campaign, with optional field filtering.

        Args:
            campaign_id: str. Unique identifier for the campaign whose feedback message is to be fetched.
            feedback_id: str. Unique identifier for the feedback message to retrieve.
            fields: Optional[list[str]]. List of fields to include in the response. If None, all fields are included.
            exclude_fields: Optional[list[str]]. List of fields to exclude from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: The feedback message data as a dictionary.

        Raises:
            ValueError: If 'campaign_id' or 'feedback_id' is None.
            requests.HTTPError: If the HTTP request to the API fails.

        Tags:
            get, feedback, campaign, api, data-retrieval
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if feedback_id is None:
            raise ValueError("Missing required parameter 'feedback_id'")
        url = f"{self.base_url}/campaigns/{campaign_id}/feedback/{feedback_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_update_feedback_message(
        self, campaign_id, feedback_id, block_id=None, message=None, is_complete=None
    ) -> dict[str, Any]:
        """
        Updates the feedback message for a specified campaign and feedback entry.

        Args:
            campaign_id: str. Unique identifier for the campaign. Required.
            feedback_id: str. Unique identifier for the feedback entry. Required.
            block_id: Optional[str]. Identifier for the feedback block to update. If None, this field is not changed.
            message: Optional[str]. The new feedback message content. If None, this field is not changed.
            is_complete: Optional[bool]. Whether the feedback is marked as complete. If None, this field is not changed.

        Returns:
            dict[str, Any]: A dictionary containing the updated feedback information as returned by the API.

        Raises:
            ValueError: Raised if 'campaign_id' or 'feedback_id' is not provided.
            requests.HTTPError: Raised if the HTTP PATCH request to the API fails with an error status code.

        Tags:
            update, feedback, campaign, api
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if feedback_id is None:
            raise ValueError("Missing required parameter 'feedback_id'")
        request_body = {
            "block_id": block_id,
            "message": message,
            "is_complete": is_complete,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/campaigns/{campaign_id}/feedback/{feedback_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_remove_feedback_message(self, campaign_id, feedback_id) -> Any:
        """
        Removes a specific feedback message from a campaign.

        Args:
            campaign_id: The unique identifier of the campaign from which the feedback message will be removed.
            feedback_id: The unique identifier of the feedback message to remove.

        Returns:
            The parsed JSON response from the API indicating the result of the delete operation.

        Raises:
            ValueError: Raised if either 'campaign_id' or 'feedback_id' is None.
            requests.HTTPError: Raised if the HTTP DELETE request to the API fails.

        Tags:
            remove, feedback, campaign, api, management
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if feedback_id is None:
            raise ValueError("Missing required parameter 'feedback_id'")
        url = f"{self.base_url}/campaigns/{campaign_id}/feedback/{feedback_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def campaigns_get_send_checklist(
        self, campaign_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves the send checklist for a specified campaign, optionally filtering the response fields.

        Args:
            campaign_id: str. The unique identifier for the campaign whose send checklist is to be retrieved.
            fields: Optional[str or list of str]. Specific fields to include in the response. If not provided, all fields are returned.
            exclude_fields: Optional[str or list of str]. Specific fields to exclude from the response. If not provided, no fields are excluded.

        Returns:
            dict. The JSON response containing the send checklist details for the specified campaign.

        Raises:
            ValueError: Raised if 'campaign_id' is None.
            HTTPError: Raised if the HTTP request to the API fails (non-2xx response).

        Tags:
            get, campaign, checklist, api
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/campaigns/{campaign_id}/send-checklist"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def connected_sites_list_all(
        self, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of all connected sites with optional filtering, field selection, and pagination.

        Args:
            fields: Optional[str | list[str]]. A comma-separated string or list of fields to include in the response.
            exclude_fields: Optional[str | list[str]]. A comma-separated string or list of fields to exclude from the response.
            count: Optional[int]. The number of records to return in the response.
            offset: Optional[int]. The number of records to skip for pagination.

        Returns:
            dict[str, Any]: A dictionary containing details of connected sites as returned by the API.

        Raises:
            requests.HTTPError: If the underlying HTTP request fails or returns a non-successful status code.

        Tags:
            list, connected-sites, api, management
        """
        url = f"{self.base_url}/connected-sites"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def connected_sites_create_new_mailchimp_site(
        self, foreign_id, domain
    ) -> dict[str, Any]:
        """
        Creates a new connected site in Mailchimp with the specified foreign ID and domain.

        Args:
            foreign_id: str. The unique identifier for the site to be created. Must not be None.
            domain: str. The domain name associated with the new Mailchimp site. Must not be None.

        Returns:
            dict[str, Any]: A dictionary containing the API response data for the newly created connected site.

        Raises:
            ValueError: Raised if 'foreign_id' or 'domain' is None.
            requests.HTTPError: Raised if the HTTP request to the Mailchimp API fails.

        Tags:
            create, connected-sites, mailchimp, api
        """
        if foreign_id is None:
            raise ValueError("Missing required parameter 'foreign_id'")
        if domain is None:
            raise ValueError("Missing required parameter 'domain'")
        request_body = {
            "foreign_id": foreign_id,
            "domain": domain,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/connected-sites"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def connected_sites_get_info(
        self, connected_site_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieve detailed information for a specific connected site by ID, with optional field filtering.

        Args:
            connected_site_id: str. The unique identifier of the connected site to retrieve information for.
            fields: Optional[str or list of str]. Specific fields to include in the response. If None, all fields are included.
            exclude_fields: Optional[str or list of str]. Specific fields to omit from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: The JSON response containing details of the connected site.

        Raises:
            ValueError: If 'connected_site_id' is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status code.

        Tags:
            get, connected-site, info, api, management
        """
        if connected_site_id is None:
            raise ValueError("Missing required parameter 'connected_site_id'")
        url = f"{self.base_url}/connected-sites/{connected_site_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def connected_sites_remove_site(self, connected_site_id) -> Any:
        """
        Removes a connected site by its unique identifier.

        Args:
            connected_site_id: The unique identifier of the connected site to be removed. Must not be None.

        Returns:
            The response from the server as a deserialized JSON object containing the result of the removal operation.

        Raises:
            ValueError: If 'connected_site_id' is None.
            requests.HTTPError: If the HTTP request to remove the site fails.

        Tags:
            remove, connected-site, management, api
        """
        if connected_site_id is None:
            raise ValueError("Missing required parameter 'connected_site_id'")
        url = f"{self.base_url}/connected-sites/{connected_site_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def connected_sites_verify_script_installation(self, connected_site_id) -> Any:
        """
        Verifies whether the tracking script is properly installed on a specified connected site.

        Args:
            connected_site_id: The unique identifier of the connected site whose script installation is to be verified.

        Returns:
            dict: A JSON-decoded response containing the results of the verification.

        Raises:
            ValueError: If the required 'connected_site_id' parameter is not provided.
            requests.HTTPError: If the HTTP request to the verification endpoint fails or returns an error status.

        Tags:
            verify, connected-site, ai
        """
        if connected_site_id is None:
            raise ValueError("Missing required parameter 'connected_site_id'")
        url = f"{self.base_url}/connected-sites/{connected_site_id}/actions/verify-script-installation"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def conversations_get_all_conversations(
        self,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        has_unread_messages=None,
        list_id=None,
        campaign_id=None,
    ) -> dict[str, Any]:
        """
        Get all conversations from the API.

        Args:
            fields: A comma-separated string of fields to include in the response.
            exclude_fields: A comma-separated string of fields to exclude from the response.
            count: The number of records to return.
            offset: The number of records to skip.
            has_unread_messages: Filter conversations by whether they have unread messages.
            list_id: The unique ID for the list to filter conversations by.
            campaign_id: The unique ID for the campaign to filter conversations by.

        Returns:
            A dictionary containing the conversation data retrieved from the API.

        Raises:
            HTTPError: Raised when the API request returns an error status code.

        Tags:
            list, retrieve, conversations, filter, api
        """
        url = f"{self.base_url}/conversations"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("has_unread_messages", has_unread_messages),
                ("list_id", list_id),
                ("campaign_id", campaign_id),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def conversations_get_by_id(
        self, conversation_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieve the details of a conversation by its unique identifier.

        Args:
            conversation_id: str. The unique identifier of the conversation to retrieve. Must not be None.
            fields: Optional[list[str]]. A list of fields to include in the response. If None, all fields are returned.
            exclude_fields: Optional[list[str]]. A list of fields to exclude from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: A dictionary containing the conversation details as returned by the API.

        Raises:
            ValueError: Raised if 'conversation_id' is None.
            requests.HTTPError: Raised if the HTTP request to retrieve the conversation fails.

        Tags:
            get, conversations, api, management
        """
        if conversation_id is None:
            raise ValueError("Missing required parameter 'conversation_id'")
        url = f"{self.base_url}/conversations/{conversation_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def conversations_list_messages_from_conversation(
        self,
        conversation_id,
        fields=None,
        exclude_fields=None,
        is_read=None,
        before_timestamp=None,
        since_timestamp=None,
    ) -> dict[str, Any]:
        """
        Retrieves messages from a specified conversation.

        Args:
            conversation_id: The unique identifier for the conversation. Required.
            fields: Optional. Specific fields to include in the response.
            exclude_fields: Optional. Fields to exclude from the response.
            is_read: Optional. Filter messages by read status.
            before_timestamp: Optional. Return messages created before this timestamp.
            since_timestamp: Optional. Return messages created since this timestamp.

        Returns:
            A dictionary containing the conversation messages and related metadata.

        Raises:
            ValueError: Raised when the required 'conversation_id' parameter is None.
            HTTPError: Raised when the API request fails.

        Tags:
            list, retrieve, messages, conversation
        """
        if conversation_id is None:
            raise ValueError("Missing required parameter 'conversation_id'")
        url = f"{self.base_url}/conversations/{conversation_id}/messages"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("is_read", is_read),
                ("before_timestamp", before_timestamp),
                ("since_timestamp", since_timestamp),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def conversations_get_message_by_id(
        self, conversation_id, message_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieve a specific message from a conversation by its ID, with optional control over included and excluded fields.

        Args:
            conversation_id: str. The unique identifier of the conversation containing the message.
            message_id: str. The unique identifier of the message to retrieve.
            fields: Optional[list[str]]. A list of field names to include in the response. If None, all default fields are included.
            exclude_fields: Optional[list[str]]. A list of field names to exclude from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: A dictionary containing the message data as returned by the server.

        Raises:
            ValueError: If 'conversation_id' or 'message_id' is None.
            requests.HTTPError: If the HTTP request to the server fails or returns an error status.

        Tags:
            get, message, conversations, api
        """
        if conversation_id is None:
            raise ValueError("Missing required parameter 'conversation_id'")
        if message_id is None:
            raise ValueError("Missing required parameter 'message_id'")
        url = f"{self.base_url}/conversations/{conversation_id}/messages/{message_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def customer_journeys_trigger_step_action(
        self, journey_id, step_id, email_address
    ) -> dict[str, Any]:
        """
        Triggers a specific action for a step in a customer journey for the given email address.

        Args:
            journey_id: str. Unique identifier of the customer journey.
            step_id: str. Identifier of the step within the journey for which the action should be triggered.
            email_address: str. Email address of the customer involved in the journey step.

        Returns:
            dict[str, Any]: The JSON response from the API after triggering the action.

        Raises:
            ValueError: If any of journey_id, step_id, or email_address is None.
            requests.HTTPError: If the underlying HTTP request fails or returns an error status.

        Tags:
            trigger, customer-journey, action, api
        """
        if journey_id is None:
            raise ValueError("Missing required parameter 'journey_id'")
        if step_id is None:
            raise ValueError("Missing required parameter 'step_id'")
        if email_address is None:
            raise ValueError("Missing required parameter 'email_address'")
        request_body = {
            "email_address": email_address,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/customer-journeys/journeys/{journey_id}/steps/{step_id}/actions/trigger"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def file_manager_upload_file(
        self, name, file_data, folder_id=None
    ) -> dict[str, Any]:
        """
        Uploads a file to the file manager service, associating it with a specified name and optionally a folder.

        Args:
            name: str. The name to assign to the uploaded file. Must not be None.
            file_data: Any. The file data to upload. Must not be None.
            folder_id: Optional[str]. The ID of the folder to upload the file into. If None, uploads to the default location.

        Returns:
            dict[str, Any]: The JSON response from the file manager service containing details of the uploaded file.

        Raises:
            ValueError: If 'name' or 'file_data' is None.
            requests.HTTPError: If the HTTP request to the file manager service fails or returns an error status.

        Tags:
            upload, file-manager, api, management
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if file_data is None:
            raise ValueError("Missing required parameter 'file_data'")
        request_body = {
            "folder_id": folder_id,
            "name": name,
            "file_data": file_data,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/file-manager/files"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def file_manager_get_file(
        self, file_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves the details of a file from the file manager by its unique ID, optionally including or excluding specific fields.

        Args:
            file_id: The unique identifier of the file to retrieve. Must not be None.
            fields: Optional; a comma-separated string or list specifying which fields to include in the response.
            exclude_fields: Optional; a comma-separated string or list specifying which fields to exclude from the response.

        Returns:
            A dictionary containing the file's metadata and details as returned by the file manager API.

        Raises:
            ValueError: If 'file_id' is None.
            requests.HTTPError: If the HTTP request to the file manager service fails with a non-2xx status code.

        Tags:
            get, file-manager, fetch, api, metadata
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/file-manager/files/{file_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def file_manager_update_file(
        self, file_id, folder_id=None, name=None
    ) -> dict[str, Any]:
        """
        Updates the specified file's metadata in the file manager, such as its folder or name.

        Args:
            file_id: str. The unique identifier of the file to update. Required.
            folder_id: str or None. The target folder's ID to move the file to. Optional.
            name: str or None. The new name for the file. Optional.

        Returns:
            dict. The JSON response from the server containing the updated file metadata.

        Raises:
            ValueError: If 'file_id' is None, indicating a missing required parameter.
            HTTPError: If the PATCH request to the server fails with a client or server error response.

        Tags:
            update, file-management, async-job, api
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        request_body = {
            "folder_id": folder_id,
            "name": name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/file-manager/files/{file_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def file_manager_remove_file_by_id(self, file_id) -> Any:
        """
        Removes a file from the file manager by its unique identifier.

        Args:
            file_id: The unique identifier of the file to be removed.

        Returns:
            The server's response as a JSON object after successfully deleting the file.

        Raises:
            ValueError: Raised if 'file_id' is None.
            requests.HTTPError: Raised if the HTTP request to delete the file fails.

        Tags:
            remove, file, management
        """
        if file_id is None:
            raise ValueError("Missing required parameter 'file_id'")
        url = f"{self.base_url}/file-manager/files/{file_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def file_manager_get_folder_list(
        self,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        created_by=None,
        before_created_at=None,
        since_created_at=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of folders from the file manager using optional filtering, field selection, and pagination parameters.

        Args:
            fields: Optional[str]. Comma-separated list of fields to include in the response.
            exclude_fields: Optional[str]. Comma-separated list of fields to exclude from the response.
            count: Optional[int]. The number of records to return in the response.
            offset: Optional[int]. The number of records to skip in the response.
            created_by: Optional[str]. Filter folders by the unique ID of the creator.
            before_created_at: Optional[str]. Return folders created before this ISO 8601 timestamp.
            since_created_at: Optional[str]. Return folders created after this ISO 8601 timestamp.

        Returns:
            dict[str, Any]: A dictionary containing the folder list and associated metadata as returned by the API.

        Raises:
            requests.HTTPError: If the HTTP request to the file manager API fails or returns an error status code.

        Tags:
            list, file-manager, folders, filter, api, batch
        """
        url = f"{self.base_url}/file-manager/folders"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("created_by", created_by),
                ("before_created_at", before_created_at),
                ("since_created_at", since_created_at),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def file_manager_add_new_folder(self, request_body=None) -> dict[str, Any]:
        """
        Creates a new folder in the file manager using the provided request body data.

        Args:
            request_body: Optional dictionary containing data for the new folder to be created. This typically includes folder name and other relevant metadata.

        Returns:
            A dictionary containing the details of the newly created folder as returned by the API.

        Raises:
            requests.HTTPError: If the HTTP request to create the new folder fails or returns an unsuccessful status code.

        Tags:
            file-manager, add, folder, create, api
        """
        url = f"{self.base_url}/file-manager/folders"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def file_manager_get_folder_info(
        self, folder_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves information about a specific folder from the file manager service.

        Args:
            folder_id: The unique identifier of the folder to retrieve information for. Required.
            fields: Optional. A comma-separated list of fields to include in the response.
            exclude_fields: Optional. A comma-separated list of fields to exclude from the response.

        Returns:
            A dictionary containing the folder information with various attributes such as name, path, and metadata.

        Raises:
            ValueError: Raised when the required 'folder_id' parameter is None.
            HTTPError: Raised when the API request fails (via raise_for_status()).

        Tags:
            get, retrieve, folder, file-manager, information
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/file-manager/folders/{folder_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def file_manager_update_specific_folder(
        self, folder_id, request_body=None
    ) -> dict[str, Any]:
        """
        Updates a specific folder in the file manager system.

        Args:
            folder_id: String identifier for the folder to be updated. Required.
            request_body: Optional dictionary containing the updated folder attributes and values. Defaults to None.

        Returns:
            A dictionary containing the JSON response with the updated folder information.

        Raises:
            ValueError: Raised when the required parameter 'folder_id' is None.
            HTTPError: Raised when the API request fails (via raise_for_status()).

        Tags:
            update, folder, file-manager, management
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/file-manager/folders/{folder_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def file_manager_delete_folder_by_id(self, folder_id) -> Any:
        """
        Deletes a folder from the file manager by its unique identifier.

        Args:
            folder_id: The unique identifier of the folder to be deleted.

        Returns:
            A JSON object containing the API response with details about the deletion operation.

        Raises:
            ValueError: Raised when 'folder_id' is None.
            HTTPError: Raised if the HTTP request to delete the folder fails.

        Tags:
            delete, file-manager, folder, api
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/file-manager/folders/{folder_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def file_manager_list_stored_files(
        self,
        folder_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        type=None,
        created_by=None,
        before_created_at=None,
        since_created_at=None,
        sort_field=None,
        sort_dir=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of stored files within a specified folder, allowing optional filtering, sorting, and field selection.

        Args:
            folder_id: str. The unique identifier of the folder whose files are to be listed.
            fields: Optional[str or list[str]]. Comma-separated list or list of fields to include in the response.
            exclude_fields: Optional[str or list[str]]. Comma-separated list or list of fields to exclude from the response.
            count: Optional[int]. The maximum number of files to return.
            offset: Optional[int]. Number of items to skip for pagination.
            type: Optional[str]. Filter files by type.
            created_by: Optional[str]. Filter files by creator's identifier.
            before_created_at: Optional[str]. Only include files created before this timestamp (ISO 8601 format).
            since_created_at: Optional[str]. Only include files created at or after this timestamp (ISO 8601 format).
            sort_field: Optional[str]. Field by which to sort the results.
            sort_dir: Optional[str]. Sort direction, 'asc' for ascending or 'desc' for descending.

        Returns:
            dict[str, Any]: The API response as a dictionary containing the list of stored files and related metadata.

        Raises:
            ValueError: If 'folder_id' is None.
            requests.HTTPError: If the API request fails or returns an HTTP error status.

        Tags:
            list, file-manager, async-job, storage
        """
        if folder_id is None:
            raise ValueError("Missing required parameter 'folder_id'")
        url = f"{self.base_url}/file-manager/folders/{folder_id}/files"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("type", type),
                ("created_by", created_by),
                ("before_created_at", before_created_at),
                ("since_created_at", since_created_at),
                ("sort_field", sort_field),
                ("sort_dir", sort_dir),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_all_info(
        self,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        before_date_created=None,
        since_date_created=None,
        before_campaign_last_sent=None,
        since_campaign_last_sent=None,
        email=None,
        sort_field=None,
        sort_dir=None,
        has_ecommerce_store=None,
        include_total_contacts=None,
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about all lists, with support for filtering, sorting, and field selection.

        Args:
            fields: Optional[list or str]. A comma-separated list or list of specific fields to include in the response.
            exclude_fields: Optional[list or str]. A comma-separated list or list of fields to exclude from the response.
            count: Optional[int]. The maximum number of lists to return.
            offset: Optional[int]. The number of lists to skip before starting to collect the result set.
            before_date_created: Optional[str]. Restrict results to lists created before this date (ISO 8601 format).
            since_date_created: Optional[str]. Restrict results to lists created after this date (ISO 8601 format).
            before_campaign_last_sent: Optional[str]. Restrict results to lists with a last campaign sent before this date (ISO 8601 format).
            since_campaign_last_sent: Optional[str]. Restrict results to lists with a last campaign sent after this date (ISO 8601 format).
            email: Optional[str]. Restrict results to lists containing a specific email address.
            sort_field: Optional[str]. The field by which to sort the results.
            sort_dir: Optional[str]. The direction of the sort (e.g., 'ASC' or 'DESC').
            has_ecommerce_store: Optional[bool]. If True, returns only lists connected to an e-commerce store.
            include_total_contacts: Optional[bool]. If True, includes the total contacts count for each list.

        Returns:
            dict[str, Any]: The API response as a dictionary containing list information, metadata, and any requested fields.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails or returns an error status.

        Tags:
            list, get, retrieve, filter, sort, batch, api
        """
        url = f"{self.base_url}/lists"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("before_date_created", before_date_created),
                ("since_date_created", since_date_created),
                ("before_campaign_last_sent", before_campaign_last_sent),
                ("since_campaign_last_sent", since_campaign_last_sent),
                ("email", email),
                ("sort_field", sort_field),
                ("sort_dir", sort_dir),
                ("has_ecommerce_store", has_ecommerce_store),
                ("include_total_contacts", include_total_contacts),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_create_new_list(
        self,
        name,
        contact,
        permission_reminder,
        campaign_defaults,
        email_type_option,
        use_archive_bar=None,
        notify_on_subscribe=None,
        notify_on_unsubscribe=None,
        double_optin=None,
        marketing_permissions=None,
    ) -> dict[str, Any]:
        """
        Creates a new mailing list with the specified parameters and returns the created list's details.

        Args:
            name: str. The name of the list to create. Required.
            contact: dict. The contact information for the list, such as company details and address. Required.
            permission_reminder: str. A reminder for subscribers about how they joined the list. Required.
            campaign_defaults: dict. Default values for campaigns sent to this list (e.g., from_name, from_email). Required.
            email_type_option: bool. Whether the list supports multiple email formats (HTML and plain-text). Required.
            use_archive_bar: bool or None. Whether to display the archive bar in campaign archives. Optional.
            notify_on_subscribe: str or None. Email address to notify when someone subscribes. Optional.
            notify_on_unsubscribe: str or None. Email address to notify when someone unsubscribes. Optional.
            double_optin: bool or None. Whether to enable double opt-in confirmation for subscribers. Optional.
            marketing_permissions: list or None. Permissions required for GDPR compliance. Optional.

        Returns:
            dict. A dictionary containing the created list's details as returned by the API.

        Raises:
            ValueError: Raised if any required parameter (name, contact, permission_reminder, campaign_defaults, or email_type_option) is None.
            requests.HTTPError: Raised if the HTTP request to create the list fails (non-2xx response).

        Tags:
            create, list-management, api, async_job
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if contact is None:
            raise ValueError("Missing required parameter 'contact'")
        if permission_reminder is None:
            raise ValueError("Missing required parameter 'permission_reminder'")
        if campaign_defaults is None:
            raise ValueError("Missing required parameter 'campaign_defaults'")
        if email_type_option is None:
            raise ValueError("Missing required parameter 'email_type_option'")
        request_body = {
            "name": name,
            "contact": contact,
            "permission_reminder": permission_reminder,
            "use_archive_bar": use_archive_bar,
            "campaign_defaults": campaign_defaults,
            "notify_on_subscribe": notify_on_subscribe,
            "notify_on_unsubscribe": notify_on_unsubscribe,
            "email_type_option": email_type_option,
            "double_optin": double_optin,
            "marketing_permissions": marketing_permissions,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_list_info(
        self, list_id, fields=None, exclude_fields=None, include_total_contacts=None
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific list, including optional field selection and total contacts count.

        Args:
            list_id: str. The unique identifier of the list to retrieve information for. Required.
            fields: Optional[str or list of str]. Specific fields to include in the response. If None, all fields are returned.
            exclude_fields: Optional[str or list of str]. Fields to exclude from the response. If None, no fields are excluded.
            include_total_contacts: Optional[bool]. Whether to include the total number of contacts in the response.

        Returns:
            dict[str, Any]: A dictionary containing the list information as returned by the API.

        Raises:
            ValueError: Raised if 'list_id' is None.
            requests.HTTPError: Raised if the HTTP request to the remote API fails.

        Tags:
            get, list, retrieve, details, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("include_total_contacts", include_total_contacts),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_update_settings(
        self,
        list_id,
        name,
        contact,
        permission_reminder,
        campaign_defaults,
        email_type_option,
        use_archive_bar=None,
        notify_on_subscribe=None,
        notify_on_unsubscribe=None,
        double_optin=None,
        marketing_permissions=None,
    ) -> dict[str, Any]:
        """
        Updates the settings of a specified mailing list with provided configuration details.

        Args:
            list_id: str. The unique identifier of the mailing list to update. Required.
            name: str. The new name for the mailing list. Required.
            contact: dict. The contact information for the list, such as company, address, and country. Required.
            permission_reminder: str. Reminder text explaining why subscribers are receiving emails. Required.
            campaign_defaults: dict. Default settings for campaigns sent to this list, such as sender name and subject. Required.
            email_type_option: bool. Determines if subscribers can choose between HTML or plain-text emails. Required.
            use_archive_bar: Optional[bool]. Whether to display the archive bar in campaign archives. Defaults to None.
            notify_on_subscribe: Optional[str]. Email address to notify when someone subscribes. Defaults to None.
            notify_on_unsubscribe: Optional[str]. Email address to notify when someone unsubscribes. Defaults to None.
            double_optin: Optional[bool]. If set, new subscribers must confirm their subscription. Defaults to None.
            marketing_permissions: Optional[list]. List of marketing permissions to apply to the list. Defaults to None.

        Returns:
            dict. The updated list settings returned by the API.

        Raises:
            ValueError: Raised if any required parameter (list_id, name, contact, permission_reminder, campaign_defaults, or email_type_option) is missing.
            HTTPError: Raised if the API response returns an unsuccessful HTTP status.

        Tags:
            update, list-management, settings, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if contact is None:
            raise ValueError("Missing required parameter 'contact'")
        if permission_reminder is None:
            raise ValueError("Missing required parameter 'permission_reminder'")
        if campaign_defaults is None:
            raise ValueError("Missing required parameter 'campaign_defaults'")
        if email_type_option is None:
            raise ValueError("Missing required parameter 'email_type_option'")
        request_body = {
            "name": name,
            "contact": contact,
            "permission_reminder": permission_reminder,
            "use_archive_bar": use_archive_bar,
            "campaign_defaults": campaign_defaults,
            "notify_on_subscribe": notify_on_subscribe,
            "notify_on_unsubscribe": notify_on_unsubscribe,
            "email_type_option": email_type_option,
            "double_optin": double_optin,
            "marketing_permissions": marketing_permissions,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_delete_list(self, list_id) -> Any:
        """
        Deletes a list with the specified list ID via a DELETE request and returns the server's response as JSON.

        Args:
            list_id: Identifier of the list to be deleted. Must not be None.

        Returns:
            The JSON-decoded response from the server after deleting the specified list.

        Raises:
            ValueError: If 'list_id' is None.
            requests.HTTPError: If the HTTP request to delete the list fails (non-2xx response status).

        Tags:
            delete, list, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_batch_subscribe_or_unsubscribe(
        self,
        list_id,
        members,
        skip_merge_validation=None,
        skip_duplicate_check=None,
        sync_tags=None,
        update_existing=None,
    ) -> dict[str, Any]:
        """
        Batch subscribes or unsubscribes members to a specified mailing list, with optional parameters for merge validation, duplicate checking, tag synchronization, and updating existing members.

        Args:
            list_id: str. The unique identifier of the mailing list to which members will be subscribed or unsubscribed.
            members: list[dict]. A list of member objects to be processed for subscription or unsubscription.
            skip_merge_validation: bool, optional. If True, skips merge field validation when processing members.
            skip_duplicate_check: bool, optional. If True, skips duplicate checking for members.
            sync_tags: bool, optional. If True, synchronizes tags for the specified members.
            update_existing: bool, optional. If True, updates existing member records with provided data.

        Returns:
            dict[str, Any]: The JSON response from the API containing the status and results of the batch subscribe/unsubscribe operation.

        Raises:
            ValueError: Raised if required parameters 'list_id' or 'members' are not provided.
            requests.HTTPError: Raised if the API request fails or returns an unsuccessful HTTP status code.

        Tags:
            list, batch, subscribe, unsubscribe, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if members is None:
            raise ValueError("Missing required parameter 'members'")
        request_body = {
            "members": members,
            "sync_tags": sync_tags,
            "update_existing": update_existing,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}"
        query_params = {
            k: v
            for k, v in [
                ("skip_merge_validation", skip_merge_validation),
                ("skip_duplicate_check", skip_duplicate_check),
            ]
            if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_all_abuse_reports(
        self, list_id, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves all abuse reports for a specific list, with optional filtering and pagination.

        Args:
            list_id: str. The unique identifier of the list for which to retrieve abuse reports.
            fields: Optional[str]. A comma-separated list of fields to include in the response. Defaults to None.
            exclude_fields: Optional[str]. A comma-separated list of fields to exclude from the response. Defaults to None.
            count: Optional[int]. The number of records to return. Defaults to None, which uses the server default.
            offset: Optional[int]. The number of records to skip for pagination. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the abuse reports and associated metadata for the specified list.

        Raises:
            ValueError: If 'list_id' is not provided.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status.

        Tags:
            list, get, abuse-reports, api, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/abuse-reports"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_abuse_report(
        self,
        list_id,
        report_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
    ) -> dict[str, Any]:
        """
        Retrieves the details of a specific abuse report for a list.

        Args:
            list_id: str. The unique identifier for the list containing the abuse report.
            report_id: str. The unique identifier for the specific abuse report to retrieve.
            fields: Optional[str or list of str]. Fields to include in the response.
            exclude_fields: Optional[str or list of str]. Fields to exclude from the response.
            count: Optional[int]. Number of records to return.
            offset: Optional[int]. Number of records to skip before returning results.

        Returns:
            dict[str, Any]: A dictionary containing details of the requested abuse report.

        Raises:
            ValueError: Raised if 'list_id' or 'report_id' is not provided.
            requests.HTTPError: Raised if the HTTP request for the abuse report fails.

        Tags:
            get, list, abuse-report, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if report_id is None:
            raise ValueError("Missing required parameter 'report_id'")
        url = f"{self.base_url}/lists/{list_id}/abuse-reports/{report_id}"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_recent_activity_stats(
        self, list_id, count=None, offset=None, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves recent activity statistics for a specified list, with optional filtering and field selection.

        Args:
            list_id: str. The unique identifier of the list for which activity statistics are requested.
            count: Optional[int]. The number of records to return. Limits the result set size.
            offset: Optional[int]. The number of records to skip in the result set, used for pagination.
            fields: Optional[str or list of str]. A comma-separated list or list of fields to include in the response.
            exclude_fields: Optional[str or list of str]. A comma-separated list or list of fields to exclude from the response.

        Returns:
            dict. A dictionary containing the recent activity statistics for the specified list.

        Raises:
            ValueError: Raised if 'list_id' is None.
            requests.HTTPError: Raised if the HTTP request to the backend API fails or returns an error status code.

        Tags:
            list, get, activity, stats, api, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/activity"
        query_params = {
            k: v
            for k, v in [
                ("count", count),
                ("offset", offset),
                ("fields", fields),
                ("exclude_fields", exclude_fields),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_list_top_email_clients(
        self, list_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves a summary of the top email clients for a specified email list.

        Args:
            list_id: str. The unique identifier for the target email list.
            fields: Optional[list[str]]. Specific fields to include in the response. Defaults to None.
            exclude_fields: Optional[list[str]]. Specific fields to exclude from the response. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing information about the top email clients for the given list.

        Raises:
            ValueError: If 'list_id' is not provided.
            HTTPError: If the HTTP request fails or returns an error status.

        Tags:
            list, email-clients, fetch, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/clients"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_growth_history_data(
        self,
        list_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        sort_field=None,
        sort_dir=None,
    ) -> dict[str, Any]:
        """
        Retrieves the growth history data for a specific list with optional filtering, sorting, and field selection.

        Args:
            list_id: str. The unique identifier of the list whose growth history data is to be fetched. Required.
            fields: Optional[list[str]]. A comma-separated list of fields to include in the response.
            exclude_fields: Optional[list[str]]. A comma-separated list of fields to exclude from the response.
            count: Optional[int]. The number of records to return.
            offset: Optional[int]. The number of records to skip in the response.
            sort_field: Optional[str]. The field by which to sort the results.
            sort_dir: Optional[str]. The direction in which to sort the results ('ASC' or 'DESC').

        Returns:
            dict[str, Any]: The growth history data for the specified list in JSON format.

        Raises:
            ValueError: If the required parameter 'list_id' is missing.
            requests.HTTPError: If the HTTP request to the API endpoint fails.

        Tags:
            list, get, growth-history, fetch, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/growth-history"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("sort_field", sort_field),
                ("sort_dir", sort_dir),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_growth_history_by_month(
        self, list_id, month, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves the growth history of a specific mailing list for a given month, with optional field filtering.

        Args:
            list_id: str. The unique identifier of the mailing list whose growth history is to be retrieved.
            month: str. The specific month for which to retrieve growth history, formatted as 'YYYY-MM'.
            fields: Optional[list[str]]. A list of fields to include in the response. Defaults to None.
            exclude_fields: Optional[list[str]]. A list of fields to exclude from the response. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the growth history data for the specified list and month.

        Raises:
            ValueError: If either 'list_id' or 'month' is None.
            HTTPError: If the HTTP request to retrieve the growth history fails.

        Tags:
            get, list, growth-history, status, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if month is None:
            raise ValueError("Missing required parameter 'month'")
        url = f"{self.base_url}/lists/{list_id}/growth-history/{month}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_list_interest_categories(
        self,
        list_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        type=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of interest categories for a specific mailing list, with optional filters and pagination.

        Args:
            list_id: str. The unique identifier for the mailing list for which to retrieve interest categories.
            fields: Optional[str or list of str]. Specific fields to include in the response. If provided, limits the fields returned.
            exclude_fields: Optional[str or list of str]. Fields to exclude from the response. If provided, removes the specified fields from the result.
            count: Optional[int]. The number of records to return in the response. Used for pagination.
            offset: Optional[int]. The number of records from a collection to skip. Used for pagination.
            type: Optional[str]. The type of interest categories to return. Used to filter results.

        Returns:
            dict[str, Any]: A dictionary containing the interest categories for the specified mailing list, optionally filtered and paginated according to the provided parameters.

        Raises:
            ValueError: Raised if 'list_id' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns a non-success status code.

        Tags:
            list, interest-categories, fetch, pagination, filter, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/interest-categories"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("type", type),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_add_interest_category(self, list_id, request_body=None) -> dict[str, Any]:
        """
        Adds an interest category to a specified list by making a POST request to the list's interest-categories endpoint.

        Args:
            list_id: The ID of the list to which the interest category will be added.
            request_body: Optional body of the request containing details for the interest category to be added.

        Returns:
            A JSON response as a dictionary containing information about the added interest category.

        Raises:
            ValueError: Raised if the 'list_id' parameter is missing or is None.
            HTTPError: Raised if there is an HTTP error (e.g., server error, invalid request) during the POST request.

        Tags:
            add, category, management, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/interest-categories"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_interest_category_info(
        self, list_id, interest_category_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific interest category for a given Mailchimp list.

        Args:
            list_id: str. The unique identifier for the Mailchimp list.
            interest_category_id: str. The unique identifier for the interest category within the list.
            fields: Optional[list or str]. A comma-separated list or list of fields to include in the response.
            exclude_fields: Optional[list or str]. A comma-separated list or list of fields to exclude from the response.

        Returns:
            dict[str, Any]: A dictionary containing the interest category information as provided by the Mailchimp API.

        Raises:
            ValueError: Raised if either 'list_id' or 'interest_category_id' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails (e.g., non-2xx response).

        Tags:
            get, list, interest-category, mailchimp, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if interest_category_id is None:
            raise ValueError("Missing required parameter 'interest_category_id'")
        url = f"{self.base_url}/lists/{list_id}/interest-categories/{interest_category_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_update_interest_category(
        self, list_id, interest_category_id, request_body=None
    ) -> dict[str, Any]:
        """
        Updates an interest category for a specific list using the provided data.

        Args:
            list_id: str. The unique identifier for the list to be updated.
            interest_category_id: str. The unique identifier for the interest category to update.
            request_body: dict or None. The data to update the interest category with. Optional.

        Returns:
            dict. The JSON response containing the updated interest category details.

        Raises:
            ValueError: If 'list_id' or 'interest_category_id' is not provided.
            HTTPError: If the HTTP request to update the category fails.

        Tags:
            update, interest-category, list, management, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if interest_category_id is None:
            raise ValueError("Missing required parameter 'interest_category_id'")
        url = f"{self.base_url}/lists/{list_id}/interest-categories/{interest_category_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_delete_interest_category(self, list_id, interest_category_id) -> Any:
        """
        Deletes an interest category from a specified list using the provided IDs.

        Args:
            list_id: str. The unique identifier for the list from which the interest category will be deleted.
            interest_category_id: str. The unique identifier of the interest category to delete from the list.

        Returns:
            dict. The server's JSON response to the delete request.

        Raises:
            ValueError: If 'list_id' or 'interest_category_id' is None.
            requests.HTTPError: If the server returns an error response status code.

        Tags:
            delete, interest-category, list, api, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if interest_category_id is None:
            raise ValueError("Missing required parameter 'interest_category_id'")
        url = f"{self.base_url}/lists/{list_id}/interest-categories/{interest_category_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_list_category_interests(
        self,
        list_id,
        interest_category_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
    ) -> dict[str, Any]:
        """
        Retrieves all interests (subcategories) for a specific interest category within a Mailchimp list.

        Args:
            list_id: str. The unique identifier for the Mailchimp list.
            interest_category_id: str. The unique identifier for the interest category within the specified list.
            fields: Optional[List[str] or str]. A comma-separated list of fields to include in the response.
            exclude_fields: Optional[List[str] or str]. A comma-separated list of fields to exclude from the response.
            count: Optional[int]. The number of records to return in the response.
            offset: Optional[int]. The number of records to skip in the response.

        Returns:
            dict. Parsed JSON response containing interest information for the specified interest category.

        Raises:
            ValueError: If 'list_id' or 'interest_category_id' is not provided.
            requests.HTTPError: If the HTTP request to the Mailchimp API fails or returns a non-2xx status code.

        Tags:
            list, category, interests, retrieve, mailchimp, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if interest_category_id is None:
            raise ValueError("Missing required parameter 'interest_category_id'")
        url = f"{self.base_url}/lists/{list_id}/interest-categories/{interest_category_id}/interests"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_add_interest_in_category(
        self, list_id, interest_category_id, request_body=None
    ) -> dict[str, Any]:
        """
        Adds a new interest to a specified interest category within a list.

        Args:
            list_id: str. The unique identifier for the target list.
            interest_category_id: str. The identifier for the interest category within the list to which the interest will be added.
            request_body: dict or None. Optional request payload containing the data for the new interest.

        Returns:
            dict. The JSON-decoded response from the API representing the created interest resource.

        Raises:
            ValueError: Raised if 'list_id' or 'interest_category_id' is None.
            requests.HTTPError: Raised if the API request fails or the response status is an HTTP error.

        Tags:
            add, interest, management, lists, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if interest_category_id is None:
            raise ValueError("Missing required parameter 'interest_category_id'")
        url = f"{self.base_url}/lists/{list_id}/interest-categories/{interest_category_id}/interests"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_interest_in_category(
        self,
        list_id,
        interest_category_id,
        interest_id,
        fields=None,
        exclude_fields=None,
    ) -> dict[str, Any]:
        """
        Retrieves interest information within a category of a list.

        Args:
            list_id: The ID of the list to retrieve from.
            interest_category_id: The ID of the category to retrieve from.
            interest_id: The ID of the interest to retrieve.
            fields: Optional fields to include in the response.
            exclude_fields: Optional fields to exclude from the response.

        Returns:
            A dictionary containing the interest information.

        Raises:
            ValueError: If any of the required parameters (list_id, interest_category_id, interest_id) are missing.

        Tags:
            retrieve, interest, list, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if interest_category_id is None:
            raise ValueError("Missing required parameter 'interest_category_id'")
        if interest_id is None:
            raise ValueError("Missing required parameter 'interest_id'")
        url = f"{self.base_url}/lists/{list_id}/interest-categories/{interest_category_id}/interests/{interest_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_update_interest_category_interest(
        self, list_id, interest_category_id, interest_id, request_body=None
    ) -> dict[str, Any]:
        """
        Updates a specific interest within an interest category for a given list by sending a PATCH request to the API.

        Args:
            list_id: str. The unique identifier for the list.
            interest_category_id: str. The unique identifier for the interest category within the list.
            interest_id: str. The unique identifier for the interest to update within the interest category.
            request_body: dict or None. The request payload containing the fields to update for the interest (defaults to None).

        Returns:
            dict. The JSON response from the API representing the updated interest.

        Raises:
            ValueError: If any of the required parameters ('list_id', 'interest_category_id', or 'interest_id') are None.
            requests.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            update, api, interest, patch, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if interest_category_id is None:
            raise ValueError("Missing required parameter 'interest_category_id'")
        if interest_id is None:
            raise ValueError("Missing required parameter 'interest_id'")
        url = f"{self.base_url}/lists/{list_id}/interest-categories/{interest_category_id}/interests/{interest_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_delete_interest_in_category(
        self, list_id, interest_category_id, interest_id
    ) -> Any:
        """
        Deletes a specific interest from a given interest category within a mailing list.

        Args:
            list_id: str. The unique identifier of the mailing list from which the interest will be deleted.
            interest_category_id: str. The unique identifier of the interest category containing the interest.
            interest_id: str. The unique identifier of the interest to delete.

        Returns:
            dict. The JSON response from the API after the interest has been deleted.

        Raises:
            ValueError: If any of the required parameters ('list_id', 'interest_category_id', or 'interest_id') is None.
            requests.HTTPError: If the API request fails or returns an error status code.

        Tags:
            delete, list-management, interest, category, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if interest_category_id is None:
            raise ValueError("Missing required parameter 'interest_category_id'")
        if interest_id is None:
            raise ValueError("Missing required parameter 'interest_id'")
        url = f"{self.base_url}/lists/{list_id}/interest-categories/{interest_category_id}/interests/{interest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_segments_info(
        self,
        list_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        type=None,
        since_created_at=None,
        before_created_at=None,
        include_cleaned=None,
        include_transactional=None,
        include_unsubscribed=None,
        since_updated_at=None,
        before_updated_at=None,
    ) -> dict[str, Any]:
        """
        Retrieves information about segments for a specific list, with support for filtering and pagination options.

        Args:
            list_id: str. The unique identifier for the list to retrieve segment information from. Required.
            fields: str or list of str, optional. A comma-separated list of fields to include in the response.
            exclude_fields: str or list of str, optional. A comma-separated list of fields to exclude from the response.
            count: int, optional. The number of records to return. Defaults to the API's standard limit.
            offset: int, optional. The number of records to skip for pagination.
            type: str, optional. The type of segments to retrieve (e.g., 'static', 'saved').
            since_created_at: str, optional. Restricts response to segments created after this ISO timestamp.
            before_created_at: str, optional. Restricts response to segments created before this ISO timestamp.
            include_cleaned: bool, optional. Whether to include cleaned email addresses in the segment information.
            include_transactional: bool, optional. Whether to include transactional addresses in the segment information.
            include_unsubscribed: bool, optional. Whether to include unsubscribed addresses in the segment information.
            since_updated_at: str, optional. Restricts response to segments updated after this ISO timestamp.
            before_updated_at: str, optional. Restricts response to segments updated before this ISO timestamp.

        Returns:
            dict. The segment information as returned by the API, typically including segment details and pagination metadata.

        Raises:
            ValueError: If 'list_id' is not provided.
            requests.HTTPError: If the API request fails (e.g., network issues, authentication errors, invalid parameters).

        Tags:
            list, get, segments, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/segments"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("type", type),
                ("since_created_at", since_created_at),
                ("before_created_at", before_created_at),
                ("include_cleaned", include_cleaned),
                ("include_transactional", include_transactional),
                ("include_unsubscribed", include_unsubscribed),
                ("since_updated_at", since_updated_at),
                ("before_updated_at", before_updated_at),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_add_new_segment(
        self, list_id, name, static_segment=None, options=None
    ) -> dict[str, Any]:
        """
        Creates a new segment for a specified list, optionally as a static segment, by sending a POST request to the appropriate API endpoint.

        Args:
            list_id: The unique identifier of the list to which the new segment will be added.
            name: The name of the new segment to create.
            static_segment: An optional list of emails or identifiers to include in the segment. If provided, creates a static segment.
            options: An optional dictionary of additional segment options.

        Returns:
            A dictionary containing the API response data for the newly created segment.

        Raises:
            ValueError: If 'list_id' or 'name' is not provided.
            requests.HTTPError: If the HTTP request to the API fails or responds with an error status code.

        Tags:
            add, segment, list-management, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "name": name,
            "static_segment": static_segment,
            "options": options,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}/segments"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_segment_info(
        self,
        list_id,
        segment_id,
        fields=None,
        exclude_fields=None,
        include_cleaned=None,
        include_transactional=None,
        include_unsubscribed=None,
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific segment within a mailing list, allowing for optional filtering and inclusion of additional segment data.

        Args:
            list_id: str. The unique identifier for the mailing list containing the segment.
            segment_id: str. The unique identifier for the segment within the mailing list.
            fields: Optional[str or list[str]]. A comma-separated list or list of fields to include in the response. If None, all fields are returned.
            exclude_fields: Optional[str or list[str]]. A comma-separated list or list of fields to exclude from the response.
            include_cleaned: Optional[bool]. Whether to include cleaned (bounced) members in the segment details.
            include_transactional: Optional[bool]. Whether to include transactional members in the segment details.
            include_unsubscribed: Optional[bool]. Whether to include unsubscribed members in the segment details.

        Returns:
            dict[str, Any]: A dictionary containing detailed information about the specified segment in the list, as returned by the API.

        Raises:
            ValueError: Raised if 'list_id' or 'segment_id' is not provided.
            requests.HTTPError: Raised if the HTTP request to retrieve the segment information fails.

        Tags:
            list, segment, get, info, api, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if segment_id is None:
            raise ValueError("Missing required parameter 'segment_id'")
        url = f"{self.base_url}/lists/{list_id}/segments/{segment_id}"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("include_cleaned", include_cleaned),
                ("include_transactional", include_transactional),
                ("include_unsubscribed", include_unsubscribed),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_delete_segment(self, list_id, segment_id) -> Any:
        """
        Deletes a specific segment from a list by its list and segment identifiers.

        Args:
            list_id: The unique identifier of the list containing the segment to delete.
            segment_id: The unique identifier of the segment to be deleted from the list.

        Returns:
            The JSON-decoded response from the API after deleting the specified segment.

        Raises:
            ValueError: Raised if either 'list_id' or 'segment_id' is None.
            requests.HTTPError: Raised if the API responds with an HTTP error status.

        Tags:
            delete, segment-management, lists, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if segment_id is None:
            raise ValueError("Missing required parameter 'segment_id'")
        url = f"{self.base_url}/lists/{list_id}/segments/{segment_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_update_segment_by_id(
        self, list_id, segment_id, name, static_segment=None, options=None
    ) -> dict[str, Any]:
        """
        Updates a specific segment within a list using the provided identifiers and parameters.

        Args:
            list_id: The unique identifier of the list containing the segment to update.
            segment_id: The unique identifier of the segment to update.
            name: The new name to assign to the segment.
            static_segment: An optional list of static segment members to update. If not provided, it will be ignored.
            options: An optional dictionary of additional options for the segment update.

        Returns:
            A dictionary representing the updated segment data as returned by the server.

        Raises:
            ValueError: Raised if 'list_id', 'segment_id', or 'name' is None.
            HTTPError: Raised if the HTTP request to update the segment fails (as triggered by response.raise_for_status()).

        Tags:
            update, list-segment, management, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if segment_id is None:
            raise ValueError("Missing required parameter 'segment_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "name": name,
            "static_segment": static_segment,
            "options": options,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}/segments/{segment_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_batch_add_remove_members(
        self, list_id, segment_id, members_to_add=None, members_to_remove=None
    ) -> dict[str, Any]:
        """
        Adds and/or removes members in bulk to a specific segment within a given list.

        Args:
            list_id: The unique identifier of the list to modify.
            segment_id: The unique identifier of the segment within the list to update.
            members_to_add: Optional. A collection of members to add to the segment. Defaults to None if no members are to be added.
            members_to_remove: Optional. A collection of members to remove from the segment. Defaults to None if no members are to be removed.

        Returns:
            A dictionary containing the server's response data about the batch add or remove operation.

        Raises:
            ValueError: If either 'list_id' or 'segment_id' is not provided.
            requests.HTTPError: If the HTTP request to the server fails (e.g., due to 4xx or 5xx status codes).

        Tags:
            lists, batch, add, remove, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if segment_id is None:
            raise ValueError("Missing required parameter 'segment_id'")
        request_body = {
            "members_to_add": members_to_add,
            "members_to_remove": members_to_remove,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}/segments/{segment_id}"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_segment_members(
        self,
        list_id,
        segment_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        include_cleaned=None,
        include_transactional=None,
        include_unsubscribed=None,
    ) -> dict[str, Any]:
        """
        Retrieve members of a specific segment within a list, with support for filtering and pagination options.

        Args:
            list_id: str. The unique identifier of the list whose segment members are to be retrieved.
            segment_id: str. The unique identifier of the segment within the list.
            fields: Optional[list[str]]. A comma-separated list of fields to include in the response.
            exclude_fields: Optional[list[str]]. A comma-separated list of fields to exclude from the response.
            count: Optional[int]. The number of records to return. Default is determined by the API settings.
            offset: Optional[int]. The number of records to skip for pagination.
            include_cleaned: Optional[bool]. Whether to include cleaned members in the response.
            include_transactional: Optional[bool]. Whether to include transactional members in the response.
            include_unsubscribed: Optional[bool]. Whether to include unsubscribed members in the response.

        Returns:
            dict[str, Any]: A dictionary containing the segment members and associated metadata as returned by the API.

        Raises:
            ValueError: If 'list_id' or 'segment_id' is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            list, segment, members, get, retrieve, filtering, pagination, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if segment_id is None:
            raise ValueError("Missing required parameter 'segment_id'")
        url = f"{self.base_url}/lists/{list_id}/segments/{segment_id}/members"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("include_cleaned", include_cleaned),
                ("include_transactional", include_transactional),
                ("include_unsubscribed", include_unsubscribed),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_add_member_to_segment(
        self, list_id, segment_id, email_address
    ) -> dict[str, Any]:
        """
        Adds a member to a specified segment within a mailing list.

        Args:
            list_id: str. The unique identifier for the list to which the segment belongs.
            segment_id: str. The unique identifier for the segment within the list.
            email_address: str. The email address of the member to add to the segment.

        Returns:
            dict[str, Any]: The API response as a dictionary containing the newly added member's data.

        Raises:
            ValueError: Raised if any of the required parameters ('list_id', 'segment_id', 'email_address') are missing.
            HTTPError: Raised if the API request fails or returns a non-success status code.

        Tags:
            add, member, segment, list, api, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if segment_id is None:
            raise ValueError("Missing required parameter 'segment_id'")
        if email_address is None:
            raise ValueError("Missing required parameter 'email_address'")
        request_body = {
            "email_address": email_address,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}/segments/{segment_id}/members"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_remove_member_from_segment(
        self, list_id, segment_id, subscriber_hash
    ) -> Any:
        """
        Removes a member from a segment within a specific list.

        Args:
            list_id: The unique ID of the list containing the segment.
            segment_id: The unique ID of the segment from which to remove the member.
            subscriber_hash: The unique identifier for the subscriber to remove from the segment.

        Returns:
            The JSON response from the API after removing the member from the segment.

        Raises:
            ValueError: Raised when any of the required parameters (list_id, segment_id, subscriber_hash) are None.
            HTTPError: Raised when the API request fails.

        Tags:
            remove, member, segment, list, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if segment_id is None:
            raise ValueError("Missing required parameter 'segment_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/lists/{list_id}/segments/{segment_id}/members/{subscriber_hash}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_search_tags_by_name(self, list_id, name=None) -> dict[str, Any]:
        """
        Searches for tags within a specific list by tag name using the list's unique identifier.

        Args:
            list_id: str. The unique identifier of the list to search for tags.
            name: Optional[str]. The name or partial name of the tag to search for. If None, retrieves all tags for the list.

        Returns:
            dict[str, Any]: A dictionary containing the search results for tags that match the specified criteria.

        Raises:
            ValueError: Raised if the required parameter 'list_id' is None.
            requests.HTTPError: Raised if the HTTP request to the external API fails (non-2xx response).

        Tags:
            search, tags, list, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/tag-search"
        query_params = {k: v for k, v in [("name", name)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_members_info(
        self,
        list_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        email_type=None,
        status=None,
        since_timestamp_opt=None,
        before_timestamp_opt=None,
        since_last_changed=None,
        before_last_changed=None,
        unique_email_id=None,
        vip_only=None,
        interest_category_id=None,
        interest_ids=None,
        interest_match=None,
        sort_field=None,
        sort_dir=None,
        since_last_campaign=None,
        unsubscribed_since=None,
    ) -> dict[str, Any]:
        """
        Fetches and returns member information for a specified list by ID, allowing for various filtering and sorting options.

        Args:
            list_id: The ID of the list to fetch members from (required).
            fields: Optional fields to include in the response.
            exclude_fields: Optional fields to exclude from the response.
            count: The number of records to return.
            offset: The offset from which to start returning records.
            email_type: Filter by email type.
            status: Filter by member status.
            since_timestamp_opt: Filter members updated since this timestamp (optional).
            before_timestamp_opt: Filter members updated before this timestamp (optional).
            since_last_changed: Filter members changed since this timestamp (optional).
            before_last_changed: Filter members changed before this timestamp (optional).
            unique_email_id: Filter by unique email ID.
            vip_only: Only include VIP members.
            interest_category_id: Filter by interest category ID.
            interest_ids: Filter by interest IDs.
            interest_match: Specify how to match interests.
            sort_field: Specify the field to sort by.
            sort_dir: Specify the direction of sorting.
            since_last_campaign: Filter members since the last campaign.
            unsubscribed_since: Filter members unsubscribed since this timestamp.

        Returns:
            A dictionary containing member information.

        Raises:
            ValueError: Raised when the 'list_id' parameter is missing.

        Tags:
            fetch, members, list-management, api-call, import
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/members"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("email_type", email_type),
                ("status", status),
                ("since_timestamp_opt", since_timestamp_opt),
                ("before_timestamp_opt", before_timestamp_opt),
                ("since_last_changed", since_last_changed),
                ("before_last_changed", before_last_changed),
                ("unique_email_id", unique_email_id),
                ("vip_only", vip_only),
                ("interest_category_id", interest_category_id),
                ("interest_ids", interest_ids),
                ("interest_match", interest_match),
                ("sort_field", sort_field),
                ("sort_dir", sort_dir),
                ("since_last_campaign", since_last_campaign),
                ("unsubscribed_since", unsubscribed_since),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_add_member_to_list(
        self,
        list_id,
        email_address,
        status,
        skip_merge_validation=None,
        tags=None,
        email_type=None,
        merge_fields=None,
        interests=None,
        language=None,
        vip=None,
        location=None,
        marketing_permissions=None,
        ip_signup=None,
        timestamp_signup=None,
        ip_opt=None,
        timestamp_opt=None,
    ) -> dict[str, Any]:
        """
        Adds a member to a specified list with the provided details.

        Args:
            list_id: The ID of the list to which the member is to be added.
            email_address: The email address of the member.
            status: The status of the member in the list.
            skip_merge_validation: Optionally skip merge validation for the request.
            tags: Optional tags for the member.
            email_type: The type of the email address.
            merge_fields: Optional merge fields for the member.
            interests: Optional interests associated with the member.
            language: Optional language preference of the member.
            vip: Whether the member is a VIP.
            location: Optional location of the member.
            marketing_permissions: Optional marketing permissions for the member.
            ip_signup: Optional IP address at signup.
            timestamp_signup: Optional timestamp of signup.
            ip_opt: Optional IP address at opt-in.
            timestamp_opt: Optional timestamp of opt-in.

        Returns:
            A dictionary containing the response from the server.

        Raises:
            ValueError: Raised when required parameters (list_id, email_address, status) are missing.

        Tags:
            add, member, list, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if email_address is None:
            raise ValueError("Missing required parameter 'email_address'")
        if status is None:
            raise ValueError("Missing required parameter 'status'")
        request_body = {
            "tags": tags,
            "email_address": email_address,
            "email_type": email_type,
            "status": status,
            "merge_fields": merge_fields,
            "interests": interests,
            "language": language,
            "vip": vip,
            "location": location,
            "marketing_permissions": marketing_permissions,
            "ip_signup": ip_signup,
            "timestamp_signup": timestamp_signup,
            "ip_opt": ip_opt,
            "timestamp_opt": timestamp_opt,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}/members"
        query_params = {
            k: v
            for k, v in [("skip_merge_validation", skip_merge_validation)]
            if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_member_info(
        self, list_id, subscriber_hash, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieve information about a specific list member from the Mailchimp API.

        Args:
            list_id: str. The unique identifier for the Mailchimp list.
            subscriber_hash: str. The MD5 hash of the lowercase version of the member's email address.
            fields: Optional[list of str]. Specific fields to include in the response. Defaults to None, which returns all fields.
            exclude_fields: Optional[list of str]. Specific fields to exclude from the response. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing information about the specified list member as returned by the Mailchimp API.

        Raises:
            ValueError: If 'list_id' or 'subscriber_hash' is None.
            requests.HTTPError: If the HTTP request to the Mailchimp API fails or returns a non-successful status code.

        Tags:
            get, list-member, mailchimp, api, info
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_add_or_update_member(
        self,
        list_id,
        subscriber_hash,
        email_address,
        status_if_new,
        skip_merge_validation=None,
        email_type=None,
        status=None,
        merge_fields=None,
        interests=None,
        language=None,
        vip=None,
        location=None,
        marketing_permissions=None,
        ip_signup=None,
        timestamp_signup=None,
        ip_opt=None,
        timestamp_opt=None,
    ) -> dict[str, Any]:
        """
        Adds a new member to a list or updates an existing member's information in the specified list.

        Args:
            list_id: str. The unique ID for the target list.
            subscriber_hash: str. The MD5 hash of the lowercase version of the member's email address.
            email_address: str. The email address of the member.
            status_if_new: str. The status to assign if the member is new (e.g., 'subscribed', 'unsubscribed').
            skip_merge_validation: bool, optional. If true, skips merge validation checks.
            email_type: str, optional. The type of email ('html' or 'text') for the member.
            status: str, optional. The member's status ('subscribed', 'unsubscribed', etc.).
            merge_fields: dict, optional. Merge fields to include for the member.
            interests: dict, optional. The member's interests.
            language: str, optional. The member's preferred language.
            vip: bool, optional. Indicates if the member is a VIP.
            location: dict, optional. The member's location details.
            marketing_permissions: list, optional. The member's marketing permissions.
            ip_signup: str, optional. IP address the member signed up from.
            timestamp_signup: str, optional. Timestamp of when the member signed up.
            ip_opt: str, optional. IP address the member opted in from.
            timestamp_opt: str, optional. Timestamp of the member's opt-in.

        Returns:
            dict. A dictionary containing the response data from the API with the details of the added or updated member.

        Raises:
            ValueError: If any required parameter ('list_id', 'subscriber_hash', 'email_address', or 'status_if_new') is missing.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status.

        Tags:
            list, add, update, member, management, important
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        if email_address is None:
            raise ValueError("Missing required parameter 'email_address'")
        if status_if_new is None:
            raise ValueError("Missing required parameter 'status_if_new'")
        request_body = {
            "email_address": email_address,
            "status_if_new": status_if_new,
            "email_type": email_type,
            "status": status,
            "merge_fields": merge_fields,
            "interests": interests,
            "language": language,
            "vip": vip,
            "location": location,
            "marketing_permissions": marketing_permissions,
            "ip_signup": ip_signup,
            "timestamp_signup": timestamp_signup,
            "ip_opt": ip_opt,
            "timestamp_opt": timestamp_opt,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}"
        query_params = {
            k: v
            for k, v in [("skip_merge_validation", skip_merge_validation)]
            if v is not None
        }
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_update_member(
        self,
        list_id,
        subscriber_hash,
        skip_merge_validation=None,
        email_address=None,
        email_type=None,
        status=None,
        merge_fields=None,
        interests=None,
        language=None,
        vip=None,
        location=None,
        marketing_permissions=None,
        ip_signup=None,
        timestamp_signup=None,
        ip_opt=None,
        timestamp_opt=None,
    ) -> dict[str, Any]:
        """
        Updates the information for a specific list member in the email marketing system, identified by list ID and subscriber hash, with the provided attributes.

        Args:
            list_id: str. The unique identifier of the list containing the member. Required.
            subscriber_hash: str. The MD5 hash of the lowercase version of the member's email address. Required.
            skip_merge_validation: bool, optional. If True, skips merge field validation when updating the member.
            email_address: str, optional. The email address for the member.
            email_type: str, optional. The email type for the member (e.g., 'html' or 'text').
            status: str, optional. The status for the member ('subscribed', 'unsubscribed', 'cleaned', 'pending', or 'transactional').
            merge_fields: dict, optional. A dictionary of merge field values to update for the member.
            interests: dict, optional. Dictionary of the member's interests by interest ID.
            language: str, optional. The language for the member (e.g., 'en', 'fr').
            vip: bool, optional. Whether the member is a VIP.
            location: dict, optional. Information about the member's geographic location.
            marketing_permissions: list, optional. List of the member's marketing permissions.
            ip_signup: str, optional. The IP address the member signed up from.
            timestamp_signup: str, optional. The timestamp when the member signed up (ISO8601 format).
            ip_opt: str, optional. The IP address the member opted in from.
            timestamp_opt: str, optional. The timestamp when the member opted in (ISO8601 format).

        Returns:
            dict. The updated member information as returned by the email marketing system's API.

        Raises:
            ValueError: Raised if either 'list_id' or 'subscriber_hash' is None.
            requests.HTTPError: Raised if the underlying API request fails with an HTTP error status.

        Tags:
            update, list, member, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        request_body = {
            "email_address": email_address,
            "email_type": email_type,
            "status": status,
            "merge_fields": merge_fields,
            "interests": interests,
            "language": language,
            "vip": vip,
            "location": location,
            "marketing_permissions": marketing_permissions,
            "ip_signup": ip_signup,
            "timestamp_signup": timestamp_signup,
            "ip_opt": ip_opt,
            "timestamp_opt": timestamp_opt,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}"
        query_params = {
            k: v
            for k, v in [("skip_merge_validation", skip_merge_validation)]
            if v is not None
        }
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_archive_member(self, list_id, subscriber_hash) -> Any:
        """
        Removes an archived member from a specified list using their unique subscriber hash.

        Args:
            list_id: The unique identifier of the list from which the member will be removed.
            subscriber_hash: The MD5 hash of the lowercase version of the member's email address.

        Returns:
            A dictionary containing the API response with details about the removed member.

        Raises:
            ValueError: Raised if either 'list_id' or 'subscriber_hash' is None.
            requests.HTTPError: Raised if the underlying HTTP DELETE request fails with an error response.

        Tags:
            lists, archive, member, delete, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_view_recent_activity_events(
        self, list_id, subscriber_hash, fields=None, exclude_fields=None, action=None
    ) -> dict[str, Any]:
        """
        Retrieves recent activity events for a specific list member, optionally filtering the results by specified fields and actions.

        Args:
            list_id: str. The unique ID of the Mailchimp list from which to fetch the member's activity events.
            subscriber_hash: str. The MD5 hash of the list member's lowercase email address.
            fields: Optional[list or str]. A comma-separated list or list of fields to include in the response. If None, all fields are returned.
            exclude_fields: Optional[list or str]. A comma-separated list or list of fields to exclude from the response.
            action: Optional[str]. Restricts results to a specific action type (e.g., 'sent', 'open', 'click').

        Returns:
            dict[str, Any]: A dictionary containing the list member's recent activity events, as returned by the Mailchimp API.

        Raises:
            ValueError: Raised if 'list_id' or 'subscriber_hash' is not provided.
            requests.HTTPError: Raised if the HTTP request to the Mailchimp API fails or returns a non-success status code.

        Tags:
            list, view, recent-activity, events, member, fetch, api, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}/activity"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("action", action),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_view_recent_activity(
        self,
        list_id,
        subscriber_hash,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        activity_filters=None,
    ) -> dict[str, Any]:
        """
        Retrieves recent activity for a specific subscriber in a mailing list.

        Args:
            list_id: The unique ID of the mailing list.
            subscriber_hash: The MD5 hash of the lowercase version of the subscriber's email address.
            fields: A comma-separated list of fields to return. If omitted, all fields will be returned.
            exclude_fields: A comma-separated list of fields to exclude from the response.
            count: The number of records to return.
            offset: The number of records from a collection to skip.
            activity_filters: Filters for specific activity types to include in the response.

        Returns:
            A dictionary containing the subscriber's activity feed data.

        Raises:
            ValueError: Raised when required parameters 'list_id' or 'subscriber_hash' are missing.
            HTTPError: Raised when the API request fails.

        Tags:
            list, member, activity, retrieve, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}/activity-feed"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("activity_filters", activity_filters),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_member_tags(
        self,
        list_id,
        subscriber_hash,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of tags assigned to a specific list member (subscriber) with optional filtering and pagination.

        Args:
            list_id: str. The unique ID for the list to query. Required.
            subscriber_hash: str. The MD5 hash identifying the subscriber in the list. Required.
            fields: Optional[list[str]]. A list of specific fields to include in the response. Defaults to None.
            exclude_fields: Optional[list[str]]. A list of fields to exclude from the response. Defaults to None.
            count: Optional[int]. The number of records to return in the response. Defaults to None.
            offset: Optional[int]. The number of records to skip in the response. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the tag data for the specified list member.

        Raises:
            ValueError: If 'list_id' or 'subscriber_hash' is None.
            requests.HTTPError: If the HTTP request to the API fails (e.g., network error or non-2xx response).

        Tags:
            list, get, tags, member, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}/tags"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_add_member_tags(
        self, list_id, subscriber_hash, tags, is_syncing=None
    ) -> Any:
        """
        Adds member tags to a subscriber in a list.

        Args:
            list_id: ID of the list
            subscriber_hash: Hash of the subscriber
            tags: Tags to be added
            is_syncing: Optional; specifies if syncing is enabled

        Returns:
            The JSON response from the API.

        Raises:
            ValueError: Raised if 'list_id', 'subscriber_hash', or 'tags' is missing.
            HTTPError: Raised if the HTTP response contains an unsuccessful status code.

        Tags:
            add, member, tag, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        if tags is None:
            raise ValueError("Missing required parameter 'tags'")
        request_body = {
            "tags": tags,
            "is_syncing": is_syncing,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}/tags"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_member_events(
        self,
        list_id,
        subscriber_hash,
        count=None,
        offset=None,
        fields=None,
        exclude_fields=None,
    ) -> dict[str, Any]:
        """
        Retrieves member events for a specific subscriber in a mailing list.

        Args:
            list_id: The unique ID for the mailing list.
            subscriber_hash: The MD5 hash of the lowercase version of the list member's email address.
            count: The number of events to return. Default is None which returns all events.
            offset: The zero-based offset of the first event to return. Default is None which starts at the first event.
            fields: A comma-separated list of fields to return. Default is None which returns all fields.
            exclude_fields: A comma-separated list of fields to exclude from the response. Default is None which excludes no fields.

        Returns:
            A dictionary containing member events data.

        Raises:
            ValueError: Raised when either list_id or subscriber_hash is None.

        Tags:
            list, retrieve, member, events, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}/events"
        query_params = {
            k: v
            for k, v in [
                ("count", count),
                ("offset", offset),
                ("fields", fields),
                ("exclude_fields", exclude_fields),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_add_member_event(
        self,
        list_id,
        subscriber_hash,
        name,
        properties=None,
        is_syncing=None,
        occurred_at=None,
    ) -> Any:
        """
        Adds a new event for a specific list member by sending a POST request with event details to the API.

        Args:
            list_id: str. The unique identifier for the target list. Required.
            subscriber_hash: str. The unique MD5 hash identifying the member in the list. Required.
            name: str. The name of the event to be recorded. Required.
            properties: dict, optional. Additional event properties or metadata to include. Defaults to None.
            is_syncing: bool, optional. Indicates if the event is currently syncing. Defaults to None.
            occurred_at: str or datetime, optional. The timestamp for when the event occurred. Defaults to None.

        Returns:
            dict. The parsed JSON response from the API containing the event data or related information.

        Raises:
            ValueError: If any of 'list_id', 'subscriber_hash', or 'name' parameters are missing or None.
            requests.HTTPError: If the API request fails or returns a non-successful status code.

        Tags:
            add, event, list-member, api, post
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "name": name,
            "properties": properties,
            "is_syncing": is_syncing,
            "occurred_at": occurred_at,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}/events"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_member_goals(
        self, list_id, subscriber_hash, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves the goal information for a specific list member in Mailchimp.

        Args:
            list_id: str. The unique identifier for the Mailchimp list.
            subscriber_hash: str. The MD5 hash of the lowercase version of the list member's email address.
            fields: Optional[list[str]]. A list of specific fields to include in the response.
            exclude_fields: Optional[list[str]]. A list of fields to exclude from the response.

        Returns:
            dict[str, Any]: A dictionary containing the goal data for the specified list member.

        Raises:
            ValueError: Raised if 'list_id' or 'subscriber_hash' is None.
            requests.HTTPError: Raised if the HTTP request to the Mailchimp API fails.

        Tags:
            list, get, member, goal, api, mailchimp
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}/goals"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_member_notes(
        self,
        list_id,
        subscriber_hash,
        sort_field=None,
        sort_dir=None,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
    ) -> dict[str, Any]:
        """
        Retrieves notes associated with a specific list member, with optional filtering, sorting, and pagination.

        Args:
            list_id: str. The unique identifier for the list containing the member.
            subscriber_hash: str. The MD5 hash of the lowercase version of the list member's email address.
            sort_field: str, optional. Field by which to sort the notes (e.g., 'created_at').
            sort_dir: str, optional. Direction to sort ('ASC' or 'DESC').
            fields: list or str, optional. Specific fields to include in the response.
            exclude_fields: list or str, optional. Specific fields to exclude from the response.
            count: int, optional. Number of records to return.
            offset: int, optional. Number of records to skip for pagination.

        Returns:
            dict[str, Any]: A dictionary containing the member notes and associated metadata.

        Raises:
            ValueError: Raised if 'list_id' or 'subscriber_hash' is not provided.
            requests.HTTPError: Raised if the API request fails (e.g., network error, permission issue).

        Tags:
            list, get, member, notes, search, batch, api, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}/notes"
        query_params = {
            k: v
            for k, v in [
                ("sort_field", sort_field),
                ("sort_dir", sort_dir),
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_add_member_note(
        self, list_id, subscriber_hash, request_body=None
    ) -> dict[str, Any]:
        """
        Adds a note to a member of a mailing list.

        Args:
            list_id: str. The unique identifier for the Mailchimp audience (list) to which the member belongs.
            subscriber_hash: str. The MD5 hash of the lowercase version of the member's email address.
            request_body: dict or None. Optional. The request payload containing the note details to be added to the member. If None, the request is sent without a body.

        Returns:
            dict. The JSON response from the API containing details of the newly created note.

        Raises:
            ValueError: If 'list_id' or 'subscriber_hash' is None.
            requests.HTTPError: If the HTTP request to add the note fails (e.g., due to a client or server error).

        Tags:
            add, list-management, member, note, api-call
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}/notes"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_member_note(
        self, list_id, subscriber_hash, note_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieve a specific note associated with a list member from the remote API.

        Args:
            list_id: str. The unique ID of the Mailchimp list.
            subscriber_hash: str. The MD5 hash of the list member's email address.
            note_id: str. The unique ID of the note to retrieve.
            fields: Optional[list[str]]. A list of fields to include in the response. If None, all fields are returned.
            exclude_fields: Optional[list[str]]. A list of fields to exclude from the response. If None, all fields are included.

        Returns:
            dict[str, Any]: A dictionary containing the details of the specified member note.

        Raises:
            ValueError: If any of the required parameters ('list_id', 'subscriber_hash', or 'note_id') are None.
            HTTPError: If the HTTP request to the API fails or returns an error status.

        Tags:
            get, list, member, note, api, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        if note_id is None:
            raise ValueError("Missing required parameter 'note_id'")
        url = (
            f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}/notes/{note_id}"
        )
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_update_note_specific_list_member(
        self, list_id, subscriber_hash, note_id, request_body=None
    ) -> dict[str, Any]:
        """
        Updates a specific note for a list member in the email marketing platform.

        Args:
            list_id: str. The unique identifier of the list containing the member.
            subscriber_hash: str. The MD5 hash of the lowercase version of the list member’s email address.
            note_id: str. The unique identifier of the note to update.
            request_body: dict or None. The note data to update. Optional; if not provided, no data is sent.

        Returns:
            dict. The updated note as returned by the API.

        Raises:
            ValueError: If any of 'list_id', 'subscriber_hash', or 'note_id' is None.
            requests.HTTPError: If the API response status code indicates an error.

        Tags:
            update, list-member, note, management, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        if note_id is None:
            raise ValueError("Missing required parameter 'note_id'")
        url = (
            f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}/notes/{note_id}"
        )
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_delete_note(self, list_id, subscriber_hash, note_id) -> Any:
        """
        Deletes a note associated with a specific subscriber in a list.

        Args:
            list_id: The unique identifier for the list containing the subscriber.
            subscriber_hash: A unique hash representing the subscriber within the list.
            note_id: The unique identifier for the note to be deleted.

        Returns:
            dict: The API response parsed as a JSON dictionary after successfully deleting the note.

        Raises:
            ValueError: Raised if any of the required parameters ('list_id', 'subscriber_hash', or 'note_id') is None.
            HTTPError: Raised if the HTTP request to delete the note fails (e.g., due to a non-2xx response code).

        Tags:
            delete, note-management, list, subscriber, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        if note_id is None:
            raise ValueError("Missing required parameter 'note_id'")
        url = (
            f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}/notes/{note_id}"
        )
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_remove_member_permanent(self, list_id, subscriber_hash) -> Any:
        """
        Permanently removes a member from a mailing list using their subscriber hash.

        Args:
            list_id: The unique identifier of the mailing list from which the member should be permanently removed.
            subscriber_hash: The MD5 hash of the lowercase version of the member's email address.

        Returns:
            A dictionary containing the API response data indicating the result of the permanent removal operation.

        Raises:
            ValueError: Raised if either 'list_id' or 'subscriber_hash' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails, such as due to network issues or an unsuccessful response.

        Tags:
            remove, member-management, list, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/lists/{list_id}/members/{subscriber_hash}/actions/delete-permanent"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_list_merge_fields(
        self,
        list_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        type=None,
        required=None,
    ) -> dict[str, Any]:
        """
        Retrieves the list merge fields for a specified list, with optional filtering and pagination parameters.

        Args:
            list_id: str. The unique identifier for the list whose merge fields are to be retrieved.
            fields: Optional[list[str]]. A comma-separated list of fields to include in the response. Defaults to None.
            exclude_fields: Optional[list[str]]. A comma-separated list of fields to exclude from the response. Defaults to None.
            count: Optional[int]. The number of records to return. Defaults to None.
            offset: Optional[int]. The number of records to skip in the response. Defaults to None.
            type: Optional[str]. Restrict results to merge fields of a specific type. Defaults to None.
            required: Optional[bool]. Restrict results to fields that are required. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the merge fields data for the specified list.

        Raises:
            ValueError: If 'list_id' is None.
            requests.HTTPError: If the HTTP request to the API endpoint fails.

        Tags:
            list, merge-fields, retrieve, api, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/merge-fields"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("type", type),
                ("required", required),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_add_merge_field(
        self,
        list_id,
        name,
        type,
        tag=None,
        required=None,
        default_value=None,
        public=None,
        display_order=None,
        options=None,
        help_text=None,
    ) -> dict[str, Any]:
        """
        Adds a new merge field to a specified mailing list.

        Args:
            list_id: The unique ID of the mailing list to add the merge field to.
            name: The display name of the merge field.
            type: The type of the merge field (e.g., 'text', 'number', 'date', etc.).
            tag: An optional merge tag that can be used for template variables.
            required: Boolean indicating whether the merge field is required.
            default_value: The default value for the merge field.
            public: Boolean indicating whether the merge field is visible to list subscribers.
            display_order: Integer indicating the order in which to display this field.
            options: A dictionary of additional options for the merge field.
            help_text: Help text to explain the merge field to subscribers.

        Returns:
            A dictionary containing the details of the newly created merge field.

        Raises:
            ValueError: Raised when any of the required parameters (list_id, name, type) are None.

        Tags:
            add, merge-field, list, create
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        request_body = {
            "tag": tag,
            "name": name,
            "type": type,
            "required": required,
            "default_value": default_value,
            "public": public,
            "display_order": display_order,
            "options": options,
            "help_text": help_text,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}/merge-fields"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_merge_field_info(
        self, list_id, merge_id, exclude_fields=None, fields=None
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific merge field within a list, allowing optional filtering of returned fields.

        Args:
            list_id: str. The unique identifier of the list containing the merge field.
            merge_id: str. The unique identifier of the merge field to retrieve information for.
            exclude_fields: Optional[list or str]. Comma-separated list or list of field names to exclude from the response.
            fields: Optional[list or str]. Comma-separated list or list of fields to include in the response.

        Returns:
            dict. The JSON response from the API containing information about the specified merge field.

        Raises:
            ValueError: If 'list_id' or 'merge_id' is None.
            requests.HTTPError: If the API request fails with an error response.

        Tags:
            get, merge-field, list, management, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if merge_id is None:
            raise ValueError("Missing required parameter 'merge_id'")
        url = f"{self.base_url}/lists/{list_id}/merge-fields/{merge_id}"
        query_params = {
            k: v
            for k, v in [("exclude_fields", exclude_fields), ("fields", fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_update_merge_field(
        self,
        list_id,
        merge_id,
        name,
        tag=None,
        required=None,
        default_value=None,
        public=None,
        display_order=None,
        options=None,
        help_text=None,
    ) -> dict[str, Any]:
        """
        Updates an existing merge field for a specific list with the provided attributes.

        Args:
            list_id: str. The unique identifier for the list containing the merge field to update.
            merge_id: str. The unique identifier of the merge field to update.
            name: str. The name for the merge field.
            tag: str or None. The merge tag for the field. Optional.
            required: bool or None. Whether the field is required. Optional.
            default_value: Any or None. The default value for the field. Optional.
            public: bool or None. Whether the field is visible to contacts. Optional.
            display_order: int or None. Order in which to display the field. Optional.
            options: dict or None. Additional options for field settings. Optional.
            help_text: str or None. Help text describing the field. Optional.

        Returns:
            dict[str, Any]: The updated merge field data as returned by the API.

        Raises:
            ValueError: If any of 'list_id', 'merge_id', or 'name' parameters are missing.
            HTTPError: If the HTTP request to update the merge field fails.

        Tags:
            update, merge-field, list, management, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if merge_id is None:
            raise ValueError("Missing required parameter 'merge_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "tag": tag,
            "name": name,
            "required": required,
            "default_value": default_value,
            "public": public,
            "display_order": display_order,
            "options": options,
            "help_text": help_text,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}/merge-fields/{merge_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_delete_merge_field(self, list_id, merge_id) -> Any:
        """
        Deletes a merge field from a specified list by its merge field ID.

        Args:
            list_id: The unique identifier of the list from which the merge field will be deleted.
            merge_id: The unique identifier of the merge field to delete.

        Returns:
            A dictionary containing the API response data after successfully deleting the merge field.

        Raises:
            ValueError: Raised if 'list_id' or 'merge_id' is None.
            HTTPError: Raised if the HTTP request to the API fails or returns an error status code.

        Tags:
            delete, merge-field, list-management, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if merge_id is None:
            raise ValueError("Missing required parameter 'merge_id'")
        url = f"{self.base_url}/lists/{list_id}/merge-fields/{merge_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_webhooks_info(self, list_id) -> dict[str, Any]:
        """
        Retrieves webhook information for the specified list.

        Args:
            list_id: The unique identifier of the list for which to fetch webhook details.

        Returns:
            A dictionary containing webhook information associated with the specified list.

        Raises:
            ValueError: If 'list_id' is None.
            requests.exceptions.HTTPError: If the HTTP request to fetch webhooks fails.

        Tags:
            list, get, webhooks, fetch, info
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/webhooks"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_create_webhook(self, list_id, request_body=None) -> dict[str, Any]:
        """
        Creates a new webhook for the specified list by sending a POST request to the API.

        Args:
            list_id: The unique ID of the list for which to create the webhook.
            request_body: Optional dictionary containing the payload to include in the webhook creation request. Defaults to None.

        Returns:
            A dictionary representing the JSON response from the API with details of the created webhook.

        Raises:
            ValueError: If 'list_id' is not provided.
            requests.HTTPError: If the API response contains an HTTP error status code.

        Tags:
            create, webhook, api, list
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/webhooks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_webhook_info(self, list_id, webhook_id) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific webhook for a given list.

        Args:
            list_id: The unique identifier of the list containing the webhook.
            webhook_id: The unique identifier of the webhook whose information is to be retrieved.

        Returns:
            A dictionary containing webhook details as returned by the API.

        Raises:
            ValueError: Raised if 'list_id' or 'webhook_id' is None.
            requests.HTTPError: Raised if the HTTP request to retrieve webhook information fails.

        Tags:
            get, webhook, list, management, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if webhook_id is None:
            raise ValueError("Missing required parameter 'webhook_id'")
        url = f"{self.base_url}/lists/{list_id}/webhooks/{webhook_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_delete_webhook(self, list_id, webhook_id) -> Any:
        """
        Deletes a webhook from a specified list.

        Args:
            list_id: The unique identifier of the list containing the webhook to be deleted.
            webhook_id: The unique identifier of the webhook to be deleted.

        Returns:
            JSON response from the server confirming the webhook deletion.

        Raises:
            ValueError: If either list_id or webhook_id parameter is None.
            HTTPError: If the HTTP request returns an unsuccessful status code.

        Tags:
            delete, webhook, management, lists
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if webhook_id is None:
            raise ValueError("Missing required parameter 'webhook_id'")
        url = f"{self.base_url}/lists/{list_id}/webhooks/{webhook_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_update_webhook_settings(
        self, list_id, webhook_id, request_body=None
    ) -> dict[str, Any]:
        """
        Updates the settings of a specific webhook associated with a list.

        Args:
            list_id: The unique identifier of the list containing the webhook to update.
            webhook_id: The unique identifier of the webhook whose settings are to be updated.
            request_body: An optional dictionary containing the webhook settings to update. Defaults to None.

        Returns:
            A dictionary representing the updated webhook configuration as returned by the API.

        Raises:
            ValueError: If 'list_id' or 'webhook_id' is None.
            requests.HTTPError: If the API response contains an HTTP error status.

        Tags:
            update, webhook, list, management, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if webhook_id is None:
            raise ValueError("Missing required parameter 'webhook_id'")
        url = f"{self.base_url}/lists/{list_id}/webhooks/{webhook_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_signup_forms(self, list_id) -> dict[str, Any]:
        """
        Retrieves the signup forms associated with a specific list by its unique identifier.

        Args:
            list_id: The unique identifier of the list whose signup forms are to be retrieved.

        Returns:
            A dictionary containing the details of the signup forms for the specified list.

        Raises:
            ValueError: Raised if the 'list_id' parameter is None.
            requests.HTTPError: Raised if the HTTP response contains an unsuccessful status code.

        Tags:
            list, get, signup-forms, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/signup-forms"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_customize_signup_form(
        self, list_id, header=None, contents=None, styles=None
    ) -> dict[str, Any]:
        """
        Customizes the signup form of a specific list by updating its header, contents, or styles via an API call.

        Args:
            list_id: str. The unique identifier for the list whose signup form is to be customized.
            header: Optional[str]. The header content for the signup form. If not provided, the header is not updated.
            contents: Optional[Any]. The main contents of the signup form. If not provided, the contents are not updated.
            styles: Optional[Any]. The style definitions for the signup form. If not provided, the styles are not updated.

        Returns:
            dict[str, Any]: The JSON response from the API containing the updated details of the signup form.

        Raises:
            ValueError: Raised if the required parameter 'list_id' is not provided.
            requests.HTTPError: Raised if the API response contains an HTTP error status.

        Tags:
            lists, customize, signup-form, update, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        request_body = {
            "header": header,
            "contents": contents,
            "styles": styles,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/lists/{list_id}/signup-forms"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_locations(
        self, list_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves the locations associated with a specific list, optionally filtering the returned fields.

        Args:
            list_id: str. The unique identifier of the list whose locations are to be retrieved. Required.
            fields: Optional[str or list of str]. Comma-separated list or list of specific fields to include in the response. Defaults to None.
            exclude_fields: Optional[str or list of str]. Comma-separated list or list of fields to exclude from the response. Defaults to None.

        Returns:
            dict. The JSON response containing details about the locations associated with the specified list.

        Raises:
            ValueError: If 'list_id' is None.
            requests.HTTPError: If the HTTP request to fetch locations fails or returns an error response.

        Tags:
            list, get, locations, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/locations"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_surveys_info(self, list_id) -> Any:
        """
        Retrieves survey information associated with a specific list ID.

        Args:
            list_id: The unique identifier of the list for which survey information is to be retrieved.

        Returns:
            A deserialized JSON object containing details of the surveys linked to the specified list.

        Raises:
            ValueError: Raised if 'list_id' is None.
            HTTPError: Raised if the HTTP request to retrieve survey information fails.

        Tags:
            list, get, surveys, info, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        url = f"{self.base_url}/lists/{list_id}/surveys"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def lists_get_survey_details(self, list_id, survey_id) -> Any:
        """
        Retrieves the details of a specific survey associated with a given list by making an HTTP GET request.

        Args:
            list_id: The unique identifier of the list containing the survey.
            survey_id: The unique identifier of the survey to retrieve details for.

        Returns:
            A JSON-decoded object with the survey details, as returned by the API.

        Raises:
            ValueError: If 'list_id' or 'survey_id' is None.
            HTTPError: If the HTTP request to the API fails or returns an error status.

        Tags:
            get, survey, details, list, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if survey_id is None:
            raise ValueError("Missing required parameter 'survey_id'")
        url = f"{self.base_url}/lists/{list_id}/surveys/{survey_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def surveys_publish_survey_action(self, list_id, survey_id) -> Any:
        """
        Publishes a specified survey for a given list by sending a publish action request.

        Args:
            list_id: The unique identifier of the list associated with the survey.
            survey_id: The unique identifier of the survey to be published.

        Returns:
            A JSON object containing the response data from the publish action.

        Raises:
            ValueError: If either 'list_id' or 'survey_id' is None.
            requests.HTTPError: If the HTTP request to publish the survey fails.

        Tags:
            publish, survey, action, management
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if survey_id is None:
            raise ValueError("Missing required parameter 'survey_id'")
        url = f"{self.base_url}/lists/{list_id}/surveys/{survey_id}/actions/publish"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def surveys_unpublish_survey_action(self, list_id, survey_id) -> Any:
        """
        Unpublishes a survey for a specific mailing list.

        Args:
            list_id: The unique identifier of the mailing list containing the survey.
            survey_id: The unique identifier of the survey to be unpublished.

        Returns:
            JSON response containing the result of the unpublish action.

        Raises:
            ValueError: If list_id or survey_id parameters are None.
            HTTPError: If the HTTP request returns an unsuccessful status code.

        Tags:
            unpublish, survey, action, mailing-list, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if survey_id is None:
            raise ValueError("Missing required parameter 'survey_id'")
        url = f"{self.base_url}/lists/{list_id}/surveys/{survey_id}/actions/unpublish"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def surveys_generate_campaign(self, list_id, survey_id) -> dict[str, Any]:
        """
        Creates an email campaign for a specific survey and list by triggering the appropriate API action.

        Args:
            list_id: str. The unique identifier of the list for which the campaign is to be generated.
            survey_id: str. The unique identifier of the survey to be used in the campaign.

        Returns:
            dict. The JSON response from the API containing details about the created email campaign.

        Raises:
            ValueError: Raised if either 'list_id' or 'survey_id' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails with a non-successful status.

        Tags:
            generate, campaign, survey, email, api
        """
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if survey_id is None:
            raise ValueError("Missing required parameter 'survey_id'")
        url = (
            f"{self.base_url}/lists/{list_id}/surveys/{survey_id}/actions/create-email"
        )
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def landing_pages_list(
        self,
        sort_dir=None,
        sort_field=None,
        fields=None,
        exclude_fields=None,
        count=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of landing pages from the API, supporting sorting, field selection, and result count customization.

        Args:
            sort_dir: Optional[str]. Direction to sort the results ('asc' or 'desc').
            sort_field: Optional[str]. Field by which to sort the landing pages.
            fields: Optional[str or list of str]. Comma-separated fields or list of fields to include in each landing page entry.
            exclude_fields: Optional[str or list of str]. Comma-separated fields or list of fields to exclude from each landing page entry.
            count: Optional[int]. Maximum number of landing pages to return.

        Returns:
            dict[str, Any]: The JSON response containing the landing page data from the API.

        Raises:
            requests.HTTPError: If the API response contains an HTTP error status code.

        Tags:
            list, landing-pages, api, query, important
        """
        url = f"{self.base_url}/landing-pages"
        query_params = {
            k: v
            for k, v in [
                ("sort_dir", sort_dir),
                ("sort_field", sort_field),
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def landing_pages_create_new_mailchimp_landing_page(
        self,
        use_default_list=None,
        title=None,
        description=None,
        name=None,
        store_id=None,
        list_id=None,
        type=None,
        template_id=None,
        tracking=None,
    ) -> dict[str, Any]:
        """
        Creates a new Mailchimp landing page with the specified attributes.

        Args:
            use_default_list: bool or None. Whether to use the default list for the landing page. If None, this parameter is omitted.
            title: str or None. The title of the landing page.
            description: str or None. A description of the landing page.
            name: str or None. The internal name for the landing page.
            store_id: str or None. The store ID to associate with the landing page.
            list_id: str or None. The audience (list) ID to associate with the landing page.
            type: str or None. The type/category of the landing page.
            template_id: str or None. The template ID for the landing page layout.
            tracking: dict or None. Tracking configuration for the landing page.

        Returns:
            dict[str, Any]: JSON response containing details of the created Mailchimp landing page.

        Raises:
            requests.HTTPError: If the server returns an unsuccessful status code in response to the API request.

        Tags:
            create, landing-page, mailchimp, api
        """
        request_body = {
            "title": title,
            "description": description,
            "name": name,
            "store_id": store_id,
            "list_id": list_id,
            "type": type,
            "template_id": template_id,
            "tracking": tracking,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/landing-pages"
        query_params = {
            k: v for k, v in [("use_default_list", use_default_list)] if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def landing_pages_get_page_info(
        self, page_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves information about a specific landing page.

        Args:
            page_id: The unique identifier for the landing page to retrieve. Required.
            fields: Comma-separated list of fields to include in the response. If specified, only these fields will be returned.
            exclude_fields: Comma-separated list of fields to exclude from the response.

        Returns:
            A dictionary containing the landing page information with keys as field names and their corresponding values.

        Raises:
            ValueError: When the required parameter 'page_id' is None.
            HTTPError: When the API request fails (through raise_for_status()).

        Tags:
            get, retrieve, landing-page, api, information
        """
        if page_id is None:
            raise ValueError("Missing required parameter 'page_id'")
        url = f"{self.base_url}/landing-pages/{page_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def landing_pages_update_page_by_id(
        self,
        page_id,
        title=None,
        description=None,
        name=None,
        store_id=None,
        list_id=None,
        tracking=None,
    ) -> dict[str, Any]:
        """
        Updates the details of a landing page identified by its unique ID.

        Args:
            page_id: str. Unique identifier of the landing page to update. Must not be None.
            title: Optional[str]. The new title for the landing page.
            description: Optional[str]. The new description for the landing page.
            name: Optional[str]. The new internal name for the landing page.
            store_id: Optional[str]. The store ID to associate with the landing page.
            list_id: Optional[str]. The subscriber list ID to associate with the landing page.
            tracking: Optional[Any]. Tracking configuration or data for the landing page.

        Returns:
            dict[str, Any]: The updated landing page data as a dictionary parsed from the service response.

        Raises:
            ValueError: If 'page_id' is None.
            requests.HTTPError: If the HTTP request to update the landing page fails (e.g., network error or non-2xx status).

        Tags:
            update, patch, landing-pages, management
        """
        if page_id is None:
            raise ValueError("Missing required parameter 'page_id'")
        request_body = {
            "title": title,
            "description": description,
            "name": name,
            "store_id": store_id,
            "list_id": list_id,
            "tracking": tracking,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/landing-pages/{page_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def landing_pages_delete_page(self, page_id) -> Any:
        """
        Deletes a landing page resource identified by the given page ID.

        Args:
            page_id: The unique identifier of the landing page to delete. Must not be None.

        Returns:
            The parsed JSON response from the server after successful deletion of the landing page.

        Raises:
            ValueError: If the 'page_id' parameter is None.
            requests.HTTPError: If the DELETE request to the server fails or the response contains an HTTP error status.

        Tags:
            delete, landing-page, management
        """
        if page_id is None:
            raise ValueError("Missing required parameter 'page_id'")
        url = f"{self.base_url}/landing-pages/{page_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def landing_pages_publish_action(self, page_id) -> Any:
        """
        Publishes a landing page by sending a POST request to the publish action endpoint for the specified page ID.

        Args:
            page_id: The unique identifier of the landing page to be published. Must not be None.

        Returns:
            The JSON-decoded response from the publish action endpoint.

        Raises:
            ValueError: If page_id is None.
            requests.HTTPError: If the HTTP request fails with a status error.

        Tags:
            publish, landing-page, async_job, action
        """
        if page_id is None:
            raise ValueError("Missing required parameter 'page_id'")
        url = f"{self.base_url}/landing-pages/{page_id}/actions/publish"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def landing_pages_unpublish_action(self, page_id) -> Any:
        """
        Unpublishes a landing page by sending a POST request to the corresponding unpublish action endpoint.

        Args:
            page_id: The unique identifier of the landing page to be unpublished.

        Returns:
            The response from the API as a deserialized JSON object.

        Raises:
            ValueError: If 'page_id' is None.
            requests.HTTPError: If the HTTP request returns an unsuccessful status code.

        Tags:
            unpublish, landing-page, async-job, management
        """
        if page_id is None:
            raise ValueError("Missing required parameter 'page_id'")
        url = f"{self.base_url}/landing-pages/{page_id}/actions/unpublish"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def landing_pages_get_content(
        self, page_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Fetches the content of a specified landing page, allowing optional filtering of fields to include or exclude.

        Args:
            page_id: str. The unique identifier of the landing page whose content is to be retrieved.
            fields: Optional[list[str] or str]. A comma-separated list or list of field names to include in the response. Defaults to None, which returns all fields.
            exclude_fields: Optional[list[str] or str]. A comma-separated list or list of field names to exclude from the response. Defaults to None.

        Returns:
            dict[str, Any]: The JSON response containing the landing page content.

        Raises:
            ValueError: If 'page_id' is None.
            requests.HTTPError: If the HTTP request to retrieve the landing page content fails.

        Tags:
            get, landing-pages, content, api, async-job
        """
        if page_id is None:
            raise ValueError("Missing required parameter 'page_id'")
        url = f"{self.base_url}/landing-pages/{page_id}/content"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_list_campaign_reports(
        self,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        type=None,
        before_send_time=None,
        since_send_time=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of campaign report summaries with optional filtering and pagination.

        Args:
            fields: Optional[str or list[str]]. Comma-separated list or array of fields to include in the response for partial responses.
            exclude_fields: Optional[str or list[str]]. Comma-separated list or array of fields to exclude from the response.
            count: Optional[int]. The number of records to return in the response.
            offset: Optional[int]. The number of records to skip for pagination.
            type: Optional[str]. Restricts results to a specific report type (e.g., 'sent', 'scheduled').
            before_send_time: Optional[str]. ISO 8601 timestamp to fetch reports sent before this time.
            since_send_time: Optional[str]. ISO 8601 timestamp to fetch reports sent since this time.

        Returns:
            dict[str, Any]: A dictionary containing the list of campaign reports and related metadata.

        Raises:
            requests.HTTPError: If the HTTP request to the reports endpoint fails or returns an unsuccessful status code.

        Tags:
            list, reports, campaign, fetch, api, management
        """
        url = f"{self.base_url}/reports"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("type", type),
                ("before_send_time", before_send_time),
                ("since_send_time", since_send_time),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_specific_campaign_report(
        self, campaign_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves a specific campaign report with optional field filtering.

        Args:
            campaign_id: str. The unique identifier of the campaign for which the report is requested.
            fields: Optional[list[str]]. Specific fields to include in the report response. Default is None.
            exclude_fields: Optional[list[str]]. Fields to exclude from the report response. Default is None.

        Returns:
            dict[str, Any]: The JSON response containing the campaign report data.

        Raises:
            ValueError: If campaign_id is None.
            requests.HTTPError: If the HTTP request to fetch the report fails or returns an error response.

        Tags:
            reports, fetch, campaign, filtering, api-call
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/reports/{campaign_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_list_abuse_reports(
        self, campaign_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves the list of abuse reports for a specified email campaign.

        Args:
            campaign_id: The unique identifier of the campaign for which to retrieve abuse reports. Must not be None.
            fields: Optional; a comma-separated list of fields to include in the response.
            exclude_fields: Optional; a comma-separated list of fields to exclude from the response.

        Returns:
            A dictionary containing the campaign's abuse report data.

        Raises:
            ValueError: If 'campaign_id' is None.
            HTTPError: If the HTTP request to the remote reports API fails or returns an unsuccessful status code.

        Tags:
            list, reports, abuse-reports, campaign, api
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/reports/{campaign_id}/abuse-reports"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_get_abuse_report(
        self, campaign_id, report_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieve detailed information about a specific abuse report for a given campaign.

        Args:
            campaign_id: str. The unique identifier of the campaign containing the abuse report.
            report_id: str. The unique identifier of the abuse report to retrieve.
            fields: Optional[list[str] or str]. Specific fields to include in the response. If not provided, all fields are returned.
            exclude_fields: Optional[list[str] or str]. Fields to exclude from the response. If not provided, no fields are excluded.

        Returns:
            dict[str, Any]: A dictionary containing details for the requested abuse report.

        Raises:
            ValueError: If either 'campaign_id' or 'report_id' is not provided.
            requests.HTTPError: If the HTTP request to the API fails (non-success status code).

        Tags:
            get, report, abuse, status, management, api
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if report_id is None:
            raise ValueError("Missing required parameter 'report_id'")
        url = f"{self.base_url}/reports/{campaign_id}/abuse-reports/{report_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_list_campaign_feedback(
        self, campaign_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves campaign feedback advice for a specified campaign report.

        Args:
            campaign_id: str. The unique identifier for the campaign whose feedback advice is to be retrieved.
            fields: Optional[list[str]]. A list of specific fields to include in the response. If None, all fields are included.
            exclude_fields: Optional[list[str]]. A list of fields to exclude from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: A dictionary containing the campaign feedback advice data as returned by the API.

        Raises:
            ValueError: If 'campaign_id' is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            reports, list, campaign, feedback, api-call
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/reports/{campaign_id}/advice"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_get_campaign_click_details(
        self,
        campaign_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        sort_field=None,
        sort_dir=None,
    ) -> dict[str, Any]:
        """
        Retrieves detailed click activity for a specific campaign report.

        Args:
            campaign_id: str. The unique identifier for the campaign whose click details are to be retrieved.
            fields: Optional[str]. A comma-separated list of fields to include in the response.
            exclude_fields: Optional[str]. A comma-separated list of fields to exclude from the response.
            count: Optional[int]. The number of records to return.
            offset: Optional[int]. The number of records to skip in the response.
            sort_field: Optional[str]. The field by which to sort returned results.
            sort_dir: Optional[str]. The order of sorting: 'ASC' for ascending or 'DESC' for descending.

        Returns:
            dict[str, Any]: A dictionary containing campaign click details as returned by the API.

        Raises:
            ValueError: Raised if the required parameter 'campaign_id' is None.
            HTTPError: Raised if the HTTP request to the API fails (e.g., due to network issues or invalid responses).

        Tags:
            reports, get, campaign, click-details, api, read
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/reports/{campaign_id}/click-details"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("sort_field", sort_field),
                ("sort_dir", sort_dir),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_specific_link_details(
        self, campaign_id, link_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific link for a campaign.

        Args:
            campaign_id: The unique identifier of the campaign for which to retrieve link details.
            link_id: The unique identifier of the link for which to retrieve details.
            fields: Optional comma-separated list of fields to include in the response. If provided, only specified fields will be returned.
            exclude_fields: Optional comma-separated list of fields to exclude from the response.

        Returns:
            A dictionary containing the detailed information about the specified link.

        Raises:
            ValueError: Raised when either campaign_id or link_id is None.
            HTTPError: Raised when the API request fails.

        Tags:
            retrieve, report, link-details, campaign, api
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if link_id is None:
            raise ValueError("Missing required parameter 'link_id'")
        url = f"{self.base_url}/reports/{campaign_id}/click-details/{link_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_list_clicked_link_subscribers(
        self,
        campaign_id,
        link_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of subscribers who clicked a specific link in a campaign.

        Args:
            campaign_id: Required. The unique identifier for the campaign.
            link_id: Required. The unique identifier for the link within the campaign.
            fields: Optional. A comma-separated list of fields to include in the response.
            exclude_fields: Optional. A comma-separated list of fields to exclude from the response.
            count: Optional. The number of records to return.
            offset: Optional. The number of records from a collection to skip.

        Returns:
            A dictionary containing information about subscribers who clicked the specified link.

        Raises:
            ValueError: Raised when required parameters 'campaign_id' or 'link_id' are not provided.
            HTTPError: Raised when the API request fails.

        Tags:
            list, reports, subscribers, clicks, campaign
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if link_id is None:
            raise ValueError("Missing required parameter 'link_id'")
        url = f"{self.base_url}/reports/{campaign_id}/click-details/{link_id}/members"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_specific_link_subscriber(
        self, campaign_id, link_id, subscriber_hash, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves click report details for a specific subscriber who clicked a particular link in a campaign.

        Args:
            campaign_id: str. The unique ID of the campaign to retrieve the report from.
            link_id: str. The unique ID of the link for which click details are requested.
            subscriber_hash: str. The hashed identifier of the subscriber whose details are to be fetched.
            fields: Optional[list[str]]. A list of fields to include in the response. Defaults to None, returning all fields.
            exclude_fields: Optional[list[str]]. A list of fields to exclude from the response. Defaults to None.

        Returns:
            dict[str, Any]: Dictionary containing the click details for the specified link and subscriber.

        Raises:
            ValueError: If any of campaign_id, link_id, or subscriber_hash is None.
            HTTPError: If the HTTP request made to retrieve the report fails (non-2xx status code).

        Tags:
            reports, subscriber, link, retrieve, get, campaign, analytics
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if link_id is None:
            raise ValueError("Missing required parameter 'link_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/reports/{campaign_id}/click-details/{link_id}/members/{subscriber_hash}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_list_campaign_open_details(
        self,
        campaign_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        since=None,
        sort_field=None,
        sort_dir=None,
    ) -> dict[str, Any]:
        """
        Retrieves detailed open reports for a specific email campaign, with optional filtering, sorting, and pagination.

        Args:
            campaign_id: str. The unique ID for the campaign whose open details are to be retrieved.
            fields: Optional[List[str]]. A comma-separated list of fields to include in the response.
            exclude_fields: Optional[List[str]]. A comma-separated list of fields to exclude from the response.
            count: Optional[int]. The number of records to return.
            offset: Optional[int]. The number of records to skip before returning results.
            since: Optional[str]. ISO 8601-formatted date string to filter results to those updated after the specified time.
            sort_field: Optional[str]. Field by which to sort results.
            sort_dir: Optional[str]. Direction in which to sort results ('ASC' or 'DESC').

        Returns:
            dict[str, Any]: A dictionary containing the open details report for the specified campaign.

        Raises:
            ValueError: If 'campaign_id' is not provided.
            requests.HTTPError: If the HTTP request to the report endpoint returns an unsuccessful status code.

        Tags:
            list, report, campaign, management
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/reports/{campaign_id}/open-details"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("since", since),
                ("sort_field", sort_field),
                ("sort_dir", sort_dir),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_open_subscriber_details(
        self, campaign_id, subscriber_hash, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves detailed open report information for a specific subscriber in a given campaign.

        Args:
            campaign_id: str. The unique identifier for the campaign whose open report details are requested.
            subscriber_hash: str. The MD5 hash of the lowercase version of the list member's email address.
            fields: Optional[list[str]]. A list of specific fields to include in the response. If None, all fields are returned.
            exclude_fields: Optional[list[str]]. A list of fields to exclude from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: A dictionary containing the detailed open report data for the specified subscriber in the campaign.

        Raises:
            ValueError: Raised if 'campaign_id' or 'subscriber_hash' is None.
            requests.HTTPError: Raised if the HTTP request to the reports API fails with a non-success status code.

        Tags:
            fetch, reports, subscriber, campaign, details, ai
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/reports/{campaign_id}/open-details/{subscriber_hash}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_list_domain_performance_stats(
        self, campaign_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves domain performance statistics for a specific campaign, with optional field filtering.

        Args:
            campaign_id: str. The unique identifier of the campaign for which domain performance stats are requested.
            fields: Optional[list[str] or str]. Specific fields to include in the response. If None, all fields are included.
            exclude_fields: Optional[list[str] or str]. Fields to exclude from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: A dictionary containing the domain performance statistics for the specified campaign.

        Raises:
            ValueError: If 'campaign_id' is None.
            requests.HTTPError: If the HTTP request to the API endpoint fails or returns an error response.

        Tags:
            reports, list, domain-performance, api, stats
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/reports/{campaign_id}/domain-performance"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_list_eepurl_activity(
        self, campaign_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves EepURL activity details for a specified campaign report.

        Args:
            campaign_id: str. The unique identifier for the campaign whose EepURL activity will be retrieved. Required.
            fields: Optional[list[str]]. A list of specific fields to include in the response. Defaults to None.
            exclude_fields: Optional[list[str]]. A list of fields to exclude from the response. Defaults to None.

        Returns:
            dict[str, Any]: The EepURL activity report data as a dictionary parsed from the JSON API response.

        Raises:
            ValueError: If 'campaign_id' is None.
            HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            list, retrieve, reports, campaign, management
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/reports/{campaign_id}/eepurl"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_list_email_activity(
        self,
        campaign_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        since=None,
    ) -> dict[str, Any]:
        """
        Retrieves the email activity report for a specific campaign, with optional filtering and field selection.

        Args:
            campaign_id: str. The unique identifier for the campaign. Required.
            fields: Optional[str or list]. A comma-separated list or list of fields to include in the response. Defaults to None.
            exclude_fields: Optional[str or list]. A comma-separated list or list of fields to exclude from the response. Defaults to None.
            count: Optional[int]. The number of records to return. Defaults to None.
            offset: Optional[int]. The number of records to skip before returning results. Defaults to None.
            since: Optional[str]. Restricts results to activity since this ISO 8601 timestamp. Defaults to None.

        Returns:
            dict. The email activity report data for the specified campaign, as returned by the API.

        Raises:
            ValueError: If 'campaign_id' is None.
            requests.HTTPError: If the HTTP request to the API fails with an error response.

        Tags:
            reports, list, email-activity, api
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/reports/{campaign_id}/email-activity"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("since", since),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_get_subscriber_activity(
        self, campaign_id, subscriber_hash, fields=None, exclude_fields=None, since=None
    ) -> dict[str, Any]:
        """
        Gets the email activity for a specific subscriber in a campaign.

        Args:
            campaign_id: The unique ID of the campaign to retrieve email activity for.
            subscriber_hash: The MD5 hash of the lowercase version of the subscriber's email address.
            fields: A comma-separated list of fields to return. Reference fields from your response object to limit what you return.
            exclude_fields: A comma-separated list of fields to exclude from the response.
            since: Restrict results to activity after a specific time, formatted as ISO 8601.

        Returns:
            A dictionary containing the subscriber's email activity data for the specified campaign.

        Raises:
            ValueError: Raised when required parameters 'campaign_id' or 'subscriber_hash' are not provided.
            HTTPError: Raised when the API request fails.

        Tags:
            get, activity, reports, email, subscriber, campaign
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/reports/{campaign_id}/email-activity/{subscriber_hash}"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("since", since),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_list_top_open_locations(
        self, campaign_id, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of top open locations for a specific campaign report, with optional filtering, field selection, and pagination.

        Args:
            campaign_id: str. The unique identifier for the campaign whose open location reports are to be fetched. Required.
            fields: str or list of str, optional. Comma-separated list or list of fields to include in the response.
            exclude_fields: str or list of str, optional. Comma-separated list or list of fields to exclude from the response.
            count: int, optional. The number of records to return in the response.
            offset: int, optional. The number of records from a collection to skip, for pagination.

        Returns:
            dict. A dictionary containing the open location report data for the specified campaign.

        Raises:
            ValueError: If 'campaign_id' is None.
            requests.HTTPError: If the HTTP request to the reports API fails or returns an unsuccessful status code.

        Tags:
            list, reports, open-locations, campaign, management
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/reports/{campaign_id}/locations"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_list_campaign_recipients(
        self, campaign_id, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of recipients for a specific email campaign report.

        Args:
            campaign_id: str. Unique identifier for the campaign whose recipients are being listed.
            fields: Optional[list[str]]. Specific fields to include in the response. If None, all fields are returned.
            exclude_fields: Optional[list[str]]. Specific fields to exclude from the response. If None, no fields are excluded.
            count: Optional[int]. The number of records to return. If None, the default number is returned.
            offset: Optional[int]. The number of records to skip for pagination. If None, returns from the start.

        Returns:
            dict. A JSON-decoded dictionary containing recipient information for the specified campaign report.

        Raises:
            ValueError: Raised if 'campaign_id' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns a non-success status code.

        Tags:
            list, recipients, campaign, reports, api, management
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/reports/{campaign_id}/sent-to"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_campaign_recipient_info(
        self, campaign_id, subscriber_hash, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a recipient's interaction with a specific campaign report.

        Args:
            campaign_id: str. The unique ID for the campaign whose recipient information will be retrieved.
            subscriber_hash: str. The MD5 hash of the lowercase version of the list member’s email address.
            fields: list[str] or None. Optional list of fields to include in the response.
            exclude_fields: list[str] or None. Optional list of fields to exclude from the response.

        Returns:
            dict[str, Any]: A dictionary containing the recipient information for the specified campaign report.

        Raises:
            ValueError: If 'campaign_id' or 'subscriber_hash' is None.
            requests.HTTPError: If the HTTP request to the reports API endpoint fails.

        Tags:
            reports, fetch, campaign, recipient-info, api
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/reports/{campaign_id}/sent-to/{subscriber_hash}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_list_child_campaign_reports(
        self, campaign_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Lists child campaign reports for a specified campaign.

        Args:
            campaign_id: The ID of the parent campaign to retrieve sub-reports for.
            fields: Optional comma-separated list of fields to include in the response.
            exclude_fields: Optional comma-separated list of fields to exclude from the response.

        Returns:
            A dictionary containing the child campaign reports data.

        Raises:
            ValueError: Raised when the required campaign_id parameter is None.
            HTTPError: Raised when the API request fails.

        Tags:
            list, reports, campaigns
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/reports/{campaign_id}/sub-reports"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_list_unsubscribed_members(
        self, campaign_id, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of unsubscribed members for a specified campaign.

        Args:
            campaign_id: The ID of the campaign for which to retrieve unsubscribed members.
            fields: Optional list of fields to include in the response.
            exclude_fields: Optional list of fields to exclude from the response.
            count: Optional number of records to return.
            offset: Optional offset for pagination.

        Returns:
            A dictionary containing the list of unsubscribed members.

        Raises:
            ValueError: Raised if the 'campaign_id' is None.

        Tags:
            list, report, campaign, unsubscribed, management
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/reports/{campaign_id}/unsubscribed"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_get_unsubscribed_member_info(
        self, campaign_id, subscriber_hash, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves information about a member who unsubscribed from a specific campaign report.

        Args:
            campaign_id: str. The unique identifier for the campaign whose unsubscribed member information is being requested.
            subscriber_hash: str. The MD5 hash of the lowercase version of the list member's email address.
            fields: Optional[list[str]]. A list of specific fields to include in the response. Defaults to None.
            exclude_fields: Optional[list[str]]. A list of fields to exclude from the response. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing information about the unsubscribed member for the given campaign.

        Raises:
            ValueError: Raised if 'campaign_id' or 'subscriber_hash' is not provided.
            requests.HTTPError: Raised if the HTTP request to the API fails.

        Tags:
            reports, get, member-info, unsubscribed, api
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        if subscriber_hash is None:
            raise ValueError("Missing required parameter 'subscriber_hash'")
        url = f"{self.base_url}/reports/{campaign_id}/unsubscribed/{subscriber_hash}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reports_get_campaign_product_activity(
        self,
        campaign_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        sort_field=None,
    ) -> dict[str, Any]:
        """
        Retrieves ecommerce product activity reports for a specified campaign, with optional filtering, pagination, and sorting.

        Args:
            campaign_id: str. The unique identifier for the campaign whose product activity report is to be fetched.
            fields: Optional[list[str]]. List of specific fields to include in the response. Defaults to None.
            exclude_fields: Optional[list[str]]. List of fields to exclude from the response. Defaults to None.
            count: Optional[int]. The number of records to return per page. Defaults to None.
            offset: Optional[int]. The number of records to skip for pagination. Defaults to None.
            sort_field: Optional[str]. The field by which to sort the results. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the campaign's ecommerce product activity data as returned by the API.

        Raises:
            ValueError: If 'campaign_id' is not provided.
            requests.HTTPError: If the API request fails or returns a non-successful HTTP response.

        Tags:
            reports, get, campaign, product-activity, api, fetch
        """
        if campaign_id is None:
            raise ValueError("Missing required parameter 'campaign_id'")
        url = f"{self.base_url}/reports/{campaign_id}/ecommerce-product-activity"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("sort_field", sort_field),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def templates_list_available_templates(
        self,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        created_by=None,
        since_date_created=None,
        before_date_created=None,
        type=None,
        category=None,
        folder_id=None,
        sort_field=None,
        content_type=None,
        sort_dir=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of available email templates with optional filtering, sorting, and pagination.

        Args:
            fields: Optional[str]. Comma-separated list of fields to include in the response.
            exclude_fields: Optional[str]. Comma-separated list of fields to exclude from the response.
            count: Optional[int]. The number of records to return in the response (for pagination).
            offset: Optional[int]. The number of records from a collection to skip (for pagination).
            created_by: Optional[str]. Filter templates by the user who created them.
            since_date_created: Optional[str]. Filters templates created after this ISO 8601 date/time.
            before_date_created: Optional[str]. Filters templates created before this ISO 8601 date/time.
            type: Optional[str]. Filter by template type (e.g., 'user', 'gallery').
            category: Optional[str]. Filter templates by category.
            folder_id: Optional[str]. Filter templates by folder ID.
            sort_field: Optional[str]. Field name to sort results by.
            content_type: Optional[str]. Filter templates by content type.
            sort_dir: Optional[str]. Sort direction, either 'ASC' for ascending or 'DESC' for descending.

        Returns:
            dict[str, Any]: A dictionary containing the list of available templates and related metadata.

        Raises:
            requests.HTTPError: If the HTTP request to the templates endpoint fails or returns an error status code.

        Tags:
            list, templates, filter, management
        """
        url = f"{self.base_url}/templates"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("created_by", created_by),
                ("since_date_created", since_date_created),
                ("before_date_created", before_date_created),
                ("type", type),
                ("category", category),
                ("folder_id", folder_id),
                ("sort_field", sort_field),
                ("content_type", content_type),
                ("sort_dir", sort_dir),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def templates_create_new_template(self, request_body=None) -> dict[str, Any]:
        """
        Creates a new template by sending a POST request to the templates endpoint.

        Args:
            request_body: Optional request payload as a dictionary to be sent in the POST request body. Defaults to None.

        Returns:
            A dictionary containing the JSON response from the templates API endpoint.

        Raises:
            HTTPError: If the HTTP request to the templates endpoint returns an unsuccessful status code.

        Tags:
            create, template, api, post
        """
        url = f"{self.base_url}/templates"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def templates_get_info(
        self, template_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieve detailed information about a specific template, with optional field filtering.

        Args:
            template_id: str. The unique identifier of the template to retrieve. Must not be None.
            fields: Optional[str or list of str]. Fields to include in the response. If None, all fields are returned.
            exclude_fields: Optional[str or list of str]. Fields to exclude from the response. If None, no fields are excluded.

        Returns:
            dict. A dictionary containing the template's information as returned by the API.

        Raises:
            ValueError: If 'template_id' is None.
            requests.HTTPError: If the HTTP request to retrieve the template fails.

        Tags:
            get, templates, info, api, management
        """
        if template_id is None:
            raise ValueError("Missing required parameter 'template_id'")
        url = f"{self.base_url}/templates/{template_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def templates_update_template_by_id(
        self, template_id, request_body=None
    ) -> dict[str, Any]:
        """
        Updates an existing template by its unique ID using provided data.

        Args:
            template_id: str. The unique identifier of the template to update. Must not be None.
            request_body: dict or None. The data to update the template with. If None, the template is updated with no additional data.

        Returns:
            dict[str, Any]: The JSON response containing the updated template details.

        Raises:
            ValueError: Raised if template_id is None.
            requests.HTTPError: Raised if the HTTP PATCH request to the template endpoint fails (e.g., network issues, server returns error status).

        Tags:
            update, template, patch, api
        """
        if template_id is None:
            raise ValueError("Missing required parameter 'template_id'")
        url = f"{self.base_url}/templates/{template_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def templates_delete_specific_template(self, template_id) -> Any:
        """
        Deletes a specific template identified by its template ID.

        Args:
            template_id: The unique identifier of the template to delete. Must not be None.

        Returns:
            The JSON response from the server after deleting the template.

        Raises:
            ValueError: If 'template_id' is None.
            requests.HTTPError: If the HTTP request for deletion fails.

        Tags:
            delete, template, api, management
        """
        if template_id is None:
            raise ValueError("Missing required parameter 'template_id'")
        url = f"{self.base_url}/templates/{template_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def templates_view_default_content(
        self, template_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves the default content for a specific template, optionally filtering included or excluded fields.

        Args:
            template_id: str. The unique identifier of the template whose default content is to be retrieved.
            fields: Optional[list[str]] or str. Comma-separated list or iterable specifying which fields to include in the response. If None, all default fields are included.
            exclude_fields: Optional[list[str]] or str. Comma-separated list or iterable specifying fields to exclude from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: The default content of the specified template as a dictionary.

        Raises:
            ValueError: If 'template_id' is None.
            requests.HTTPError: If the HTTP request to retrieve the template content fails.

        Tags:
            fetch, template, default-content, api, http
        """
        if template_id is None:
            raise ValueError("Missing required parameter 'template_id'")
        url = f"{self.base_url}/templates/{template_id}/default-content"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_list_account_orders(
        self,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        campaign_id=None,
        outreach_id=None,
        customer_id=None,
        has_outreach=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of ecommerce orders for the account with optional filtering and field selection.

        Args:
            fields: Optional[list[str]]. Specific fields to include in the response for each order.
            exclude_fields: Optional[list[str]]. Fields to exclude from the response for each order.
            count: Optional[int]. The number of orders to return in the response.
            offset: Optional[int]. The number of orders to skip before starting to collect the response set.
            campaign_id: Optional[str]. Filter orders by associated campaign ID.
            outreach_id: Optional[str]. Filter orders by outreach ID.
            customer_id: Optional[str]. Filter orders by customer ID.
            has_outreach: Optional[bool]. Filter orders that have or do not have associated outreach activity.

        Returns:
            dict[str, Any]: A dictionary containing the list of orders and related metadata as returned by the ecommerce API.

        Raises:
            requests.HTTPError: If the request to the ecommerce API fails or returns an unsuccessful status code.

        Tags:
            list, ecommerce, orders, account, filter, api
        """
        url = f"{self.base_url}/ecommerce/orders"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("campaign_id", campaign_id),
                ("outreach_id", outreach_id),
                ("customer_id", customer_id),
                ("has_outreach", has_outreach),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_list_stores(
        self, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of e-commerce stores accessible to the authenticated user, with optional filtering and pagination.

        Args:
            fields: Optional[list or str]. Specific fields to include in the response. Can be a comma-separated string or list of field names.
            exclude_fields: Optional[list or str]. Fields to exclude from the response. Can be a comma-separated string or list of field names.
            count: Optional[int]. Number of store records to return. Used for pagination.
            offset: Optional[int]. Number of store records to skip from the start. Used for pagination.

        Returns:
            dict[str, Any]: A dictionary containing the list of e-commerce stores and associated metadata as provided by the API.

        Raises:
            requests.HTTPError: If the API request returns an unsuccessful status code.

        Tags:
            list, ecommerce, stores, api, management
        """
        url = f"{self.base_url}/ecommerce/stores"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_add_store_to_mailchimp_account(
        self,
        id,
        list_id,
        name,
        currency_code,
        platform=None,
        domain=None,
        is_syncing=None,
        email_address=None,
        money_format=None,
        primary_locale=None,
        timezone=None,
        phone=None,
        address=None,
    ) -> dict[str, Any]:
        """
        Adds an ecommerce store to a Mailchimp account using the provided parameters.

        Args:
            id: The unique identifier for the store.
            list_id: The ID of the list associated with the store.
            name: The name of the store.
            currency_code: The currency code used by the store.
            platform: The platform type of the store. Optional.
            domain: The domain of the store. Optional.
            is_syncing: Indicates whether the store is syncing with Mailchimp. Optional.
            email_address: The email address associated with the store. Optional.
            money_format: The money format used by the store. Optional.
            primary_locale: The primary locale of the store. Optional.
            timezone: The timezone of the store. Optional.
            phone: The phone number of the store. Optional.
            address: The address of the store. Optional.

        Returns:
            A dictionary containing the response from Mailchimp after adding the store.

        Raises:
            ValueError: Raised when any of the required parameters (id, list_id, name, currency_code) are missing.
            requests.HTTPError: Raised if there is an HTTP error during the POST request.

        Tags:
            store, ecommerce, mailchimp, management
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        if list_id is None:
            raise ValueError("Missing required parameter 'list_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if currency_code is None:
            raise ValueError("Missing required parameter 'currency_code'")
        request_body = {
            "id": id,
            "list_id": list_id,
            "name": name,
            "platform": platform,
            "domain": domain,
            "is_syncing": is_syncing,
            "email_address": email_address,
            "currency_code": currency_code,
            "money_format": money_format,
            "primary_locale": primary_locale,
            "timezone": timezone,
            "phone": phone,
            "address": address,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_store_info(
        self, store_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Fetches information about a specific e-commerce store, allowing optional inclusion or exclusion of specified fields.

        Args:
            store_id: str. The unique identifier for the store to retrieve information for.
            fields: Optional[list[str]]. List of fields to include in the response. If None, all fields are included.
            exclude_fields: Optional[list[str]]. List of fields to exclude from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: A dictionary containing the store information as returned by the e-commerce API.

        Raises:
            ValueError: If 'store_id' is not provided or is None.
            requests.HTTPError: If the HTTP request to the API fails (e.g., network error, 4xx or 5xx status codes).

        Tags:
            get, ecommerce, store, info, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_update_store(
        self,
        store_id,
        name=None,
        platform=None,
        domain=None,
        is_syncing=None,
        email_address=None,
        currency_code=None,
        money_format=None,
        primary_locale=None,
        timezone=None,
        phone=None,
        address=None,
    ) -> dict[str, Any]:
        """
        Updates an e-commerce store with the specified parameters.

        Args:
            store_id: Required. The unique identifier of the store to update.
            name: Optional. The new name for the store.
            platform: Optional. The e-commerce platform the store uses.
            domain: Optional. The domain URL of the store.
            is_syncing: Optional. Boolean indicating whether the store is actively syncing.
            email_address: Optional. The contact email address for the store.
            currency_code: Optional. The currency code used by the store (e.g., 'USD', 'EUR').
            money_format: Optional. The format used to display prices in the store.
            primary_locale: Optional. The primary language/locale of the store.
            timezone: Optional. The timezone where the store operates.
            phone: Optional. The contact phone number for the store.
            address: Optional. The physical address of the store.

        Returns:
            A dictionary containing the updated store information from the API response.

        Raises:
            ValueError: Raised when 'store_id' parameter is None.
            HTTPError: Raised when the API request fails.

        Tags:
            update, ecommerce, store, api, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        request_body = {
            "name": name,
            "platform": platform,
            "domain": domain,
            "is_syncing": is_syncing,
            "email_address": email_address,
            "currency_code": currency_code,
            "money_format": money_format,
            "primary_locale": primary_locale,
            "timezone": timezone,
            "phone": phone,
            "address": address,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_delete_store(self, store_id) -> dict[str, Any]:
        """
        Deletes an e-commerce store identified by the given store ID.

        Args:
            store_id: str. The unique identifier of the e-commerce store to be deleted.

        Returns:
            dict. The JSON response from the API after successfully deleting the store.

        Raises:
            ValueError: Raised if the store_id parameter is None.
            requests.HTTPError: Raised if the HTTP DELETE request fails or returns an error status code.

        Tags:
            delete, ecommerce, api, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_store_carts(
        self, store_id, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of carts from an e-commerce store with optional field filtering and pagination.

        Args:
            store_id: str. The unique identifier for the store whose carts will be retrieved. Required.
            fields: Optional[str]. Comma-separated list of fields to include in the response. Defaults to None.
            exclude_fields: Optional[str]. Comma-separated list of fields to exclude from the response. Defaults to None.
            count: Optional[int]. The number of records to return per page for pagination. Defaults to None.
            offset: Optional[int]. The number of records to skip for pagination. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the list of carts and associated metadata returned by the API.

        Raises:
            ValueError: Raised if 'store_id' is None.
            requests.HTTPError: Raised if the HTTP request to fetch carts fails (non-2xx status code).

        Tags:
            get, list, carts, ecommerce, api, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/carts"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_add_cart_to_store(
        self,
        store_id,
        id,
        customer,
        currency_code,
        order_total,
        lines,
        campaign_id=None,
        checkout_url=None,
        tax_total=None,
    ) -> dict[str, Any]:
        """
        Adds a shopping cart to the specified e-commerce store with customer, order, and line item details.

        Args:
            store_id: str. The unique identifier of the store where the cart will be added.
            id: str. The unique identifier for the cart.
            customer: dict. Customer information associated with the cart.
            currency_code: str. The ISO currency code representing the cart's currency.
            order_total: float or int. The total amount for the order.
            lines: list. Line items included in the cart.
            campaign_id: Optional[str]. The marketing campaign ID associated with the cart, if any.
            checkout_url: Optional[str]. The URL where the customer can complete the checkout process.
            tax_total: Optional[float or int]. The total tax amount for the order, if applicable.

        Returns:
            dict[str, Any]: The JSON response from the API containing the created cart details.

        Raises:
            ValueError: Raised if any required parameter ('store_id', 'id', 'customer', 'currency_code', 'order_total', or 'lines') is missing.
            HTTPError: Raised if the API response indicates an unsuccessful request.

        Tags:
            add, cart, ecommerce, store, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        if customer is None:
            raise ValueError("Missing required parameter 'customer'")
        if currency_code is None:
            raise ValueError("Missing required parameter 'currency_code'")
        if order_total is None:
            raise ValueError("Missing required parameter 'order_total'")
        if lines is None:
            raise ValueError("Missing required parameter 'lines'")
        request_body = {
            "id": id,
            "customer": customer,
            "campaign_id": campaign_id,
            "checkout_url": checkout_url,
            "currency_code": currency_code,
            "order_total": order_total,
            "tax_total": tax_total,
            "lines": lines,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/carts"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_cart_info(
        self, store_id, cart_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific ecommerce cart from the specified store.

        Args:
            store_id: The unique identifier of the store containing the cart.
            cart_id: The unique identifier of the cart to retrieve.
            fields: Optional; a comma-separated list or array specifying fields to include in the response.
            exclude_fields: Optional; a comma-separated list or array specifying fields to exclude from the response.

        Returns:
            A dictionary containing the cart information as returned by the API.

        Raises:
            ValueError: Raised if 'store_id' or 'cart_id' is None.
            requests.HTTPError: Raised if the API request fails or returns an unsuccessful status code.

        Tags:
            get, ecommerce, cart, info, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if cart_id is None:
            raise ValueError("Missing required parameter 'cart_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/carts/{cart_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_update_cart_by_id(
        self,
        store_id,
        cart_id,
        customer=None,
        campaign_id=None,
        checkout_url=None,
        currency_code=None,
        order_total=None,
        tax_total=None,
        lines=None,
    ) -> dict[str, Any]:
        """
        Updates an existing e-commerce cart for a specified store and cart ID with new details such as customer info, campaign, checkout URL, currency, totals, and line items.

        Args:
            store_id: str. The unique identifier of the store containing the cart to update. Required.
            cart_id: str. The unique identifier of the cart to update. Required.
            customer: Optional[dict]. Customer information to associate with the cart.
            campaign_id: Optional[str]. Identifier for the marketing campaign linked to this cart.
            checkout_url: Optional[str]. URL where the customer can complete their purchase.
            currency_code: Optional[str]. The ISO currency code for this cart's totals.
            order_total: Optional[float]. The total value of the order.
            tax_total: Optional[float]. Total tax amount for the cart.
            lines: Optional[list]. A list of line item details to update in the cart.

        Returns:
            dict. A dictionary containing the updated cart details as returned by the API.

        Raises:
            ValueError: If 'store_id' or 'cart_id' is not provided.
            requests.HTTPError: If the HTTP request fails (non-2xx response code).

        Tags:
            update, cart, ecommerce, async-job, api, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if cart_id is None:
            raise ValueError("Missing required parameter 'cart_id'")
        request_body = {
            "customer": customer,
            "campaign_id": campaign_id,
            "checkout_url": checkout_url,
            "currency_code": currency_code,
            "order_total": order_total,
            "tax_total": tax_total,
            "lines": lines,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/carts/{cart_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_remove_cart(self, store_id, cart_id) -> Any:
        """
        Removes a specific cart from an e-commerce store by cart ID.

        Args:
            store_id: The unique identifier of the e-commerce store containing the cart to remove.
            cart_id: The unique identifier of the cart to be removed.

        Returns:
            A dictionary containing the JSON response from the delete operation.

        Raises:
            ValueError: Raised if 'store_id' or 'cart_id' is None.
            requests.HTTPError: Raised if the HTTP request fails or returns an error status.

        Tags:
            remove, cart, ecommerce, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if cart_id is None:
            raise ValueError("Missing required parameter 'cart_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/carts/{cart_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_list_cart_lines(
        self,
        store_id,
        cart_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
    ) -> dict[str, Any]:
        """
        Retrieves the list of line items from a specific e-commerce cart within a store.

        Args:
            store_id: str. The unique identifier for the store containing the cart.
            cart_id: str. The unique identifier for the cart whose lines are to be listed.
            fields: Optional[str]. Comma-separated list of fields to include in the response.
            exclude_fields: Optional[str]. Comma-separated list of fields to exclude from the response.
            count: Optional[int]. The number of records to return in the response.
            offset: Optional[int]. The number of records to skip in the response.

        Returns:
            dict[str, Any]: The server's JSON response containing the list of cart line items and related metadata.

        Raises:
            ValueError: If 'store_id' or 'cart_id' is not provided.
            requests.HTTPError: If the HTTP request to the server fails (e.g., non-2xx response).

        Tags:
            list, ecommerce, cart, batch
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if cart_id is None:
            raise ValueError("Missing required parameter 'cart_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/carts/{cart_id}/lines"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_add_cart_line_item(
        self, store_id, cart_id, id, product_id, product_variant_id, quantity, price
    ) -> dict[str, Any]:
        """
        Adds a line item to an existing cart in the specified ecommerce store.

        Args:
            store_id: str. Unique identifier of the ecommerce store.
            cart_id: str. Unique identifier of the cart to which the line item will be added.
            id: str. Unique identifier for the cart line item.
            product_id: str. Unique identifier of the product to add.
            product_variant_id: str. Unique identifier of the product variant.
            quantity: int. Number of units of the product to add to the cart.
            price: float. Price per unit of the product variant.

        Returns:
            dict. JSON-decoded response data containing details of the added cart line item.

        Raises:
            ValueError: If any required parameter is None.
            requests.HTTPError: If the HTTP request to the ecommerce API fails (e.g., returns a non-success status code).

        Tags:
            add, cart, ecommerce, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if cart_id is None:
            raise ValueError("Missing required parameter 'cart_id'")
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        if product_variant_id is None:
            raise ValueError("Missing required parameter 'product_variant_id'")
        if quantity is None:
            raise ValueError("Missing required parameter 'quantity'")
        if price is None:
            raise ValueError("Missing required parameter 'price'")
        request_body = {
            "id": id,
            "product_id": product_id,
            "product_variant_id": product_variant_id,
            "quantity": quantity,
            "price": price,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/carts/{cart_id}/lines"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_cart_line_item(
        self, store_id, cart_id, line_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves a specific cart line item from an e-commerce store by store, cart, and line identifiers, with optional field selection.

        Args:
            store_id: The unique identifier of the e-commerce store.
            cart_id: The unique identifier of the cart within the store.
            line_id: The unique identifier of the line item in the cart.
            fields: Optional; a comma-separated list of fields to include in the response.
            exclude_fields: Optional; a comma-separated list of fields to exclude from the response.

        Returns:
            A dictionary containing the details of the specified cart line item.

        Raises:
            ValueError: Raised if 'store_id', 'cart_id', or 'line_id' is None.
            requests.HTTPError: Raised if the HTTP request returned an unsuccessful status code.

        Tags:
            get, ecommerce, cart, line-item, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if cart_id is None:
            raise ValueError("Missing required parameter 'cart_id'")
        if line_id is None:
            raise ValueError("Missing required parameter 'line_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/carts/{cart_id}/lines/{line_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_update_cart_line_item(
        self,
        store_id,
        cart_id,
        line_id,
        product_id=None,
        product_variant_id=None,
        quantity=None,
        price=None,
    ) -> dict[str, Any]:
        """
        Updates a specific line item in an e-commerce cart with new product details, quantity, or price.

        Args:
            store_id: str. Unique identifier of the store containing the cart.
            cart_id: str. Unique identifier of the cart containing the line item.
            line_id: str. Unique identifier of the line item to update.
            product_id: Optional[str]. New product ID to associate with the line item, if changing.
            product_variant_id: Optional[str]. Specific product variant ID to update, if applicable.
            quantity: Optional[int]. New quantity for the line item.
            price: Optional[float]. New price for the line item. If omitted, price remains unchanged.

        Returns:
            dict[str, Any]: JSON object representing the updated cart line item.

        Raises:
            ValueError: Raised if any of the required parameters 'store_id', 'cart_id', or 'line_id' are missing.
            HTTPError: Raised if the HTTP PATCH request to update the cart line item fails.

        Tags:
            update, cart, ecommerce, line-item, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if cart_id is None:
            raise ValueError("Missing required parameter 'cart_id'")
        if line_id is None:
            raise ValueError("Missing required parameter 'line_id'")
        request_body = {
            "product_id": product_id,
            "product_variant_id": product_variant_id,
            "quantity": quantity,
            "price": price,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/carts/{cart_id}/lines/{line_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_delete_cart_line_item(self, store_id, cart_id, line_id) -> Any:
        """
        Deletes a specific line item from a shopping cart in the specified store.

        Args:
            store_id: The unique identifier of the store containing the cart.
            cart_id: The unique identifier of the cart from which the line item will be removed.
            line_id: The unique identifier of the line item to delete from the cart.

        Returns:
            The response from the API as a JSON object, typically containing the status or result of the delete operation.

        Raises:
            ValueError: If any of 'store_id', 'cart_id', or 'line_id' is None.
            requests.HTTPError: If the HTTP request to delete the cart line item fails.

        Tags:
            delete, ecommerce, cart, line-item, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if cart_id is None:
            raise ValueError("Missing required parameter 'cart_id'")
        if line_id is None:
            raise ValueError("Missing required parameter 'line_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/carts/{cart_id}/lines/{line_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_store_customers(
        self,
        store_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        email_address=None,
    ) -> dict[str, Any]:
        """
        Retrieves customers for a specified ecommerce store.

        Args:
            store_id: Required ID of the ecommerce store to retrieve customers from.
            fields: Optional fields to include in the customer data.
            exclude_fields: Optional fields to exclude from the customer data.
            count: Optional number of customers to return per page.
            offset: Optional offset for pagination in retrieving customers.
            email_address: Optional filter to retrieve customers by email address.

        Returns:
            A dictionary containing customer data for the specified ecommerce store.

        Raises:
            ValueError: Raised if the required 'store_id' parameter is missing.

        Tags:
            ecommerce, customer-retrieval
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/customers"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("email_address", email_address),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_add_customer_to_store(
        self,
        store_id,
        id,
        email_address,
        opt_in_status,
        company=None,
        first_name=None,
        last_name=None,
        address=None,
    ) -> dict[str, Any]:
        """
        Adds a customer to a specified e-commerce store.

        Args:
            store_id: str. Unique identifier of the e-commerce store to which the customer will be added.
            id: str. Unique identifier for the customer within the store.
            email_address: str. Email address of the customer.
            opt_in_status: str. The customer's opt-in status for marketing communications.
            company: str, optional. Company name associated with the customer.
            first_name: str, optional. First name of the customer.
            last_name: str, optional. Last name of the customer.
            address: dict or None, optional. Mailing address information for the customer.

        Returns:
            dict. The JSON response containing the details of the newly added customer.

        Raises:
            ValueError: Raised if any of the required parameters ('store_id', 'id', 'email_address', 'opt_in_status') are missing.
            requests.HTTPError: Raised if the HTTP response status code indicates an error.

        Tags:
            ecommerce, add, customer, create, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        if email_address is None:
            raise ValueError("Missing required parameter 'email_address'")
        if opt_in_status is None:
            raise ValueError("Missing required parameter 'opt_in_status'")
        request_body = {
            "id": id,
            "email_address": email_address,
            "opt_in_status": opt_in_status,
            "company": company,
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/customers"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_customer_info(
        self, store_id, customer_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieve detailed information about a specific customer in an e-commerce store.

        Args:
            store_id: str. The unique identifier of the e-commerce store.
            customer_id: str. The unique identifier of the customer whose information is to be retrieved.
            fields: Optional[list or str]. A list of specific fields to include in the response. If None, all fields are included.
            exclude_fields: Optional[list or str]. A list of fields to exclude from the response.

        Returns:
            dict[str, Any]: The customer's information as a dictionary containing the requested data fields.

        Raises:
            ValueError: If either 'store_id' or 'customer_id' is not provided.
            requests.HTTPError: If the HTTP request to retrieve customer information fails.

        Tags:
            get, customer-info, ecommerce, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if customer_id is None:
            raise ValueError("Missing required parameter 'customer_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/customers/{customer_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_add_or_update_customer(
        self,
        store_id,
        customer_id,
        id,
        email_address,
        opt_in_status,
        company=None,
        first_name=None,
        last_name=None,
        address=None,
    ) -> dict[str, Any]:
        """
        Adds a new e-commerce customer or updates an existing customer record for a specific store.

        Args:
            store_id: str. Unique identifier for the e-commerce store.
            customer_id: str. Unique identifier for the customer within the store.
            id: str. Global unique identifier for the customer resource.
            email_address: str. Customer's email address.
            opt_in_status: bool. Indicates whether the customer has opted in to marketing emails.
            company: str, optional. Customer's company name.
            first_name: str, optional. Customer's first name.
            last_name: str, optional. Customer's last name.
            address: dict, optional. Customer's physical address information.

        Returns:
            dict. The updated or created customer object as returned by the API.

        Raises:
            ValueError: If any required parameter (store_id, customer_id, id, email_address, or opt_in_status) is missing.
            requests.HTTPError: If the HTTP request to update or add the customer fails (non-2xx response).

        Tags:
            add, update, customer, ecommerce
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if customer_id is None:
            raise ValueError("Missing required parameter 'customer_id'")
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        if email_address is None:
            raise ValueError("Missing required parameter 'email_address'")
        if opt_in_status is None:
            raise ValueError("Missing required parameter 'opt_in_status'")
        request_body = {
            "id": id,
            "email_address": email_address,
            "opt_in_status": opt_in_status,
            "company": company,
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/customers/{customer_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_update_customer(
        self,
        store_id,
        customer_id,
        opt_in_status=None,
        company=None,
        first_name=None,
        last_name=None,
        address=None,
    ) -> dict[str, Any]:
        """
        Updates an existing customer's information in an e-commerce store.

        Args:
            store_id: str. Unique identifier of the e-commerce store.
            customer_id: str. Unique identifier of the customer to update.
            opt_in_status: Optional[bool]. Indicates whether the customer is opted in or out of marketing communications.
            company: Optional[str]. The company name associated with the customer.
            first_name: Optional[str]. Customer's first name.
            last_name: Optional[str]. Customer's last name.
            address: Optional[dict]. Customer's address information, structured as a dictionary.

        Returns:
            dict. JSON response containing the updated customer information returned by the API.

        Raises:
            ValueError: Raised if either 'store_id' or 'customer_id' is None.
            HTTPError: Raised if the HTTP request to update the customer fails.

        Tags:
            update, ecommerce, customer, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if customer_id is None:
            raise ValueError("Missing required parameter 'customer_id'")
        request_body = {
            "opt_in_status": opt_in_status,
            "company": company,
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/customers/{customer_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_remove_customer(self, store_id, customer_id) -> Any:
        """
        Removes a customer from an e-commerce store

        Args:
            store_id: The unique identifier of the store from which the customer is being removed
            customer_id: The unique identifier of the customer to be removed

        Returns:
            A JSON response from the server indicating the result of the customer removal

        Raises:
            ValueError: Raised if either the store_id or customer_id is missing

        Tags:
            remove, ecommerce, customer-management, api-call
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if customer_id is None:
            raise ValueError("Missing required parameter 'customer_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/customers/{customer_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_store_promo_rules(
        self, store_id, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of promotional rules for a specified e-commerce store, with optional filtering and pagination.

        Args:
            store_id: str. Unique identifier of the store for which to retrieve promo rules.
            fields: Optional[str or list of str]. Comma-separated list or list of fields to include in the response.
            exclude_fields: Optional[str or list of str]. Comma-separated list or list of fields to exclude from the response.
            count: Optional[int]. Number of records to return in the response.
            offset: Optional[int]. Number of records to skip, used for pagination.

        Returns:
            dict[str, Any]: A dictionary containing the promotional rules and associated metadata for the specified store.

        Raises:
            ValueError: If 'store_id' is None.
            HTTPError: If the HTTP request to the API fails or an unexpected status code is received.

        Tags:
            get, ecommerce, promo-rules, list
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/promo-rules"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_add_promo_rule(
        self,
        store_id,
        description,
        id,
        amount,
        type,
        target,
        title=None,
        starts_at=None,
        ends_at=None,
        enabled=None,
        created_at_foreign=None,
        updated_at_foreign=None,
    ) -> dict[str, Any]:
        """
        Creates and adds a new promotional rule to a specified ecommerce store.

        Args:
            store_id: str. Unique identifier of the store where the promo rule will be added.
            description: str. Detailed description of the promotional rule.
            id: str. Unique identifier for the promotional rule.
            amount: float|int. Value representing the discount or benefit of the promo rule.
            type: str. Type or category of the promotional rule (e.g., percentage, fixed amount).
            target: str. Target entity or product category the promo rule applies to.
            title: str, optional. Title or short name for the promotional rule.
            starts_at: str, optional. Start date and time for the rule's validity in ISO 8601 format.
            ends_at: str, optional. End date and time for the rule's validity in ISO 8601 format.
            enabled: bool, optional. Indicates whether the rule is currently active.
            created_at_foreign: str, optional. Timestamp indicating when the promo rule was created in an external system.
            updated_at_foreign: str, optional. Timestamp indicating when the promo rule was last updated in an external system.

        Returns:
            dict. JSON response containing details of the created promotional rule.

        Raises:
            ValueError: If any required parameter ('store_id', 'description', 'id', 'amount', 'type', or 'target') is missing.
            requests.HTTPError: If the API request fails or returns an unsuccessful status code.

        Tags:
            add, promo-rule, ecommerce, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if description is None:
            raise ValueError("Missing required parameter 'description'")
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        if amount is None:
            raise ValueError("Missing required parameter 'amount'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        if target is None:
            raise ValueError("Missing required parameter 'target'")
        request_body = {
            "title": title,
            "description": description,
            "id": id,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "amount": amount,
            "type": type,
            "target": target,
            "enabled": enabled,
            "created_at_foreign": created_at_foreign,
            "updated_at_foreign": updated_at_foreign,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/promo-rules"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_store_promo_rule(
        self, store_id, promo_rule_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves a specific promotional rule for an e-commerce store, optionally filtering the response fields.

        Args:
            store_id: str. The unique identifier for the store whose promotional rule is to be fetched.
            promo_rule_id: str. The unique identifier of the promotional rule to retrieve.
            fields: Optional[List[str]]. Comma-separated list or list of fields to include in the response (default is None, returning all fields).
            exclude_fields: Optional[List[str]]. Comma-separated list or list of fields to exclude from the response (default is None, excluding no fields).

        Returns:
            dict[str, Any]: A dictionary containing the promotional rule's details as returned by the e-commerce API.

        Raises:
            ValueError: Raised if 'store_id' or 'promo_rule_id' is None.
            requests.HTTPError: Raised if the underlying HTTP request to the API fails or returns an error status code.

        Tags:
            get, ecommerce, promo-rule, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if promo_rule_id is None:
            raise ValueError("Missing required parameter 'promo_rule_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/promo-rules/{promo_rule_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_update_promo_rule(
        self,
        store_id,
        promo_rule_id,
        title=None,
        description=None,
        starts_at=None,
        ends_at=None,
        amount=None,
        type=None,
        target=None,
        enabled=None,
        created_at_foreign=None,
        updated_at_foreign=None,
    ) -> dict[str, Any]:
        """
        Updates an existing promotional rule for an ecommerce store.

        Args:
            store_id: Required string identifier for the store containing the promotional rule.
            promo_rule_id: Required string identifier for the promotional rule to update.
            title: Optional string for the name or title of the promotional rule.
            description: Optional string providing details about the promotional rule.
            starts_at: Optional datetime string indicating when the promotion begins.
            ends_at: Optional datetime string indicating when the promotion ends.
            amount: Optional number specifying the discount amount or percentage.
            type: Optional string indicating the type of promotion (e.g., percentage, fixed amount).
            target: Optional string specifying what the promotion applies to (e.g., products, orders).
            enabled: Optional boolean indicating whether the promotion is active.
            created_at_foreign: Optional datetime string for tracking creation time in external systems.
            updated_at_foreign: Optional datetime string for tracking update time in external systems.

        Returns:
            Dictionary containing the updated promotional rule data from the API response.

        Raises:
            ValueError: Raised when required parameters 'store_id' or 'promo_rule_id' are None.
            HTTPError: Raised when the API request fails.

        Tags:
            update, ecommerce, promotion, patch, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if promo_rule_id is None:
            raise ValueError("Missing required parameter 'promo_rule_id'")
        request_body = {
            "title": title,
            "description": description,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "amount": amount,
            "type": type,
            "target": target,
            "enabled": enabled,
            "created_at_foreign": created_at_foreign,
            "updated_at_foreign": updated_at_foreign,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/promo-rules/{promo_rule_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_delete_promo_rule(self, store_id, promo_rule_id) -> Any:
        """
        Deletes a specific promotional rule from an e-commerce store.

        Args:
            store_id: The unique identifier of the e-commerce store containing the promotional rule to delete.
            promo_rule_id: The unique identifier of the promotional rule to be deleted.

        Returns:
            A JSON response containing the result of the deletion operation.

        Raises:
            ValueError: Raised if 'store_id' or 'promo_rule_id' is None.
            requests.HTTPError: Raised if the HTTP request to delete the promotional rule fails.

        Tags:
            delete, promo-rule, ecommerce, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if promo_rule_id is None:
            raise ValueError("Missing required parameter 'promo_rule_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/promo-rules/{promo_rule_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_store_promo_codes(
        self,
        store_id,
        promo_rule_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of promo codes associated with a specific promo rule for a store from the e-commerce API.

        Args:
            store_id: str. The unique identifier of the store whose promo codes are to be retrieved.
            promo_rule_id: str. The unique identifier of the promo rule corresponding to the desired promo codes.
            fields: Optional[str or list of str]. Specific fields to include in the response.
            exclude_fields: Optional[str or list of str]. Specific fields to exclude from the response.
            count: Optional[int]. The number of records to return in the response.
            offset: Optional[int]. The number of records to skip in the response.

        Returns:
            dict[str, Any]: A dictionary containing the promo codes data retrieved from the API.

        Raises:
            ValueError: If 'store_id' or 'promo_rule_id' is None.
            requests.HTTPError: If the API request fails or returns an unsuccessful status code.

        Tags:
            get, ecommerce, promo-codes, management, list
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if promo_rule_id is None:
            raise ValueError("Missing required parameter 'promo_rule_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/promo-rules/{promo_rule_id}/promo-codes"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_add_promo_code(
        self,
        store_id,
        promo_rule_id,
        id,
        code,
        redemption_url,
        usage_count=None,
        enabled=None,
        created_at_foreign=None,
        updated_at_foreign=None,
    ) -> dict[str, Any]:
        """
        Adds a promotional code to a specific promotion rule within an ecommerce store.

        Args:
            store_id: str. The unique identifier of the ecommerce store.
            promo_rule_id: str. The unique identifier of the promotion rule to which the promo code will be added.
            id: str. The unique identifier for the new promo code.
            code: str. The promotional code string to be added.
            redemption_url: str. The URL where the promo code can be redeemed.
            usage_count: Optional[int]. The number of times the promo code can be used. If None, usage is unlimited.
            enabled: Optional[bool]. Whether the promo code is currently enabled.
            created_at_foreign: Optional[str]. The external creation timestamp for the promo code, if available.
            updated_at_foreign: Optional[str]. The external update timestamp for the promo code, if available.

        Returns:
            dict[str, Any]: A dictionary containing the details of the created promo code as returned by the API.

        Raises:
            ValueError: Raised if any of the required parameters ('store_id', 'promo_rule_id', 'id', 'code', 'redemption_url') is None.
            requests.HTTPError: Raised if the API request fails or returns an error status code.

        Tags:
            add, promo-code, ecommerce, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if promo_rule_id is None:
            raise ValueError("Missing required parameter 'promo_rule_id'")
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        if code is None:
            raise ValueError("Missing required parameter 'code'")
        if redemption_url is None:
            raise ValueError("Missing required parameter 'redemption_url'")
        request_body = {
            "id": id,
            "code": code,
            "redemption_url": redemption_url,
            "usage_count": usage_count,
            "enabled": enabled,
            "created_at_foreign": created_at_foreign,
            "updated_at_foreign": updated_at_foreign,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/promo-rules/{promo_rule_id}/promo-codes"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_promo_code(
        self, store_id, promo_rule_id, promo_code_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Fetches a promo code for an ecommerce store using a specific promo rule and promo code ID.

        Args:
            store_id: The ID of the store.
            promo_rule_id: The ID of the promo rule.
            promo_code_id: The ID of the promo code.
            fields: Optional list of fields to include in the response.
            exclude_fields: Optional list of fields to exclude from the response.

        Returns:
            A dictionary containing the promo code details.

        Raises:
            ValueError: Raised when any of the required parameters (store_id, promo_rule_id, promo_code_id) are missing.

        Tags:
            get, promo, ecommerce
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if promo_rule_id is None:
            raise ValueError("Missing required parameter 'promo_rule_id'")
        if promo_code_id is None:
            raise ValueError("Missing required parameter 'promo_code_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/promo-rules/{promo_rule_id}/promo-codes/{promo_code_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_update_promo_code(
        self,
        store_id,
        promo_rule_id,
        promo_code_id,
        code=None,
        redemption_url=None,
        usage_count=None,
        enabled=None,
        created_at_foreign=None,
        updated_at_foreign=None,
    ) -> dict[str, Any]:
        """
        Updates an existing promo code for a specific store and promotion rule with the provided details.

        Args:
            store_id: str. Unique identifier for the store containing the promo code. Required.
            promo_rule_id: str. Unique identifier for the promotion rule associated with the promo code. Required.
            promo_code_id: str. Unique identifier for the promo code to update. Required.
            code: Optional[str]. Updated promo code string. If not provided, existing value remains unchanged.
            redemption_url: Optional[str]. Updated URL for promo code redemption. If not provided, existing value remains unchanged.
            usage_count: Optional[int]. Updated total allowed usage count. If not provided, existing value remains unchanged.
            enabled: Optional[bool]. Whether the promo code is enabled. If not provided, existing value remains unchanged.
            created_at_foreign: Optional[str]. External creation timestamp in ISO format. If not provided, existing value remains unchanged.
            updated_at_foreign: Optional[str]. External update timestamp in ISO format. If not provided, existing value remains unchanged.

        Returns:
            dict[str, Any]: JSON response containing the updated promo code details.

        Raises:
            ValueError: If any of the required parameters ('store_id', 'promo_rule_id', or 'promo_code_id') is missing.
            requests.HTTPError: If the HTTP request to update the promo code fails.

        Tags:
            update, ecommerce, promo-code, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if promo_rule_id is None:
            raise ValueError("Missing required parameter 'promo_rule_id'")
        if promo_code_id is None:
            raise ValueError("Missing required parameter 'promo_code_id'")
        request_body = {
            "code": code,
            "redemption_url": redemption_url,
            "usage_count": usage_count,
            "enabled": enabled,
            "created_at_foreign": created_at_foreign,
            "updated_at_foreign": updated_at_foreign,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/promo-rules/{promo_rule_id}/promo-codes/{promo_code_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_delete_promo_code(
        self, store_id, promo_rule_id, promo_code_id
    ) -> Any:
        """
        Deletes a specific promotional code from an e-commerce store.

        Args:
            store_id: str. The unique identifier of the e-commerce store.
            promo_rule_id: str. The unique identifier of the promotion rule associated with the promo code.
            promo_code_id: str. The unique identifier of the promo code to be deleted.

        Returns:
            dict. The JSON response from the API after deleting the promo code.

        Raises:
            ValueError: Raised if any of the required parameters ('store_id', 'promo_rule_id', or 'promo_code_id') are missing.
            requests.HTTPError: Raised if the HTTP request to delete the promo code fails.

        Tags:
            delete, ecommerce, promo-code, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if promo_rule_id is None:
            raise ValueError("Missing required parameter 'promo_rule_id'")
        if promo_code_id is None:
            raise ValueError("Missing required parameter 'promo_code_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/promo-rules/{promo_rule_id}/promo-codes/{promo_code_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_list_store_orders(
        self,
        store_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        customer_id=None,
        has_outreach=None,
        campaign_id=None,
        outreach_id=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of orders for a specified e-commerce store, with optional filtering and field selection.

        Args:
            store_id: str. The unique identifier for the e-commerce store. Required.
            fields: Optional[str or list of str]. Comma-separated list or list of specific fields to include in the response.
            exclude_fields: Optional[str or list of str]. Comma-separated list or list of fields to exclude from the response.
            count: Optional[int]. Number of records to return in the response.
            offset: Optional[int]. Number of records to skip from the beginning of the response.
            customer_id: Optional[str]. Restricts results to orders for this customer ID.
            has_outreach: Optional[bool]. Restricts results to orders with outreach activity if True, or without if False.
            campaign_id: Optional[str]. Restricts results to orders associated with this campaign ID.
            outreach_id: Optional[str]. Restricts results to orders associated with this outreach ID.

        Returns:
            dict[str, Any]: A dictionary object containing the list of orders and related metadata for the specified store.

        Raises:
            ValueError: If 'store_id' is not provided.
            requests.HTTPError: If the HTTP request fails or returns an error response.

        Tags:
            list, ecommerce, orders, api, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/orders"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("customer_id", customer_id),
                ("has_outreach", has_outreach),
                ("campaign_id", campaign_id),
                ("outreach_id", outreach_id),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_add_order_to_store(
        self,
        store_id,
        id,
        customer,
        currency_code,
        order_total,
        lines,
        campaign_id=None,
        landing_site=None,
        financial_status=None,
        fulfillment_status=None,
        order_url=None,
        discount_total=None,
        tax_total=None,
        shipping_total=None,
        tracking_code=None,
        processed_at_foreign=None,
        cancelled_at_foreign=None,
        updated_at_foreign=None,
        shipping_address=None,
        billing_address=None,
        promos=None,
        outreach=None,
        tracking_number=None,
        tracking_carrier=None,
        tracking_url=None,
    ) -> dict[str, Any]:
        """
        Adds a new order to the specified e-commerce store by submitting order and customer details to the backend API.

        Args:
            store_id: str. Unique identifier for the e-commerce store.
            id: str. Unique identifier for the order.
            customer: dict. Customer information associated with the order.
            currency_code: str. ISO currency code for the order.
            order_total: float or int. Total amount for the order.
            lines: list. List of order line items, each representing a product or service in the order.
            campaign_id: Optional[str]. Identifier for the marketing campaign associated with the order.
            landing_site: Optional[str]. The landing site URL for the order.
            financial_status: Optional[str]. The financial status of the order (e.g., paid, pending).
            fulfillment_status: Optional[str]. The fulfillment status of the order (e.g., fulfilled, unfulfilled).
            order_url: Optional[str]. A URL link to the order details.
            discount_total: Optional[float or int]. Total discount applied to the order.
            tax_total: Optional[float or int]. Total tax amount for the order.
            shipping_total: Optional[float or int]. Total shipping cost for the order.
            tracking_code: Optional[str]. Tracking code for order fulfillment.
            processed_at_foreign: Optional[str]. Timestamp when the order was processed (foreign system).
            cancelled_at_foreign: Optional[str]. Timestamp if the order was cancelled (foreign system).
            updated_at_foreign: Optional[str]. Timestamp when the order was updated (foreign system).
            shipping_address: Optional[dict]. Shipping address information.
            billing_address: Optional[dict]. Billing address information.
            promos: Optional[list]. List of applied promotional codes or discounts.
            outreach: Optional[dict]. Outreach channel or campaign details.
            tracking_number: Optional[str]. Shipment tracking number.
            tracking_carrier: Optional[str]. Carrier used for shipping.
            tracking_url: Optional[str]. URL to track the shipment.

        Returns:
            dict. A JSON dictionary containing the details of the created order as returned by the backend API.

        Raises:
            ValueError: If any of the required parameters ('store_id', 'id', 'customer', 'currency_code', 'order_total', or 'lines') are missing or None.
            requests.HTTPError: If the API request fails (non-success HTTP status code).

        Tags:
            add, order, ecommerce, store, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        if customer is None:
            raise ValueError("Missing required parameter 'customer'")
        if currency_code is None:
            raise ValueError("Missing required parameter 'currency_code'")
        if order_total is None:
            raise ValueError("Missing required parameter 'order_total'")
        if lines is None:
            raise ValueError("Missing required parameter 'lines'")
        request_body = {
            "id": id,
            "customer": customer,
            "campaign_id": campaign_id,
            "landing_site": landing_site,
            "financial_status": financial_status,
            "fulfillment_status": fulfillment_status,
            "currency_code": currency_code,
            "order_total": order_total,
            "order_url": order_url,
            "discount_total": discount_total,
            "tax_total": tax_total,
            "shipping_total": shipping_total,
            "tracking_code": tracking_code,
            "processed_at_foreign": processed_at_foreign,
            "cancelled_at_foreign": cancelled_at_foreign,
            "updated_at_foreign": updated_at_foreign,
            "shipping_address": shipping_address,
            "billing_address": billing_address,
            "promos": promos,
            "lines": lines,
            "outreach": outreach,
            "tracking_number": tracking_number,
            "tracking_carrier": tracking_carrier,
            "tracking_url": tracking_url,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/orders"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_store_order_info(
        self, store_id, order_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves information for a specific order from an e-commerce store.

        Args:
            store_id: str. The unique identifier for the e-commerce store.
            order_id: str. The unique identifier for the order within the store.
            fields: Optional[list[str]]. A list of fields to include in the response. Defaults to None.
            exclude_fields: Optional[list[str]]. A list of fields to exclude from the response. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the order details retrieved from the store.

        Raises:
            ValueError: If 'store_id' or 'order_id' is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status.

        Tags:
            get, order-info, ecommerce, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if order_id is None:
            raise ValueError("Missing required parameter 'order_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/orders/{order_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_update_specific_order(
        self,
        store_id,
        order_id,
        customer=None,
        campaign_id=None,
        landing_site=None,
        financial_status=None,
        fulfillment_status=None,
        currency_code=None,
        order_total=None,
        order_url=None,
        discount_total=None,
        tax_total=None,
        shipping_total=None,
        tracking_code=None,
        processed_at_foreign=None,
        cancelled_at_foreign=None,
        updated_at_foreign=None,
        shipping_address=None,
        billing_address=None,
        promos=None,
        lines=None,
        outreach=None,
        tracking_number=None,
        tracking_carrier=None,
        tracking_url=None,
    ) -> dict[str, Any]:
        """
        Updates details for a specific e-commerce order in the store, modifying only the provided fields.

        Args:
            store_id: str. The unique identifier for the e-commerce store. Required.
            order_id: str. The unique identifier for the order to update. Required.
            customer: Optional[dict]. Information about the customer associated with the order.
            campaign_id: Optional[str]. Identifier for the campaign linked to the order.
            landing_site: Optional[str]. The landing site URL where the order originated.
            financial_status: Optional[str]. Financial status of the order (e.g., paid, refunded).
            fulfillment_status: Optional[str]. Fulfillment status of the order (e.g., fulfilled, unfulfilled).
            currency_code: Optional[str]. Currency code used in the transaction (e.g., USD, EUR).
            order_total: Optional[float]. Total value of the order.
            order_url: Optional[str]. URL linking to the order details.
            discount_total: Optional[float]. Total discount applied to the order.
            tax_total: Optional[float]. Total tax charged for the order.
            shipping_total: Optional[float]. Total shipping cost for the order.
            tracking_code: Optional[str]. Tracking code associated with the order's shipment.
            processed_at_foreign: Optional[str]. Timestamp when the order was processed (external system, ISO 8601).
            cancelled_at_foreign: Optional[str]. Timestamp when the order was cancelled (external system, ISO 8601).
            updated_at_foreign: Optional[str]. Timestamp of the last update to the order (external system, ISO 8601).
            shipping_address: Optional[dict]. Shipping address information for the order.
            billing_address: Optional[dict]. Billing address information for the order.
            promos: Optional[list]. List of promotional codes or discounts applied.
            lines: Optional[list]. Individual items or products within the order.
            outreach: Optional[dict]. Outreach or marketing attribution details.
            tracking_number: Optional[str]. Package tracking number for fulfillment.
            tracking_carrier: Optional[str]. Carrier responsible for shipping (e.g., UPS, FedEx).
            tracking_url: Optional[str]. URL to track the shipment progress.

        Returns:
            dict[str, Any]: The updated order record as returned by the e-commerce API.

        Raises:
            ValueError: If 'store_id' or 'order_id' is not provided.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status code.

        Tags:
            update, order, ecommerce, api, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if order_id is None:
            raise ValueError("Missing required parameter 'order_id'")
        request_body = {
            "customer": customer,
            "campaign_id": campaign_id,
            "landing_site": landing_site,
            "financial_status": financial_status,
            "fulfillment_status": fulfillment_status,
            "currency_code": currency_code,
            "order_total": order_total,
            "order_url": order_url,
            "discount_total": discount_total,
            "tax_total": tax_total,
            "shipping_total": shipping_total,
            "tracking_code": tracking_code,
            "processed_at_foreign": processed_at_foreign,
            "cancelled_at_foreign": cancelled_at_foreign,
            "updated_at_foreign": updated_at_foreign,
            "shipping_address": shipping_address,
            "billing_address": billing_address,
            "promos": promos,
            "lines": lines,
            "outreach": outreach,
            "tracking_number": tracking_number,
            "tracking_carrier": tracking_carrier,
            "tracking_url": tracking_url,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/orders/{order_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_delete_order(self, store_id, order_id) -> Any:
        """
        Deletes an order from an ecommerce store based on the provided store ID and order ID.

        Args:
            store_id: The unique identifier of the ecommerce store.
            order_id: The unique identifier of the order to be deleted.

        Returns:
            The server's JSON response after deleting the order.

        Raises:
            ValueError: Raised when either 'store_id' or 'order_id' is missing.

        Tags:
            delete, ecommerce, order-management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if order_id is None:
            raise ValueError("Missing required parameter 'order_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/orders/{order_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_store_order_lines(
        self,
        store_id,
        order_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
    ) -> dict[str, Any]:
        """
        Retrieves the order line items for a specific order in a store, with optional field selection and pagination.

        Args:
            store_id: str. The unique identifier of the store whose order lines are to be retrieved.
            order_id: str. The unique identifier of the order for which to fetch line items.
            fields: Optional[str or list of str]. Comma-separated string or list specifying which fields to include in the response.
            exclude_fields: Optional[str or list of str]. Comma-separated string or list specifying which fields to exclude from the response.
            count: Optional[int]. The number of order lines to return (for pagination).
            offset: Optional[int]. The number of order lines to skip before starting to return results (for pagination).

        Returns:
            dict. The response JSON as a dictionary containing the order line items for the given order.

        Raises:
            ValueError: If either 'store_id' or 'order_id' is not provided.
            requests.HTTPError: If the HTTP request fails or an error response is returned.

        Tags:
            get, list, order-lines, ecommerce, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if order_id is None:
            raise ValueError("Missing required parameter 'order_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/orders/{order_id}/lines"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_add_order_line_item(
        self,
        store_id,
        order_id,
        id,
        product_id,
        product_variant_id,
        quantity,
        price,
        discount=None,
    ) -> dict[str, Any]:
        """
        Adds a line item to an existing order in the specified e-commerce store.

        Args:
            store_id: str. The unique identifier of the store where the order resides.
            order_id: str. The unique identifier of the order to which the line item will be added.
            id: str. The unique identifier for the new order line item.
            product_id: str. The unique identifier of the product being ordered.
            product_variant_id: str. The unique identifier of the product variant being ordered.
            quantity: int. The number of units for this line item.
            price: float. The unit price for the line item.
            discount: Optional[float]. The discount amount applied to this line item, if any.

        Returns:
            dict[str, Any]: A dictionary representing the created order line item as returned by the API.

        Raises:
            ValueError: If any required parameter (store_id, order_id, id, product_id, product_variant_id, quantity, or price) is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an error response.

        Tags:
            ecommerce, add, order-line, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if order_id is None:
            raise ValueError("Missing required parameter 'order_id'")
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        if product_variant_id is None:
            raise ValueError("Missing required parameter 'product_variant_id'")
        if quantity is None:
            raise ValueError("Missing required parameter 'quantity'")
        if price is None:
            raise ValueError("Missing required parameter 'price'")
        request_body = {
            "id": id,
            "product_id": product_id,
            "product_variant_id": product_variant_id,
            "quantity": quantity,
            "price": price,
            "discount": discount,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/orders/{order_id}/lines"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_order_line_item(
        self, store_id, order_id, line_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves a specific line item from an order in the specified ecommerce store.

        Args:
            store_id: str. The unique identifier of the store containing the order.
            order_id: str. The unique identifier of the order from which to retrieve the line item.
            line_id: str. The unique identifier of the line item to retrieve.
            fields: Optional[str or list[str]]. Comma-separated list or list of fields to include in the response. Defaults to None.
            exclude_fields: Optional[str or list[str]]. Comma-separated list or list of fields to exclude from the response. Defaults to None.

        Returns:
            dict. JSON representation of the requested order line item.

        Raises:
            ValueError: If any of the required parameters 'store_id', 'order_id', or 'line_id' are None.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status code.

        Tags:
            get, order, order-line-item, ecommerce, fetch, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if order_id is None:
            raise ValueError("Missing required parameter 'order_id'")
        if line_id is None:
            raise ValueError("Missing required parameter 'line_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/orders/{order_id}/lines/{line_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_update_order_line(
        self,
        store_id,
        order_id,
        line_id,
        product_id=None,
        product_variant_id=None,
        quantity=None,
        price=None,
        discount=None,
    ) -> dict[str, Any]:
        """
        Updates an existing order line in a store's e-commerce order with new product or pricing information.

        Args:
            store_id: str. Unique identifier for the store the order belongs to.
            order_id: str. Unique identifier for the order containing the line item.
            line_id: str. Unique identifier for the order line to update.
            product_id: Optional[str]. New product ID to assign to the order line. If not provided, the product remains unchanged.
            product_variant_id: Optional[str]. New product variant ID for the order line. If not provided, the variant remains unchanged.
            quantity: Optional[int]. New quantity for the order line. If not provided, the quantity remains unchanged.
            price: Optional[float]. New price for the order line. If not provided, the price remains unchanged.
            discount: Optional[float]. New discount to apply to the order line. If not provided, the discount remains unchanged.

        Returns:
            dict[str, Any]: A dictionary containing the updated order line details as returned by the API.

        Raises:
            ValueError: If 'store_id', 'order_id', or 'line_id' is not provided.
            requests.HTTPError: If the HTTP request to update the order line fails (e.g., invalid data, network issue, server error).

        Tags:
            ecommerce, update, order-line, api, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if order_id is None:
            raise ValueError("Missing required parameter 'order_id'")
        if line_id is None:
            raise ValueError("Missing required parameter 'line_id'")
        request_body = {
            "product_id": product_id,
            "product_variant_id": product_variant_id,
            "quantity": quantity,
            "price": price,
            "discount": discount,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/orders/{order_id}/lines/{line_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_delete_order_line(self, store_id, order_id, line_id) -> Any:
        """
        Deletes a specific line item from an order in the specified store via the e-commerce API.

        Args:
            store_id: The unique identifier of the store containing the order.
            order_id: The unique identifier of the order from which the line item will be deleted.
            line_id: The unique identifier of the line item to delete from the order.

        Returns:
            A dictionary containing the API response data for the deleted order line.

        Raises:
            ValueError: Raised if any of the required parameters ('store_id', 'order_id', or 'line_id') are None.
            requests.HTTPError: Raised if the API response contains an HTTP error status.

        Tags:
            delete, ecommerce, order-management, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if order_id is None:
            raise ValueError("Missing required parameter 'order_id'")
        if line_id is None:
            raise ValueError("Missing required parameter 'line_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/orders/{order_id}/lines/{line_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_store_products(
        self, store_id, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves products from a specified ecommerce store

        Args:
            store_id: Unique identifier of the ecommerce store to fetch products from
            fields: Optional fields to include in the response
            exclude_fields: Optional fields to exclude from the response
            count: Optional number of items to retrieve
            offset: Optional offset for pagination

        Returns:
            Dictionary containing the retrieved store products and related metadata

        Raises:
            ValueError: If the required parameter 'store_id' is missing

        Tags:
            ecommerce, store-products
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_add_product_to_store(
        self,
        store_id,
        title,
        id,
        variants,
        description=None,
        handle=None,
        url=None,
        type=None,
        vendor=None,
        image_url=None,
        images=None,
        published_at_foreign=None,
    ) -> dict[str, Any]:
        """
        Adds a product to the specified e-commerce store with provided details and variants.

        Args:
            store_id: Unique identifier of the store to which the product will be added. Required.
            title: Title or name of the product. Required.
            id: Unique identifier of the product. Required.
            variants: A list or structure specifying the product's variants (e.g., sizes, colors). Required.
            description: Optional detailed description of the product.
            handle: Optional URL-friendly handle for the product.
            url: Optional external URL for the product page.
            type: Optional product type or category.
            vendor: Optional name of the product's vendor.
            image_url: Optional main image URL for the product.
            images: Optional list of additional image URLs for the product.
            published_at_foreign: Optional external published date for the product.

        Returns:
            A dictionary containing the added product's details as returned by the API.

        Raises:
            ValueError: If any of the required parameters ('store_id', 'title', 'id', or 'variants') is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            add, product, ecommerce, store-management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if title is None:
            raise ValueError("Missing required parameter 'title'")
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        if variants is None:
            raise ValueError("Missing required parameter 'variants'")
        request_body = {
            "title": title,
            "description": description,
            "id": id,
            "handle": handle,
            "url": url,
            "type": type,
            "vendor": vendor,
            "image_url": image_url,
            "variants": variants,
            "images": images,
            "published_at_foreign": published_at_foreign,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_store_product_info(
        self, store_id, product_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific product from an e-commerce store.

        Args:
            store_id: str. Unique identifier of the store whose product information is being retrieved.
            product_id: str. Unique identifier of the product to fetch details for.
            fields: Optional[list[str]]. List of fields to include in the response. If None, all fields are returned.
            exclude_fields: Optional[list[str]]. List of fields to exclude from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: A dictionary containing the product information as returned by the e-commerce API.

        Raises:
            ValueError: Raised if 'store_id' or 'product_id' is None.
            HTTPError: Raised if the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            fetch, get, ecommerce, product-info, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_update_product(
        self,
        store_id,
        product_id,
        title=None,
        description=None,
        handle=None,
        url=None,
        type=None,
        vendor=None,
        image_url=None,
        variants=None,
        images=None,
        published_at_foreign=None,
    ) -> dict[str, Any]:
        """
        Updates an existing product in an e-commerce store with the provided details.

        Args:
            store_id: str. Unique identifier of the store containing the product.
            product_id: str. Unique identifier of the product to be updated.
            title: Optional[str]. New title of the product.
            description: Optional[str]. New description of the product.
            handle: Optional[str]. New handle or slug for the product.
            url: Optional[str]. New URL for the product listing.
            type: Optional[str]. Product type or category.
            vendor: Optional[str]. Name of the product's vendor.
            image_url: Optional[str]. URL to the main image of the product.
            variants: Optional[Any]. List or structure describing product variants (e.g., size, color).
            images: Optional[Any]. List of additional image URLs or image info for the product.
            published_at_foreign: Optional[Any]. External publication timestamp or related metadata.

        Returns:
            dict[str, Any]: Dictionary containing the updated product information as returned by the API.

        Raises:
            ValueError: If 'store_id' or 'product_id' is not provided.
            requests.HTTPError: If the API request fails with a non-success HTTP status code.

        Tags:
            update, ecommerce, product-management, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        request_body = {
            "title": title,
            "description": description,
            "handle": handle,
            "url": url,
            "type": type,
            "vendor": vendor,
            "image_url": image_url,
            "variants": variants,
            "images": images,
            "published_at_foreign": published_at_foreign,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_delete_product(self, store_id, product_id) -> Any:
        """
        Deletes a product from an e-commerce store by store and product ID.

        Args:
            store_id: The unique identifier of the e-commerce store containing the product to be deleted.
            product_id: The unique identifier of the product to delete from the store.

        Returns:
            dict: The JSON response from the API after deleting the product.

        Raises:
            ValueError: Raised if either 'store_id' or 'product_id' is None.
            requests.HTTPError: Raised if the API request fails or returns an unsuccessful status code.

        Tags:
            delete, ecommerce, product-management, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_list_product_variants(
        self,
        store_id,
        product_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of variants for a specified product in a given e-commerce store, with optional filtering and pagination.

        Args:
            store_id: The unique identifier of the store containing the product.
            product_id: The unique identifier of the product for which variants are to be listed.
            fields: Comma-separated list of fields to include in the response. Optional.
            exclude_fields: Comma-separated list of fields to exclude from the response. Optional.
            count: The number of records to return in the response. Optional.
            offset: The number of records from a collection to skip. Used for pagination. Optional.

        Returns:
            A dictionary containing the list of product variants and associated metadata returned by the API.

        Raises:
            ValueError: If either 'store_id' or 'product_id' is not provided.
            requests.HTTPError: If the HTTP request to the e-commerce API fails or the response status indicates an error.

        Tags:
            list, ecommerce, product-variants, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}/variants"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_add_product_variant(
        self, store_id, product_id, request_body=None
    ) -> dict[str, Any]:
        """
        Adds a new product variant to the specified product in an ecommerce store.

        Args:
            store_id: The unique identifier of the store where the product is located.
            product_id: The unique identifier of the product to which the variant will be added.
            request_body: Optional. A dictionary containing the details of the variant to be added. Defaults to None.

        Returns:
            A dictionary containing the JSON response from the ecommerce API representing the newly created product variant.

        Raises:
            ValueError: Raised if 'store_id' or 'product_id' is not provided.
            requests.HTTPError: Raised if the API request fails with a non-successful HTTP status code.

        Tags:
            ecommerce, add, product-variant, api-call
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}/variants"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_product_variant_info(
        self, store_id, product_id, variant_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific product variant from an e-commerce store, with optional field selection.

        Args:
            store_id: str. Unique identifier for the store containing the product variant.
            product_id: str. Unique identifier for the product containing the variant.
            variant_id: str. Unique identifier for the variant whose information is to be retrieved.
            fields: Optional[list[str] or str]. Specific fields to include in the response. If None, all fields are included.
            exclude_fields: Optional[list[str] or str]. Specific fields to exclude from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: A dictionary containing the detailed information of the requested product variant.

        Raises:
            ValueError: Raised if any of 'store_id', 'product_id', or 'variant_id' is None.
            requests.exceptions.HTTPError: Raised if the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            get, ecommerce, product-variant, info, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        if variant_id is None:
            raise ValueError("Missing required parameter 'variant_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}/variants/{variant_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_add_or_update_product_variant(
        self, store_id, product_id, variant_id, request_body=None
    ) -> dict[str, Any]:
        """
        Adds a new product variant or updates an existing variant in the specified store's product catalog.

        Args:
            store_id: The unique identifier of the store containing the product.
            product_id: The unique identifier of the product to which the variant belongs.
            variant_id: The unique identifier for the product variant to add or update.
            request_body: Optional. A dictionary containing the variant details to add or update.

        Returns:
            A dictionary representing the JSON response from the API, typically containing details about the added or updated variant.

        Raises:
            ValueError: Raised if any of the required parameters ('store_id', 'product_id', or 'variant_id') is None.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an error status code.

        Tags:
            ecommerce, add, update, product-variant, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        if variant_id is None:
            raise ValueError("Missing required parameter 'variant_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}/variants/{variant_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_update_product_variant(
        self,
        store_id,
        product_id,
        variant_id,
        title=None,
        url=None,
        sku=None,
        price=None,
        inventory_quantity=None,
        image_url=None,
        backorders=None,
        visibility=None,
    ) -> dict[str, Any]:
        """
        Updates a product variant in the specified e-commerce store with provided attributes.

        Args:
            store_id: str. Unique identifier of the store containing the product.
            product_id: str. Unique identifier of the product to which the variant belongs.
            variant_id: str. Unique identifier of the variant to update.
            title: Optional[str]. New title for the product variant.
            url: Optional[str]. URL of the product variant.
            sku: Optional[str]. Stock Keeping Unit for the variant.
            price: Optional[float]. Price of the variant.
            inventory_quantity: Optional[int]. Available inventory count for the variant.
            image_url: Optional[str]. URL of the variant's image.
            backorders: Optional[bool]. Indicates if backorders are allowed for this variant.
            visibility: Optional[str]. Visibility status of the variant (e.g., 'visible', 'hidden').

        Returns:
            dict[str, Any]: The updated product variant data returned by the API.

        Raises:
            ValueError: If any of the required parameters 'store_id', 'product_id', or 'variant_id' are missing.
            requests.HTTPError: If the server returns an unsuccessful status code during the PATCH request.

        Tags:
            update, ecommerce, product-variant, api, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        if variant_id is None:
            raise ValueError("Missing required parameter 'variant_id'")
        request_body = {
            "title": title,
            "url": url,
            "sku": sku,
            "price": price,
            "inventory_quantity": inventory_quantity,
            "image_url": image_url,
            "backorders": backorders,
            "visibility": visibility,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}/variants/{variant_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_delete_product_variant(self, store_id, product_id, variant_id) -> Any:
        """
        Deletes a specific product variant from an ecommerce store by issuing a DELETE request to the API.

        Args:
            store_id: The unique identifier of the store containing the product.
            product_id: The unique identifier of the product to which the variant belongs.
            variant_id: The unique identifier of the product variant to be deleted.

        Returns:
            The parsed JSON response from the API containing the result of the deletion operation.

        Raises:
            ValueError: Raised if any of the store_id, product_id, or variant_id parameters are None.
            requests.HTTPError: Raised if the HTTP request returned an unsuccessful status code.

        Tags:
            delete, ecommerce, variant, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        if variant_id is None:
            raise ValueError("Missing required parameter 'variant_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}/variants/{variant_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_product_images(
        self,
        store_id,
        product_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
    ) -> dict[str, Any]:
        """
        Retrieves product images for a given store and product from an ecommerce API.

        Args:
            store_id: The ID of the store where the product is located.
            product_id: The ID of the product whose images are to be retrieved.
            fields: Optional list of fields to include in the response.
            exclude_fields: Optional list of fields to exclude from the response.
            count: Optional number of records to return.
            offset: Optional offset for pagination.

        Returns:
            A dictionary containing product image data.

        Raises:
            ValueError: Raised if either 'store_id' or 'product_id' is missing.

        Tags:
            retrieve, ecommerce, images, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        url = (
            f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}/images"
        )
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_add_product_image(
        self, store_id, product_id, id, url, variant_ids=None
    ) -> dict[str, Any]:
        """
        Adds an image to a product in the specified e-commerce store.

        Args:
            store_id: str. The unique identifier of the e-commerce store.
            product_id: str. The unique identifier of the product to which the image will be added.
            id: str. The unique identifier for the image.
            url: str. The URL of the image to add.
            variant_ids: Optional[list[str]]. A list of variant IDs that this image applies to. If omitted, the image is associated with the product generally.

        Returns:
            dict[str, Any]: The API response as a dictionary containing details of the newly added product image.

        Raises:
            ValueError: If any required parameter ('store_id', 'product_id', 'id', or 'url') is None.
            requests.HTTPError: If the API request fails and an HTTP error is encountered.

        Tags:
            add, product-image, ecommerce, api, management
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        if url is None:
            raise ValueError("Missing required parameter 'url'")
        request_body = {
            "id": id,
            "url": url,
            "variant_ids": variant_ids,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = (
            f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}/images"
        )
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_get_product_image_info(
        self, store_id, product_id, image_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific product image from the e-commerce store, allowing optional filtering of returned fields.

        Args:
            store_id: The unique identifier of the e-commerce store containing the product.
            product_id: The unique identifier of the product whose image information is to be retrieved.
            image_id: The unique identifier of the product image for which information is requested.
            fields: Optional; list of fields to include in the response. If None, all fields are included.
            exclude_fields: Optional; list of fields to exclude from the response.

        Returns:
            A dictionary containing details of the specified product image, with fields filtered according to 'fields' and 'exclude_fields' if provided.

        Raises:
            ValueError: Raised if any of the required parameters ('store_id', 'product_id', or 'image_id') are None.
            requests.HTTPError: Raised if the HTTP request to the e-commerce API fails (e.g., returns a non-2xx status code).

        Tags:
            get, ecommerce, product-image, detail
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        if image_id is None:
            raise ValueError("Missing required parameter 'image_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}/images/{image_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_update_product_image(
        self, store_id, product_id, image_id, id=None, url=None, variant_ids=None
    ) -> dict[str, Any]:
        """
        Updates details of a product image in an ecommerce store using the provided identifiers and optional parameters.

        Args:
            store_id: str. Unique identifier of the ecommerce store.
            product_id: str. Unique identifier of the product within the store.
            image_id: str. Unique identifier of the product image to be updated.
            id: Optional[str]. New ID for the image resource, if updating.
            url: Optional[str]. URL of the new or updated image.
            variant_ids: Optional[list[str]]. List of variant IDs associated with the image.

        Returns:
            dict[str, Any]: JSON response containing the updated product image details from the server.

        Raises:
            ValueError: If any of the required parameters 'store_id', 'product_id', or 'image_id' is None.
            requests.HTTPError: If the HTTP PATCH request to the API endpoint fails or returns an error response.

        Tags:
            update, ecommerce, product-management, image, api
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        if image_id is None:
            raise ValueError("Missing required parameter 'image_id'")
        request_body = {
            "id": id,
            "url": url,
            "variant_ids": variant_ids,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}/images/{image_id}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def ecommerce_delete_product_image(self, store_id, product_id, image_id) -> Any:
        """
        Deletes an image from a specified product in an e-commerce store.

        Args:
            store_id: The unique identifier of the e-commerce store containing the product.
            product_id: The unique identifier of the product from which the image will be deleted.
            image_id: The unique identifier of the image to delete from the product.

        Returns:
            A JSON object containing the server's response to the delete operation.

        Raises:
            ValueError: Raised if any of 'store_id', 'product_id', or 'image_id' parameters are None.
            HTTPError: Raised if the HTTP request to delete the image fails (e.g., non-2xx response status).

        Tags:
            delete, ecommerce, image-management, product
        """
        if store_id is None:
            raise ValueError("Missing required parameter 'store_id'")
        if product_id is None:
            raise ValueError("Missing required parameter 'product_id'")
        if image_id is None:
            raise ValueError("Missing required parameter 'image_id'")
        url = f"{self.base_url}/ecommerce/stores/{store_id}/products/{product_id}/images/{image_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_campaigns_by_query_terms(
        self, query, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Searches for campaigns matching the specified query terms and returns the results as a dictionary.

        Args:
            query: str. Query terms to search campaigns. Required.
            fields: Optional[list[str]]. Specific fields to include in the response. Defaults to None.
            exclude_fields: Optional[list[str]]. Specific fields to exclude from the response. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the matched campaigns and their details.

        Raises:
            ValueError: Raised if the 'query' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the campaigns API endpoint fails with a non-successful status code.

        Tags:
            search, campaigns, api, async_job
        """
        if query is None:
            raise ValueError("Missing required parameter 'query'")
        url = f"{self.base_url}/search-campaigns"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("query", query),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_members_list_members(
        self, query, fields=None, exclude_fields=None, list_id=None
    ) -> dict[str, Any]:
        """
        Searches for and retrieves a list of members matching the given query from a specific list, with optional field filtering.

        Args:
            query: The search query string used to filter members. Required.
            fields: Optional comma-separated list of fields to include in the response. Defaults to None.
            exclude_fields: Optional comma-separated list of fields to exclude from the response. Defaults to None.
            list_id: Optional unique ID of the list to filter search results. Defaults to None.

        Returns:
            A dictionary containing the search results for the matching members.

        Raises:
            ValueError: If the 'query' parameter is not provided.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status.

        Tags:
            search, list, members, api, batch
        """
        if query is None:
            raise ValueError("Missing required parameter 'query'")
        url = f"{self.base_url}/search-members"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("query", query),
                ("list_id", list_id),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def ping_health_check(
        self,
    ) -> dict[str, Any]:
        """
        Checks the health status of the service by sending a ping request and returns the server's response as JSON.

        Args:
            None: This function takes no arguments

        Returns:
            dict: JSON-decoded response from the health check endpoint, containing service status information.

        Raises:
            requests.HTTPError: If the HTTP request to the health check endpoint returns an unsuccessful status code.

        Tags:
            health-check, ping, status, api
        """
        url = f"{self.base_url}/ping"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def facebook_ads_list_ads(
        self,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        sort_field=None,
        sort_dir=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of Facebook ads with optional filtering, field selection, pagination, and sorting.

        Args:
            fields: Optional[list or str]. Specific fields to include in each ad record returned.
            exclude_fields: Optional[list or str]. Fields to exclude from each ad record in the response.
            count: Optional[int]. Number of ads to retrieve per request.
            offset: Optional[int]. Number of ads to skip before starting to collect the result set.
            sort_field: Optional[str]. Field by which to sort the ad results.
            sort_dir: Optional[str]. Sort direction ('asc' or 'desc').

        Returns:
            dict[str, Any]: A dictionary containing the list of Facebook ads and associated metadata.

        Raises:
            requests.HTTPError: If the HTTP request to the Facebook Ads endpoint fails or returns an unsuccessful status code.

        Tags:
            list, facebook-ads, management, pagination, filtering
        """
        url = f"{self.base_url}/facebook-ads"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("sort_field", sort_field),
                ("sort_dir", sort_dir),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def facebook_ads_get_info(
        self, outreach_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific Facebook Ads outreach object using its ID, with optional field selection or exclusion.

        Args:
            outreach_id: The unique identifier of the Facebook Ads outreach object to retrieve.
            fields: Optional; a list or comma-separated string specifying which fields to include in the response.
            exclude_fields: Optional; a list or comma-separated string specifying which fields to exclude from the response.

        Returns:
            A dictionary containing the requested Facebook Ads outreach information.

        Raises:
            ValueError: Raised if the 'outreach_id' parameter is None.
            HTTPError: Raised if the HTTP request to the Facebook Ads API fails or returns a non-2xx response.

        Tags:
            get, facebook-ads, info, api
        """
        if outreach_id is None:
            raise ValueError("Missing required parameter 'outreach_id'")
        url = f"{self.base_url}/facebook-ads/{outreach_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reporting_list_facebook_ads_reports(
        self,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        sort_field=None,
        sort_dir=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of Facebook Ads reports with optional filtering, pagination, and sorting.

        Args:
            fields: Optional[list[str]]. List of fields to include in the response for each report.
            exclude_fields: Optional[list[str]]. List of fields to exclude from the response.
            count: Optional[int]. Maximum number of reports to return.
            offset: Optional[int]. Number of reports to skip before starting to collect the result set.
            sort_field: Optional[str]. Field by which to sort the results.
            sort_dir: Optional[str]. Sort direction, either 'asc' or 'desc'.

        Returns:
            dict[str, Any]: Parsed JSON response containing the Facebook Ads reports.

        Raises:
            requests.HTTPError: If the HTTP request to the reporting service fails or returns an unsuccessful status code.

        Tags:
            list, reporting, facebook-ads, async_job, management
        """
        url = f"{self.base_url}/reporting/facebook-ads"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("sort_field", sort_field),
                ("sort_dir", sort_dir),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reporting_facebook_ad_report(
        self, outreach_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves detailed Facebook Ads reporting data for a specific outreach using the given outreach ID.

        Args:
            outreach_id: str. The unique identifier for the outreach whose Facebook Ads report is to be fetched. Must not be None.
            fields: Optional[list[str]]. Specific fields to include in the returned report. If None, all available fields are included.
            exclude_fields: Optional[list[str]]. Fields to exclude from the returned report. If None, no fields are excluded.

        Returns:
            dict[str, Any]: A dictionary containing the Facebook Ads report data for the specified outreach.

        Raises:
            ValueError: Raised if 'outreach_id' is None.
            requests.HTTPError: Raised if the HTTP request to the reporting endpoint fails or returns a non-success status code.

        Tags:
            report, facebook-ads, fetch, sync, api
        """
        if outreach_id is None:
            raise ValueError("Missing required parameter 'outreach_id'")
        url = f"{self.base_url}/reporting/facebook-ads/{outreach_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reporting_list_facebook_ecommerce_report(
        self,
        outreach_id,
        fields=None,
        exclude_fields=None,
        count=None,
        offset=None,
        sort_field=None,
    ) -> dict[str, Any]:
        """
        Retrieves a Facebook e-commerce product activity report for a specified outreach ID.

        Args:
            outreach_id: Required string identifier for the Facebook ad outreach campaign.
            fields: Optional string of comma-separated field names to include in the response.
            exclude_fields: Optional string of comma-separated field names to exclude from the response.
            count: Optional integer specifying the number of records to return.
            offset: Optional integer specifying the number of records to skip.
            sort_field: Optional string specifying the field to sort results by.

        Returns:
            A dictionary containing the Facebook e-commerce product activity report data.

        Raises:
            ValueError: Raised when the required outreach_id parameter is None.
            HTTPError: Raised when the API request fails.

        Tags:
            list, report, facebook, ecommerce, product-activity, reporting
        """
        if outreach_id is None:
            raise ValueError("Missing required parameter 'outreach_id'")
        url = f"{self.base_url}/reporting/facebook-ads/{outreach_id}/ecommerce-product-activity"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
                ("sort_field", sort_field),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reporting_get_landing_page_report(
        self, outreach_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves a landing page report for a specific outreach ID from the reporting API.

        Args:
            outreach_id: str. Unique identifier for the outreach whose landing page report is to be fetched. Must not be None.
            fields: Optional[list[str]]. List of specific fields to include in the report response. If None, all fields are included.
            exclude_fields: Optional[list[str]]. List of fields to exclude from the report response. If None, no fields are excluded.

        Returns:
            dict. Parsed JSON response containing the landing page report data.

        Raises:
            ValueError: If 'outreach_id' is None.
            requests.HTTPError: If the HTTP request to the reporting API fails or returns an error status.

        Tags:
            report, get, landing-page, api
        """
        if outreach_id is None:
            raise ValueError("Missing required parameter 'outreach_id'")
        url = f"{self.base_url}/reporting/landing-pages/{outreach_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reporting_list_landing_pages_reports(
        self, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of landing pages reports with optional filtering, field selection, and pagination.

        Args:
            fields: Optional[str | list[str]]. Comma-separated list or list of fields to include in the response.
            exclude_fields: Optional[str | list[str]]. Comma-separated list or list of fields to exclude from the response.
            count: Optional[int]. The number of records to return in the response.
            offset: Optional[int]. The number of records to skip for pagination.

        Returns:
            dict[str, Any]: A dictionary representing the JSON response containing landing pages reports.

        Raises:
            requests.HTTPError: If the HTTP request to the reporting API fails or returns an unsuccessful status code.

        Tags:
            list, reporting, landing-pages, sync
        """
        url = f"{self.base_url}/reporting/landing-pages"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reporting_list_survey_reports(
        self, fields=None, exclude_fields=None, count=None, offset=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of survey reports with optional filtering and pagination.

        Args:
            fields: Optional[str | list[str]]. Comma-separated field names, or list of fields, specifying which fields to include in each survey report returned.
            exclude_fields: Optional[str | list[str]]. Comma-separated field names, or list of fields, specifying fields to exclude from each survey report returned.
            count: Optional[int]. Number of survey reports to return. Limits the number of results in the response.
            offset: Optional[int]. Number of survey reports to skip before starting to return results. Useful for pagination.

        Returns:
            dict[str, Any]: A dictionary representing the response containing the list of survey reports and associated metadata.

        Raises:
            requests.HTTPError: If the HTTP request to the reporting API fails or returns a non-success status code.

        Tags:
            list, reporting, survey, api, pagination
        """
        url = f"{self.base_url}/reporting/surveys"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("count", count),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reporting_get_survey_report(
        self, survey_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves a survey report by its ID with optional field inclusions or exclusions.

        Args:
            survey_id: The ID of the survey to retrieve the report for.
            fields: Optional list of fields to include in the report.
            exclude_fields: Optional list of fields to exclude from the report.

        Returns:
            A dictionary containing the survey report.

        Raises:
            ValueError: Raised if the required 'survey_id' parameter is missing.

        Tags:
            reporting, survey, management
        """
        if survey_id is None:
            raise ValueError("Missing required parameter 'survey_id'")
        url = f"{self.base_url}/reporting/surveys/{survey_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reporting_list_survey_questions_reports(
        self, survey_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Fetches a list of survey question reports for a specified survey, with optional control over included or excluded fields.

        Args:
            survey_id: str. The unique identifier of the survey for which to retrieve question reports. Required.
            fields: Optional[str]. Comma-separated list of fields to include in the response. If None, all fields are included.
            exclude_fields: Optional[str]. Comma-separated list of fields to exclude from the response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: A dictionary containing the JSON response with the survey question reports data.

        Raises:
            ValueError: If 'survey_id' is None.
            HTTPError: If the HTTP request to the reporting API fails or returns an error status.

        Tags:
            reporting, list, survey, questions, reports, api
        """
        if survey_id is None:
            raise ValueError("Missing required parameter 'survey_id'")
        url = f"{self.base_url}/reporting/surveys/{survey_id}/questions"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reporting_survey_question_report(
        self, survey_id, question_id, fields=None, exclude_fields=None
    ) -> dict[str, Any]:
        """
        Retrieves a detailed report for a specific survey question, with optional field filtering.

        Args:
            survey_id: str. The unique identifier for the survey whose question report is requested.
            question_id: str. The unique identifier for the question within the survey.
            fields: Optional[list[str]] or str. Specific fields to include in the report response. If None, all available fields are included.
            exclude_fields: Optional[list[str]] or str. Fields to exclude from the report response. If None, no fields are excluded.

        Returns:
            dict[str, Any]: A dictionary containing the survey question report data as returned by the API.

        Raises:
            ValueError: Raised when either 'survey_id' or 'question_id' is None.
            HTTPError: Raised if the HTTP request to the API fails with an unsuccessful status code.

        Tags:
            report, survey, question, fetch, api
        """
        if survey_id is None:
            raise ValueError("Missing required parameter 'survey_id'")
        if question_id is None:
            raise ValueError("Missing required parameter 'question_id'")
        url = f"{self.base_url}/reporting/surveys/{survey_id}/questions/{question_id}"
        query_params = {
            k: v
            for k, v in [("fields", fields), ("exclude_fields", exclude_fields)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reporting_survey_question_answers_list(
        self,
        survey_id,
        question_id,
        fields=None,
        exclude_fields=None,
        respondent_familiarity_is=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of answers for a specific survey question, with optional filtering and field selection.

        Args:
            survey_id: str. The unique identifier of the survey whose question answers are to be retrieved.
            question_id: str. The unique identifier of the question within the survey.
            fields: Optional[List[str]]. A list of fields to include in the response, if specified.
            exclude_fields: Optional[List[str]]. A list of fields to exclude from the response, if specified.
            respondent_familiarity_is: Optional[str]. If specified, filters answers based on respondent familiarity.

        Returns:
            dict[str, Any]: A dictionary containing the list of answers and associated metadata for the specified survey question.

        Raises:
            ValueError: If 'survey_id' or 'question_id' is not provided.
            requests.HTTPError: If the HTTP request to the API fails or an invalid response is received.

        Tags:
            list, reporting, survey, question-answers, filter, api-call
        """
        if survey_id is None:
            raise ValueError("Missing required parameter 'survey_id'")
        if question_id is None:
            raise ValueError("Missing required parameter 'question_id'")
        url = f"{self.base_url}/reporting/surveys/{survey_id}/questions/{question_id}/answers"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("respondent_familiarity_is", respondent_familiarity_is),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reporting_survey_responses_list(
        self,
        survey_id,
        fields=None,
        exclude_fields=None,
        answered_question=None,
        chose_answer=None,
        respondent_familiarity_is=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of survey response data for a specified survey, with optional filtering and field selection.

        Args:
            survey_id: str. The unique identifier of the survey for which to list responses.
            fields: Optional[list[str]]. Specific fields to include in each response; if None, all fields are returned.
            exclude_fields: Optional[list[str]]. Fields to exclude from each response; mutually exclusive with 'fields'.
            answered_question: Optional[str]. Filters responses to only those that have answered a given question.
            chose_answer: Optional[str]. Filters responses to only those that selected a specific answer.
            respondent_familiarity_is: Optional[str]. Filters responses based on the respondent's familiarity level.

        Returns:
            dict[str, Any]: A dictionary containing the list of survey responses matching the specified filters.

        Raises:
            ValueError: If 'survey_id' is None.
            requests.HTTPError: If the HTTP request for survey responses fails (e.g., non-2xx status code).

        Tags:
            list, survey, reporting, filtering, management
        """
        if survey_id is None:
            raise ValueError("Missing required parameter 'survey_id'")
        url = f"{self.base_url}/reporting/surveys/{survey_id}/responses"
        query_params = {
            k: v
            for k, v in [
                ("fields", fields),
                ("exclude_fields", exclude_fields),
                ("answered_question", answered_question),
                ("chose_answer", chose_answer),
                ("respondent_familiarity_is", respondent_familiarity_is),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def reporting_single_survey_response(
        self, survey_id, response_id
    ) -> dict[str, Any]:
        """
        Retrieves detailed information for a single survey response based on the provided survey and response identifiers.

        Args:
            survey_id: str. The unique identifier of the survey whose response is to be retrieved.
            response_id: str. The unique identifier of the specific response to fetch.

        Returns:
            dict. A dictionary containing the JSON data of the specified survey response.

        Raises:
            ValueError: Raised if either 'survey_id' or 'response_id' is not provided.
            requests.HTTPError: Raised if the HTTP request to retrieve the survey response fails.

        Tags:
            reporting, survey, fetch, single-response, api
        """
        if survey_id is None:
            raise ValueError("Missing required parameter 'survey_id'")
        if response_id is None:
            raise ValueError("Missing required parameter 'response_id'")
        url = f"{self.base_url}/reporting/surveys/{survey_id}/responses/{response_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def verified_domains_get_info(self, domain_name) -> dict[str, Any]:
        """
        Retrieves information about a verified domain by its domain name.

        Args:
            domain_name: str. The domain name for which to retrieve verified domain information.

        Returns:
            dict[str, Any]: A dictionary containing details about the specified verified domain.

        Raises:
            ValueError: If 'domain_name' is None.
            HTTPError: If the HTTP request to retrieve the domain information fails.

        Tags:
            get, verified-domain, info, management
        """
        if domain_name is None:
            raise ValueError("Missing required parameter 'domain_name'")
        url = f"{self.base_url}/verified-domains/{domain_name}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def verified_domains_delete_domain(self, domain_name) -> Any:
        """
        Deletes a verified domain by its domain name using a DELETE request to the API endpoint.

        Args:
            domain_name: str. The name of the verified domain to delete. Must not be None.

        Returns:
            dict. The JSON-decoded response from the API after deleting the specified domain.

        Raises:
            ValueError: Raised if 'domain_name' is None.
            requests.HTTPError: Raised if the HTTP DELETE request returns an unsuccessful status code.

        Tags:
            delete, domain-management, api
        """
        if domain_name is None:
            raise ValueError("Missing required parameter 'domain_name'")
        url = f"{self.base_url}/verified-domains/{domain_name}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def verified_domains_verify_domain_for_sending(
        self, domain_name, code
    ) -> dict[str, Any]:
        """
        Verifies a specified domain for sending capabilities using a provided verification code.

        Args:
            domain_name: The domain name to verify for sending (str).
            code: The verification code to confirm domain ownership (str).

        Returns:
            A dictionary containing the server's response data after verifying the domain.

        Raises:
            ValueError: Raised if 'domain_name' or 'code' is None.
            requests.HTTPError: Raised if the HTTP response status is not successful.

        Tags:
            verify, domain, sending, api, async_job
        """
        if domain_name is None:
            raise ValueError("Missing required parameter 'domain_name'")
        if code is None:
            raise ValueError("Missing required parameter 'code'")
        request_body = {
            "code": code,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/verified-domains/{domain_name}/actions/verify"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def verified_domains_list_sending_domains(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves a list of verified sending domains associated with the account.

        Args:
            None: This function takes no arguments

        Returns:
            A dictionary containing information about the verified sending domains.

        Raises:
            requests.exceptions.HTTPError: Raised if the HTTP request to the verified domains endpoint fails with a non-2xx status code.

        Tags:
            list, sending-domains, verified-domains, api
        """
        url = f"{self.base_url}/verified-domains"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def verified_domains_add_domain_to_account(
        self, verification_email
    ) -> dict[str, Any]:
        """
        Adds a domain to the account for verification using the provided email address.

        Args:
            verification_email: str. The email address used to verify the domain. Must not be None.

        Returns:
            dict. The JSON response containing details of the added domain or verification process.

        Raises:
            ValueError: Raised if 'verification_email' is None.
            requests.HTTPError: Raised if the HTTP request to add the domain fails.

        Tags:
            verified-domains, add, account-management, post
        """
        if verification_email is None:
            raise ValueError("Missing required parameter 'verification_email'")
        request_body = {
            "verification_email": verification_email,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/verified-domains"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.root_list_resources,
            self.activity_feed_get_latest_chimp_chatter,
            self.account_exports_list_for_given_account,
            self.account_exports_create_new_export,
            self.account_export_info,
            self.authorized_apps_list_connected_applications,
            self.authorized_apps_get_info,
            self.automations_list_summary,
            self.automations_create_classic,
            self.automations_get_classic_workflow_info,
            self.automations_pause_workflow_emails,
            self.automations_start_all_emails,
            self.automations_archive_action,
            self.automations_get_classic_workflow_emails,
            self.automations_get_email_info,
            self.automations_delete_workflow_email,
            self.automations_update_workflow_email,
            self.automations_list_queue_emails,
            self.automations_add_subscriber_to_workflow_email,
            self.automations_classic_automation_subscriber_info,
            self.automations_pause_automated_email,
            self.automations_start_automated_email,
            self.automations_get_removed_subscribers,
            self.automations_remove_subscriber_from_workflow,
            self.automations_get_removed_subscriber_info,
            self.batches_list_requests_summary,
            self.batches_start_operation_process,
            self.batches_get_operation_status,
            self.batches_stop_request,
            self.batch_webhooks_list_webhooks,
            self.batch_webhooks_add_webhook,
            self.batch_webhooks_get_info,
            self.batch_webhooks_update_webhook,
            self.batch_webhooks_remove_webhook,
            self.template_folders_list_folders,
            self.template_folders_add_new_folder,
            self.template_folders_get_info,
            self.template_folders_update_specific_folder,
            self.template_folders_delete_specific_folder,
            self.campaign_folders_list_campaign_folders,
            self.campaign_folders_add_new_folder,
            self.campaign_folders_get_folder_info,
            self.campaign_folders_update_specific_folder,
            self.campaign_folders_delete_folder,
            self.campaigns_get_all,
            self.campaigns_create_new_mailchimp_campaign,
            self.campaigns_get_info,
            self.campaigns_update_settings,
            self.campaigns_remove_campaign,
            self.campaigns_cancel_send_action,
            self.campaigns_replicate_action,
            self.campaigns_send_action,
            self.campaigns_schedule_delivery,
            self.campaigns_unschedule_action,
            self.campaigns_send_test_email,
            self.campaigns_pause_rss_campaign,
            self.campaigns_resume_rss_campaign,
            self.campaigns_resend_action,
            self.campaigns_get_content,
            self.campaigns_set_content,
            self.campaigns_list_feedback,
            self.campaigns_add_feedback,
            self.campaigns_get_feedback_message,
            self.campaigns_update_feedback_message,
            self.campaigns_remove_feedback_message,
            self.campaigns_get_send_checklist,
            self.connected_sites_list_all,
            self.connected_sites_create_new_mailchimp_site,
            self.connected_sites_get_info,
            self.connected_sites_remove_site,
            self.connected_sites_verify_script_installation,
            self.conversations_get_all_conversations,
            self.conversations_get_by_id,
            self.conversations_list_messages_from_conversation,
            self.conversations_get_message_by_id,
            self.customer_journeys_trigger_step_action,
            self.file_manager_upload_file,
            self.file_manager_get_file,
            self.file_manager_update_file,
            self.file_manager_remove_file_by_id,
            self.file_manager_get_folder_list,
            self.file_manager_add_new_folder,
            self.file_manager_get_folder_info,
            self.file_manager_update_specific_folder,
            self.file_manager_delete_folder_by_id,
            self.lists_get_all_info,
            self.lists_create_new_list,
            self.lists_get_list_info,
            self.lists_update_settings,
            self.lists_delete_list,
            self.lists_batch_subscribe_or_unsubscribe,
            self.lists_get_all_abuse_reports,
            self.lists_get_abuse_report,
            self.lists_get_recent_activity_stats,
            self.lists_list_top_email_clients,
            self.lists_get_growth_history_data,
            self.lists_get_growth_history_by_month,
            self.lists_list_interest_categories,
            self.lists_add_interest_category,
            self.lists_get_interest_category_info,
            self.lists_update_interest_category,
            self.lists_delete_interest_category,
            self.lists_list_category_interests,
            self.lists_add_interest_in_category,
            self.lists_get_interest_in_category,
            self.lists_update_interest_category_interest,
            self.lists_delete_interest_in_category,
            self.lists_get_segments_info,
            self.lists_add_new_segment,
            self.lists_get_segment_info,
            self.lists_delete_segment,
            self.lists_update_segment_by_id,
            self.lists_batch_add_remove_members,
            self.lists_get_segment_members,
            self.lists_add_member_to_segment,
            self.lists_remove_member_from_segment,
            self.lists_search_tags_by_name,
            self.lists_get_members_info,
            self.lists_add_member_to_list,
            self.lists_get_member_info,
            self.lists_add_or_update_member,
            self.lists_update_member,
            self.lists_archive_member,
            self.lists_view_recent_activity_events,
            self.lists_view_recent_activity,
            self.lists_get_member_tags,
            self.lists_add_member_tags,
            self.lists_get_member_events,
            self.lists_add_member_event,
            self.lists_get_member_goals,
            self.lists_get_member_notes,
            self.lists_add_member_note,
            self.lists_get_member_note,
            self.lists_update_note_specific_list_member,
            self.lists_delete_note,
            self.lists_remove_member_permanent,
            self.lists_list_merge_fields,
            self.lists_add_merge_field,
            self.lists_get_merge_field_info,
            self.lists_update_merge_field,
            self.lists_delete_merge_field,
            self.lists_get_webhooks_info,
            self.lists_create_webhook,
            self.lists_get_webhook_info,
            self.lists_delete_webhook,
            self.lists_update_webhook_settings,
            self.lists_get_signup_forms,
            self.lists_customize_signup_form,
            self.lists_get_locations,
            self.lists_get_surveys_info,
            self.lists_get_survey_details,
            self.surveys_publish_survey_action,
            self.surveys_unpublish_survey_action,
            self.surveys_generate_campaign,
            self.landing_pages_list,
            self.landing_pages_create_new_mailchimp_landing_page,
            self.landing_pages_get_page_info,
            self.landing_pages_update_page_by_id,
            self.landing_pages_delete_page,
            self.landing_pages_publish_action,
            self.landing_pages_unpublish_action,
            self.landing_pages_get_content,
            self.reports_list_campaign_reports,
            self.reports_specific_campaign_report,
            self.reports_list_abuse_reports,
            self.reports_get_abuse_report,
            self.reports_list_campaign_feedback,
            self.reports_get_campaign_click_details,
            self.reports_specific_link_details,
            self.reports_list_clicked_link_subscribers,
            self.reports_specific_link_subscriber,
            self.reports_list_campaign_open_details,
            self.reports_open_subscriber_details,
            self.reports_list_domain_performance_stats,
            self.reports_list_eepurl_activity,
            self.reports_list_email_activity,
            self.reports_get_subscriber_activity,
            self.reports_list_top_open_locations,
            self.reports_list_campaign_recipients,
            self.reports_campaign_recipient_info,
            self.reports_list_child_campaign_reports,
            self.reports_list_unsubscribed_members,
            self.reports_get_unsubscribed_member_info,
            self.reports_get_campaign_product_activity,
            self.templates_list_available_templates,
            self.templates_create_new_template,
            self.templates_get_info,
            self.templates_update_template_by_id,
            self.templates_delete_specific_template,
            self.templates_view_default_content,
            self.ecommerce_list_account_orders,
            self.ecommerce_list_stores,
            self.ecommerce_add_store_to_mailchimp_account,
            self.ecommerce_get_store_info,
            self.ecommerce_update_store,
            self.ecommerce_delete_store,
            self.ecommerce_get_store_carts,
            self.ecommerce_add_cart_to_store,
            self.ecommerce_get_cart_info,
            self.ecommerce_update_cart_by_id,
            self.ecommerce_remove_cart,
            self.ecommerce_list_cart_lines,
            self.ecommerce_add_cart_line_item,
            self.ecommerce_get_cart_line_item,
            self.ecommerce_update_cart_line_item,
            self.ecommerce_delete_cart_line_item,
            self.ecommerce_get_store_customers,
            self.ecommerce_add_customer_to_store,
            self.ecommerce_get_customer_info,
            self.ecommerce_add_or_update_customer,
            self.ecommerce_update_customer,
            self.ecommerce_remove_customer,
            self.ecommerce_get_store_promo_rules,
            self.ecommerce_add_promo_rule,
            self.ecommerce_get_store_promo_rule,
            self.ecommerce_update_promo_rule,
            self.ecommerce_delete_promo_rule,
            self.ecommerce_get_store_promo_codes,
            self.ecommerce_add_promo_code,
            self.ecommerce_get_promo_code,
            self.ecommerce_update_promo_code,
            self.ecommerce_delete_promo_code,
            self.ecommerce_list_store_orders,
            self.ecommerce_add_order_to_store,
            self.ecommerce_get_store_order_info,
            self.ecommerce_update_specific_order,
            self.ecommerce_delete_order,
            self.ecommerce_get_store_order_lines,
            self.ecommerce_add_order_line_item,
            self.ecommerce_get_order_line_item,
            self.ecommerce_update_order_line,
            self.ecommerce_delete_order_line,
            self.ecommerce_get_store_products,
            self.ecommerce_add_product_to_store,
            self.ecommerce_get_store_product_info,
            self.ecommerce_update_product,
            self.ecommerce_delete_product,
            self.ecommerce_list_product_variants,
            self.ecommerce_add_product_variant,
            self.ecommerce_get_product_variant_info,
            self.ecommerce_add_or_update_product_variant,
            self.ecommerce_update_product_variant,
            self.ecommerce_delete_product_variant,
            self.ecommerce_get_product_images,
            self.ecommerce_add_product_image,
            self.ecommerce_get_product_image_info,
            self.ecommerce_update_product_image,
            self.ecommerce_delete_product_image,
            self.search_campaigns_by_query_terms,
            self.search_members_list_members,
            self.ping_health_check,
            self.facebook_ads_list_ads,
            self.facebook_ads_get_info,
            self.reporting_list_facebook_ads_reports,
            self.reporting_facebook_ad_report,
            self.reporting_list_facebook_ecommerce_report,
            self.reporting_get_landing_page_report,
            self.reporting_list_landing_pages_reports,
            self.reporting_list_survey_reports,
            self.reporting_get_survey_report,
            self.reporting_list_survey_questions_reports,
            self.reporting_survey_question_report,
            self.reporting_survey_question_answers_list,
            self.reporting_survey_responses_list,
            self.reporting_single_survey_response,
            self.verified_domains_get_info,
            self.verified_domains_delete_domain,
            self.verified_domains_verify_domain_for_sending,
            self.verified_domains_list_sending_domains,
            self.verified_domains_add_domain_to_account,
        ]
