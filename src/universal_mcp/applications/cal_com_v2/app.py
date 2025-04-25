from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class CalComV2App(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="cal-com-v2", integration=integration, **kwargs)
        self.base_url = "https://api.cal.com"

    def cal_provider_controller_verify_client_id(self, clientId) -> dict[str, Any]:
        """
        Verifies the validity of the provided client ID by sending a GET request to the provider verification endpoint.

        Args:
            clientId: str. The unique identifier of the client to verify.

        Returns:
            dict[str, Any]: A dictionary containing the provider data associated with the specified client ID as returned by the API.

        Raises:
            ValueError: Raised if 'clientId' is None.
            requests.HTTPError: Raised if the HTTP request to the provider verification endpoint fails with an error status.

        Tags:
            verify, provider, api, sync
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        url = f"{self.base_url}/v2/provider/{clientId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def cal_provider_controller_verify_access_token(self, clientId) -> dict[str, Any]:
        """
        Verifies the validity of a provider's access token for the specified client ID by making an authenticated request to the provider API.

        Args:
            clientId: str. The unique identifier of the client whose access token should be verified.

        Returns:
            dict[str, Any]: The JSON response containing the verification result and related access token details from the provider API.

        Raises:
            ValueError: Raised if 'clientId' is None.
            requests.exceptions.HTTPError: Raised if the HTTP request to the provider API fails with an error status.

        Tags:
            verify, access-token, controller, provider, api
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        url = f"{self.base_url}/v2/provider/{clientId}/access-token"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def gcal_controller_redirect(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves the Google Calendar OAuth authorization URL by making a GET request to the API and returns the response as a dictionary.

        Returns:
            dict[str, Any]: Dictionary containing the OAuth authorization URL and related response data from the API.

        Raises:
            HTTPError: If the API response contains an HTTP error status code, an HTTPError is raised by response.raise_for_status().

        Tags:
            gcal, oauth, redirect, get, api, controller
        """
        url = f"{self.base_url}/v2/gcal/oauth/auth-url"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def gcal_controller_save(self, state, code) -> dict[str, Any]:
        """
        Saves Google Calendar OAuth credentials by exchanging the provided state and code via an authenticated API request.

        Args:
            state: The OAuth state parameter returned from the authorization flow (str).
            code: The authorization code received from Google after user consent (str).

        Returns:
            A dictionary containing the response data from the Google Calendar OAuth save endpoint.

        Raises:
            ValueError: If either 'state' or 'code' is None.
            requests.HTTPError: If the API request returns an unsuccessful status code.

        Tags:
            gcal, oauth, save, controller, api-call
        """
        if state is None:
            raise ValueError("Missing required parameter 'state'")
        if code is None:
            raise ValueError("Missing required parameter 'code'")
        url = f"{self.base_url}/v2/gcal/oauth/save"
        query_params = {
            k: v for k, v in [("state", state), ("code", code)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def gcal_controller_check(
        self,
    ) -> dict[str, Any]:
        """
        Checks the connection status of Google Calendar integration via the API.

        Returns:
            A dictionary containing the status and details of the Google Calendar integration as returned by the API.

        Raises:
            HTTPError: If the HTTP request to the Google Calendar check endpoint returns an unsuccessful status code.

        Tags:
            check, status, gcal, integration
        """
        url = f"{self.base_url}/v2/gcal/check"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def oauth_client_users_controller_get_managed_users(
        self, clientId, limit=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of managed users for a specified OAuth client.

        Args:
            clientId: The unique identifier of the OAuth client whose managed users are to be retrieved.
            limit: Optional maximum number of users to return. If None, the default server-side limit is used.

        Returns:
            A dictionary containing the list of managed users and associated metadata returned by the API.

        Raises:
            ValueError: If the required parameter 'clientId' is not provided.
            requests.HTTPError: If the HTTP request to the API fails or returns a non-success status code.

        Tags:
            list, users, management, api
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        url = f"{self.base_url}/v2/oauth-clients/{clientId}/users"
        query_params = {k: v for k, v in [("limit", limit)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def oauth_client_users_controller_create_user(
        self,
        clientId,
        email,
        name,
        timeFormat=None,
        weekStart=None,
        timeZone=None,
        locale=None,
        avatarUrl=None,
    ) -> dict[str, Any]:
        """
        Creates a new user for a specified OAuth client by sending user details to the OAuth service.

        Args:
            clientId: str. The ID of the OAuth client for which the user is to be created. Required.
            email: str. The email address of the user to be created. Required.
            name: str. The name of the user to be created. Required.
            timeFormat: Optional[str]. The preferred time format for the user, if any.
            weekStart: Optional[str]. The day the user's week starts on, if specified.
            timeZone: Optional[str]. The user's preferred time zone, if specified.
            locale: Optional[str]. The locale setting for the user, if specified.
            avatarUrl: Optional[str]. URL for the user's avatar image, if specified.

        Returns:
            dict[str, Any]: A dictionary containing the details of the created user as returned by the OAuth service.

        Raises:
            ValueError: If any of the required parameters (clientId, email, or name) are missing.
            requests.HTTPError: If the HTTP request to create the user fails (e.g., due to client or server error).

        Tags:
            create, user-management, oauth, api-call
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        if email is None:
            raise ValueError("Missing required parameter 'email'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "email": email,
            "name": name,
            "timeFormat": timeFormat,
            "weekStart": weekStart,
            "timeZone": timeZone,
            "locale": locale,
            "avatarUrl": avatarUrl,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/oauth-clients/{clientId}/users"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def oauth_client_users_controller_get_user_by_id(
        self, clientId, userId
    ) -> dict[str, Any]:
        """
        Retrieves user information for a specific OAuth client and user ID.

        Args:
            clientId: The unique identifier of the OAuth client. Must not be None.
            userId: The unique identifier of the user. Must not be None.

        Returns:
            A dictionary containing user information retrieved from the OAuth client's user endpoint.

        Raises:
            ValueError: Raised if either 'clientId' or 'userId' is None.
            requests.HTTPError: Raised if the HTTP request to the API endpoint fails with an error status.

        Tags:
            get, user, oauth-client, api
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        url = f"{self.base_url}/v2/oauth-clients/{clientId}/users/{userId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def oauth_client_users_controller_update_user(
        self,
        clientId,
        userId,
        email=None,
        name=None,
        timeFormat=None,
        defaultScheduleId=None,
        weekStart=None,
        timeZone=None,
        locale=None,
        avatarUrl=None,
    ) -> dict[str, Any]:
        """
        Updates a user's details for a specific OAuth client by sending a PATCH request with provided user information.

        Args:
            clientId: str. The unique identifier of the OAuth client. Required.
            userId: str. The unique identifier of the user to be updated. Required.
            email: str, optional. The new email address of the user.
            name: str, optional. The new name of the user.
            timeFormat: str, optional. The preferred time format for the user (e.g., '12h' or '24h').
            defaultScheduleId: str, optional. The default schedule identifier for the user.
            weekStart: str or int, optional. The preferred starting day of the week for the user, e.g., 'Monday' or 1.
            timeZone: str, optional. The time zone for the user.
            locale: str, optional. The locale/language preference for the user.
            avatarUrl: str, optional. The URL of the user's avatar image.

        Returns:
            dict. The updated user information as returned by the API.

        Raises:
            ValueError: If 'clientId' or 'userId' is None.
            requests.HTTPError: If the PATCH request to the API fails or returns an unsuccessful status code.

        Tags:
            update, user-management, oauth-client, api, patch
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        request_body = {
            "email": email,
            "name": name,
            "timeFormat": timeFormat,
            "defaultScheduleId": defaultScheduleId,
            "weekStart": weekStart,
            "timeZone": timeZone,
            "locale": locale,
            "avatarUrl": avatarUrl,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/oauth-clients/{clientId}/users/{userId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def oauth_client_users_controller_delete_user(
        self, clientId, userId
    ) -> dict[str, Any]:
        """
        Deletes a specific user associated with an OAuth client by client and user ID.

        Args:
            clientId: str. The unique identifier of the OAuth client whose user is to be deleted.
            userId: str. The unique identifier of the user to be deleted from the OAuth client.

        Returns:
            dict. The server's response as a dictionary after deleting the user.

        Raises:
            ValueError: Raised if clientId or userId is None.
            requests.HTTPError: Raised if the HTTP request fails or returns an error status.

        Tags:
            delete, oauth-client, user-management, api
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        url = f"{self.base_url}/v2/oauth-clients/{clientId}/users/{userId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def oauth_client_users_controller_force_refresh(
        self, clientId, userId
    ) -> dict[str, Any]:
        """
        Forces a token refresh for a specific OAuth client user by issuing a POST request to the relevant API endpoint.

        Args:
            clientId: str. The unique identifier of the OAuth client whose user token needs to be refreshed.
            userId: str. The unique identifier of the user associated with the OAuth client.

        Returns:
            dict[str, Any]: The JSON response from the API containing the result of the force refresh operation.

        Raises:
            ValueError: Raised if either 'clientId' or 'userId' is None.
            requests.HTTPError: Raised if the API response contains an HTTP error status.

        Tags:
            force-refresh, oauth-client, user-management, api
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        url = (
            f"{self.base_url}/v2/oauth-clients/{clientId}/users/{userId}/force-refresh"
        )
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def oauth_flow_controller_refresh_tokens(
        self, clientId, refreshToken
    ) -> dict[str, Any]:
        """
        Requests a new access token using the provided client ID and refresh token through the OAuth flow.

        Args:
            clientId: str. The unique client identifier for the OAuth application.
            refreshToken: str. The refresh token used to obtain a new access token.

        Returns:
            dict[str, Any]: The JSON response containing the new access token and related metadata.

        Raises:
            ValueError: Raised if either 'clientId' or 'refreshToken' is None.
            requests.HTTPError: Raised if the HTTP request to refresh the token fails (non-2xx response).

        Tags:
            oauth, refresh, token-management, api
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        if refreshToken is None:
            raise ValueError("Missing required parameter 'refreshToken'")
        request_body = {
            "refreshToken": refreshToken,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/oauth/{clientId}/refresh"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def oauth_client_webhooks_controller_create_oauth_client_webhook(
        self,
        clientId,
        active,
        subscriberUrl,
        triggers,
        payloadTemplate=None,
        secret=None,
    ) -> dict[str, Any]:
        """
        Creates a new webhook for an OAuth client with the specified configuration parameters.

        Args:
            clientId: str. The unique identifier of the OAuth client for which the webhook is created.
            active: bool. Specifies whether the webhook should be active upon creation.
            subscriberUrl: str. The URL to which webhook notifications will be sent.
            triggers: list. A list of event triggers that determine when the webhook will be invoked.
            payloadTemplate: Optional[str]. An optional template for customizing the webhook payload.
            secret: Optional[str]. An optional secret used to sign webhook payloads for verification.

        Returns:
            dict[str, Any]: A dictionary containing the details of the created webhook, as returned by the server.

        Raises:
            ValueError: If any of the required parameters ('clientId', 'active', 'subscriberUrl', 'triggers') is missing or None.
            requests.HTTPError: If the HTTP request to create the webhook fails or returns an error response.

        Tags:
            create, webhook, oauth-client, api, management
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        if active is None:
            raise ValueError("Missing required parameter 'active'")
        if subscriberUrl is None:
            raise ValueError("Missing required parameter 'subscriberUrl'")
        if triggers is None:
            raise ValueError("Missing required parameter 'triggers'")
        request_body = {
            "payloadTemplate": payloadTemplate,
            "active": active,
            "subscriberUrl": subscriberUrl,
            "triggers": triggers,
            "secret": secret,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/oauth-clients/{clientId}/webhooks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def oauth_client_webhooks_controller_get_oauth_client_webhooks(
        self, clientId, take=None, skip=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of webhook configurations associated with a specified OAuth client.

        Args:
            clientId: str. The unique identifier of the OAuth client whose webhooks are to be fetched.
            take: Optional[int]. The maximum number of webhook records to return. Used for pagination.
            skip: Optional[int]. The number of webhook records to skip before returning results. Used for pagination.

        Returns:
            dict[str, Any]: A dictionary containing the webhook configurations for the specified OAuth client.

        Raises:
            ValueError: Raised if the required parameter 'clientId' is not provided.
            requests.HTTPError: Raised if the HTTP request to the web service fails or returns an error status code.

        Tags:
            list, webhook-management, oauth-client, fetch
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        url = f"{self.base_url}/v2/oauth-clients/{clientId}/webhooks"
        query_params = {
            k: v for k, v in [("take", take), ("skip", skip)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def oauth_client_webhooks_controller_delete_all_oauth_client_webhooks(
        self, clientId
    ) -> dict[str, Any]:
        """
        Deletes all OAuth client webhooks for the specified client ID.

        Args:
            clientId: str. The unique identifier of the OAuth client whose webhooks are to be deleted.

        Returns:
            dict[str, Any]: A dictionary containing the server response data after deleting the webhooks.

        Raises:
            ValueError: Raised if the required parameter 'clientId' is None.
            requests.HTTPError: Raised if the HTTP request to delete the webhooks fails with an unsuccessful status code.

        Tags:
            delete, webhooks, oauth-client, management
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        url = f"{self.base_url}/v2/oauth-clients/{clientId}/webhooks"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def oauth_client_webhooks_controller_update_oauth_client_webhook(
        self,
        clientId,
        webhookId,
        payloadTemplate=None,
        active=None,
        subscriberUrl=None,
        triggers=None,
        secret=None,
    ) -> dict[str, Any]:
        """
        Updates an existing OAuth client webhook with new configuration parameters.

        Args:
            clientId: str. The unique identifier of the OAuth client whose webhook is being updated. Required.
            webhookId: str. The unique identifier of the webhook to update. Required.
            payloadTemplate: Optional[str]. The template for the webhook payload, if updating.
            active: Optional[bool]. Whether the webhook should be active. Pass True to activate, False to deactivate.
            subscriberUrl: Optional[str]. The URL that will receive webhook events.
            triggers: Optional[list[str]]. A list of trigger event types for which the webhook should fire.
            secret: Optional[str]. Shared secret used to sign webhook payloads for verification.

        Returns:
            dict[str, Any]: A dictionary containing the updated webhook configuration as returned by the API.

        Raises:
            ValueError: If either 'clientId' or 'webhookId' is not provided.
            requests.HTTPError: If the HTTP request to update the webhook fails (e.g., network or API error).

        Tags:
            update, webhook, oauth-client, management
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        if webhookId is None:
            raise ValueError("Missing required parameter 'webhookId'")
        request_body = {
            "payloadTemplate": payloadTemplate,
            "active": active,
            "subscriberUrl": subscriberUrl,
            "triggers": triggers,
            "secret": secret,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/oauth-clients/{clientId}/webhooks/{webhookId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def oauth_client_webhooks_controller_get_oauth_client_webhook(
        self, clientId, webhookId
    ) -> dict[str, Any]:
        """
        Retrieves the details of a specific OAuth client webhook by client and webhook ID.

        Args:
            clientId: str. The unique identifier of the OAuth client whose webhook is to be retrieved.
            webhookId: str. The unique identifier of the webhook associated with the specified OAuth client.

        Returns:
            dict[str, Any]: A dictionary containing the details of the requested OAuth client webhook as returned by the API.

        Raises:
            ValueError: Raised if either 'clientId' or 'webhookId' is None.
            requests.HTTPError: Raised if the HTTP request to fetch the webhook details fails (non-2xx response).

        Tags:
            get, webhook, oauth-client, retrieve, api
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        if webhookId is None:
            raise ValueError("Missing required parameter 'webhookId'")
        url = f"{self.base_url}/v2/oauth-clients/{clientId}/webhooks/{webhookId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def oauth_client_webhooks_controller_delete_oauth_client_webhook(
        self, clientId, webhookId
    ) -> dict[str, Any]:
        """
        Deletes a specific webhook associated with an OAuth client.

        Args:
            clientId: str. Unique identifier of the OAuth client whose webhook will be deleted.
            webhookId: str. Unique identifier of the webhook to delete.

        Returns:
            dict. The response from the server, parsed as a JSON-compatible dictionary.

        Raises:
            ValueError: Raised if either 'clientId' or 'webhookId' is not provided.
            requests.HTTPError: Raised if the server returns an unsuccessful HTTP response status.

        Tags:
            delete, webhook, oauth-client, async_job, management
        """
        if clientId is None:
            raise ValueError("Missing required parameter 'clientId'")
        if webhookId is None:
            raise ValueError("Missing required parameter 'webhookId'")
        url = f"{self.base_url}/v2/oauth-clients/{clientId}/webhooks/{webhookId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_attributes_controller_get_organization_attributes(
        self, orgId, take=None, skip=None
    ) -> dict[str, Any]:
        """
        Retrieves the attributes of a specified organization using its organization ID, with optional pagination parameters.

        Args:
            orgId: str. The unique identifier of the organization whose attributes are to be retrieved.
            take: Optional[int]. The maximum number of attributes to return. Defaults to None.
            skip: Optional[int]. The number of attributes to skip before starting to collect the result set. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the organization's attributes as returned by the API.

        Raises:
            ValueError: If 'orgId' is None.
            HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            get, organization, attributes, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/attributes"
        query_params = {
            k: v for k, v in [("take", take), ("skip", skip)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_attributes_controller_create_organization_attribute(
        self, orgId, name, slug, type, options, enabled=None
    ) -> dict[str, Any]:
        """
        Creates a new organization attribute by sending a POST request with the specified parameters to the organization's attributes endpoint.

        Args:
            orgId: str. Unique identifier of the organization. Required.
            name: str. Name of the attribute to create. Required.
            slug: str. URL-friendly, unique identifier for the attribute. Required.
            type: str. Data type of the attribute (e.g., 'string', 'number'). Required.
            options: Any. Allowed options or configuration for the attribute. Required.
            enabled: bool or None. Specifies whether the attribute is enabled. Optional; defaults to None.

        Returns:
            dict. JSON response from the API containing details of the created organization attribute.

        Raises:
            ValueError: If any of the required parameters ('orgId', 'name', 'slug', 'type', or 'options') is None.
            requests.HTTPError: If the HTTP request to the API endpoint fails or returns an error status code.

        Tags:
            create, attribute-management, organization, api, http
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if slug is None:
            raise ValueError("Missing required parameter 'slug'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        if options is None:
            raise ValueError("Missing required parameter 'options'")
        request_body = {
            "name": name,
            "slug": slug,
            "type": type,
            "options": options,
            "enabled": enabled,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/attributes"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_attributes_controller_get_organization_attribute(
        self, orgId, attributeId
    ) -> dict[str, Any]:
        """
        Retrieves a specific attribute for an organization by organization and attribute IDs.

        Args:
            orgId: The unique identifier of the organization whose attribute is to be retrieved.
            attributeId: The unique identifier of the attribute to fetch for the specified organization.

        Returns:
            A dictionary containing the organization's attribute details as returned by the API.

        Raises:
            ValueError: Raised if 'orgId' or 'attributeId' is not provided.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an error response.

        Tags:
            get, organization, attribute, management
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if attributeId is None:
            raise ValueError("Missing required parameter 'attributeId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/attributes/{attributeId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_attributes_controller_update_organization_attribute(
        self, orgId, attributeId, name=None, slug=None, type=None, enabled=None
    ) -> dict[str, Any]:
        """
        Updates a specific attribute of an organization using the provided parameters.

        Args:
            orgId: str. The unique identifier of the organization whose attribute is to be updated.
            attributeId: str. The unique identifier of the attribute to update within the organization.
            name: str, optional. The new name for the attribute. If None, the name will not be changed.
            slug: str, optional. The new slug for the attribute. If None, the slug will not be changed.
            type: str, optional. The new type for the attribute. If None, the type will not be changed.
            enabled: bool, optional. The enabled status for the attribute. If None, the enabled status will not be changed.

        Returns:
            dict[str, Any]: The updated organization attribute as returned by the API.

        Raises:
            ValueError: Raised if 'orgId' or 'attributeId' is None.
            requests.HTTPError: Raised if the API request fails with an unsuccessful HTTP status code.

        Tags:
            update, organization-attribute, management, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if attributeId is None:
            raise ValueError("Missing required parameter 'attributeId'")
        request_body = {
            "name": name,
            "slug": slug,
            "type": type,
            "enabled": enabled,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/attributes/{attributeId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_attributes_controller_delete_organization_attribute(
        self, orgId, attributeId
    ) -> dict[str, Any]:
        """
        Deletes an attribute from a specific organization by its organization ID and attribute ID.

        Args:
            orgId: str. Unique identifier of the organization whose attribute is to be deleted.
            attributeId: str. Unique identifier of the attribute to delete.

        Returns:
            dict[str, Any]: The JSON response from the API after deleting the attribute.

        Raises:
            ValueError: Raised if either 'orgId' or 'attributeId' is None.
            requests.HTTPError: Raised if the HTTP request to delete the attribute fails (non-success status code).

        Tags:
            delete, organization, attribute-management, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if attributeId is None:
            raise ValueError("Missing required parameter 'attributeId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/attributes/{attributeId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_options_attributes_controller_create_organization_attribute_option(
        self, orgId, attributeId, value, slug
    ) -> dict[str, Any]:
        """
        Creates a new attribute option for a specific organization attribute.

        Args:
            orgId: str. The unique identifier of the organization.
            attributeId: str. The unique identifier of the attribute to which the option will be added.
            value: str. The display value for the attribute option to be created.
            slug: str. The slug (unique, URL-friendly identifier) for the attribute option.

        Returns:
            dict[str, Any]: A dictionary containing the created attribute option's details as returned by the API.

        Raises:
            ValueError: Raised if any of 'orgId', 'attributeId', 'value', or 'slug' is None.
            requests.HTTPError: Raised if the API request fails or returns an error response.

        Tags:
            create, attribute-option, organization, controller, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if attributeId is None:
            raise ValueError("Missing required parameter 'attributeId'")
        if value is None:
            raise ValueError("Missing required parameter 'value'")
        if slug is None:
            raise ValueError("Missing required parameter 'slug'")
        request_body = {
            "value": value,
            "slug": slug,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = (
            f"{self.base_url}/v2/organizations/{orgId}/attributes/{attributeId}/options"
        )
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_options_attributes_controller_get_organization_attribute_options(
        self, orgId, attributeId
    ) -> dict[str, Any]:
        """
        Retrieves the available options for a specific organization attribute by organization and attribute IDs.

        Args:
            orgId: The unique identifier of the organization whose attribute options are to be retrieved.
            attributeId: The unique identifier of the attribute for which options are to be listed.

        Returns:
            A dictionary representing the JSON response containing the list of attribute options for the specified organization and attribute.

        Raises:
            ValueError: Raised if either 'orgId' or 'attributeId' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails with a non-successful status code.

        Tags:
            get, list, organization, attributes, options, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if attributeId is None:
            raise ValueError("Missing required parameter 'attributeId'")
        url = (
            f"{self.base_url}/v2/organizations/{orgId}/attributes/{attributeId}/options"
        )
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_options_attributes_controller_delete_organization_attribute_option(
        self, orgId, attributeId, optionId
    ) -> dict[str, Any]:
        """
        Deletes a specific attribute option from an organization's attributes via the API.

        Args:
            orgId: str. The unique identifier of the organization.
            attributeId: str. The unique identifier of the attribute within the organization.
            optionId: str. The unique identifier of the attribute option to be deleted.

        Returns:
            dict[str, Any]: The JSON response from the API after successfully deleting the attribute option.

        Raises:
            ValueError: Raised if any of the required parameters ('orgId', 'attributeId', or 'optionId') are None.
            requests.HTTPError: Raised if the API request fails with an HTTP error status.

        Tags:
            delete, attribute-option, organization, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if attributeId is None:
            raise ValueError("Missing required parameter 'attributeId'")
        if optionId is None:
            raise ValueError("Missing required parameter 'optionId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/attributes/{attributeId}/options/{optionId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_options_attributes_controller_update_organization_attribute_option(
        self, orgId, attributeId, optionId, value=None, slug=None
    ) -> dict[str, Any]:
        """
        Updates an existing organization attribute option with new values for 'value' and/or 'slug'.

        Args:
            orgId: str. Unique identifier for the organization. Required.
            attributeId: str. Unique identifier for the attribute within the organization. Required.
            optionId: str. Unique identifier for the attribute option to update. Required.
            value: Optional[str]. New value for the attribute option. If None, the value is not updated.
            slug: Optional[str]. New slug for the attribute option. If None, the slug is not updated.

        Returns:
            dict[str, Any]: The updated organization attribute option as returned by the API.

        Raises:
            ValueError: If 'orgId', 'attributeId', or 'optionId' is None.
            requests.HTTPError: If the HTTP PATCH request fails or the server returns an error.

        Tags:
            update, attribute-option, organization, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if attributeId is None:
            raise ValueError("Missing required parameter 'attributeId'")
        if optionId is None:
            raise ValueError("Missing required parameter 'optionId'")
        request_body = {
            "value": value,
            "slug": slug,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/attributes/{attributeId}/options/{optionId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_options_attributes_controller_assign_organization_attribute_option_to_user(
        self, orgId, userId, attributeId, value=None, attributeOptionId=None
    ) -> dict[str, Any]:
        """
        Assigns a specific organization attribute option to a user within the given organization.

        Args:
            orgId: str. The unique identifier of the organization.
            userId: str. The unique identifier of the user to whom the attribute option is being assigned.
            attributeId: str. The unique identifier of the attribute being assigned.
            value: Optional[Any]. The value to assign to the attribute, if applicable. Defaults to None.
            attributeOptionId: Optional[Any]. The ID of the attribute option to assign, if applicable. Defaults to None.

        Returns:
            dict[str, Any]: The JSON response from the API confirming assignment of the attribute option to the user.

        Raises:
            ValueError: Raised if any of the required parameters ('orgId', 'userId', or 'attributeId') are missing.
            requests.HTTPError: Raised if the HTTP request to the API fails (non-successful status code).

        Tags:
            assign, organization-attributes, controller, user-management, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        if attributeId is None:
            raise ValueError("Missing required parameter 'attributeId'")
        request_body = {
            "value": value,
            "attributeOptionId": attributeOptionId,
            "attributeId": attributeId,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/attributes/options/{userId}"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_options_attributes_controller_get_organization_attribute_options_for_user(
        self, orgId, userId
    ) -> dict[str, Any]:
        """
        Retrieves available attribute options for a user within a specified organization.

        Args:
            orgId: The unique identifier of the organization whose attribute options are to be retrieved.
            userId: The unique identifier of the user for whom the organization attribute options are being requested.

        Returns:
            A dictionary containing the attribute options available to the specified user within the given organization.

        Raises:
            ValueError: Raised if 'orgId' or 'userId' is None.
            requests.HTTPError: Raised if the HTTP request to the attribute options endpoint fails.

        Tags:
            get, organization, attributes, user, sync, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/attributes/options/{userId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_options_attributes_controller_unassign_organization_attribute_option_from_user(
        self, orgId, userId, attributeOptionId
    ) -> dict[str, Any]:
        """
        Unassigns a specific organization attribute option from a user within the given organization.

        Args:
            orgId: str. The unique identifier of the organization.
            userId: str. The unique identifier of the user from whom the attribute option will be unassigned.
            attributeOptionId: str. The unique identifier of the attribute option to be removed from the user.

        Returns:
            dict[str, Any]: A dictionary containing the server's response data following the unassignment action.

        Raises:
            ValueError: Raised if any of the required parameters ('orgId', 'userId', or 'attributeOptionId') are missing or None.
            requests.HTTPError: Raised if the server returns an unsuccessful HTTP response status.

        Tags:
            unassign, organization-management, attribute-option, user-management, delete
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        if attributeOptionId is None:
            raise ValueError("Missing required parameter 'attributeOptionId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/attributes/options/{userId}/{attributeOptionId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_event_types_controller_create_team_event_type(
        self,
        orgId,
        teamId,
        lengthInMinutes,
        lengthInMinutesOptions,
        title,
        slug,
        schedulingType,
        hosts,
        description=None,
        locations=None,
        bookingFields=None,
        disableGuests=None,
        slotInterval=None,
        minimumBookingNotice=None,
        beforeEventBuffer=None,
        afterEventBuffer=None,
        scheduleId=None,
        bookingLimitsCount=None,
        onlyShowFirstAvailableSlot=None,
        bookingLimitsDuration=None,
        bookingWindow=None,
        offsetStart=None,
        bookerLayouts=None,
        confirmationPolicy=None,
        recurrence=None,
        requiresBookerEmailVerification=None,
        hideCalendarNotes=None,
        lockTimeZoneToggleOnBookingPage=None,
        color=None,
        seats=None,
        customName=None,
        destinationCalendar=None,
        useDestinationCalendarEmail=None,
        hideCalendarEventDetails=None,
        successRedirectUrl=None,
        assignAllTeamMembers=None,
    ) -> dict[str, Any]:
        """
        Creates a new event type for a specified team within an organization.

        Args:
            orgId: str. The unique identifier of the organization.
            teamId: str. The unique identifier of the team.
            lengthInMinutes: int. Duration of the event type in minutes.
            lengthInMinutesOptions: list. Available duration options for the event type in minutes.
            title: str. Title of the event type.
            slug: str. URL-friendly string identifier for the event type.
            schedulingType: str. Type of scheduling used for the event (e.g., collective, round-robin).
            hosts: list. List of user IDs or host information for the event.
            description: Optional[str]. Description of the event type.
            locations: Optional[list]. Possible locations where the event can take place.
            bookingFields: Optional[list]. Additional fields the booker must fill out.
            disableGuests: Optional[bool]. If True, guests are not allowed.
            slotInterval: Optional[int]. Interval in minutes between available booking slots.
            minimumBookingNotice: Optional[int]. Minimum notice in minutes required before booking.
            beforeEventBuffer: Optional[int]. Buffer time in minutes before the event starts.
            afterEventBuffer: Optional[int]. Buffer time in minutes after the event ends.
            scheduleId: Optional[str]. Identifier for a specific schedule to associate with the event.
            bookingLimitsCount: Optional[int]. Maximum number of bookings allowed within the limit window.
            onlyShowFirstAvailableSlot: Optional[bool]. If True, only the first available slot is shown.
            bookingLimitsDuration: Optional[int]. Duration in minutes for which booking limits apply.
            bookingWindow: Optional[int]. Number of days ahead for which bookings can be made.
            offsetStart: Optional[int]. Offset in minutes from the start of the working day for the first slot.
            bookerLayouts: Optional[list]. Custom layouts shown to the booker.
            confirmationPolicy: Optional[dict]. Rules or settings for confirming bookings.
            recurrence: Optional[dict]. Recurrence rules for the event type.
            requiresBookerEmailVerification: Optional[bool]. If True, booker's email must be verified.
            hideCalendarNotes: Optional[bool]. If True, calendar notes are hidden from the booker.
            lockTimeZoneToggleOnBookingPage: Optional[bool]. If True, disables time zone switching for bookers.
            color: Optional[str]. Color code or identifier for the event type.
            seats: Optional[int]. Number of available seats per event.
            customName: Optional[str]. Custom display name for the event type.
            destinationCalendar: Optional[str]. Calendar to which booked events are added.
            useDestinationCalendarEmail: Optional[bool]. If True, uses destination calendar email for event notifications.
            hideCalendarEventDetails: Optional[bool]. If True, hides event details in the calendar entry.
            successRedirectUrl: Optional[str]. URL to redirect users after successful booking.
            assignAllTeamMembers: Optional[bool]. If True, assigns all team members as hosts for the event.

        Returns:
            dict[str, Any]: Details of the newly created team event type as returned by the API.

        Raises:
            ValueError: If any required parameter (orgId, teamId, lengthInMinutes, lengthInMinutesOptions, title, slug, schedulingType, hosts) is missing or None.
            HTTPError: If the API request fails or returns a non-success status code.

        Tags:
            create, event-type, team, organization, management, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if lengthInMinutes is None:
            raise ValueError("Missing required parameter 'lengthInMinutes'")
        if lengthInMinutesOptions is None:
            raise ValueError("Missing required parameter 'lengthInMinutesOptions'")
        if title is None:
            raise ValueError("Missing required parameter 'title'")
        if slug is None:
            raise ValueError("Missing required parameter 'slug'")
        if schedulingType is None:
            raise ValueError("Missing required parameter 'schedulingType'")
        if hosts is None:
            raise ValueError("Missing required parameter 'hosts'")
        request_body = {
            "lengthInMinutes": lengthInMinutes,
            "lengthInMinutesOptions": lengthInMinutesOptions,
            "title": title,
            "slug": slug,
            "description": description,
            "locations": locations,
            "bookingFields": bookingFields,
            "disableGuests": disableGuests,
            "slotInterval": slotInterval,
            "minimumBookingNotice": minimumBookingNotice,
            "beforeEventBuffer": beforeEventBuffer,
            "afterEventBuffer": afterEventBuffer,
            "scheduleId": scheduleId,
            "bookingLimitsCount": bookingLimitsCount,
            "onlyShowFirstAvailableSlot": onlyShowFirstAvailableSlot,
            "bookingLimitsDuration": bookingLimitsDuration,
            "bookingWindow": bookingWindow,
            "offsetStart": offsetStart,
            "bookerLayouts": bookerLayouts,
            "confirmationPolicy": confirmationPolicy,
            "recurrence": recurrence,
            "requiresBookerEmailVerification": requiresBookerEmailVerification,
            "hideCalendarNotes": hideCalendarNotes,
            "lockTimeZoneToggleOnBookingPage": lockTimeZoneToggleOnBookingPage,
            "color": color,
            "seats": seats,
            "customName": customName,
            "destinationCalendar": destinationCalendar,
            "useDestinationCalendarEmail": useDestinationCalendarEmail,
            "hideCalendarEventDetails": hideCalendarEventDetails,
            "successRedirectUrl": successRedirectUrl,
            "schedulingType": schedulingType,
            "hosts": hosts,
            "assignAllTeamMembers": assignAllTeamMembers,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/{teamId}/event-types"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_event_types_controller_get_team_event_types(
        self, orgId, teamId, eventSlug=None
    ) -> dict[str, Any]:
        """
        Retrieves the event types available for a specific team within an organization.

        Args:
            orgId: str. The unique identifier of the organization. Required.
            teamId: str. The unique identifier of the team within the organization. Required.
            eventSlug: str or None. Optional slug to filter event types by a specific event. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the team event types as returned by the API.

        Raises:
            ValueError: If 'orgId' or 'teamId' is not provided.
            requests.HTTPError: If the API request to retrieve event types fails with an HTTP error response.

        Tags:
            get, event-types, team, organization, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/{teamId}/event-types"
        query_params = {k: v for k, v in [("eventSlug", eventSlug)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_event_types_controller_get_team_event_type(
        self, orgId, teamId, eventTypeId
    ) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific event type within a team for a given organization.

        Args:
            orgId: The unique identifier of the organization.
            teamId: The unique identifier of the team within the organization.
            eventTypeId: The unique identifier of the event type to retrieve.

        Returns:
            A dictionary containing the event type details as returned by the API.

        Raises:
            ValueError: If any of 'orgId', 'teamId', or 'eventTypeId' is None.
            requests.HTTPError: If the HTTP request to the backend API fails with a non-success response.

        Tags:
            get, event-type, team, organization, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/{teamId}/event-types/{eventTypeId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_event_types_controller_create_phone_call(
        self,
        orgId,
        teamId,
        eventTypeId,
        yourPhoneNumber,
        numberToCall,
        calApiKey,
        enabled,
        templateType,
        schedulerName=None,
        guestName=None,
        guestEmail=None,
        guestCompany=None,
        beginMessage=None,
        generalPrompt=None,
    ) -> dict[str, Any]:
        """
        Creates a phone call event type for a specific organization, team, and event type using provided phone and template details.

        Args:
            orgId: The unique identifier of the organization.
            teamId: The unique identifier of the team within the organization.
            eventTypeId: The unique identifier of the event type to attach the phone call event to.
            yourPhoneNumber: The phone number initiating the call.
            numberToCall: The recipient's phone number.
            calApiKey: API key used to authorize the calendar integration for the call event.
            enabled: Boolean indicating whether the phone call event is enabled.
            templateType: The type of template to use for the phone call event.
            schedulerName: Optional; the name of the scheduler initiating the call.
            guestName: Optional; the name of the guest being called.
            guestEmail: Optional; the email address of the guest being called.
            guestCompany: Optional; the company name of the guest being called.
            beginMessage: Optional; message to be played or sent at the start of the call.
            generalPrompt: Optional; a general prompt message for the call.

        Returns:
            A dictionary containing the details and status of the created phone call event type as returned by the backend API.

        Raises:
            ValueError: Raised if any of the required parameters (orgId, teamId, eventTypeId, yourPhoneNumber, numberToCall, calApiKey, enabled, or templateType) are missing or None.
            requests.HTTPError: Raised if the API request fails or returns an unsuccessful status code.

        Tags:
            create, event-type, phone-call, management, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        if yourPhoneNumber is None:
            raise ValueError("Missing required parameter 'yourPhoneNumber'")
        if numberToCall is None:
            raise ValueError("Missing required parameter 'numberToCall'")
        if calApiKey is None:
            raise ValueError("Missing required parameter 'calApiKey'")
        if enabled is None:
            raise ValueError("Missing required parameter 'enabled'")
        if templateType is None:
            raise ValueError("Missing required parameter 'templateType'")
        request_body = {
            "yourPhoneNumber": yourPhoneNumber,
            "numberToCall": numberToCall,
            "calApiKey": calApiKey,
            "enabled": enabled,
            "templateType": templateType,
            "schedulerName": schedulerName,
            "guestName": guestName,
            "guestEmail": guestEmail,
            "guestCompany": guestCompany,
            "beginMessage": beginMessage,
            "generalPrompt": generalPrompt,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/{teamId}/event-types/{eventTypeId}/create-phone-call"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_event_types_controller_get_teams_event_types(
        self, orgId, take=None, skip=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of event types associated with all teams in a specified organization.

        Args:
            orgId: str. The unique identifier of the organization whose teams' event types are to be fetched.
            take: Optional[int]. The maximum number of event types to return. Used for pagination. Defaults to None.
            skip: Optional[int]. The number of event types to skip before starting to collect the result set. Used for pagination. Defaults to None.

        Returns:
            dict[str, Any]: The JSON-parsed response containing event type information for all teams within the specified organization.

        Raises:
            ValueError: If 'orgId' is not provided.
            requests.HTTPError: If the HTTP request to the API endpoint fails.

        Tags:
            get, event-types, teams, organization, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/event-types"
        query_params = {
            k: v for k, v in [("take", take), ("skip", skip)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_memberships_controller_get_all_memberships(
        self, orgId, take=None, skip=None
    ) -> dict[str, Any]:
        """
        Retrieves all membership records for a specified organization, with optional pagination.

        Args:
            orgId: str. The unique identifier of the organization for which to retrieve memberships.
            take: Optional[int]. The maximum number of membership records to return. Used for pagination.
            skip: Optional[int]. The number of membership records to skip before starting to collect the result set. Used for pagination.

        Returns:
            dict[str, Any]: A dictionary containing the membership records and related metadata returned by the API.

        Raises:
            ValueError: Raised if 'orgId' is not provided.
            requests.HTTPError: Raised if the HTTP request to the memberships API endpoint fails.

        Tags:
            list, memberships, organization, api, management
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/memberships"
        query_params = {
            k: v for k, v in [("take", take), ("skip", skip)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_memberships_controller_create_membership(
        self, orgId, userId, role, accepted=None, disableImpersonation=None
    ) -> dict[str, Any]:
        """
        Creates a new organization membership by sending a POST request with the specified user ID, role, and optional parameters.

        Args:
            orgId: str. The unique identifier of the organization in which to create the membership. Required.
            userId: str. The unique identifier of the user to be added as a member. Required.
            role: str. The role to assign to the user within the organization. Required.
            accepted: bool or None. Indicates whether the membership is pre-accepted. Optional.
            disableImpersonation: bool or None. If True, prevents impersonation for this membership. Optional.

        Returns:
            dict[str, Any]: The JSON response containing details of the newly created membership.

        Raises:
            ValueError: Raised if 'orgId', 'userId', or 'role' is not provided.
            requests.HTTPError: Raised if the HTTP request to create the membership fails.

        Tags:
            create, membership, organization, post, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        if role is None:
            raise ValueError("Missing required parameter 'role'")
        request_body = {
            "userId": userId,
            "accepted": accepted,
            "role": role,
            "disableImpersonation": disableImpersonation,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/memberships"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_memberships_controller_get_org_membership(
        self, orgId, membershipId
    ) -> dict[str, Any]:
        """
        Retrieves the details of a specific organization membership by organization and membership IDs.

        Args:
            orgId: str. The unique identifier of the organization.
            membershipId: str. The unique identifier of the membership within the organization.

        Returns:
            dict[str, Any]: A dictionary containing the membership details as returned by the API.

        Raises:
            ValueError: Raised if either 'orgId' or 'membershipId' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns a non-success status code.

        Tags:
            get, membership, organizations, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if membershipId is None:
            raise ValueError("Missing required parameter 'membershipId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/memberships/{membershipId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_memberships_controller_delete_membership(
        self, orgId, membershipId
    ) -> dict[str, Any]:
        """
        Deletes a membership from an organization using the specified organization and membership IDs.

        Args:
            orgId: str. The unique identifier of the organization.
            membershipId: str. The unique identifier of the membership to be deleted.

        Returns:
            dict[str, Any]: The JSON response from the API after deleting the membership.

        Raises:
            ValueError: Raised if 'orgId' or 'membershipId' is None.
            requests.HTTPError: Raised if the HTTP request for deleting the membership fails.

        Tags:
            delete, membership, organizations, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if membershipId is None:
            raise ValueError("Missing required parameter 'membershipId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/memberships/{membershipId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_memberships_controller_update_membership(
        self, orgId, membershipId, accepted=None, role=None, disableImpersonation=None
    ) -> dict[str, Any]:
        """
        Updates an organization's membership with specified fields such as acceptance status, role, or impersonation settings.

        Args:
            orgId: str. Unique identifier of the organization whose membership is being updated. Required.
            membershipId: str. Unique identifier of the membership to update. Required.
            accepted: Optional[bool]. Indicates whether the membership invitation is accepted or not.
            role: Optional[str]. The new role to assign to the membership.
            disableImpersonation: Optional[bool]. If True, disables impersonation for this membership.

        Returns:
            dict[str, Any]: The JSON response from the API containing the updated membership details.

        Raises:
            ValueError: Raised if 'orgId' or 'membershipId' is not provided.
            requests.exceptions.HTTPError: Raised if the API response contains an HTTP error status.

        Tags:
            update, membership, organization, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if membershipId is None:
            raise ValueError("Missing required parameter 'membershipId'")
        request_body = {
            "accepted": accepted,
            "role": role,
            "disableImpersonation": disableImpersonation,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/memberships/{membershipId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_schedules_controller_get_organization_schedules(
        self, orgId, take=None, skip=None
    ) -> dict[str, Any]:
        """
        Retrieves a paginated list of schedules for the specified organization.

        Args:
            orgId: str. The unique identifier of the organization whose schedules are to be retrieved.
            take: Optional[int]. The maximum number of schedule items to return. If None, a default server limit is used.
            skip: Optional[int]. The number of schedule items to skip before starting to collect the result set. Useful for pagination.

        Returns:
            dict[str, Any]: A dictionary containing the organization's schedules and related pagination metadata.

        Raises:
            ValueError: Raised if 'orgId' is None.
            requests.HTTPError: Raised if the HTTP request fails or the server responds with an error status.

        Tags:
            get, list, schedules, organization, pagination, management
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/schedules"
        query_params = {
            k: v for k, v in [("take", take), ("skip", skip)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_schedules_controller_create_user_schedule(
        self,
        orgId,
        userId,
        name,
        timeZone,
        isDefault,
        availability=None,
        overrides=None,
    ) -> dict[str, Any]:
        """
        Creates a new user schedule for a specified user within an organization.

        Args:
            orgId: str. The ID of the organization to which the user belongs.
            userId: str. The ID of the user for whom the schedule is being created.
            name: str. The name of the schedule.
            timeZone: str. The time zone for the schedule (e.g., 'America/New_York').
            isDefault: bool. Indicates whether this schedule is the user's default schedule.
            availability: Optional[list[dict]]. A list describing the user's general availability blocks. Defaults to None.
            overrides: Optional[list[dict]]. A list of schedule override entries for exceptions or special rules. Defaults to None.

        Returns:
            dict[str, Any]: The newly created schedule as a dictionary parsed from the API response.

        Raises:
            ValueError: If any required parameter ('orgId', 'userId', 'name', 'timeZone', or 'isDefault') is missing or None.
            requests.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            create, schedule-management, user, organization, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if timeZone is None:
            raise ValueError("Missing required parameter 'timeZone'")
        if isDefault is None:
            raise ValueError("Missing required parameter 'isDefault'")
        request_body = {
            "name": name,
            "timeZone": timeZone,
            "availability": availability,
            "isDefault": isDefault,
            "overrides": overrides,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/users/{userId}/schedules"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_schedules_controller_get_user_schedules(
        self, orgId, userId
    ) -> dict[str, Any]:
        """
        Retrieves the schedule data for a specific user within an organization.

        Args:
            orgId: The unique identifier of the organization.
            userId: The unique identifier of the user whose schedules are to be fetched.

        Returns:
            A dictionary containing the user's schedules from the organization's scheduling API.

        Raises:
            ValueError: Raised if either 'orgId' or 'userId' is None.
            requests.HTTPError: Raised if the HTTP request to the schedules API returns an unsuccessful status code.

        Tags:
            get, schedules, user, organization, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/users/{userId}/schedules"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_schedules_controller_get_user_schedule(
        self, orgId, userId, scheduleId
    ) -> dict[str, Any]:
        """
        Retrieves a specific user's schedule from an organization by schedule ID.

        Args:
            orgId: str. The unique identifier of the organization.
            userId: str. The unique identifier of the user within the organization.
            scheduleId: str. The unique identifier of the schedule to retrieve.

        Returns:
            dict[str, Any]: The JSON response containing details of the user's schedule.

        Raises:
            ValueError: If any of the required parameters ('orgId', 'userId', or 'scheduleId') is None.
            requests.HTTPError: If the HTTP request to the schedule service fails (non-2xx response).

        Tags:
            get, schedules, user-management, organization
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        if scheduleId is None:
            raise ValueError("Missing required parameter 'scheduleId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/users/{userId}/schedules/{scheduleId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_schedules_controller_update_user_schedule(
        self,
        orgId,
        userId,
        scheduleId,
        name=None,
        timeZone=None,
        availability=None,
        isDefault=None,
        overrides=None,
    ) -> dict[str, Any]:
        """
        Updates a user's schedule within an organization with the provided details.

        Args:
            orgId: The unique identifier of the organization.
            userId: The unique identifier of the user whose schedule is being updated.
            scheduleId: The unique identifier of the schedule to update.
            name: Optional. The name to assign to the schedule.
            timeZone: Optional. The time zone associated with the schedule.
            availability: Optional. The user's availability information for the schedule.
            isDefault: Optional. Whether this schedule should be set as the default for the user.
            overrides: Optional. Any specific overrides to apply to the schedule.

        Returns:
            A dictionary representing the updated schedule data as returned by the API.

        Raises:
            ValueError: If any of 'orgId', 'userId', or 'scheduleId' is None.
            requests.HTTPError: If the HTTP PATCH request fails or returns an error response.

        Tags:
            update, schedule-management, user, organization, async_job
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        if scheduleId is None:
            raise ValueError("Missing required parameter 'scheduleId'")
        request_body = {
            "name": name,
            "timeZone": timeZone,
            "availability": availability,
            "isDefault": isDefault,
            "overrides": overrides,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/users/{userId}/schedules/{scheduleId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_schedules_controller_delete_user_schedule(
        self, orgId, userId, scheduleId
    ) -> dict[str, Any]:
        """
        Deletes a specific user schedule from an organization by schedule ID.

        Args:
            orgId: str. Unique identifier of the organization.
            userId: str. Unique identifier of the user whose schedule is to be deleted.
            scheduleId: str. Unique identifier of the schedule to delete.

        Returns:
            dict[str, Any]: The server's JSON response confirming deletion or providing additional details.

        Raises:
            ValueError: Raised if 'orgId', 'userId', or 'scheduleId' is None.
            requests.HTTPError: Raised if the HTTP request to delete the schedule fails with a client or server error.

        Tags:
            delete, schedule-management, user-management, organization
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        if scheduleId is None:
            raise ValueError("Missing required parameter 'scheduleId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/users/{userId}/schedules/{scheduleId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_teams_controller_get_all_teams(
        self, orgId, take=None, skip=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of teams for a specified organization, with optional pagination.

        Args:
            orgId: str. The unique identifier of the organization for which to fetch teams.
            take: Optional[int]. The maximum number of teams to return. If None, the server default is used.
            skip: Optional[int]. The number of teams to skip before starting to collect the result set. If None, no teams are skipped.

        Returns:
            dict[str, Any]: A dictionary containing the list of teams and related metadata as returned by the API.

        Raises:
            ValueError: If 'orgId' is None.
            HTTPError: If the API request results in an HTTP error status code.

        Tags:
            list, teams, organization, async_job, management
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/teams"
        query_params = {
            k: v for k, v in [("take", take), ("skip", skip)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_teams_controller_create_team(
        self,
        orgId,
        name,
        slug=None,
        logoUrl=None,
        calVideoLogo=None,
        appLogo=None,
        appIconLogo=None,
        bio=None,
        hideBranding=None,
        isPrivate=None,
        hideBookATeamMember=None,
        metadata=None,
        theme=None,
        brandColor=None,
        darkBrandColor=None,
        bannerUrl=None,
        timeFormat=None,
        timeZone=None,
        weekStart=None,
        autoAcceptCreator=None,
    ) -> dict[str, Any]:
        """
        Creates a new team within the specified organization with customizable details and branding options.

        Args:
            orgId: str. Unique identifier of the organization in which to create the team. Required.
            name: str. Name of the team to create. Required.
            slug: str, optional. Custom slug or URL segment for the team.
            logoUrl: str, optional. URL to the team's logo image.
            calVideoLogo: str, optional. URL to the team's calendar video logo.
            appLogo: str, optional. URL to the team's application logo.
            appIconLogo: str, optional. URL to the team's application icon logo.
            bio: str, optional. Short biography or description for the team.
            hideBranding: bool, optional. If True, hides team branding in external views.
            isPrivate: bool, optional. If True, sets the team as private.
            hideBookATeamMember: bool, optional. Determines whether 'Book a Team Member' feature is hidden.
            metadata: dict, optional. Additional structured metadata for the team.
            theme: str, optional. Name of the visual theme to apply to the team.
            brandColor: str, optional. Primary brand color in hex format.
            darkBrandColor: str, optional. Dark mode brand color in hex format.
            bannerUrl: str, optional. URL to the team's banner image.
            timeFormat: str, optional. Preferred time display format for the team.
            timeZone: str, optional. Time zone identifier for the team.
            weekStart: str, optional. Specifies which day the team's calendar week should start on.
            autoAcceptCreator: bool, optional. If True, automatically accepts the team creator.

        Returns:
            dict. JSON response containing details of the newly created team.

        Raises:
            ValueError: Raised when a required parameter ('orgId' or 'name') is missing.
            requests.HTTPError: Raised if the HTTP request to create the team fails (e.g., due to invalid input or server error).

        Tags:
            create, teams, organization, management, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "name": name,
            "slug": slug,
            "logoUrl": logoUrl,
            "calVideoLogo": calVideoLogo,
            "appLogo": appLogo,
            "appIconLogo": appIconLogo,
            "bio": bio,
            "hideBranding": hideBranding,
            "isPrivate": isPrivate,
            "hideBookATeamMember": hideBookATeamMember,
            "metadata": metadata,
            "theme": theme,
            "brandColor": brandColor,
            "darkBrandColor": darkBrandColor,
            "bannerUrl": bannerUrl,
            "timeFormat": timeFormat,
            "timeZone": timeZone,
            "weekStart": weekStart,
            "autoAcceptCreator": autoAcceptCreator,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/teams"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_teams_controller_get_my_teams(
        self, orgId, take=None, skip=None
    ) -> dict[str, Any]:
        """
        Retrieves the list of teams for the current user within a specified organization.

        Args:
            orgId: str. The unique identifier of the organization. Must not be None.
            take: Optional[int]. The maximum number of teams to return. Used for pagination.
            skip: Optional[int]. The number of teams to skip before starting to collect the result set. Used for pagination.

        Returns:
            dict[str, Any]: A dictionary containing the user's teams in the specified organization as returned by the API.

        Raises:
            ValueError: If 'orgId' is None.
            requests.HTTPError: If the HTTP request fails or returns a non-success status code.

        Tags:
            list, teams, organization, management, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/me"
        query_params = {
            k: v for k, v in [("take", take), ("skip", skip)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_teams_controller_get_team(self, orgId, teamId) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific team within an organization by team and organization ID.

        Args:
            orgId: The unique identifier of the organization containing the team. Must not be None.
            teamId: The unique identifier of the team to retrieve. Must not be None.

        Returns:
            A dictionary containing the team's details as returned from the API endpoint.

        Raises:
            ValueError: Raised if either 'orgId' or 'teamId' is None.
            requests.HTTPError: Raised if the HTTP request to the API endpoint fails.

        Tags:
            get, team, organizations, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/{teamId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_teams_controller_delete_team(
        self, orgId, teamId
    ) -> dict[str, Any]:
        """
        Deletes a specific team from an organization by its organization and team IDs.

        Args:
            orgId: str. The unique identifier of the organization containing the team to delete.
            teamId: str. The unique identifier of the team to be deleted.

        Returns:
            dict[str, Any]: The JSON response from the API after the team is deleted.

        Raises:
            ValueError: Raised when 'orgId' or 'teamId' is None.
            requests.HTTPError: Raised if the HTTP request to delete the team fails.

        Tags:
            delete, team-management, organizations, api-call
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/{teamId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_teams_controller_update_team(
        self,
        orgId,
        teamId,
        name=None,
        slug=None,
        logoUrl=None,
        calVideoLogo=None,
        appLogo=None,
        appIconLogo=None,
        bio=None,
        hideBranding=None,
        isPrivate=None,
        hideBookATeamMember=None,
        metadata=None,
        theme=None,
        brandColor=None,
        darkBrandColor=None,
        bannerUrl=None,
        timeFormat=None,
        timeZone=None,
        weekStart=None,
        bookingLimits=None,
        includeManagedEventsInLimits=None,
    ) -> dict[str, Any]:
        """
        Updates the details of an existing team in an organization with the specified parameters.

        Args:
            orgId: str. The unique identifier of the organization. Required.
            teamId: str. The unique identifier of the team to update. Required.
            name: str, optional. The name of the team.
            slug: str, optional. A unique URL-friendly identifier for the team.
            logoUrl: str, optional. URL for the team's logo.
            calVideoLogo: str, optional. URL for the team's Calendly video logo.
            appLogo: str, optional. URL for the team's app logo.
            appIconLogo: str, optional. URL for the team's app icon logo.
            bio: str, optional. A brief biography or description of the team.
            hideBranding: bool, optional. Whether to hide the team's branding.
            isPrivate: bool, optional. Whether the team is private.
            hideBookATeamMember: bool, optional. Whether to hide the option to book a team member.
            metadata: dict or None, optional. Additional metadata for the team.
            theme: str, optional. UI theme identifier for the team.
            brandColor: str, optional. Brand color in HEX or CSS format.
            darkBrandColor: str, optional. Brand color used for dark themes.
            bannerUrl: str, optional. URL for the team's banner image.
            timeFormat: str, optional. Preferred time format for the team.
            timeZone: str, optional. Time zone associated with the team.
            weekStart: str or int, optional. First day of the week for the team's schedule.
            bookingLimits: dict or None, optional. Booking limits settings for the team.
            includeManagedEventsInLimits: bool, optional. Whether to include managed events in booking limits.

        Returns:
            dict[str, Any]: The updated team data as returned by the API.

        Raises:
            ValueError: If 'orgId' or 'teamId' is None.
            requests.HTTPError: If the API request fails due to an HTTP error.

        Tags:
            update, team-management, organization, api, patch
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        request_body = {
            "name": name,
            "slug": slug,
            "logoUrl": logoUrl,
            "calVideoLogo": calVideoLogo,
            "appLogo": appLogo,
            "appIconLogo": appIconLogo,
            "bio": bio,
            "hideBranding": hideBranding,
            "isPrivate": isPrivate,
            "hideBookATeamMember": hideBookATeamMember,
            "metadata": metadata,
            "theme": theme,
            "brandColor": brandColor,
            "darkBrandColor": darkBrandColor,
            "bannerUrl": bannerUrl,
            "timeFormat": timeFormat,
            "timeZone": timeZone,
            "weekStart": weekStart,
            "bookingLimits": bookingLimits,
            "includeManagedEventsInLimits": includeManagedEventsInLimits,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/{teamId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_teams_memberships_controller_get_all_org_team_memberships(
        self, orgId, teamId, take=None, skip=None
    ) -> dict[str, Any]:
        """
        Retrieves all memberships for a specific team within an organization, with optional pagination.

        Args:
            orgId: The unique identifier of the organization.
            teamId: The unique identifier of the team within the organization.
            take: Optional; the maximum number of memberships to return.
            skip: Optional; the number of memberships to skip before starting to collect the result set.

        Returns:
            A dictionary containing the list of team membership records and associated metadata.

        Raises:
            ValueError: Raised if 'orgId' or 'teamId' is not provided.
            requests.HTTPError: Raised if the HTTP request to the API fails with an error status.

        Tags:
            list, memberships, organization, team, api, fetch
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/{teamId}/memberships"
        query_params = {
            k: v for k, v in [("take", take), ("skip", skip)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_teams_memberships_controller_create_org_team_membership(
        self, orgId, teamId, userId, role, accepted=None, disableImpersonation=None
    ) -> dict[str, Any]:
        """
        Creates a team membership for a user within an organization, assigning a specified role and optional attributes.

        Args:
            orgId: str. The unique identifier of the organization.
            teamId: str. The unique identifier of the team within the organization.
            userId: str. The unique identifier of the user to add as a team member.
            role: str. The role to assign to the user within the team.
            accepted: Optional[bool]. Indicates whether the user has accepted the team membership. Defaults to None.
            disableImpersonation: Optional[bool]. Whether to disable impersonation for this membership. Defaults to None.

        Returns:
            dict[str, Any]: The JSON-decoded response representing the created team membership.

        Raises:
            ValueError: If any of orgId, teamId, userId, or role is None.
            requests.HTTPError: If the HTTP request to create the membership fails.

        Tags:
            create, membership, organization, team, management, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        if role is None:
            raise ValueError("Missing required parameter 'role'")
        request_body = {
            "userId": userId,
            "accepted": accepted,
            "role": role,
            "disableImpersonation": disableImpersonation,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/{teamId}/memberships"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_teams_memberships_controller_get_org_team_membership(
        self, orgId, teamId, membershipId
    ) -> dict[str, Any]:
        """
        Retrieve details of a specific team membership within an organization.

        Args:
            orgId: str. Unique identifier of the organization.
            teamId: str. Unique identifier of the team within the organization.
            membershipId: str. Unique identifier of the membership to retrieve.

        Returns:
            dict. A dictionary containing the details of the team membership.

        Raises:
            ValueError: Raised if any of the required parameters ('orgId', 'teamId', or 'membershipId') are None.
            HTTPError: Raised if the HTTP request to the API endpoint returns an unsuccessful status code.

        Tags:
            get, membership, organization, team, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if membershipId is None:
            raise ValueError("Missing required parameter 'membershipId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/{teamId}/memberships/{membershipId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_teams_memberships_controller_delete_org_team_membership(
        self, orgId, teamId, membershipId
    ) -> dict[str, Any]:
        """
        Deletes a specific team membership from an organization by its identifiers.

        Args:
            orgId: The unique identifier of the organization containing the team.
            teamId: The unique identifier of the team from which the membership will be deleted.
            membershipId: The unique identifier of the membership to be deleted.

        Returns:
            A dictionary containing the response data from the delete operation.

        Raises:
            ValueError: Raised if any of 'orgId', 'teamId', or 'membershipId' is None.
            requests.HTTPError: Raised if the HTTP request to delete the membership fails (non-success status code).

        Tags:
            delete, membership, organizations, teams, api-call
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if membershipId is None:
            raise ValueError("Missing required parameter 'membershipId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/{teamId}/memberships/{membershipId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_teams_memberships_controller_update_org_team_membership(
        self,
        orgId,
        teamId,
        membershipId,
        accepted=None,
        role=None,
        disableImpersonation=None,
    ) -> dict[str, Any]:
        """
        Updates a specific team membership within an organization, modifying attributes such as acceptance status, role, and impersonation settings.

        Args:
            orgId: str. Unique identifier of the organization.
            teamId: str. Unique identifier of the team within the organization.
            membershipId: str. Unique identifier of the membership to update.
            accepted: Optional[bool]. If provided, sets whether the membership is accepted.
            role: Optional[str]. If provided, updates the role of the member within the team.
            disableImpersonation: Optional[bool]. If provided, enables or disables impersonation for the membership.

        Returns:
            dict[str, Any]: The updated membership information as returned by the API.

        Raises:
            ValueError: Raised if any of the required parameters 'orgId', 'teamId', or 'membershipId' are missing.
            requests.HTTPError: Raised if the HTTP PATCH request to the server fails or returns an error response.

        Tags:
            update, membership, team, organization, api, management
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if membershipId is None:
            raise ValueError("Missing required parameter 'membershipId'")
        request_body = {
            "accepted": accepted,
            "role": role,
            "disableImpersonation": disableImpersonation,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/{teamId}/memberships/{membershipId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_teams_schedules_controller_get_user_schedules(
        self, orgId, teamId, userId
    ) -> dict[str, Any]:
        """
        Retrieves the schedule information for a specific user within a team and organization.

        Args:
            orgId: The unique identifier of the organization.
            teamId: The unique identifier of the team within the organization.
            userId: The unique identifier of the user whose schedules are to be retrieved.

        Returns:
            A dictionary containing the schedule details for the specified user.

        Raises:
            ValueError: Raised if any of the required parameters ('orgId', 'teamId', or 'userId') are None.
            requests.HTTPError: Raised if the HTTP request to retrieve user schedules fails.

        Tags:
            get, user-schedules, team, organization, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/teams/{teamId}/users/{userId}/schedules"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_users_controller_get_organizations_users(
        self, orgId, take=None, skip=None, emails=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of user information for a given organization, with optional filtering and pagination.

        Args:
            orgId: str. Unique identifier of the organization whose users are being retrieved.
            take: Optional[int]. Limits the number of users returned in the response.
            skip: Optional[int]. Number of users to skip from the start of the result set (useful for pagination).
            emails: Optional[str or list]. Filter returned users by one or more email addresses.

        Returns:
            dict[str, Any]: A dictionary containing user information for the specified organization, as returned by the API.

        Raises:
            ValueError: If the required parameter 'orgId' is not provided.
            requests.HTTPError: If the HTTP request to the API fails with a non-success status code.

        Tags:
            list, users, organizations, api, pagination, filtering
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/users"
        query_params = {
            k: v
            for k, v in [("take", take), ("skip", skip), ("emails", emails)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_users_controller_create_organization_user(
        self,
        orgId,
        email,
        username=None,
        weekday=None,
        brandColor=None,
        darkBrandColor=None,
        hideBranding=None,
        timeZone=None,
        theme=None,
        appTheme=None,
        timeFormat=None,
        defaultScheduleId=None,
        locale=None,
        avatarUrl=None,
        organizationRole=None,
        autoAccept=None,
    ) -> dict[str, Any]:
        """
        Creates a new user within a specified organization by sending a POST request with the provided user details.

        Args:
            orgId: str. Unique identifier of the organization.
            email: str. Email address of the user to be created.
            username: str, optional. Username for the new user.
            weekday: str, optional. Preferred start day of the week for the user.
            brandColor: str, optional. Brand color associated with the user or organization.
            darkBrandColor: str, optional. Dark theme brand color.
            hideBranding: bool, optional. Whether to hide branding for the user.
            timeZone: str, optional. Time zone for the user.
            theme: str, optional. Theme for the user interface.
            appTheme: str, optional. Application theme for the user.
            timeFormat: str, optional. Time format preference (e.g., 12-hour or 24-hour).
            defaultScheduleId: str, optional. Default schedule identifier for the user.
            locale: str, optional. Locale for language and region settings.
            avatarUrl: str, optional. URL to the user's avatar image.
            organizationRole: str, optional. Role of the user within the organization.
            autoAccept: bool, optional. If set, user auto-accepts invitations and requests.

        Returns:
            dict. JSON response containing the details of the newly created organization user.

        Raises:
            ValueError: If the required parameter 'orgId' or 'email' is missing.
            requests.HTTPError: If the HTTP request to the server fails or returns a non-success status code.

        Tags:
            create, organization-user, management, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if email is None:
            raise ValueError("Missing required parameter 'email'")
        request_body = {
            "email": email,
            "username": username,
            "weekday": weekday,
            "brandColor": brandColor,
            "darkBrandColor": darkBrandColor,
            "hideBranding": hideBranding,
            "timeZone": timeZone,
            "theme": theme,
            "appTheme": appTheme,
            "timeFormat": timeFormat,
            "defaultScheduleId": defaultScheduleId,
            "locale": locale,
            "avatarUrl": avatarUrl,
            "organizationRole": organizationRole,
            "autoAccept": autoAccept,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/users"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_users_controller_delete_organization_user(
        self, orgId, userId
    ) -> dict[str, Any]:
        """
        Deletes a user from the specified organization.

        Args:
            orgId: The unique identifier of the organization from which the user will be removed.
            userId: The unique identifier of the user to delete from the organization.

        Returns:
            A dictionary containing the JSON response from the delete operation.

        Raises:
            ValueError: Raised if either 'orgId' or 'userId' is None.
            requests.HTTPError: Raised if the HTTP request to delete the user fails.

        Tags:
            delete, organization-user, management
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/users/{userId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_webhooks_controller_get_all_organization_webhooks(
        self, orgId, take=None, skip=None
    ) -> dict[str, Any]:
        """
        Retrieves all webhooks configured for the specified organization, with optional pagination.

        Args:
            orgId: str. The unique identifier of the organization for which to fetch webhooks.
            take: Optional[int]. The maximum number of webhooks to retrieve. Used for pagination.
            skip: Optional[int]. The number of webhooks to skip before starting to collect the result set. Used for pagination.

        Returns:
            dict[str, Any]: A dictionary containing webhook information for the specified organization.

        Raises:
            ValueError: Raised if the 'orgId' parameter is None.
            requests.HTTPError: Raised if the HTTP request to fetch webhooks fails (e.g., network issues, 4xx/5xx HTTP response).

        Tags:
            list, webhooks, organization-management, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/webhooks"
        query_params = {
            k: v for k, v in [("take", take), ("skip", skip)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_webhooks_controller_create_organization_webhook(
        self, orgId, active, subscriberUrl, triggers, payloadTemplate=None, secret=None
    ) -> dict[str, Any]:
        """
        Creates a new webhook for an organization with specified parameters.

        Args:
            orgId: str. The unique identifier of the organization for which the webhook is being created.
            active: bool. Indicates whether the webhook should be active upon creation.
            subscriberUrl: str. The URL where webhook payloads will be delivered.
            triggers: list. The list of event triggers that will cause the webhook to fire.
            payloadTemplate: Optional[str]. A custom template for the webhook payload. If not provided, a default template is used.
            secret: Optional[str]. A secret used to sign webhook payloads for added security.

        Returns:
            dict[str, Any]: The JSON response containing details of the created webhook.

        Raises:
            ValueError: Raised if any of the required parameters ('orgId', 'active', 'subscriberUrl', 'triggers') are missing.
            requests.HTTPError: Raised if the HTTP request to create the webhook fails (non-success response from the API).

        Tags:
            create, webhook, organization, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if active is None:
            raise ValueError("Missing required parameter 'active'")
        if subscriberUrl is None:
            raise ValueError("Missing required parameter 'subscriberUrl'")
        if triggers is None:
            raise ValueError("Missing required parameter 'triggers'")
        request_body = {
            "payloadTemplate": payloadTemplate,
            "active": active,
            "subscriberUrl": subscriberUrl,
            "triggers": triggers,
            "secret": secret,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/webhooks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_webhooks_controller_get_organization_webhook(
        self, orgId, webhookId
    ) -> dict[str, Any]:
        """
        Retrieves details for a specific webhook associated with an organization.

        Args:
            orgId: The unique identifier of the organization whose webhook is to be retrieved.
            webhookId: The unique identifier of the webhook within the specified organization.

        Returns:
            A dictionary containing the details of the requested webhook.

        Raises:
            ValueError: Raised if 'orgId' or 'webhookId' is None.
            requests.HTTPError: Raised if the HTTP request to the API endpoint fails.

        Tags:
            get, webhooks, organization, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if webhookId is None:
            raise ValueError("Missing required parameter 'webhookId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/webhooks/{webhookId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_webhooks_controller_delete_webhook(
        self, orgId, webhookId
    ) -> dict[str, Any]:
        """
        Deletes a webhook from the specified organization by its webhook ID.

        Args:
            orgId: str. The unique identifier of the organization from which the webhook will be deleted.
            webhookId: str. The unique identifier of the webhook to delete.

        Returns:
            dict[str, Any]: The API response as a dictionary containing the result of the deletion operation.

        Raises:
            ValueError: Raised if 'orgId' or 'webhookId' is None.
            requests.HTTPError: Raised if the HTTP request for webhook deletion fails with an error status code.

        Tags:
            delete, webhook, organization, api
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if webhookId is None:
            raise ValueError("Missing required parameter 'webhookId'")
        url = f"{self.base_url}/v2/organizations/{orgId}/webhooks/{webhookId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def organizations_webhooks_controller_update_org_webhook(
        self,
        orgId,
        webhookId,
        payloadTemplate=None,
        active=None,
        subscriberUrl=None,
        triggers=None,
        secret=None,
    ) -> dict[str, Any]:
        """
        Updates an organization's webhook configuration.

        Args:
            orgId: String identifier of the organization. Required.
            webhookId: String identifier of the webhook to update. Required.
            payloadTemplate: Optional template that defines the structure of the webhook payload.
            active: Optional boolean flag indicating whether the webhook is active.
            subscriberUrl: Optional URL where webhook notifications will be sent.
            triggers: Optional list of events that will trigger the webhook.
            secret: Optional secret key used to validate webhook requests.

        Returns:
            Dictionary containing the updated webhook configuration details.

        Raises:
            ValueError: When required parameters 'orgId' or 'webhookId' are None.
            HTTPError: When the API request fails.

        Tags:
            update, webhook, organization, management
        """
        if orgId is None:
            raise ValueError("Missing required parameter 'orgId'")
        if webhookId is None:
            raise ValueError("Missing required parameter 'webhookId'")
        request_body = {
            "payloadTemplate": payloadTemplate,
            "active": active,
            "subscriberUrl": subscriberUrl,
            "triggers": triggers,
            "secret": secret,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/organizations/{orgId}/webhooks/{webhookId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def bookings_controller_2024_08_13_get_bookings(
        self,
        status=None,
        attendeeEmail=None,
        attendeeName=None,
        eventTypeIds=None,
        eventTypeId=None,
        teamsIds=None,
        teamId=None,
        afterStart=None,
        beforeEnd=None,
        sortStart=None,
        sortEnd=None,
        sortCreated=None,
        take=None,
        skip=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of bookings filtered by various query parameters such as status, attendee details, event type, team, and date ranges.

        Args:
            status: Optional; filter bookings by status (e.g., 'confirmed', 'canceled').
            attendeeEmail: Optional; filter bookings by the attendee's email address.
            attendeeName: Optional; filter bookings by the attendee's name.
            eventTypeIds: Optional; filter bookings by a list of event type IDs.
            eventTypeId: Optional; filter bookings by a specific event type ID.
            teamsIds: Optional; filter bookings by a list of team IDs.
            teamId: Optional; filter bookings by a specific team ID.
            afterStart: Optional; filter bookings with a start date/time after this value (ISO 8601 format or timestamp).
            beforeEnd: Optional; filter bookings with an end date/time before this value (ISO 8601 format or timestamp).
            sortStart: Optional; specify sorting by start time ('asc' or 'desc').
            sortEnd: Optional; specify sorting by end time ('asc' or 'desc').
            sortCreated: Optional; specify sorting by creation time ('asc' or 'desc').
            take: Optional; limit on the number of bookings to return.
            skip: Optional; number of bookings to skip for pagination.

        Returns:
            dict[str, Any]: A dictionary containing the retrieved bookings and related metadata.

        Raises:
            HTTPError: If the HTTP request to the bookings API fails or returns an error status code.

        Tags:
            list, bookings, filter, api
        """
        url = f"{self.base_url}/v2/bookings"
        query_params = {
            k: v
            for k, v in [
                ("status", status),
                ("attendeeEmail", attendeeEmail),
                ("attendeeName", attendeeName),
                ("eventTypeIds", eventTypeIds),
                ("eventTypeId", eventTypeId),
                ("teamsIds", teamsIds),
                ("teamId", teamId),
                ("afterStart", afterStart),
                ("beforeEnd", beforeEnd),
                ("sortStart", sortStart),
                ("sortEnd", sortEnd),
                ("sortCreated", sortCreated),
                ("take", take),
                ("skip", skip),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def bookings_controller_2024_08_13_get_booking(self, bookingUid) -> dict[str, Any]:
        """
        Retrieves the details of a booking by its unique identifier.

        Args:
            bookingUid: str. The unique identifier of the booking to retrieve.

        Returns:
            dict. A dictionary containing the booking details retrieved from the API.

        Raises:
            ValueError: If 'bookingUid' is None.
            requests.HTTPError: If the HTTP request to the bookings API fails or returns an error response.

        Tags:
            get, booking, api, controller
        """
        if bookingUid is None:
            raise ValueError("Missing required parameter 'bookingUid'")
        url = f"{self.base_url}/v2/bookings/{bookingUid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def bookings_controller_2024_08_13_reschedule_booking(
        self, bookingUid
    ) -> dict[str, Any]:
        """
        Reschedules an existing booking by sending a reschedule request for the specified booking UID.

        Args:
            bookingUid: str. The unique identifier of the booking to be rescheduled.

        Returns:
            dict. A dictionary containing the response data for the rescheduled booking.

        Raises:
            ValueError: Raised when the required parameter 'bookingUid' is missing or None.
            HTTPError: Raised if the HTTP request to the reschedule endpoint fails.

        Tags:
            reschedule, bookings, controller, api
        """
        if bookingUid is None:
            raise ValueError("Missing required parameter 'bookingUid'")
        url = f"{self.base_url}/v2/bookings/{bookingUid}/reschedule"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def bookings_controller_2024_08_13_cancel_booking(
        self, bookingUid
    ) -> dict[str, Any]:
        """
        Cancels an existing booking identified by the provided booking UID.

        Args:
            bookingUid: str. The unique identifier of the booking to cancel.

        Returns:
            dict. JSON response from the API confirming the booking has been cancelled or providing error details.

        Raises:
            ValueError: If 'bookingUid' is None.
            requests.HTTPError: If the HTTP request to cancel the booking fails.

        Tags:
            cancel, booking, api
        """
        if bookingUid is None:
            raise ValueError("Missing required parameter 'bookingUid'")
        url = f"{self.base_url}/v2/bookings/{bookingUid}/cancel"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def bookings_controller_2024_08_13_mark_no_show(
        self, bookingUid, host=None, attendees=None
    ) -> dict[str, Any]:
        """
        Marks a booking as a no-show (absent) for the specified booking UID, optionally specifying host and attendee information.

        Args:
            bookingUid: str. The unique identifier for the booking to be marked as absent. Required.
            host: Optional[Any]. Host information to associate with the no-show event. Defaults to None.
            attendees: Optional[Any]. Attendee information to associate with the no-show event. Defaults to None.

        Returns:
            dict[str, Any]: The parsed JSON response from the backend service after marking the booking as absent.

        Raises:
            ValueError: If 'bookingUid' is None.
            requests.HTTPError: If the HTTP request to mark the booking as absent fails (non-2xx response).

        Tags:
            mark, booking, no-show, management, api
        """
        if bookingUid is None:
            raise ValueError("Missing required parameter 'bookingUid'")
        request_body = {
            "host": host,
            "attendees": attendees,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/bookings/{bookingUid}/mark-absent"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def bookings_controller_2024_08_13_reassign_booking(
        self, bookingUid
    ) -> dict[str, Any]:
        """
        Reassigns an existing booking identified by its unique identifier.

        Args:
            bookingUid: str. The unique identifier of the booking to be reassigned. Must not be None.

        Returns:
            dict. The response data from the reassignment request as a dictionary.

        Raises:
            ValueError: If 'bookingUid' is None.
            requests.HTTPError: If the HTTP reassignment request fails.

        Tags:
            reassign, booking, controller, api
        """
        if bookingUid is None:
            raise ValueError("Missing required parameter 'bookingUid'")
        url = f"{self.base_url}/v2/bookings/{bookingUid}/reassign"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def bookings_controller_2024_08_13_reassign_booking_to_user(
        self, bookingUid, userId, reason=None
    ) -> dict[str, Any]:
        """
        Reassigns a booking to a different user with an optional reason.

        Args:
            bookingUid: str. The unique identifier of the booking to be reassigned.
            userId: str. The unique identifier of the user to whom the booking will be reassigned.
            reason: Optional[str]. The reason for reassigning the booking. Defaults to None.

        Returns:
            dict[str, Any]: The JSON response from the booking reassignment API containing updated booking information.

        Raises:
            ValueError: Raised if 'bookingUid' or 'userId' is None.
            requests.HTTPError: Raised if the HTTP request to reassign the booking fails.

        Tags:
            reassign, booking, api, management
        """
        if bookingUid is None:
            raise ValueError("Missing required parameter 'bookingUid'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        request_body = {
            "reason": reason,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/bookings/{bookingUid}/reassign/{userId}"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def bookings_controller_2024_08_13_confirm_booking(
        self, bookingUid
    ) -> dict[str, Any]:
        """
        Confirms a booking identified by its unique UID via a POST request to the bookings API.

        Args:
            bookingUid: str. The unique identifier of the booking to confirm.

        Returns:
            dict. The JSON response from the bookings API after confirming the booking.

        Raises:
            ValueError: If 'bookingUid' is None.
            HTTPError: If the HTTP request to the bookings API fails with a non-success status code.

        Tags:
            confirm, booking, api, post
        """
        if bookingUid is None:
            raise ValueError("Missing required parameter 'bookingUid'")
        url = f"{self.base_url}/v2/bookings/{bookingUid}/confirm"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def bookings_controller_2024_08_13_decline_booking(
        self, bookingUid, reason=None
    ) -> dict[str, Any]:
        """
        Declines a booking identified by its unique UID, providing an optional reason for the decline.

        Args:
            bookingUid: str. The unique identifier for the booking to be declined. Must not be None.
            reason: Optional[str]. The reason for declining the booking. If not provided, the decline will proceed without a reason.

        Returns:
            dict[str, Any]: A dictionary containing the response data from the booking decline operation.

        Raises:
            ValueError: Raised if 'bookingUid' is None, indicating a required parameter is missing.
            requests.HTTPError: Raised if the HTTP request to the backend API fails or returns an unsuccessful status code.

        Tags:
            decline, booking, management, api
        """
        if bookingUid is None:
            raise ValueError("Missing required parameter 'bookingUid'")
        request_body = {
            "reason": reason,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/bookings/{bookingUid}/decline"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def calendars_controller_create_ics_feed(
        self, urls, readOnly=None
    ) -> dict[str, Any]:
        """
        Creates or updates an ICS feed for multiple calendar URLs with optional read-only access.

        Args:
            urls: list[str]. A list of calendar URLs to include in the ICS feed. This parameter is required.
            readOnly: bool or None. If set to True, the ICS feed will be created with read-only permissions. If None, the default server behavior is applied.

        Returns:
            dict[str, Any]: A dictionary containing the server response data for the created or updated ICS feed.

        Raises:
            ValueError: Raised if the required parameter 'urls' is not provided.
            requests.HTTPError: Raised if the HTTP response from the server indicates an unsuccessful status code.

        Tags:
            create, calendars, ics-feed, management
        """
        if urls is None:
            raise ValueError("Missing required parameter 'urls'")
        request_body = {
            "urls": urls,
            "readOnly": readOnly,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/calendars/ics-feed/save"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def calendars_controller_check_ics_feed(
        self,
    ) -> dict[str, Any]:
        """
        Checks the status and validity of the ICS calendar feed using the calendar service API.

        Args:
            None: This function takes no arguments

        Returns:
            A dictionary containing the result of the ICS feed check, including status and any relevant information returned by the API.

        Raises:
            requests.HTTPError: If the HTTP request to the ICS feed check endpoint returns an unsuccessful status code.

        Tags:
            check, calendar, ics-feed, api
        """
        url = f"{self.base_url}/v2/calendars/ics-feed/check"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def calendars_controller_get_busy_times(
        self, loggedInUsersTz, credentialId, externalId, dateFrom=None, dateTo=None
    ) -> dict[str, Any]:
        """
        Fetches the busy time slots from a calendar provider for a specified external calendar within an optional date range.

        Args:
            loggedInUsersTz: str. The timezone of the logged-in user (IANA timezone name, e.g., 'America/New_York').
            credentialId: str. The unique identifier for the user's calendar credential.
            externalId: str. The unique identifier for the external calendar whose busy times are being fetched.
            dateFrom: str or None. Optional start date (ISO 8601 format) for the query range. If not specified, busy times are fetched without a lower bound.
            dateTo: str or None. Optional end date (ISO 8601 format) for the query range. If not specified, busy times are fetched without an upper bound.

        Returns:
            dict. A dictionary containing the busy time slots information as returned by the calendar provider's API.

        Raises:
            ValueError: If any of the required parameters ('loggedInUsersTz', 'credentialId', or 'externalId') are missing or None.
            requests.HTTPError: If the HTTP request to the calendar API fails or returns an error status.

        Tags:
            get, calendar, busy-times, external-api, query
        """
        if loggedInUsersTz is None:
            raise ValueError("Missing required parameter 'loggedInUsersTz'")
        if credentialId is None:
            raise ValueError("Missing required parameter 'credentialId'")
        if externalId is None:
            raise ValueError("Missing required parameter 'externalId'")
        url = f"{self.base_url}/v2/calendars/busy-times"
        query_params = {
            k: v
            for k, v in [
                ("loggedInUsersTz", loggedInUsersTz),
                ("dateFrom", dateFrom),
                ("dateTo", dateTo),
                ("credentialId", credentialId),
                ("externalId", externalId),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def calendars_controller_get_calendars(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves a list of available calendars from the API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            A dictionary containing the JSON response with calendar data.

        Raises:
            requests.HTTPError: If the HTTP request to the calendars endpoint returns an unsuccessful status code.

        Tags:
            get, list, calendars, api
        """
        url = f"{self.base_url}/v2/calendars"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def calendars_controller_redirect(self, calendar) -> dict[str, Any]:
        """
        Redirects to the calendar connection endpoint and returns the response as a dictionary.

        Args:
            calendar: str. The unique identifier of the calendar to connect.

        Returns:
            dict[str, Any]: A dictionary containing the JSON response from the calendar connection endpoint.

        Raises:
            ValueError: Raised when the 'calendar' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the connection endpoint fails.

        Tags:
            redirect, calendar, controller, api
        """
        if calendar is None:
            raise ValueError("Missing required parameter 'calendar'")
        url = f"{self.base_url}/v2/calendars/{calendar}/connect"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def calendars_controller_save(self, calendar, state, code) -> Any:
        """
        Saves the state of a specified calendar by sending a request to the API endpoint with given parameters.

        Args:
            calendar: The identifier of the calendar to be saved.
            state: The state information to save for the calendar.
            code: The authorization or access code required for saving the calendar.

        Returns:
            The parsed JSON response from the API containing the result of the save operation.

        Raises:
            ValueError: Raised if any of the required parameters ('calendar', 'state', or 'code') is None.
            requests.exceptions.HTTPError: Raised if the HTTP request to the API endpoint fails or returns an unsuccessful status.

        Tags:
            save, calendar-management, api-call
        """
        if calendar is None:
            raise ValueError("Missing required parameter 'calendar'")
        if state is None:
            raise ValueError("Missing required parameter 'state'")
        if code is None:
            raise ValueError("Missing required parameter 'code'")
        url = f"{self.base_url}/v2/calendars/{calendar}/save"
        query_params = {
            k: v for k, v in [("state", state), ("code", code)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def calendars_controller_sync_credentials(self, calendar) -> Any:
        """
        Synchronizes calendar credentials by sending a POST request for the specified calendar.

        Args:
            calendar: The unique identifier or name of the calendar to synchronize credentials for.

        Returns:
            A JSON object containing the response data from the calendar credentials synchronization request.

        Raises:
            ValueError: Raised if the 'calendar' parameter is None.
            HTTPError: Raised if the HTTP request returns an unsuccessful status code.

        Tags:
            sync, credentials, calendar
        """
        if calendar is None:
            raise ValueError("Missing required parameter 'calendar'")
        url = f"{self.base_url}/v2/calendars/{calendar}/credentials"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def calendars_controller_check(self, calendar) -> dict[str, Any]:
        """
        Checks the status or validity of a specified calendar by making a GET request to the corresponding API endpoint.

        Args:
            calendar: str. The identifier of the calendar to check.

        Returns:
            dict[str, Any]: A dictionary containing the response data from the API regarding the specified calendar.

        Raises:
            ValueError: If 'calendar' is None.
            HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            check, calendar, api
        """
        if calendar is None:
            raise ValueError("Missing required parameter 'calendar'")
        url = f"{self.base_url}/v2/calendars/{calendar}/check"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def calendars_controller_delete_calendar_credentials(
        self, calendar, id
    ) -> dict[str, Any]:
        """
        Disconnects and deletes calendar credentials for a specified calendar by sending a POST request to the external service.

        Args:
            calendar: str. The identifier of the calendar for which credentials should be deleted.
            id: str. The credential or user ID to be removed from the calendar.

        Returns:
            dict[str, Any]: The JSON response from the external service indicating the result of the disconnection operation.

        Raises:
            ValueError: Raised if either 'calendar' or 'id' is None.
            requests.HTTPError: Raised if the HTTP request to disconnect calendar credentials returns an unsuccessful status code.

        Tags:
            delete, calendar, credentials, management
        """
        if calendar is None:
            raise ValueError("Missing required parameter 'calendar'")
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        request_body = {
            "id": id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/calendars/{calendar}/disconnect"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def conferencing_controller_connect(self, app) -> dict[str, Any]:
        """
        Connects to the conferencing service for the specified application and returns the response data.

        Args:
            app: The application identifier to connect conferencing for. Must not be None.

        Returns:
            A dictionary containing the JSON response data from the conferencing connect endpoint.

        Raises:
            ValueError: If 'app' is None.
            requests.HTTPError: If the HTTP request returns an unsuccessful status code.

        Tags:
            connect, conferencing, api, async-job
        """
        if app is None:
            raise ValueError("Missing required parameter 'app'")
        url = f"{self.base_url}/v2/conferencing/{app}/connect"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def conferencing_controller_redirect(
        self, app, returnTo, onErrorReturnTo
    ) -> dict[str, Any]:
        """
        Constructs and requests an OAuth conferencing redirect URL for the specified app, handling success and error redirects.

        Args:
            app: str. The identifier of the conferencing application to initiate the OAuth flow for.
            returnTo: str. The URL to redirect to upon successful authentication.
            onErrorReturnTo: str. The URL to redirect to if authentication fails.

        Returns:
            dict[str, Any]: A dictionary containing the JSON response from the OAuth URL endpoint.

        Raises:
            ValueError: If any of the required parameters ('app', 'returnTo', 'onErrorReturnTo') are None.
            requests.HTTPError: If the HTTP response indicates an unsuccessful status code.

        Tags:
            conferencing, redirect, oauth, controller, api
        """
        if app is None:
            raise ValueError("Missing required parameter 'app'")
        if returnTo is None:
            raise ValueError("Missing required parameter 'returnTo'")
        if onErrorReturnTo is None:
            raise ValueError("Missing required parameter 'onErrorReturnTo'")
        url = f"{self.base_url}/v2/conferencing/{app}/oauth/auth-url"
        query_params = {
            k: v
            for k, v in [("returnTo", returnTo), ("onErrorReturnTo", onErrorReturnTo)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def conferencing_controller_save(self, app, state, code) -> Any:
        """
        Handles an OAuth callback by sending the provided authorization code and state to the conferencing app's endpoint and returns the resulting authentication data.

        Args:
            app: str. The identifier for the conferencing application (e.g., 'zoom', 'teams').
            state: str. The state parameter received during the OAuth callback, used to validate the OAuth flow.
            code: str. The authorization code received from the OAuth provider to exchange for tokens.

        Returns:
            dict. The JSON response from the conferencing provider containing authentication or user information.

        Raises:
            ValueError: If any of 'app', 'state', or 'code' parameters are None.
            requests.HTTPError: If the HTTP request to the OAuth callback endpoint fails.

        Tags:
            conferencing, oauth, controller, save, authentication
        """
        if app is None:
            raise ValueError("Missing required parameter 'app'")
        if state is None:
            raise ValueError("Missing required parameter 'state'")
        if code is None:
            raise ValueError("Missing required parameter 'code'")
        url = f"{self.base_url}/v2/conferencing/{app}/oauth/callback"
        query_params = {
            k: v for k, v in [("state", state), ("code", code)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def conferencing_controller_list_installed_conferencing_apps(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves a list of all installed conferencing applications from the conferencing API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            A dictionary containing details of the installed conferencing applications as returned by the API.

        Raises:
            HTTPError: If the HTTP request to the conferencing API endpoint fails or returns an unsuccessful status code.

        Tags:
            list, conferencing, api
        """
        url = f"{self.base_url}/v2/conferencing"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def conferencing_controller_default(self, app) -> dict[str, Any]:
        """
        Retrieves the default conferencing configuration for a specified application.

        Args:
            app: str. The identifier of the application whose default conferencing configuration is to be fetched.

        Returns:
            dict[str, Any]: The default conferencing configuration for the given application as a dictionary.

        Raises:
            ValueError: If the 'app' parameter is None.
            requests.HTTPError: If the HTTP request to fetch the default conferencing configuration fails.

        Tags:
            retrieve, conferencing, default, management
        """
        if app is None:
            raise ValueError("Missing required parameter 'app'")
        url = f"{self.base_url}/v2/conferencing/{app}/default"
        query_params = {}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def conferencing_controller_get_default(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves the default conferencing settings from the server.

        Args:
            None: This function takes no arguments

        Returns:
            A dictionary containing the default conferencing settings as returned by the API.

        Raises:
            requests.HTTPError: If the HTTP request to fetch the default conferencing settings fails or an error response is returned.

        Tags:
            get, conferencing, settings
        """
        url = f"{self.base_url}/v2/conferencing/default"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def conferencing_controller_disconnect(self, app) -> dict[str, Any]:
        """
        Disconnects an active conferencing session for the specified application.

        Args:
            app: str. The unique identifier of the application for which the conferencing session should be disconnected.

        Returns:
            dict. A dictionary containing the server's JSON response to the disconnect operation.

        Raises:
            ValueError: Raised if the 'app' parameter is None.
            requests.HTTPError: Raised if the HTTP request to disconnect the conferencing session fails.

        Tags:
            disconnect, conferencing, management
        """
        if app is None:
            raise ValueError("Missing required parameter 'app'")
        url = f"{self.base_url}/v2/conferencing/{app}/disconnect"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def destination_calendars_controller_update_destination_calendars(
        self, integration, externalId
    ) -> dict[str, Any]:
        """
        Updates destination calendar information using the provided integration and external ID.

        Args:
            integration: Integration identifier or data required for updating the destination calendar.
            externalId: External identifier associated with the destination calendar.

        Returns:
            A dictionary containing the JSON response from the updated destination calendar API.

        Raises:
            ValueError: Raised if 'integration' or 'externalId' is None.
            requests.HTTPError: Raised if the HTTP request for updating the destination calendar fails.

        Tags:
            update, destination-calendars, calendar-management, api
        """
        if integration is None:
            raise ValueError("Missing required parameter 'integration'")
        if externalId is None:
            raise ValueError("Missing required parameter 'externalId'")
        request_body = {
            "integration": integration,
            "externalId": externalId,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/destination-calendars"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def event_types_controller_2024_06_14_get_event_types(
        self, username=None, eventSlug=None, usernames=None, orgSlug=None, orgId=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of event types from the API using optional filtering parameters.

        Args:
            username: Optional; a string specifying a single username to filter event types by user.
            eventSlug: Optional; a string specifying a particular event slug to filter event types.
            usernames: Optional; a list or string of usernames to filter event types by multiple users.
            orgSlug: Optional; a string specifying the organization slug to filter event types by organization.
            orgId: Optional; an integer or string specifying the organization ID to filter event types.

        Returns:
            A dictionary containing the JSON response from the API with the filtered list of event types.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails or returns an error response.

        Tags:
            get, list, event-types, api, filter
        """
        url = f"{self.base_url}/v2/event-types"
        query_params = {
            k: v
            for k, v in [
                ("username", username),
                ("eventSlug", eventSlug),
                ("usernames", usernames),
                ("orgSlug", orgSlug),
                ("orgId", orgId),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def event_types_controller_2024_06_14_get_event_type_by_id(
        self, eventTypeId
    ) -> dict[str, Any]:
        """
        Retrieves detailed information for a specific event type by its unique identifier.

        Args:
            eventTypeId: str. The unique identifier of the event type to retrieve. Must not be None.

        Returns:
            dict[str, Any]: A dictionary containing the event type details as returned from the API.

        Raises:
            ValueError: Raised if 'eventTypeId' is None.
            requests.HTTPError: Raised if the API response indicates an HTTP error.

        Tags:
            get, event-type, api
        """
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        url = f"{self.base_url}/v2/event-types/{eventTypeId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def event_types_controller_2024_06_14_delete_event_type(
        self, eventTypeId
    ) -> dict[str, Any]:
        """
        Deletes an event type specified by its ID from the event types resource.

        Args:
            eventTypeId: str. The unique identifier of the event type to be deleted.

        Returns:
            dict. Parsed JSON response from the API indicating the status or result of the delete operation.

        Raises:
            ValueError: Raised if 'eventTypeId' is None.
            HTTPError: Raised if the HTTP request to delete the event type fails with a non-success status code.

        Tags:
            delete, event-type, api
        """
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        url = f"{self.base_url}/v2/event-types/{eventTypeId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def event_type_webhooks_controller_create_event_type_webhook(
        self,
        eventTypeId,
        active,
        subscriberUrl,
        triggers,
        payloadTemplate=None,
        secret=None,
    ) -> dict[str, Any]:
        """
        Creates a new webhook for a specific event type, registering a subscriber endpoint to receive event notifications based on defined triggers.

        Args:
            eventTypeId: str. Unique identifier of the event type for which the webhook will be created.
            active: bool. Indicates whether the webhook should be active upon creation.
            subscriberUrl: str. URL of the subscriber endpoint that will receive webhook event notifications.
            triggers: list. List of event triggers that determine when the webhook will be invoked.
            payloadTemplate: Optional[str]. Custom template for the webhook payload. Defaults to None.
            secret: Optional[str]. Secret used for validating webhook requests. Defaults to None.

        Returns:
            dict. JSON response containing details of the created webhook.

        Raises:
            ValueError: Raised if any required parameter (eventTypeId, active, subscriberUrl, or triggers) is missing.
            requests.HTTPError: Raised if the HTTP request to create the webhook fails with an error response.

        Tags:
            create, webhook, event-type, management
        """
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        if active is None:
            raise ValueError("Missing required parameter 'active'")
        if subscriberUrl is None:
            raise ValueError("Missing required parameter 'subscriberUrl'")
        if triggers is None:
            raise ValueError("Missing required parameter 'triggers'")
        request_body = {
            "payloadTemplate": payloadTemplate,
            "active": active,
            "subscriberUrl": subscriberUrl,
            "triggers": triggers,
            "secret": secret,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/event-types/{eventTypeId}/webhooks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def event_type_webhooks_controller_get_event_type_webhooks(
        self, eventTypeId, take=None, skip=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of webhooks associated with a specific event type, supporting optional pagination.

        Args:
            eventTypeId: str. The unique identifier for the event type whose webhooks are to be fetched. Required.
            take: Optional[int]. The maximum number of webhooks to return. Used for pagination.
            skip: Optional[int]. The number of webhooks to skip before starting to collect the result set. Used for pagination.

        Returns:
            dict[str, Any]: A dictionary containing details of the webhooks associated with the specified event type.

        Raises:
            ValueError: Raised if 'eventTypeId' is None.
            requests.HTTPError: Raised if the HTTP request to fetch webhooks fails (e.g., due to non-2xx response).

        Tags:
            list, webhooks, event-type, api, pagination
        """
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        url = f"{self.base_url}/v2/event-types/{eventTypeId}/webhooks"
        query_params = {
            k: v for k, v in [("take", take), ("skip", skip)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def event_type_webhooks_controller_delete_all_event_type_webhooks(
        self, eventTypeId
    ) -> dict[str, Any]:
        """
        Deletes all webhooks associated with a specific event type.

        Args:
            eventTypeId: str. Unique identifier for the event type whose webhooks are to be deleted.

        Returns:
            dict[str, Any]: A dictionary representing the response content from the API after deleting the webhooks.

        Raises:
            ValueError: Raised if 'eventTypeId' is None.
            HTTPError: Raised if the HTTP response indicates an error status.

        Tags:
            delete, webhooks, event-type, api, management
        """
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        url = f"{self.base_url}/v2/event-types/{eventTypeId}/webhooks"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def event_type_webhooks_controller_update_event_type_webhook(
        self,
        eventTypeId,
        webhookId,
        payloadTemplate=None,
        active=None,
        subscriberUrl=None,
        triggers=None,
        secret=None,
    ) -> dict[str, Any]:
        """
        Updates an existing webhook for a specific event type with the provided parameters.

        Args:
            eventTypeId: str. Unique identifier for the event type whose webhook is to be updated. Required.
            webhookId: str. Unique identifier for the webhook to update. Required.
            payloadTemplate: Optional[str]. Custom payload template configuration for the webhook.
            active: Optional[bool]. Indicates whether the webhook should be active.
            subscriberUrl: Optional[str]. The URL that will receive event callbacks.
            triggers: Optional[list]. List of event triggers that activate this webhook.
            secret: Optional[str]. Secret key used to sign webhook payloads for verification.

        Returns:
            dict[str, Any]: A dictionary representing the updated webhook resource as returned by the API.

        Raises:
            ValueError: Raised if required parameters 'eventTypeId' or 'webhookId' are missing.
            requests.HTTPError: Raised if the API request fails or returns an unsuccessful status code.

        Tags:
            update, webhook, management, event-type, api
        """
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        if webhookId is None:
            raise ValueError("Missing required parameter 'webhookId'")
        request_body = {
            "payloadTemplate": payloadTemplate,
            "active": active,
            "subscriberUrl": subscriberUrl,
            "triggers": triggers,
            "secret": secret,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/event-types/{eventTypeId}/webhooks/{webhookId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def event_type_webhooks_controller_get_event_type_webhook(
        self, eventTypeId, webhookId
    ) -> dict[str, Any]:
        """
        Retrieves details of a specific webhook configured for a given event type.

        Args:
            eventTypeId: The unique identifier of the event type for which the webhook is configured.
            webhookId: The unique identifier of the webhook to retrieve.

        Returns:
            A dictionary containing the webhook details associated with the specified event type.

        Raises:
            ValueError: Raised if either 'eventTypeId' or 'webhookId' is not provided (i.e., is None).
            requests.HTTPError: Raised if the HTTP request to retrieve the webhook details fails.

        Tags:
            get, webhook, event-type, management
        """
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        if webhookId is None:
            raise ValueError("Missing required parameter 'webhookId'")
        url = f"{self.base_url}/v2/event-types/{eventTypeId}/webhooks/{webhookId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def event_type_webhooks_controller_delete_event_type_webhook(
        self, eventTypeId, webhookId
    ) -> dict[str, Any]:
        """
        Deletes a webhook associated with a specific event type by sending a DELETE request to the corresponding API endpoint.

        Args:
            eventTypeId: The unique identifier of the event type whose webhook should be deleted.
            webhookId: The unique identifier of the webhook to be deleted.

        Returns:
            A dictionary containing the API response data after successfully deleting the webhook.

        Raises:
            ValueError: Raised if either 'eventTypeId' or 'webhookId' is None.
            requests.HTTPError: Raised if the HTTP request to delete the webhook fails (non-2xx status code).

        Tags:
            delete, webhook, event-type, api, management
        """
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        if webhookId is None:
            raise ValueError("Missing required parameter 'webhookId'")
        url = f"{self.base_url}/v2/event-types/{eventTypeId}/webhooks/{webhookId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def me_controller_get_me(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves the authenticated user's profile information from the API.

        Returns:
            dict[str, Any]: A dictionary containing the user's profile details as returned by the API.

        Raises:
            requests.HTTPError: If the HTTP request to retrieve the user profile fails or returns a non-success status code.

        Tags:
            get, user, profile, api
        """
        url = f"{self.base_url}/v2/me"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def me_controller_update_me(
        self,
        email=None,
        name=None,
        timeFormat=None,
        defaultScheduleId=None,
        weekStart=None,
        timeZone=None,
        locale=None,
        avatarUrl=None,
    ) -> dict[str, Any]:
        """
        Updates the current user's profile information with the provided fields.

        Args:
            email: Optional[str]. The new email address to update for the user.
            name: Optional[str]. The new display name for the user.
            timeFormat: Optional[str]. The preferred time format (e.g., '24h' or '12h') for the user.
            defaultScheduleId: Optional[str]. The default schedule identifier to assign to the user.
            weekStart: Optional[str]. The desired start day of the week (e.g., 'Monday').
            timeZone: Optional[str]. The user's preferred time zone.
            locale: Optional[str]. The user's preferred locale (e.g., 'en-US').
            avatarUrl: Optional[str]. URL for the new avatar image for the user.

        Returns:
            dict[str, Any]: The updated user profile information as returned by the API.

        Raises:
            requests.HTTPError: If the server returns an unsuccessful status code or the request fails.

        Tags:
            update, profile, user, controller, api
        """
        request_body = {
            "email": email,
            "name": name,
            "timeFormat": timeFormat,
            "defaultScheduleId": defaultScheduleId,
            "weekStart": weekStart,
            "timeZone": timeZone,
            "locale": locale,
            "avatarUrl": avatarUrl,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/me"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def schedules_controller_2024_06_11_create_schedule(
        self, name, timeZone, isDefault, availability=None, overrides=None
    ) -> dict[str, Any]:
        """
        Creates a new schedule with the specified name, time zone, and settings.

        Args:
            name: str. The name for the new schedule. Must not be None.
            timeZone: str. The IANA time zone identifier for the schedule. Must not be None.
            isDefault: bool. Indicates if this schedule is the default. Must not be None.
            availability: Optional[list[dict]]. The standard availability blocks for the schedule, or None.
            overrides: Optional[list[dict]]. Override rules to apply to this schedule, or None.

        Returns:
            dict. The API response containing details of the newly created schedule.

        Raises:
            ValueError: If any of the required parameters ('name', 'timeZone', or 'isDefault') are None.
            requests.HTTPError: If the API request to create the schedule fails (e.g., non-2xx response).

        Tags:
            create, schedule, management, api
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        if timeZone is None:
            raise ValueError("Missing required parameter 'timeZone'")
        if isDefault is None:
            raise ValueError("Missing required parameter 'isDefault'")
        request_body = {
            "name": name,
            "timeZone": timeZone,
            "availability": availability,
            "isDefault": isDefault,
            "overrides": overrides,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/schedules"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def schedules_controller_2024_06_11_get_schedules(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves the current list of schedules from the remote API.

        Returns:
            A dictionary containing the API response data for all schedules.

        Raises:
            HTTPError: If the HTTP request to retrieve schedules fails or returns an unsuccessful status code.

        Tags:
            get, list, schedules, api
        """
        url = f"{self.base_url}/v2/schedules"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def schedules_controller_2024_06_11_get_default_schedule(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves the default schedule configuration from the API.

        Returns:
            A dictionary containing the default schedule configuration returned by the API.

        Raises:
            HTTPError: If the HTTP request to the API endpoint fails or returns an unsuccessful status code.

        Tags:
            get, schedule, api, management
        """
        url = f"{self.base_url}/v2/schedules/default"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def schedules_controller_2024_06_11_get_schedule(
        self, scheduleId
    ) -> dict[str, Any]:
        """
        Retrieves the details of a specific schedule by its ID.

        Args:
            scheduleId: The unique identifier of the schedule to retrieve.

        Returns:
            A dictionary containing the schedule details as returned by the API.

        Raises:
            ValueError: If the required parameter 'scheduleId' is not provided.
            requests.HTTPError: If the HTTP request to fetch the schedule fails due to a non-success status code.

        Tags:
            get, schedule, fetch, api
        """
        if scheduleId is None:
            raise ValueError("Missing required parameter 'scheduleId'")
        url = f"{self.base_url}/v2/schedules/{scheduleId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def schedules_controller_2024_06_11_update_schedule(
        self,
        scheduleId,
        name=None,
        timeZone=None,
        availability=None,
        isDefault=None,
        overrides=None,
    ) -> dict[str, Any]:
        """
        Updates an existing schedule with new details such as name, time zone, availability, default status, or overrides.

        Args:
            scheduleId: str. The unique identifier of the schedule to update. Required.
            name: str, optional. The new name of the schedule.
            timeZone: str, optional. The time zone of the schedule (e.g., 'America/New_York').
            availability: Any, optional. The updated availability settings for the schedule.
            isDefault: bool, optional. Whether this schedule should be set as the default.
            overrides: Any, optional. A list or mapping of overrides to apply to the schedule.

        Returns:
            dict. The updated schedule object returned by the API.

        Raises:
            ValueError: If 'scheduleId' is not provided.
            requests.HTTPError: If the HTTP request to update the schedule fails (non-success status code).

        Tags:
            update, schedules, management, api, patch
        """
        if scheduleId is None:
            raise ValueError("Missing required parameter 'scheduleId'")
        request_body = {
            "name": name,
            "timeZone": timeZone,
            "availability": availability,
            "isDefault": isDefault,
            "overrides": overrides,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/schedules/{scheduleId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def schedules_controller_2024_06_11_delete_schedule(
        self, scheduleId
    ) -> dict[str, Any]:
        """
        Deletes a schedule by its unique identifier.

        Args:
            scheduleId: str. The unique identifier of the schedule to delete.

        Returns:
            dict[str, Any]: The server response parsed as a dictionary containing the deletion result.

        Raises:
            ValueError: If 'scheduleId' is None.
            HTTPError: If the HTTP request to delete the schedule fails.

        Tags:
            delete, schedule, management
        """
        if scheduleId is None:
            raise ValueError("Missing required parameter 'scheduleId'")
        url = f"{self.base_url}/v2/schedules/{scheduleId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def selected_calendars_controller_add_selected_calendar(
        self, integration, externalId, credentialId
    ) -> dict[str, Any]:
        """
        Adds a selected calendar to the user's account using the specified integration, external calendar ID, and credential ID.

        Args:
            integration: The name or type of the calendar integration service (e.g., 'google', 'outlook').
            externalId: The external ID of the calendar to add, as provided by the integration service.
            credentialId: The credential identifier used to authenticate with the calendar integration.

        Returns:
            A dictionary containing the details of the created selected calendar as returned by the API.

        Raises:
            ValueError: Raised if any of the required parameters ('integration', 'externalId', 'credentialId') are None.
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an error status code.

        Tags:
            add, calendar, integration, controller
        """
        if integration is None:
            raise ValueError("Missing required parameter 'integration'")
        if externalId is None:
            raise ValueError("Missing required parameter 'externalId'")
        if credentialId is None:
            raise ValueError("Missing required parameter 'credentialId'")
        request_body = {
            "integration": integration,
            "externalId": externalId,
            "credentialId": credentialId,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/selected-calendars"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def selected_calendars_controller_remove_selected_calendar(
        self, integration, externalId, credentialId
    ) -> dict[str, Any]:
        """
        Removes a selected calendar integration by sending a DELETE request with the provided identifiers.

        Args:
            integration: str. The integration type or name associated with the selected calendar to be removed.
            externalId: str. The external identifier of the calendar to be removed.
            credentialId: str. The identifier for the credentials associated with the calendar integration.

        Returns:
            dict[str, Any]: The server response as a dictionary containing the result of the removal operation.

        Raises:
            ValueError: Raised if any of the required parameters ('integration', 'externalId', or 'credentialId') are missing.
            requests.HTTPError: Raised if the HTTP request to remove the selected calendar fails (e.g., network errors, server errors).

        Tags:
            remove, selected-calendar, controller, integration, delete
        """
        if integration is None:
            raise ValueError("Missing required parameter 'integration'")
        if externalId is None:
            raise ValueError("Missing required parameter 'externalId'")
        if credentialId is None:
            raise ValueError("Missing required parameter 'credentialId'")
        url = f"{self.base_url}/v2/selected-calendars"
        query_params = {
            k: v
            for k, v in [
                ("integration", integration),
                ("externalId", externalId),
                ("credentialId", credentialId),
            ]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def slots_controller_reserve_slot(
        self, eventTypeId, slotUtcStartDate, slotUtcEndDate, bookingUid=None
    ) -> dict[str, Any]:
        """
        Reserves a timeslot for a specified event type and returns the reservation details.

        Args:
            eventTypeId: Unique identifier for the event type to reserve a slot for. Must not be None.
            slotUtcStartDate: UTC start datetime for the slot to be reserved. Must not be None.
            slotUtcEndDate: UTC end datetime for the slot to be reserved. Must not be None.
            bookingUid: Optional. Unique identifier of an existing booking to associate with the slot. If not provided, a new reservation is created.

        Returns:
            A dictionary containing the details of the reserved slot as returned by the API.

        Raises:
            ValueError: If any of the required parameters ('eventTypeId', 'slotUtcStartDate', 'slotUtcEndDate') are None.
            requests.HTTPError: If the HTTP request to reserve the slot fails or an unsuccessful status code is returned.

        Tags:
            reserve, slot, event-management, api, important
        """
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        if slotUtcStartDate is None:
            raise ValueError("Missing required parameter 'slotUtcStartDate'")
        if slotUtcEndDate is None:
            raise ValueError("Missing required parameter 'slotUtcEndDate'")
        request_body = {
            "eventTypeId": eventTypeId,
            "slotUtcStartDate": slotUtcStartDate,
            "slotUtcEndDate": slotUtcEndDate,
            "bookingUid": bookingUid,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/slots/reserve"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def slots_controller_delete_selected_slot(self, uid) -> dict[str, Any]:
        """
        Deletes the selected slot identified by the given UID using a DELETE request to the slots API.

        Args:
            uid: str. Unique identifier of the slot to be deleted. Must not be None.

        Returns:
            dict[str, Any]: JSON response from the API indicating the result of the deletion operation.

        Raises:
            ValueError: If 'uid' is None.
            requests.HTTPError: If the HTTP request to the API fails (e.g., network error, 4XX/5XX HTTP status).

        Tags:
            delete, slots, api, management
        """
        if uid is None:
            raise ValueError("Missing required parameter 'uid'")
        url = f"{self.base_url}/v2/slots/selected-slot"
        query_params = {k: v for k, v in [("uid", uid)] if v is not None}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def slots_controller_get_available_slots(
        self,
        startTime,
        endTime,
        eventTypeId,
        eventTypeSlug=None,
        usernameList=None,
        duration=None,
        rescheduleUid=None,
        timeZone=None,
        orgSlug=None,
        slotFormat=None,
    ) -> dict[str, Any]:
        """
        Fetches available time slots for a specified event type between given start and end times, with optional filters such as users, duration, timezone, and organization.

        Args:
            startTime: str. The start datetime (ISO 8601 format) to search for available slots. Required.
            endTime: str. The end datetime (ISO 8601 format) to search for available slots. Required.
            eventTypeId: str. The unique identifier of the event type to check slots for. Required.
            eventTypeSlug: str, optional. Slug identifier for the event type.
            usernameList: list[str], optional. List of usernames to restrict slot availability to specific users.
            duration: int, optional. Desired slot duration in minutes.
            rescheduleUid: str, optional. Unique identifier if rescheduling an existing event.
            timeZone: str, optional. IANA timezone name (e.g., 'America/New_York').
            orgSlug: str, optional. Slug identifier for the organization context.
            slotFormat: str, optional. Desired format for slot output.

        Returns:
            dict. JSON response containing available slots and related metadata for the specified criteria.

        Raises:
            ValueError: If any of the required parameters ('startTime', 'endTime', 'eventTypeId') are missing.
            requests.HTTPError: If the HTTP request to fetch slots fails with an error response.

        Tags:
            list, slots, available, search, async_job, management, important
        """
        if startTime is None:
            raise ValueError("Missing required parameter 'startTime'")
        if endTime is None:
            raise ValueError("Missing required parameter 'endTime'")
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        url = f"{self.base_url}/v2/slots/available"
        query_params = {
            k: v
            for k, v in [
                ("startTime", startTime),
                ("endTime", endTime),
                ("eventTypeId", eventTypeId),
                ("eventTypeSlug", eventTypeSlug),
                ("usernameList", usernameList),
                ("duration", duration),
                ("rescheduleUid", rescheduleUid),
                ("timeZone", timeZone),
                ("orgSlug", orgSlug),
                ("slotFormat", slotFormat),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def stripe_controller_redirect(
        self,
    ) -> dict[str, Any]:
        """
        Initiates a redirect to the Stripe Connect endpoint and returns the response as a JSON dictionary.

        Returns:
            dict[str, Any]: The parsed JSON response from the Stripe Connect endpoint.

        Raises:
            HTTPError: Raised if the HTTP request to the Stripe Connect endpoint returns an unsuccessful status code.

        Tags:
            stripe, redirect, controller, api-call
        """
        url = f"{self.base_url}/v2/stripe/connect"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def stripe_controller_save(self, state, code) -> dict[str, Any]:
        """
        Saves the Stripe connection state and authorization code by making a request to the Stripe save endpoint.

        Args:
            state: The OAuth state parameter used to validate the Stripe connection (str, required).
            code: The authorization code received from Stripe after user authentication (str, required).

        Returns:
            A dictionary containing the JSON response from the Stripe save endpoint.

        Raises:
            ValueError: Raised if 'state' or 'code' is None.

        Tags:
            stripe, save, api, management
        """
        if state is None:
            raise ValueError("Missing required parameter 'state'")
        if code is None:
            raise ValueError("Missing required parameter 'code'")
        url = f"{self.base_url}/v2/stripe/save"
        query_params = {
            k: v for k, v in [("state", state), ("code", code)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def stripe_controller_check(
        self,
    ) -> dict[str, Any]:
        """
        Checks the Stripe integration status by querying the Stripe check endpoint and returns the response as a dictionary.

        Args:
            None: This function takes no arguments

        Returns:
            A dictionary containing the response data from the Stripe check endpoint.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request to the Stripe check endpoint returns an unsuccessful status code.
            requests.exceptions.RequestException: For errors during the HTTP request, such as network issues or timeouts.

        Tags:
            check, stripe, status, api
        """
        url = f"{self.base_url}/v2/stripe/check"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def stripe_controller_check_team_stripe_connection(self, teamId) -> dict[str, Any]:
        """
        Checks whether a Stripe connection exists for the specified team by making a GET request to the Stripe service endpoint.

        Args:
            teamId: str. The unique identifier of the team for which to check the Stripe connection.

        Returns:
            dict[str, Any]: The JSON response from the Stripe check endpoint containing the connection status details.

        Raises:
            ValueError: Raised if 'teamId' is None.
            requests.HTTPError: Raised if the HTTP request to the Stripe endpoint fails.

        Tags:
            check, stripe, team, api
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        url = f"{self.base_url}/v2/stripe/check/{teamId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_controller_create_team(
        self,
        name,
        slug=None,
        logoUrl=None,
        calVideoLogo=None,
        appLogo=None,
        appIconLogo=None,
        bio=None,
        hideBranding=None,
        isPrivate=None,
        hideBookATeamMember=None,
        metadata=None,
        theme=None,
        brandColor=None,
        darkBrandColor=None,
        bannerUrl=None,
        timeFormat=None,
        timeZone=None,
        weekStart=None,
        autoAcceptCreator=None,
    ) -> dict[str, Any]:
        """
        Creates a new team with the specified attributes and returns the created team's details as a dictionary.

        Args:
            name: str. The name of the team to create. Required.
            slug: str or None. Optional team slug (short identifier).
            logoUrl: str or None. Optional URL to the team's logo.
            calVideoLogo: str or None. Optional URL to the calendar video logo.
            appLogo: str or None. Optional URL to the app logo.
            appIconLogo: str or None. Optional URL to the app icon logo.
            bio: str or None. Optional biography or description of the team.
            hideBranding: bool or None. Whether to hide branding. Optional.
            isPrivate: bool or None. Whether the team is private. Optional.
            hideBookATeamMember: bool or None. Whether to hide the 'Book a Team Member' option. Optional.
            metadata: dict or None. Optional metadata for the team.
            theme: str or None. Optional theme identifier.
            brandColor: str or None. Optional brand color in hex format.
            darkBrandColor: str or None. Optional dark brand color in hex format.
            bannerUrl: str or None. Optional URL to the team's banner image.
            timeFormat: str or None. Optional preferred time format (e.g., '12h', '24h').
            timeZone: str or None. Optional primary time zone for the team.
            weekStart: str or None. Optional day the week starts on (e.g., 'Monday').
            autoAcceptCreator: bool or None. Whether to auto-accept the team creator.

        Returns:
            dict. A dictionary containing details of the newly created team as returned by the API.

        Raises:
            ValueError: If the required parameter 'name' is not provided.
            requests.HTTPError: If the API response indicates an error (non-2xx status code).

        Tags:
            create, team-management, api, important
        """
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "name": name,
            "slug": slug,
            "logoUrl": logoUrl,
            "calVideoLogo": calVideoLogo,
            "appLogo": appLogo,
            "appIconLogo": appIconLogo,
            "bio": bio,
            "hideBranding": hideBranding,
            "isPrivate": isPrivate,
            "hideBookATeamMember": hideBookATeamMember,
            "metadata": metadata,
            "theme": theme,
            "brandColor": brandColor,
            "darkBrandColor": darkBrandColor,
            "bannerUrl": bannerUrl,
            "timeFormat": timeFormat,
            "timeZone": timeZone,
            "weekStart": weekStart,
            "autoAcceptCreator": autoAcceptCreator,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/teams"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_controller_get_teams(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves a list of teams from the API using a GET request.

        Args:
            None: This function takes no arguments

        Returns:
            dict[str, Any]: The parsed JSON response containing the list of teams and associated data.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.

        Tags:
            get, teams, api-call, list, important
        """
        url = f"{self.base_url}/v2/teams"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_controller_get_team(self, teamId) -> dict[str, Any]:
        """
        Retrieves details about a specific team by its unique identifier.

        Args:
            teamId: str. The unique identifier of the team to retrieve.

        Returns:
            dict[str, Any]: A dictionary containing the team's details as returned by the API.

        Raises:
            ValueError: If the 'teamId' parameter is None.
            requests.exceptions.HTTPError: If the HTTP request to retrieve the team details fails.

        Tags:
            get, team, management, api, important
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        url = f"{self.base_url}/v2/teams/{teamId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_controller_update_team(
        self,
        teamId,
        name=None,
        slug=None,
        logoUrl=None,
        calVideoLogo=None,
        appLogo=None,
        appIconLogo=None,
        bio=None,
        hideBranding=None,
        isPrivate=None,
        hideBookATeamMember=None,
        metadata=None,
        theme=None,
        brandColor=None,
        darkBrandColor=None,
        bannerUrl=None,
        timeFormat=None,
        timeZone=None,
        weekStart=None,
        bookingLimits=None,
        includeManagedEventsInLimits=None,
    ) -> dict[str, Any]:
        """
        Updates the details of an existing team with the provided attributes.

        Args:
            teamId: str. The unique identifier of the team to update. Required.
            name: str, optional. The display name for the team.
            slug: str, optional. URL-friendly team identifier.
            logoUrl: str, optional. URL of the team's primary logo.
            calVideoLogo: str, optional. URL of the team's logo for calendar video integrations.
            appLogo: str, optional. URL of the team's logo for app displays.
            appIconLogo: str, optional. URL of the team's icon logo for apps.
            bio: str, optional. Text description or biography for the team.
            hideBranding: bool, optional. Whether to hide all branding for the team.
            isPrivate: bool, optional. Whether the team is private.
            hideBookATeamMember: bool, optional. Whether to hide the 'Book a Team Member' option.
            metadata: dict, optional. Custom metadata associated with the team.
            theme: str, optional. Identifier or configuration for the team's visual theme.
            brandColor: str, optional. Hex color code for the default brand color.
            darkBrandColor: str, optional. Hex color code for the brand color in dark mode.
            bannerUrl: str, optional. URL for the team's banner image.
            timeFormat: str, optional. Preferred time display format (e.g., '24h' or '12h').
            timeZone: str, optional. Default time zone for the team.
            weekStart: str, optional. Day of the week the team's calendar should start on.
            bookingLimits: dict, optional. Limits on bookings for the team.
            includeManagedEventsInLimits: bool, optional. Whether managed events are included in booking limits.

        Returns:
            dict[str, Any]: A dictionary containing the updated team details as returned by the backend API.

        Raises:
            ValueError: If 'teamId' is not provided.
            requests.HTTPError: If the API request fails or returns an error response.

        Tags:
            update, team, management, api, patch
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        request_body = {
            "name": name,
            "slug": slug,
            "logoUrl": logoUrl,
            "calVideoLogo": calVideoLogo,
            "appLogo": appLogo,
            "appIconLogo": appIconLogo,
            "bio": bio,
            "hideBranding": hideBranding,
            "isPrivate": isPrivate,
            "hideBookATeamMember": hideBookATeamMember,
            "metadata": metadata,
            "theme": theme,
            "brandColor": brandColor,
            "darkBrandColor": darkBrandColor,
            "bannerUrl": bannerUrl,
            "timeFormat": timeFormat,
            "timeZone": timeZone,
            "weekStart": weekStart,
            "bookingLimits": bookingLimits,
            "includeManagedEventsInLimits": includeManagedEventsInLimits,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/teams/{teamId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_controller_delete_team(self, teamId) -> dict[str, Any]:
        """
        Deletes a team by its unique identifier using an HTTP DELETE request.

        Args:
            teamId: The unique identifier of the team to be deleted. Must not be None.

        Returns:
            A dictionary containing the response data from the API upon successful deletion of the team.

        Raises:
            ValueError: If 'teamId' is None.
            requests.HTTPError: If the HTTP request fails or the response status code indicates an error.

        Tags:
            delete, team-management, api
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        url = f"{self.base_url}/v2/teams/{teamId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_event_types_controller_create_team_event_type(
        self,
        teamId,
        lengthInMinutes,
        lengthInMinutesOptions,
        title,
        slug,
        schedulingType,
        hosts,
        description=None,
        locations=None,
        bookingFields=None,
        disableGuests=None,
        slotInterval=None,
        minimumBookingNotice=None,
        beforeEventBuffer=None,
        afterEventBuffer=None,
        scheduleId=None,
        bookingLimitsCount=None,
        onlyShowFirstAvailableSlot=None,
        bookingLimitsDuration=None,
        bookingWindow=None,
        offsetStart=None,
        bookerLayouts=None,
        confirmationPolicy=None,
        recurrence=None,
        requiresBookerEmailVerification=None,
        hideCalendarNotes=None,
        lockTimeZoneToggleOnBookingPage=None,
        color=None,
        seats=None,
        customName=None,
        destinationCalendar=None,
        useDestinationCalendarEmail=None,
        hideCalendarEventDetails=None,
        successRedirectUrl=None,
        assignAllTeamMembers=None,
    ) -> dict[str, Any]:
        """
        Creates a new team event type by sending a POST request with the specified configuration parameters.

        Args:
            teamId: str. Unique identifier of the team for which the event type is being created.
            lengthInMinutes: int. Default duration of the event in minutes.
            lengthInMinutesOptions: list[int]. List of allowed event durations (in minutes).
            title: str. Title of the event type.
            slug: str. URL-friendly unique string identifier for the event type.
            schedulingType: str. The method or policy by which the event can be scheduled.
            hosts: list[str] or list[int]. Identifiers of team members who will host the event.
            description: str, optional. Description of the event type.
            locations: list[dict] or None, optional. Possible locations for the event.
            bookingFields: list[dict] or None, optional. Additional custom fields required during booking.
            disableGuests: bool or None, optional. Whether to disable guest addition for the event.
            slotInterval: int or None, optional. Interval in minutes between possible time slots.
            minimumBookingNotice: int or None, optional. Minimum notice (in minutes) required to book the event.
            beforeEventBuffer: int or None, optional. Buffer time (in minutes) before the event.
            afterEventBuffer: int or None, optional. Buffer time (in minutes) after the event.
            scheduleId: str or None, optional. Identifier of the associated schedule.
            bookingLimitsCount: int or None, optional. Maximum number of bookings allowed.
            onlyShowFirstAvailableSlot: bool or None, optional. Show only the first available slot to bookers.
            bookingLimitsDuration: int or None, optional. Booking window duration limit.
            bookingWindow: int or None, optional. Number of days in advance users can book.
            offsetStart: int or None, optional. Offset (in minutes) applied to the event’s start time.
            bookerLayouts: list[dict] or None, optional. Custom layouts for booker-facing forms.
            confirmationPolicy: dict or None, optional. Policies governing booking confirmations.
            recurrence: dict or None, optional. Recurrence rules for repeated bookings.
            requiresBookerEmailVerification: bool or None, optional. Whether email verification is required for bookers.
            hideCalendarNotes: bool or None, optional. Whether to hide calendar notes from bookers.
            lockTimeZoneToggleOnBookingPage: bool or None, optional. Lock the time zone toggle on the booking page.
            color: str or None, optional. Color code associated with the event type.
            seats: int or None, optional. Maximum number of seats available per event.
            customName: str or None, optional. Custom label or name for the event type.
            destinationCalendar: str or None, optional. Calendar to which bookings should be added.
            useDestinationCalendarEmail: bool or None, optional. Use calendar email as booking reference.
            hideCalendarEventDetails: bool or None, optional. Hide calendar event details from participants.
            successRedirectUrl: str or None, optional. Redirect URL after successful booking.
            assignAllTeamMembers: bool or None, optional. Assign all current team members as hosts.

        Returns:
            dict[str, Any]: The JSON response from the server containing details of the created event type.

        Raises:
            ValueError: Raised if any of the required parameters ('teamId', 'lengthInMinutes', 'lengthInMinutesOptions', 'title', 'slug', 'schedulingType', or 'hosts') are missing or None.
            HTTPError: Raised if the HTTP request to create the event type fails with an error response from the server.

        Tags:
            create, event-type, team, api, management
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if lengthInMinutes is None:
            raise ValueError("Missing required parameter 'lengthInMinutes'")
        if lengthInMinutesOptions is None:
            raise ValueError("Missing required parameter 'lengthInMinutesOptions'")
        if title is None:
            raise ValueError("Missing required parameter 'title'")
        if slug is None:
            raise ValueError("Missing required parameter 'slug'")
        if schedulingType is None:
            raise ValueError("Missing required parameter 'schedulingType'")
        if hosts is None:
            raise ValueError("Missing required parameter 'hosts'")
        request_body = {
            "lengthInMinutes": lengthInMinutes,
            "lengthInMinutesOptions": lengthInMinutesOptions,
            "title": title,
            "slug": slug,
            "description": description,
            "locations": locations,
            "bookingFields": bookingFields,
            "disableGuests": disableGuests,
            "slotInterval": slotInterval,
            "minimumBookingNotice": minimumBookingNotice,
            "beforeEventBuffer": beforeEventBuffer,
            "afterEventBuffer": afterEventBuffer,
            "scheduleId": scheduleId,
            "bookingLimitsCount": bookingLimitsCount,
            "onlyShowFirstAvailableSlot": onlyShowFirstAvailableSlot,
            "bookingLimitsDuration": bookingLimitsDuration,
            "bookingWindow": bookingWindow,
            "offsetStart": offsetStart,
            "bookerLayouts": bookerLayouts,
            "confirmationPolicy": confirmationPolicy,
            "recurrence": recurrence,
            "requiresBookerEmailVerification": requiresBookerEmailVerification,
            "hideCalendarNotes": hideCalendarNotes,
            "lockTimeZoneToggleOnBookingPage": lockTimeZoneToggleOnBookingPage,
            "color": color,
            "seats": seats,
            "customName": customName,
            "destinationCalendar": destinationCalendar,
            "useDestinationCalendarEmail": useDestinationCalendarEmail,
            "hideCalendarEventDetails": hideCalendarEventDetails,
            "successRedirectUrl": successRedirectUrl,
            "schedulingType": schedulingType,
            "hosts": hosts,
            "assignAllTeamMembers": assignAllTeamMembers,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/teams/{teamId}/event-types"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_event_types_controller_get_team_event_types(
        self, teamId, eventSlug=None
    ) -> dict[str, Any]:
        """
        Retrieves event type details for a specified team, optionally filtering by event slug.

        Args:
            teamId: Unique identifier of the team for which to retrieve event types. Must not be None.
            eventSlug: Optional slug to filter event types by a specific event. Defaults to None.

        Returns:
            Dictionary containing event type details for the specified team, as parsed from the API response JSON.

        Raises:
            ValueError: If 'teamId' is not provided (None).
            requests.HTTPError: If the HTTP request to the event types endpoint returns an unsuccessful status code.

        Tags:
            get, list, event-types, team, api
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        url = f"{self.base_url}/v2/teams/{teamId}/event-types"
        query_params = {k: v for k, v in [("eventSlug", eventSlug)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_event_types_controller_get_team_event_type(
        self, teamId, eventTypeId
    ) -> dict[str, Any]:
        """
        Retrieves details of a specific event type for a given team.

        Args:
            teamId: str. Unique identifier of the team whose event type is to be retrieved.
            eventTypeId: str. Unique identifier of the event type to retrieve.

        Returns:
            dict. A dictionary containing details of the specified event type.

        Raises:
            ValueError: Raised if 'teamId' or 'eventTypeId' is None.
            HTTPError: Raised if the request to the API endpoint returns an unsuccessful status code.

        Tags:
            get, event-type, team, api, management
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        url = f"{self.base_url}/v2/teams/{teamId}/event-types/{eventTypeId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_event_types_controller_delete_team_event_type(
        self, teamId, eventTypeId
    ) -> dict[str, Any]:
        """
        Deletes an event type from a specified team using the given team and event type IDs.

        Args:
            teamId: The unique identifier of the team from which the event type will be deleted.
            eventTypeId: The unique identifier of the event type to delete from the team.

        Returns:
            A dictionary containing the API response data as parsed from JSON.

        Raises:
            ValueError: Raised if either 'teamId' or 'eventTypeId' parameters are not provided.
            HTTPError: Raised if the HTTP request fails or the server responds with an error status code.

        Tags:
            delete, event-type, team-management, api
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        url = f"{self.base_url}/v2/teams/{teamId}/event-types/{eventTypeId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_event_types_controller_create_phone_call(
        self,
        teamId,
        eventTypeId,
        yourPhoneNumber,
        numberToCall,
        calApiKey,
        enabled,
        templateType,
        schedulerName=None,
        guestName=None,
        guestEmail=None,
        guestCompany=None,
        beginMessage=None,
        generalPrompt=None,
    ) -> dict[str, Any]:
        """
        Creates a new phone call event type for a specific team and event type by sending a POST request with the provided call and template details.

        Args:
            teamId: str. Unique identifier of the team for which the phone call event type is being created.
            eventTypeId: str. Unique identifier of the event type under which the phone call is created.
            yourPhoneNumber: str. Phone number to initiate the call from.
            numberToCall: str. Phone number to be called.
            calApiKey: str. API key for the Cal service to authorize the call.
            enabled: bool. Whether this phone call event type is enabled.
            templateType: str. The type of template used for the call.
            schedulerName: Optional[str]. Name of the scheduler initiating the call.
            guestName: Optional[str]. Name of the guest associated with the call.
            guestEmail: Optional[str]. Email of the guest.
            guestCompany: Optional[str]. Company name of the guest.
            beginMessage: Optional[str]. Message to play or deliver at the start of the call.
            generalPrompt: Optional[str]. General prompt or instruction for the call.

        Returns:
            dict[str, Any]: A dictionary containing the JSON response from the server with details of the created phone call event type.

        Raises:
            ValueError: If any of the required parameters (teamId, eventTypeId, yourPhoneNumber, numberToCall, calApiKey, enabled, or templateType) are missing or None.
            requests.HTTPError: If the HTTP request to the server returns an unsuccessful status code.

        Tags:
            create, event-type, phone-call, teams, api, management
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if eventTypeId is None:
            raise ValueError("Missing required parameter 'eventTypeId'")
        if yourPhoneNumber is None:
            raise ValueError("Missing required parameter 'yourPhoneNumber'")
        if numberToCall is None:
            raise ValueError("Missing required parameter 'numberToCall'")
        if calApiKey is None:
            raise ValueError("Missing required parameter 'calApiKey'")
        if enabled is None:
            raise ValueError("Missing required parameter 'enabled'")
        if templateType is None:
            raise ValueError("Missing required parameter 'templateType'")
        request_body = {
            "yourPhoneNumber": yourPhoneNumber,
            "numberToCall": numberToCall,
            "calApiKey": calApiKey,
            "enabled": enabled,
            "templateType": templateType,
            "schedulerName": schedulerName,
            "guestName": guestName,
            "guestEmail": guestEmail,
            "guestCompany": guestCompany,
            "beginMessage": beginMessage,
            "generalPrompt": generalPrompt,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/teams/{teamId}/event-types/{eventTypeId}/create-phone-call"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_memberships_controller_create_team_membership(
        self, teamId, userId, accepted=None, role=None, disableImpersonation=None
    ) -> dict[str, Any]:
        """
        Creates a membership for a user in the specified team with optional role, acceptance, and impersonation settings.

        Args:
            teamId: str. The unique identifier of the team to which the user will be added.
            userId: str. The unique identifier of the user to be added as a member to the team.
            accepted: Optional[bool]. Whether the membership is pre-accepted (if applicable).
            role: Optional[str]. The role to assign to the user within the team (e.g., 'member', 'admin').
            disableImpersonation: Optional[bool]. If True, disables impersonation capabilities for this membership.

        Returns:
            dict[str, Any]: The JSON-decoded server response representing the created team membership details.

        Raises:
            ValueError: If 'teamId' or 'userId' is None.
            requests.HTTPError: If the HTTP request fails or returns an unsuccessful status code.

        Tags:
            create, team-membership, management
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if userId is None:
            raise ValueError("Missing required parameter 'userId'")
        request_body = {
            "userId": userId,
            "accepted": accepted,
            "role": role,
            "disableImpersonation": disableImpersonation,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/teams/{teamId}/memberships"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_memberships_controller_get_team_memberships(
        self, teamId, take=None, skip=None
    ) -> dict[str, Any]:
        """
        Retrieves the list of team memberships for a specified team, supporting optional pagination.

        Args:
            teamId: str. The unique identifier of the team for which memberships are requested.
            take: Optional[int]. The maximum number of team memberships to return.
            skip: Optional[int]. The number of team memberships to skip before retrieving the results.

        Returns:
            dict[str, Any]: A dictionary containing team membership information as returned by the API.

        Raises:
            ValueError: Raised if the 'teamId' parameter is not provided.
            requests.HTTPError: Raised if the HTTP request to retrieve memberships fails (e.g., network issues, non-2xx response).

        Tags:
            list, team-memberships, management, api
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        url = f"{self.base_url}/v2/teams/{teamId}/memberships"
        query_params = {
            k: v for k, v in [("take", take), ("skip", skip)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_memberships_controller_get_team_membership(
        self, teamId, membershipId
    ) -> dict[str, Any]:
        """
        Retrieves a specific team membership's details by team and membership ID.

        Args:
            teamId: The unique identifier of the team whose membership information is to be retrieved.
            membershipId: The unique identifier of the membership within the specified team.

        Returns:
            A dictionary containing the membership details as returned from the API.

        Raises:
            ValueError: Raised if either 'teamId' or 'membershipId' is None.
            requests.HTTPError: Raised if the HTTP request to the team's membership API endpoint fails.

        Tags:
            get, team, membership, api
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if membershipId is None:
            raise ValueError("Missing required parameter 'membershipId'")
        url = f"{self.base_url}/v2/teams/{teamId}/memberships/{membershipId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_memberships_controller_update_team_membership(
        self, teamId, membershipId, accepted=None, role=None, disableImpersonation=None
    ) -> dict[str, Any]:
        """
        Updates a team membership's properties, such as acceptance status, role, or impersonation settings, for a given team and membership ID.

        Args:
            teamId: str. The unique identifier of the team whose membership is to be updated.
            membershipId: str. The unique identifier of the specific membership to update.
            accepted: Optional[bool]. Whether the membership is accepted. If None, this property is not updated.
            role: Optional[str]. The new role to assign to the membership. If None, this property is not updated.
            disableImpersonation: Optional[bool]. Whether to disable impersonation for the member. If None, this property is not updated.

        Returns:
            dict[str, Any]: The updated team membership information as a JSON-compatible dictionary.

        Raises:
            ValueError: Raised if 'teamId' or 'membershipId' parameters are missing.
            requests.HTTPError: Raised if the HTTP request to update the team membership fails.

        Tags:
            update, team-membership, management, async_job
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if membershipId is None:
            raise ValueError("Missing required parameter 'membershipId'")
        request_body = {
            "accepted": accepted,
            "role": role,
            "disableImpersonation": disableImpersonation,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/teams/{teamId}/memberships/{membershipId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def teams_memberships_controller_delete_team_membership(
        self, teamId, membershipId
    ) -> dict[str, Any]:
        """
        Deletes a specific team membership by membership and team identifiers.

        Args:
            teamId: The unique identifier of the team containing the membership to be deleted.
            membershipId: The unique identifier of the membership to delete from the team.

        Returns:
            A dictionary containing the API response data after deleting the team membership.

        Raises:
            ValueError: Raised if 'teamId' or 'membershipId' is None.
            HTTPError: Raised if the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            delete, membership-management, team, api
        """
        if teamId is None:
            raise ValueError("Missing required parameter 'teamId'")
        if membershipId is None:
            raise ValueError("Missing required parameter 'membershipId'")
        url = f"{self.base_url}/v2/teams/{teamId}/memberships/{membershipId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def timezones_controller_get_time_zones(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves the list of available time zones from the API.

        Args:
            None: This function takes no arguments

        Returns:
            dict: A dictionary containing time zone information as returned by the API.

        Raises:
            HTTPError: If the API request fails or returns an unsuccessful HTTP status code.

        Tags:
            get, timezones, api, list
        """
        url = f"{self.base_url}/v2/timezones"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def webhooks_controller_create_webhook(
        self, active, subscriberUrl, triggers, payloadTemplate=None, secret=None
    ) -> dict[str, Any]:
        """
        Creates a new webhook subscription with the specified configuration.

        Args:
            active: bool. Specifies whether the webhook should be active upon creation.
            subscriberUrl: str. The URL to which webhook events will be delivered.
            triggers: list. The list of event triggers that will invoke the webhook.
            payloadTemplate: str or None. Optional JSON template for customizing the event payload. Defaults to None.
            secret: str or None. Optional secret for signing webhook payloads. Defaults to None.

        Returns:
            dict. A dictionary containing the created webhook's details as returned by the API.

        Raises:
            ValueError: Raised if any required parameter ('active', 'subscriberUrl', or 'triggers') is missing.
            requests.HTTPError: Raised if the webhook creation request fails with an HTTP error status.

        Tags:
            create, webhook, management, api
        """
        if active is None:
            raise ValueError("Missing required parameter 'active'")
        if subscriberUrl is None:
            raise ValueError("Missing required parameter 'subscriberUrl'")
        if triggers is None:
            raise ValueError("Missing required parameter 'triggers'")
        request_body = {
            "payloadTemplate": payloadTemplate,
            "active": active,
            "subscriberUrl": subscriberUrl,
            "triggers": triggers,
            "secret": secret,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/webhooks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def webhooks_controller_get_webhooks(self, take=None, skip=None) -> dict[str, Any]:
        """
        Retrieves a list of registered webhooks from the API with optional pagination parameters.

        Args:
            take: Optional; int. The maximum number of webhooks to retrieve. If None, the API default is used.
            skip: Optional; int. The number of webhooks to skip from the beginning of the list. If None, no webhooks are skipped.

        Returns:
            dict[str, Any]: A dictionary containing the list of webhooks and related metadata as returned by the API.

        Raises:
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an error status code.

        Tags:
            list, webhooks, get, api, batch
        """
        url = f"{self.base_url}/v2/webhooks"
        query_params = {
            k: v for k, v in [("take", take), ("skip", skip)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def webhooks_controller_update_webhook(
        self,
        webhookId,
        payloadTemplate=None,
        active=None,
        subscriberUrl=None,
        triggers=None,
        secret=None,
    ) -> dict[str, Any]:
        """
        Updates the specified webhook's configuration with provided parameters.

        Args:
            webhookId: str. Unique identifier of the webhook to update. Required.
            payloadTemplate: Optional[str]. Custom payload template to use for webhook requests.
            active: Optional[bool]. Specifies whether the webhook should be active.
            subscriberUrl: Optional[str]. URL to which the webhook sends notifications.
            triggers: Optional[list]. List of events that trigger the webhook.
            secret: Optional[str]. Secret key used for webhook security validation.

        Returns:
            dict[str, Any]: A dictionary containing the updated webhook's details as returned by the API.

        Raises:
            ValueError: Raised if 'webhookId' is None.
            requests.HTTPError: Raised if the underlying HTTP request fails (non-2XX response).

        Tags:
            update, webhook, management, api
        """
        if webhookId is None:
            raise ValueError("Missing required parameter 'webhookId'")
        request_body = {
            "payloadTemplate": payloadTemplate,
            "active": active,
            "subscriberUrl": subscriberUrl,
            "triggers": triggers,
            "secret": secret,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/webhooks/{webhookId}"
        query_params = {}
        response = self._patch(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def webhooks_controller_get_webhook(self, webhookId) -> dict[str, Any]:
        """
        Retrieves details of a specific webhook using its unique identifier.

        Args:
            webhookId: The unique identifier (str) of the webhook to retrieve. Must not be None.

        Returns:
            A dictionary containing the webhook's details as returned by the server.

        Raises:
            ValueError: If 'webhookId' is None.
            requests.HTTPError: If the HTTP request to retrieve the webhook fails.

        Tags:
            get, webhook, fetch, api
        """
        if webhookId is None:
            raise ValueError("Missing required parameter 'webhookId'")
        url = f"{self.base_url}/v2/webhooks/{webhookId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def webhooks_controller_delete_webhook(self, webhookId) -> dict[str, Any]:
        """
        Deletes a webhook by its unique identifier.

        Args:
            webhookId: str. The unique identifier of the webhook to be deleted.

        Returns:
            dict. The response from the server as a JSON-decoded dictionary containing information about the deleted webhook.

        Raises:
            ValueError: If 'webhookId' is None.
            requests.HTTPError: If the HTTP request to delete the webhook fails.

        Tags:
            delete, webhook, management
        """
        if webhookId is None:
            raise ValueError("Missing required parameter 'webhookId'")
        url = f"{self.base_url}/v2/webhooks/{webhookId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.cal_provider_controller_verify_client_id,
            self.cal_provider_controller_verify_access_token,
            self.gcal_controller_redirect,
            self.gcal_controller_save,
            self.gcal_controller_check,
            self.oauth_client_users_controller_get_managed_users,
            self.oauth_client_users_controller_create_user,
            self.oauth_client_users_controller_get_user_by_id,
            self.oauth_client_users_controller_update_user,
            self.oauth_client_users_controller_delete_user,
            self.oauth_client_users_controller_force_refresh,
            self.oauth_flow_controller_refresh_tokens,
            self.oauth_client_webhooks_controller_create_oauth_client_webhook,
            self.oauth_client_webhooks_controller_get_oauth_client_webhooks,
            self.oauth_client_webhooks_controller_delete_all_oauth_client_webhooks,
            self.oauth_client_webhooks_controller_update_oauth_client_webhook,
            self.oauth_client_webhooks_controller_get_oauth_client_webhook,
            self.oauth_client_webhooks_controller_delete_oauth_client_webhook,
            self.organizations_attributes_controller_get_organization_attributes,
            self.organizations_attributes_controller_create_organization_attribute,
            self.organizations_attributes_controller_get_organization_attribute,
            self.organizations_attributes_controller_update_organization_attribute,
            self.organizations_attributes_controller_delete_organization_attribute,
            self.organizations_options_attributes_controller_create_organization_attribute_option,
            self.organizations_options_attributes_controller_get_organization_attribute_options,
            self.organizations_options_attributes_controller_delete_organization_attribute_option,
            self.organizations_options_attributes_controller_update_organization_attribute_option,
            self.organizations_options_attributes_controller_assign_organization_attribute_option_to_user,
            self.organizations_options_attributes_controller_get_organization_attribute_options_for_user,
            self.organizations_options_attributes_controller_unassign_organization_attribute_option_from_user,
            self.organizations_event_types_controller_create_team_event_type,
            self.organizations_event_types_controller_get_team_event_types,
            self.organizations_event_types_controller_get_team_event_type,
            self.organizations_event_types_controller_create_phone_call,
            self.organizations_event_types_controller_get_teams_event_types,
            self.organizations_memberships_controller_get_all_memberships,
            self.organizations_memberships_controller_create_membership,
            self.organizations_memberships_controller_get_org_membership,
            self.organizations_memberships_controller_delete_membership,
            self.organizations_memberships_controller_update_membership,
            self.organizations_schedules_controller_get_organization_schedules,
            self.organizations_schedules_controller_create_user_schedule,
            self.organizations_schedules_controller_get_user_schedules,
            self.organizations_schedules_controller_get_user_schedule,
            self.organizations_schedules_controller_update_user_schedule,
            self.organizations_schedules_controller_delete_user_schedule,
            self.organizations_teams_controller_get_all_teams,
            self.organizations_teams_controller_create_team,
            self.organizations_teams_controller_get_my_teams,
            self.organizations_teams_controller_get_team,
            self.organizations_teams_controller_delete_team,
            self.organizations_teams_controller_update_team,
            self.organizations_teams_memberships_controller_get_all_org_team_memberships,
            self.organizations_teams_memberships_controller_create_org_team_membership,
            self.organizations_teams_memberships_controller_get_org_team_membership,
            self.organizations_teams_memberships_controller_delete_org_team_membership,
            self.organizations_teams_memberships_controller_update_org_team_membership,
            self.organizations_teams_schedules_controller_get_user_schedules,
            self.organizations_users_controller_get_organizations_users,
            self.organizations_users_controller_create_organization_user,
            self.organizations_users_controller_delete_organization_user,
            self.organizations_webhooks_controller_get_all_organization_webhooks,
            self.organizations_webhooks_controller_create_organization_webhook,
            self.organizations_webhooks_controller_get_organization_webhook,
            self.organizations_webhooks_controller_delete_webhook,
            self.organizations_webhooks_controller_update_org_webhook,
            self.bookings_controller_2024_08_13_get_bookings,
            self.bookings_controller_2024_08_13_get_booking,
            self.bookings_controller_2024_08_13_reschedule_booking,
            self.bookings_controller_2024_08_13_cancel_booking,
            self.bookings_controller_2024_08_13_mark_no_show,
            self.bookings_controller_2024_08_13_reassign_booking,
            self.bookings_controller_2024_08_13_reassign_booking_to_user,
            self.bookings_controller_2024_08_13_confirm_booking,
            self.bookings_controller_2024_08_13_decline_booking,
            self.calendars_controller_create_ics_feed,
            self.calendars_controller_check_ics_feed,
            self.calendars_controller_get_busy_times,
            self.calendars_controller_get_calendars,
            self.calendars_controller_redirect,
            self.calendars_controller_save,
            self.calendars_controller_sync_credentials,
            self.calendars_controller_check,
            self.calendars_controller_delete_calendar_credentials,
            self.conferencing_controller_connect,
            self.conferencing_controller_redirect,
            self.conferencing_controller_save,
            self.conferencing_controller_list_installed_conferencing_apps,
            self.conferencing_controller_default,
            self.conferencing_controller_get_default,
            self.conferencing_controller_disconnect,
            self.destination_calendars_controller_update_destination_calendars,
            self.event_types_controller_2024_06_14_get_event_types,
            self.event_types_controller_2024_06_14_get_event_type_by_id,
            self.event_types_controller_2024_06_14_delete_event_type,
            self.event_type_webhooks_controller_create_event_type_webhook,
            self.event_type_webhooks_controller_get_event_type_webhooks,
            self.event_type_webhooks_controller_delete_all_event_type_webhooks,
            self.event_type_webhooks_controller_update_event_type_webhook,
            self.event_type_webhooks_controller_get_event_type_webhook,
            self.event_type_webhooks_controller_delete_event_type_webhook,
            self.me_controller_get_me,
            self.me_controller_update_me,
            self.schedules_controller_2024_06_11_create_schedule,
            self.schedules_controller_2024_06_11_get_schedules,
            self.schedules_controller_2024_06_11_get_default_schedule,
            self.schedules_controller_2024_06_11_get_schedule,
            self.schedules_controller_2024_06_11_update_schedule,
            self.schedules_controller_2024_06_11_delete_schedule,
            self.selected_calendars_controller_add_selected_calendar,
            self.selected_calendars_controller_remove_selected_calendar,
            self.slots_controller_reserve_slot,
            self.slots_controller_delete_selected_slot,
            self.slots_controller_get_available_slots,
            self.stripe_controller_redirect,
            self.stripe_controller_save,
            self.stripe_controller_check,
            self.stripe_controller_check_team_stripe_connection,
            self.teams_controller_create_team,
            self.teams_controller_get_teams,
            self.teams_controller_get_team,
            self.teams_controller_update_team,
            self.teams_controller_delete_team,
            self.teams_event_types_controller_create_team_event_type,
            self.teams_event_types_controller_get_team_event_types,
            self.teams_event_types_controller_get_team_event_type,
            self.teams_event_types_controller_delete_team_event_type,
            self.teams_event_types_controller_create_phone_call,
            self.teams_memberships_controller_create_team_membership,
            self.teams_memberships_controller_get_team_memberships,
            self.teams_memberships_controller_get_team_membership,
            self.teams_memberships_controller_update_team_membership,
            self.teams_memberships_controller_delete_team_membership,
            self.timezones_controller_get_time_zones,
            self.webhooks_controller_create_webhook,
            self.webhooks_controller_get_webhooks,
            self.webhooks_controller_update_webhook,
            self.webhooks_controller_get_webhook,
            self.webhooks_controller_delete_webhook,
        ]
