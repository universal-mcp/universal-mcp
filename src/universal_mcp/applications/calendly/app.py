from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class CalendlyApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        """
        Initializes a new instance of the Calendly API application with the specified integration and additional configuration options.

        Args:
            integration: An optional Integration object to associate with the Calendly API application. Defaults to None.
            **kwargs: Arbitrary keyword arguments that are passed to the superclass initializer for additional configuration.

        Returns:
            None
        """
        super().__init__(name="calendly", integration=integration, **kwargs)
        self.base_url = "https://api.calendly.com"

    def list_event_invitees(
        self, uuid, status=None, sort=None, email=None, page_token=None, count=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of invitees for a specific scheduled event, optionally filtered and paginated by status, email, sorting order, and paging parameters.

        Args:
            uuid: str. The unique identifier of the scheduled event for which to list invitees.
            status: Optional[str]. Filter invitees by their invitation status (e.g., accepted, declined, pending).
            sort: Optional[str]. Sorting order of the invitees list (e.g., by name or date).
            email: Optional[str]. Filter invitees by their email address.
            page_token: Optional[str]. A token indicating the page of results to retrieve for pagination.
            count: Optional[int]. The maximum number of invitees to return per page.

        Returns:
            dict[str, Any]: A dictionary containing the list of event invitees and pagination details, as returned by the API.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/scheduled_events/{uuid}/invitees"
        query_params = {
            k: v
            for k, v in [
                ("status", status),
                ("sort", sort),
                ("email", email),
                ("page_token", page_token),
                ("count", count),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_event(self, uuid) -> dict[str, Any]:
        """
        Retrieves the details of a scheduled event given its UUID.

        Args:
            uuid: str. The unique identifier of the scheduled event to retrieve.

        Returns:
            dict[str, Any]: A dictionary containing the scheduled event details as returned by the API.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/scheduled_events/{uuid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_event_invitee(self, event_uuid, invitee_uuid) -> dict[str, Any]:
        """
        Retrieves details about a specific invitee for a given scheduled event.

        Args:
            event_uuid: The unique identifier of the scheduled event.
            invitee_uuid: The unique identifier of the invitee to retrieve.

        Returns:
            A dictionary containing invitee details as returned by the API.
        """
        if event_uuid is None:
            raise ValueError("Missing required parameter 'event_uuid'")
        if invitee_uuid is None:
            raise ValueError("Missing required parameter 'invitee_uuid'")
        url = f"{self.base_url}/scheduled_events/{event_uuid}/invitees/{invitee_uuid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_events(
        self,
        user=None,
        organization=None,
        invitee_email=None,
        status=None,
        sort=None,
        min_start_time=None,
        max_start_time=None,
        page_token=None,
        count=None,
        group=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of scheduled events filtered by optional user, organization, invitee email, status, date range, sorting, and pagination criteria.

        Args:
            user: Optional[str]: The user identifier to filter events by a specific user.
            organization: Optional[str]: The organization identifier to filter events by a specific organization.
            invitee_email: Optional[str]: The email address of the invitee to filter events.
            status: Optional[str]: The status to filter events (e.g., 'scheduled', 'cancelled').
            sort: Optional[str]: Sorting criteria for the events (e.g., by start time).
            min_start_time: Optional[str]: Minimum start time (ISO 8601 format) to filter events.
            max_start_time: Optional[str]: Maximum start time (ISO 8601 format) to filter events.
            page_token: Optional[str]: Token for fetching the next page of results.
            count: Optional[int]: The maximum number of events to return.
            group: Optional[str]: Group identifier to filter events by group.

        Returns:
            dict[str, Any]: A dictionary containing the list of scheduled events and associated metadata.
        """
        url = f"{self.base_url}/scheduled_events"
        query_params = {
            k: v
            for k, v in [
                ("user", user),
                ("organization", organization),
                ("invitee_email", invitee_email),
                ("status", status),
                ("sort", sort),
                ("min_start_time", min_start_time),
                ("max_start_time", max_start_time),
                ("page_token", page_token),
                ("count", count),
                ("group", group),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_event_type(self, uuid) -> dict[str, Any]:
        """
        Retrieves the event type details for the specified UUID from the API.

        Args:
            uuid: str. The unique identifier of the event type to retrieve.

        Returns:
            dict. A dictionary containing the event type details as returned by the API.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/event_types/{uuid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_user_sevent_types(
        self,
        active=None,
        organization=None,
        user=None,
        user_availability_schedule=None,
        sort=None,
        admin_managed=None,
        page_token=None,
        count=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of user event types with optional filtering, sorting, and pagination parameters.

        Args:
            active: Optional; filter event types by active status (bool or compatible).
            organization: Optional; filter event types by organization identifier.
            user: Optional; filter event types by user identifier.
            user_availability_schedule: Optional; filter by user availability schedule identifier.
            sort: Optional; comma-separated string or list for sorting results.
            admin_managed: Optional; filter event types managed by an admin (bool or compatible).
            page_token: Optional; token for paginating through result pages.
            count: Optional; maximum number of event types to return.

        Returns:
            A dictionary containing the list of user event types and associated pagination or metadata information.
        """
        url = f"{self.base_url}/event_types"
        query_params = {
            k: v
            for k, v in [
                ("active", active),
                ("organization", organization),
                ("user", user),
                ("user_availability_schedule", user_availability_schedule),
                ("sort", sort),
                ("admin_managed", admin_managed),
                ("page_token", page_token),
                ("count", count),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_user(self, uuid) -> dict[str, Any]:
        """
        Retrieves detailed user information for a given UUID from the remote API.

        Args:
            uuid: The unique identifier (UUID) of the user to retrieve.

        Returns:
            A dictionary containing the user's details as returned by the API.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/users/{uuid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_current_user(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves information about the currently authenticated user from the API.

        Args:
            self: Instance of the class containing API connection details and HTTP methods.

        Returns:
            A dictionary containing the current user's information as returned by the API.
        """
        url = f"{self.base_url}/users/me"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_organization_invitations(
        self, uuid, count=None, page_token=None, sort=None, email=None, status=None
    ) -> dict[str, Any]:
        """
        Retrieves a paginated list of invitations for a specified organization, with optional filtering and sorting.

        Args:
            uuid: str. Unique identifier of the organization whose invitations are to be listed.
            count: Optional[int]. Maximum number of invitations to return per page.
            page_token: Optional[str]. Token indicating the page of results to retrieve.
            sort: Optional[str]. Sorting criteria for the invitations (e.g., by date or status).
            email: Optional[str]. Filter invitations sent to a specific email address.
            status: Optional[str]. Filter invitations by their status (e.g., pending, accepted, expired).

        Returns:
            dict[str, Any]: A dictionary containing the list of organization invitations and pagination information.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/organizations/{uuid}/invitations"
        query_params = {
            k: v
            for k, v in [
                ("count", count),
                ("page_token", page_token),
                ("sort", sort),
                ("email", email),
                ("status", status),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def invite_user_to_organization(self, uuid, email=None) -> dict[str, Any]:
        """
        Sends an invitation to a specified email address to join an organization identified by its UUID.

        Args:
            uuid: str. The unique identifier of the organization to which the user is being invited.
            email: Optional[str]. The email address of the user to invite. If None, the invite is created without an email.

        Returns:
            dict[str, Any]. A dictionary containing the JSON response from the API after sending the invitation.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        request_body = {
            "email": email,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/organizations/{uuid}/invitations"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_organization_invitation(self, org_uuid, uuid) -> dict[str, Any]:
        """
        Retrieves a specific invitation for an organization using its unique identifiers.

        Args:
            org_uuid: str. The unique identifier of the organization whose invitation is to be retrieved.
            uuid: str. The unique identifier of the invitation to fetch.

        Returns:
            dict. A dictionary containing the invitation details as returned by the API.
        """
        if org_uuid is None:
            raise ValueError("Missing required parameter 'org_uuid'")
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/organizations/{org_uuid}/invitations/{uuid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def revoke_user_sorganization_invitation(self, org_uuid, uuid) -> Any:
        """
        Revokes a user's invitation to an organization by deleting the specified invitation resource.

        Args:
            org_uuid: The unique identifier of the organization from which the user's invitation will be revoked.
            uuid: The unique identifier of the invitation to be revoked.

        Returns:
            The JSON response from the API after successfully revoking the invitation.
        """
        if org_uuid is None:
            raise ValueError("Missing required parameter 'org_uuid'")
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/organizations/{org_uuid}/invitations/{uuid}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_organization_membership(self, uuid) -> dict[str, Any]:
        """
        Retrieves the membership information for a specified organization membership UUID.

        Args:
            uuid: str. The unique identifier of the organization membership to retrieve.

        Returns:
            dict. A dictionary containing the organization membership details as returned by the API.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/organization_memberships/{uuid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def remove_user_from_organization(self, uuid) -> Any:
        """
        Removes a user from the organization by deleting their membership using the specified UUID.

        Args:
            uuid: str. The unique identifier of the organization membership to remove.

        Returns:
            dict. The response data from the organization membership removal request.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/organization_memberships/{uuid}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_organization_memberships(
        self, page_token=None, count=None, email=None, organization=None, user=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of organization memberships, optionally filtered by pagination, email, organization, or user parameters.

        Args:
            page_token: Optional; A string token to specify the page of results to retrieve for pagination.
            count: Optional; An integer specifying the maximum number of memberships to return.
            email: Optional; A string to filter memberships by user email address.
            organization: Optional; A string to filter memberships by organization identifier.
            user: Optional; A string to filter memberships by user identifier.

        Returns:
            A dictionary containing the organization membership data returned by the API.
        """
        url = f"{self.base_url}/organization_memberships"
        query_params = {
            k: v
            for k, v in [
                ("page_token", page_token),
                ("count", count),
                ("email", email),
                ("organization", organization),
                ("user", user),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_webhook_subscription(self, webhook_uuid) -> dict[str, Any]:
        """
        Retrieves the details of a webhook subscription identified by its UUID.

        Args:
            webhook_uuid: The unique identifier (UUID) of the webhook subscription to retrieve.

        Returns:
            A dictionary containing the webhook subscription details as returned by the API.
        """
        if webhook_uuid is None:
            raise ValueError("Missing required parameter 'webhook_uuid'")
        url = f"{self.base_url}/webhook_subscriptions/{webhook_uuid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_webhook_subscription(self, webhook_uuid) -> Any:
        """
        Deletes a webhook subscription identified by its UUID.

        Args:
            webhook_uuid: The unique identifier (UUID) of the webhook subscription to delete.

        Returns:
            The JSON-decoded response from the server after deleting the webhook subscription.
        """
        if webhook_uuid is None:
            raise ValueError("Missing required parameter 'webhook_uuid'")
        url = f"{self.base_url}/webhook_subscriptions/{webhook_uuid}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_webhook_subscriptions(
        self,
        organization=None,
        user=None,
        page_token=None,
        count=None,
        sort=None,
        scope=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of webhook subscriptions, optionally filtered and paginated based on input criteria.

        Args:
            organization: Optional; str or None. Identifier of the organization to filter subscriptions by organization.
            user: Optional; str or None. Identifier of the user to filter subscriptions created by a specific user.
            page_token: Optional; str or None. Token to retrieve a specific page of results for pagination.
            count: Optional; int or None. Maximum number of subscriptions to return in the response.
            sort: Optional; str or None. Sorting order for the returned subscriptions.
            scope: Optional; str or None. Scope to filter webhook subscriptions.

        Returns:
            dict: A dictionary containing the list of webhook subscriptions matching the query parameters and any associated metadata (e.g., paging info).
        """
        url = f"{self.base_url}/webhook_subscriptions"
        query_params = {
            k: v
            for k, v in [
                ("organization", organization),
                ("user", user),
                ("page_token", page_token),
                ("count", count),
                ("sort", sort),
                ("scope", scope),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_webhook_subscription(
        self,
        events=None,
        group=None,
        organization=None,
        scope=None,
        signing_key=None,
        url=None,
        user=None,
    ) -> dict[str, Any]:
        """
        Creates a new webhook subscription with the specified parameters and returns the subscription details as a dictionary.

        Args:
            events: Optional[list[str]]; A list of event names that will trigger the webhook.
            group: Optional[str]; The group identifier to which the webhook is scoped.
            organization: Optional[str]; The organization identifier for the webhook subscription.
            scope: Optional[str]; The scope within which the webhook is active.
            signing_key: Optional[str]; The key used to sign webhook payloads for verification.
            url: Optional[str]; The URL endpoint to which the webhook events will be delivered.
            user: Optional[str]; The user identifier associated with this webhook subscription.

        Returns:
            dict[str, Any]: A dictionary containing the details of the created webhook subscription as returned by the API.
        """
        request_body = {
            "events": events,
            "group": group,
            "organization": organization,
            "scope": scope,
            "signing_key": signing_key,
            "url": url,
            "user": user,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/webhook_subscriptions"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_single_use_scheduling_link(
        self, max_event_count=None, owner=None, owner_type=None
    ) -> dict[str, Any]:
        """
        Creates a single-use scheduling link by sending a POST request with optional restrictions.

        Args:
            max_event_count: Optional; int or None. The maximum number of events that can be scheduled using the link.
            owner: Optional; str or None. The identifier for the owner of the scheduling link.
            owner_type: Optional; str or None. The type of the owner (e.g., 'user', 'team').

        Returns:
            dict[str, Any]: The response data from the scheduling link creation API as a dictionary.
        """
        request_body = {
            "max_event_count": max_event_count,
            "owner": owner,
            "owner_type": owner_type,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/scheduling_links"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_invitee_data(self, emails=None) -> dict[str, Any]:
        """
        Deletes invitee data for the specified email addresses by sending a POST request to the data compliance API.

        Args:
            emails: Optional list of email addresses (list[str] or None) to identify the invitees whose data should be deleted. If None, no emails are included in the request.

        Returns:
            A dictionary containing the JSON response from the API indicating the result of the deletion request.
        """
        request_body = {
            "emails": emails,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/data_compliance/deletion/invitees"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_scheduled_event_data(
        self, end_time=None, start_time=None
    ) -> dict[str, Any]:
        """
        Deletes scheduled event data within the specified time range by sending a deletion request to the data compliance service.

        Args:
            end_time: Optional; The end of the time interval for which scheduled event data should be deleted. If None, no upper bound is set.
            start_time: Optional; The start of the time interval for which scheduled event data should be deleted. If None, no lower bound is set.

        Returns:
            A dictionary containing the response from the data compliance deletion endpoint.
        """
        request_body = {
            "end_time": end_time,
            "start_time": start_time,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/data_compliance/deletion/events"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_invitee_no_show(self, uuid) -> dict[str, Any]:
        """
        Retrieves details about an invitee who did not show up for a scheduled event, identified by a unique UUID.

        Args:
            uuid: The unique identifier (UUID) of the invitee no-show to retrieve.

        Returns:
            A dictionary containing details of the invitee no-show record.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/invitee_no_shows/{uuid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_invitee_no_show(self, uuid) -> Any:
        """
        Deletes an invitee no-show record identified by the given UUID.

        Args:
            uuid: The unique identifier (UUID) of the invitee no-show to delete. Must not be None.

        Returns:
            The response data as a JSON object after successfully deleting the invitee no-show record.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/invitee_no_shows/{uuid}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_invitee_no_show(self, invitee=None) -> dict[str, Any]:
        """
        Creates an invitee no-show record by sending a POST request to the invitee_no_shows endpoint.

        Args:
            invitee: Optional; information about the invitee to be included in the request body. If None, the invitee field is omitted.

        Returns:
            A dictionary containing the server's JSON response to the creation request.
        """
        request_body = {
            "invitee": invitee,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/invitee_no_shows"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_group(self, uuid) -> dict[str, Any]:
        """
        Retrieves information for a group identified by its UUID from the server.

        Args:
            uuid: The unique identifier (UUID) of the group to retrieve.

        Returns:
            A dictionary containing the group's details as returned by the server.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/groups/{uuid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_groups(
        self, organization=None, page_token=None, count=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of groups from the API, optionally filtered by organization and paginated using a page token and count.

        Args:
            organization: Optional; a string specifying the organization to filter the groups by.
            page_token: Optional; a string token indicating the page of results to retrieve for pagination.
            count: Optional; an integer specifying the maximum number of groups to return.

        Returns:
            A dictionary containing the JSON response from the API with the list of groups and any relevant pagination details.
        """
        url = f"{self.base_url}/groups"
        query_params = {
            k: v
            for k, v in [
                ("organization", organization),
                ("page_token", page_token),
                ("count", count),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_group_relationship(self, uuid) -> dict[str, Any]:
        """
        Retrieves the relationship information for a group specified by UUID from the API.

        Args:
            uuid: The unique identifier (UUID) of the group whose relationship data is to be retrieved.

        Returns:
            A dictionary containing the group relationship information as returned by the API.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/group_relationships/{uuid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_group_relationships(
        self, count=None, page_token=None, organization=None, owner=None, group=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of group relationships from the server, optionally filtered by pagination and various group ownership parameters.

        Args:
            count: Optional; Maximum number of records to retrieve. Used for pagination.
            page_token: Optional; Token indicating the page of results to retrieve. Used for pagination.
            organization: Optional; Filter relationships to a specific organization.
            owner: Optional; Filter relationships by the owner's identifier.
            group: Optional; Filter relationships by the group's identifier.

        Returns:
            A dictionary containing the JSON response from the server, typically including metadata and a list of group relationships.
        """
        url = f"{self.base_url}/group_relationships"
        query_params = {
            k: v
            for k, v in [
                ("count", count),
                ("page_token", page_token),
                ("organization", organization),
                ("owner", owner),
                ("group", group),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_routing_form(self, uuid) -> dict[str, Any]:
        """
        Retrieves a routing form by its unique identifier from the server.

        Args:
            uuid: The unique identifier of the routing form to retrieve.

        Returns:
            A dictionary representing the routing form data retrieved from the server.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/routing_forms/{uuid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_routing_forms(
        self, organization=None, count=None, page_token=None, sort=None
    ) -> dict[str, Any]:
        """
        Retrieves a paginated list of routing forms from the API, optionally filtered and sorted by organization, count, page token, or sort order.

        Args:
            organization: Optional[str]. The organization identifier to filter the routing forms by. If None, no filtering by organization is applied.
            count: Optional[int]. The maximum number of routing forms to return. If None, the default API pagination size is used.
            page_token: Optional[str]. A token indicating the page of results to retrieve for pagination. If None, retrieves the first page.
            sort: Optional[str]. The sorting order to apply to the results. If None, uses the API's default sorting.

        Returns:
            dict[str, Any]: A dictionary containing the list of routing forms and associated metadata as provided by the API response.
        """
        url = f"{self.base_url}/routing_forms"
        query_params = {
            k: v
            for k, v in [
                ("organization", organization),
                ("count", count),
                ("page_token", page_token),
                ("sort", sort),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_routing_form_submission(self, uuid) -> dict[str, Any]:
        """
        Retrieves a routing form submission by its unique identifier (UUID) from the configured API endpoint.

        Args:
            uuid: The unique identifier of the routing form submission to retrieve. Must not be None.

        Returns:
            A dictionary containing the routing form submission data retrieved from the API.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/routing_form_submissions/{uuid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_routing_form_submissions(
        self, form=None, count=None, page_token=None, sort=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of routing form submissions, optionally filtered and paginated based on provided parameters.

        Args:
            form: Optional; the identifier of the form to filter submissions by (default is None).
            count: Optional; the maximum number of submissions to return (default is None).
            page_token: Optional; token for pagination to retrieve the next set of results (default is None).
            sort: Optional; sorting preference for the submissions (default is None).

        Returns:
            A dictionary containing the retrieved routing form submissions and related metadata.
        """
        url = f"{self.base_url}/routing_form_submissions"
        query_params = {
            k: v
            for k, v in [
                ("form", form),
                ("count", count),
                ("page_token", page_token),
                ("sort", sort),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_event_type_available_times(
        self, event_type=None, start_time=None, end_time=None
    ) -> dict[str, Any]:
        """
        Retrieves available times for a specified event type within an optional date and time range.

        Args:
            event_type: Optional; the type of event to filter available times for. If None, retrieves times for all event types.
            start_time: Optional; the earliest datetime to include in the results, in an accepted string or datetime format. If None, no lower bound is applied.
            end_time: Optional; the latest datetime to include in the results, in an accepted string or datetime format. If None, no upper bound is applied.

        Returns:
            A dictionary containing the available times for the specified event type within the given range, as returned by the API.
        """
        url = f"{self.base_url}/event_type_available_times"
        query_params = {
            k: v
            for k, v in [
                ("event_type", event_type),
                ("start_time", start_time),
                ("end_time", end_time),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_activity_log_entries(
        self,
        organization=None,
        search_term=None,
        actor=None,
        sort=None,
        min_occurred_at=None,
        max_occurred_at=None,
        page_token=None,
        count=None,
        namespace=None,
        action=None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of activity log entries with optional filtering, sorting, and pagination.

        Args:
            organization: Optional; organization identifier to filter log entries by a specific organization.
            search_term: Optional; term to search for in the activity log entries.
            actor: Optional; filter results by the user or entity that performed the action.
            sort: Optional; sorting order for the results (e.g., ascending or descending by a field).
            min_occurred_at: Optional; ISO 8601 timestamp to filter entries that occurred after this date and time.
            max_occurred_at: Optional; ISO 8601 timestamp to filter entries that occurred before this date and time.
            page_token: Optional; token for paginating through large result sets.
            count: Optional; maximum number of entries to return.
            namespace: Optional; filter results by a specific namespace.
            action: Optional; filter results by a specific action performed.

        Returns:
            A dictionary containing a list of activity log entries and any associated pagination metadata.
        """
        url = f"{self.base_url}/activity_log_entries"
        query_params = {
            k: v
            for k, v in [
                ("organization", organization),
                ("search_term", search_term),
                ("actor", actor),
                ("sort", sort),
                ("min_occurred_at", min_occurred_at),
                ("max_occurred_at", max_occurred_at),
                ("page_token", page_token),
                ("count", count),
                ("namespace", namespace),
                ("action", action),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_share(
        self,
        availability_rule=None,
        duration=None,
        end_date=None,
        event_type=None,
        hide_location=None,
        location_configurations=None,
        max_booking_time=None,
        name=None,
        period_type=None,
        start_date=None,
    ) -> dict[str, Any]:
        """
        Creates a new share with the specified configuration parameters by making a POST request to the shares API endpoint.

        Args:
            availability_rule: Optional; rule defining the availability for the share.
            duration: Optional; duration of the event or booking in minutes.
            end_date: Optional; end date for the share's availability.
            event_type: Optional; type of event associated with the share.
            hide_location: Optional; whether to hide the location details.
            location_configurations: Optional; configuration details for one or more locations.
            max_booking_time: Optional; maximum allowable booking time in minutes.
            name: Optional; name of the share.
            period_type: Optional; type of period (e.g., recurring, single).
            start_date: Optional; start date for the share's availability.

        Returns:
            A dictionary containing the JSON response from the API with details of the created share.
        """
        request_body = {
            "availability_rule": availability_rule,
            "duration": duration,
            "end_date": end_date,
            "event_type": event_type,
            "hide_location": hide_location,
            "location_configurations": location_configurations,
            "max_booking_time": max_booking_time,
            "name": name,
            "period_type": period_type,
            "start_date": start_date,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/shares"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_user_busy_times(
        self, user=None, start_time=None, end_time=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of busy time intervals for a specified user within an optional date range.

        Args:
            user: Optional; The identifier of the user whose busy times are to be listed. If None, retrieves busy times for all users.
            start_time: Optional; The start of the time range (ISO 8601 format). Only busy times starting at or after this time are included. If None, no lower bound is applied.
            end_time: Optional; The end of the time range (ISO 8601 format). Only busy times ending before or at this time are included. If None, no upper bound is applied.

        Returns:
            A dictionary containing the user's busy time intervals and related metadata as returned by the API.
        """
        url = f"{self.base_url}/user_busy_times"
        query_params = {
            k: v
            for k, v in [
                ("user", user),
                ("start_time", start_time),
                ("end_time", end_time),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_user_availability_schedule(self, uuid) -> dict[str, Any]:
        """
        Retrieves the availability schedule for a user identified by the given UUID.

        Args:
            uuid: str. The UUID of the user whose availability schedule is to be retrieved.

        Returns:
            dict[str, Any]: A dictionary containing the user's availability schedule as returned by the API.
        """
        if uuid is None:
            raise ValueError("Missing required parameter 'uuid'")
        url = f"{self.base_url}/user_availability_schedules/{uuid}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_user_availability_schedules(self, user=None) -> dict[str, Any]:
        """
        Retrieves a list of user availability schedules from the API, optionally filtering by a specific user.

        Args:
            user: Optional; a string representing the user identifier to filter the availability schedules. If None, schedules for all users are retrieved.

        Returns:
            A dictionary containing the availability schedules returned by the API.
        """
        url = f"{self.base_url}/user_availability_schedules"
        query_params = {k: v for k, v in [("user", user)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_event_type_hosts(
        self, event_type=None, count=None, page_token=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of event type hosts based on provided filter, count, and pagination parameters.

        Args:
            event_type: Optional; a string specifying the event type to filter hosts by.
            count: Optional; an integer indicating the maximum number of hosts to return.
            page_token: Optional; a string token to retrieve the next page of results for pagination.

        Returns:
            A dictionary containing the JSON response with event type hosts data, which may include host details and pagination information.
        """
        url = f"{self.base_url}/event_type_memberships"
        query_params = {
            k: v
            for k, v in [
                ("event_type", event_type),
                ("count", count),
                ("page_token", page_token),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_one_off_event_type(
        self,
        co_hosts=None,
        date_setting=None,
        duration=None,
        host=None,
        location=None,
        name=None,
        timezone=None,
    ) -> dict[str, Any]:
        """
        Creates a one-off event type with specified parameters and returns the created event type details.

        Args:
            co_hosts: Optional; a list or identifier(s) representing additional hosts for the event.
            date_setting: Optional; the date configuration for the event (e.g., specific date, date range, or recurrence settings).
            duration: Optional; the length of the event, typically in minutes.
            host: Optional; the main host or organizer of the event.
            location: Optional; the location information for the event (e.g., physical address or online meeting link).
            name: Optional; the name or title of the event.
            timezone: Optional; the timezone in which the event will take place.

        Returns:
            A dictionary containing the details of the created one-off event type as returned by the API.
        """
        request_body = {
            "co_hosts": co_hosts,
            "date_setting": date_setting,
            "duration": duration,
            "host": host,
            "location": location,
            "name": name,
            "timezone": timezone,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/one_off_event_types"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_sample_webhook_data(
        self, event=None, organization=None, user=None, scope=None
    ) -> dict[str, Any]:
        """
        Retrieves sample webhook data from the API using optional filtering parameters.

        Args:
            event: Optional; a string specifying the event type to filter the webhook data.
            organization: Optional; a string representing the organization identifier to filter the data.
            user: Optional; a string identifying the user to filter the webhook data.
            scope: Optional; a string indicating the scope to filter the webhook data.

        Returns:
            A dictionary containing the JSON response with sample webhook data from the API.
        """
        url = f"{self.base_url}/sample_webhook_data"
        query_params = {
            k: v
            for k, v in [
                ("event", event),
                ("organization", organization),
                ("user", user),
                ("scope", scope),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        """
        Returns a list of method references for various event, user, group, organization, and webhook operations supported by this instance.

        Args:
            None: This method does not accept any parameters.

        Returns:
            List of callable method references available on this instance for performing event, user, group, organization, and webhook operations.
        """
        return [
            self.list_event_invitees,
            self.get_event,
            self.get_event_invitee,
            self.list_events,
            self.get_event_type,
            self.list_user_sevent_types,
            self.get_user,
            self.get_current_user,
            self.list_organization_invitations,
            self.invite_user_to_organization,
            self.get_organization_invitation,
            self.revoke_user_sorganization_invitation,
            self.get_organization_membership,
            self.remove_user_from_organization,
            self.list_organization_memberships,
            self.get_webhook_subscription,
            self.delete_webhook_subscription,
            self.list_webhook_subscriptions,
            self.create_webhook_subscription,
            self.create_single_use_scheduling_link,
            self.delete_invitee_data,
            self.delete_scheduled_event_data,
            self.get_invitee_no_show,
            self.delete_invitee_no_show,
            self.create_invitee_no_show,
            self.get_group,
            self.list_groups,
            self.get_group_relationship,
            self.list_group_relationships,
            self.get_routing_form,
            self.list_routing_forms,
            self.get_routing_form_submission,
            self.list_routing_form_submissions,
            self.list_event_type_available_times,
            self.list_activity_log_entries,
            self.create_share,
            self.list_user_busy_times,
            self.get_user_availability_schedule,
            self.list_user_availability_schedules,
            self.list_event_type_hosts,
            self.create_one_off_event_type,
            self.get_sample_webhook_data,
        ]
