from base64 import b64encode
from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class GongApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="gong", integration=integration, **kwargs)
        self.base_url = "https://api.gong.io"

    def _get_headers(self) -> dict[str, str]:
        credentials = self.integration.get_credentials()
        api_key = credentials.get("api_key")
        secret = credentials.get("secret")
        api_key_b64 = b64encode(f"{api_key}:{secret}".encode()).decode()
        return {
            "Authorization": f"Basic {api_key_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def list_calls(
        self, fromDateTime, toDateTime, cursor=None, workspaceId=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of call records within the specified date range, with optional pagination and workspace filtering.

        Args:
            fromDateTime: The start datetime (ISO 8601 string) for filtering calls. Required.
            toDateTime: The end datetime (ISO 8601 string) for filtering calls. Required.
            cursor: An optional pagination cursor to fetch the next page of results.
            workspaceId: An optional identifier to filter calls by a specific workspace.

        Returns:
            A dictionary containing the list of call records and associated metadata. The exact structure depends on the API response.

        Raises:
            ValueError: If either 'fromDateTime' or 'toDateTime' is not provided.
            requests.HTTPError: If the underlying HTTP request fails or the API response contains an HTTP error status.

        Tags:
            list, calls, fetch, pagination, management, important
        """
        if fromDateTime is None:
            raise ValueError("Missing required parameter 'fromDateTime'")
        if toDateTime is None:
            raise ValueError("Missing required parameter 'toDateTime'")
        url = f"{self.base_url}/v2/calls"
        query_params = {
            k: v
            for k, v in [
                ("fromDateTime", fromDateTime),
                ("toDateTime", toDateTime),
                ("workspaceId", workspaceId),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_call(
        self,
        clientUniqueId,
        actualStart,
        parties,
        direction,
        primaryUser,
        title=None,
        purpose=None,
        scheduledStart=None,
        scheduledEnd=None,
        duration=None,
        disposition=None,
        context=None,
        customData=None,
        speakersTimeline=None,
        meetingUrl=None,
        callProviderCode=None,
        downloadMediaUrl=None,
        workspaceId=None,
        languageCode=None,
    ) -> dict[str, Any]:
        """
        Creates and submits a new call record with detailed metadata to the remote service.

        Args:
            clientUniqueId: str. A unique identifier for the client associated with the call. Required.
            actualStart: str or datetime. The actual start time of the call. Required.
            parties: list or dict. Information about the call participants. Required.
            direction: str. Indicates call direction (e.g., 'inbound', 'outbound'). Required.
            primaryUser: str. The main user associated with the call. Required.
            title: str, optional. Title or subject of the call.
            purpose: str, optional. The purpose or reason for the call.
            scheduledStart: str or datetime, optional. The scheduled start time of the call.
            scheduledEnd: str or datetime, optional. The scheduled end time of the call.
            duration: int, optional. Duration of the call in seconds.
            disposition: str, optional. Final status or outcome of the call.
            context: dict, optional. Additional contextual information about the call.
            customData: dict, optional. Custom key-value data associated with the call.
            speakersTimeline: list, optional. Timeline of speakers during the call.
            meetingUrl: str, optional. URL for the associated meeting, if applicable.
            callProviderCode: str, optional. Identifier for the call provider.
            downloadMediaUrl: str, optional. URL to download call media.
            workspaceId: str, optional. Identifier for the workspace to associate the call with.
            languageCode: str, optional. Language code for the call content (e.g., 'en-US').

        Returns:
            dict[str, Any]: JSON response representing the created call record from the remote service.

        Raises:
            ValueError: If any of the required parameters ('clientUniqueId', 'actualStart', 'parties', 'direction', or 'primaryUser') are missing.
            HTTPError: If the remote service returns an unsuccessful status code during the call creation request.

        Tags:
            add, call, management, api, important
        """
        if clientUniqueId is None:
            raise ValueError("Missing required parameter 'clientUniqueId'")
        if actualStart is None:
            raise ValueError("Missing required parameter 'actualStart'")
        if parties is None:
            raise ValueError("Missing required parameter 'parties'")
        if direction is None:
            raise ValueError("Missing required parameter 'direction'")
        if primaryUser is None:
            raise ValueError("Missing required parameter 'primaryUser'")
        request_body = {
            "clientUniqueId": clientUniqueId,
            "title": title,
            "purpose": purpose,
            "scheduledStart": scheduledStart,
            "scheduledEnd": scheduledEnd,
            "actualStart": actualStart,
            "duration": duration,
            "parties": parties,
            "direction": direction,
            "disposition": disposition,
            "context": context,
            "customData": customData,
            "speakersTimeline": speakersTimeline,
            "meetingUrl": meetingUrl,
            "callProviderCode": callProviderCode,
            "downloadMediaUrl": downloadMediaUrl,
            "workspaceId": workspaceId,
            "languageCode": languageCode,
            "primaryUser": primaryUser,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/calls"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_call(self, id) -> dict[str, Any]:
        """
        Retrieves details for a specific call by its identifier.

        Args:
            id: The unique identifier of the call to retrieve. Must not be None.

        Returns:
            A dictionary containing the call details as returned by the API.

        Raises:
            ValueError: If the 'id' parameter is None.
            requests.HTTPError: If the HTTP request to the API fails.

        Tags:
            get, call, api, management, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v2/calls/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_calls_extensive(
        self, filter, cursor=None, contentSelector=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of extensive call records matching the specified filter criteria, with optional pagination and content selection.

        Args:
            filter: dict; Required. Specifies the filtering criteria for the call records to retrieve.
            cursor: str, optional; An optional pagination cursor to fetch the next set of results.
            contentSelector: dict or list, optional; Specifies which content fields or sections to include for each call record.

        Returns:
            dict: A dictionary containing the fetched extensive call records and any associated metadata.

        Raises:
            ValueError: Raised if the required 'filter' parameter is missing.
            requests.HTTPError: Raised if the HTTP request to the call records service fails (e.g., network error, invalid response).

        Tags:
            list, calls, fetch, filter, api, important
        """
        if filter is None:
            raise ValueError("Missing required parameter 'filter'")
        request_body = {
            "cursor": cursor,
            "filter": filter,
            "contentSelector": contentSelector,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/calls/extensive"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_permission_profile(self, profileId) -> dict[str, Any]:
        """
        Retrieve the details of a permission profile by its profile ID.

        Args:
            profileId: str. The unique identifier of the permission profile to retrieve.

        Returns:
            dict[str, Any]: The JSON-decoded response containing the permission profile details.

        Raises:
            ValueError: If the 'profileId' parameter is None.
            requests.HTTPError: If the HTTP request to the permission profile endpoint fails.

        Tags:
            get, permission-profile, fetch, api, management, important
        """
        if profileId is None:
            raise ValueError("Missing required parameter 'profileId'")
        url = f"{self.base_url}/v2/permission-profile"
        query_params = {k: v for k, v in [("profileId", profileId)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_permission_profile(
        self,
        profileId,
        id=None,
        name=None,
        description=None,
        callsAccess=None,
        libraryFolderAccess=None,
        dealsAccess=None,
        forecastPermissions=None,
        coachingAccess=None,
        insightsAccess=None,
        usageAccess=None,
        emailsAccess=None,
        scoreCalls=None,
        overrideScore=None,
        downloadCallMedia=None,
        shareCallsWithCustomers=None,
        manuallyScheduleAndUploadCalls=None,
        privateCalls=None,
        deleteCalls=None,
        trimCalls=None,
        listenInCalls=None,
        deleteEmails=None,
        callsAndSearch=None,
        library=None,
        deals=None,
        createEditAndDeleteDealsBoards=None,
        dealsInlineEditing=None,
        account=None,
        coaching=None,
        usage=None,
        teamStats=None,
        initiatives=None,
        market=None,
        activity=None,
        forecast=None,
        forecastManage=None,
        engageManageCompanyTemplates=None,
        engageManageCompanySequences=None,
        engageCreateAndManageRulesets=None,
        engageSnoozeFlowToDosForOthers=None,
        viewEngageAnalyticsActivity=None,
        viewEngageAnalyticsPerformance=None,
        viewEngageAnalyticsFlows=None,
        manageGeneralBusinessSettings=None,
        manageScorecards=None,
        exportCallsAndCoachingDataToCSV=None,
        crmDataInlineEditing=None,
        crmDataImport=None,
        viewRevenueAnalytics=None,
        manageRevenueAnalytics=None,
    ) -> dict[str, Any]:
        """
        Updates an existing permission profile with the specified access settings and permissions.

        Args:
            profileId: str. The unique identifier of the permission profile to update.
            id: Optional[str]. The new identifier for the profile (if changing).
            name: Optional[str]. The name of the permission profile.
            description: Optional[str]. The description of the permission profile.
            callsAccess: Optional[Any]. Access configuration for calls.
            libraryFolderAccess: Optional[Any]. Access controls for library folders.
            dealsAccess: Optional[Any]. Access configuration for deals.
            forecastPermissions: Optional[Any]. Permissions related to forecasting.
            coachingAccess: Optional[Any]. Access permissions for coaching features.
            insightsAccess: Optional[Any]. Access permissions for insights.
            usageAccess: Optional[Any]. Access configuration for usage data.
            emailsAccess: Optional[Any]. Access configuration for emails.
            scoreCalls: Optional[Any]. Permission to score calls.
            overrideScore: Optional[Any]. Permission to override call scores.
            downloadCallMedia: Optional[Any]. Permission to download call media.
            shareCallsWithCustomers: Optional[Any]. Permission to share calls with customers.
            manuallyScheduleAndUploadCalls: Optional[Any]. Permission to schedule and upload calls manually.
            privateCalls: Optional[Any]. Permission to mark calls as private.
            deleteCalls: Optional[Any]. Permission to delete calls.
            trimCalls: Optional[Any]. Permission to trim calls.
            listenInCalls: Optional[Any]. Permission to listen in on calls.
            deleteEmails: Optional[Any]. Permission to delete emails.
            callsAndSearch: Optional[Any]. Permissions for calls and search features.
            library: Optional[Any]. Permissions related to the content library.
            deals: Optional[Any]. Additional deals-related permissions.
            createEditAndDeleteDealsBoards: Optional[Any]. Permission to create, edit, and delete deal boards.
            dealsInlineEditing: Optional[Any]. Permission for inline editing of deals.
            account: Optional[Any]. Permissions related to account management.
            coaching: Optional[Any]. Additional coaching-related permissions.
            usage: Optional[Any]. Additional usage-related permissions.
            teamStats: Optional[Any]. Access to team statistics.
            initiatives: Optional[Any]. Permissions for initiatives management.
            market: Optional[Any]. Permissions for marketing-related features.
            activity: Optional[Any]. Access to activity data.
            forecast: Optional[Any]. General forecast permissions.
            forecastManage: Optional[Any]. Permission to manage forecasting.
            engageManageCompanyTemplates: Optional[Any]. Permission to manage company templates in Engage.
            engageManageCompanySequences: Optional[Any]. Permission to manage company sequences in Engage.
            engageCreateAndManageRulesets: Optional[Any]. Permission to create and manage Engage rulesets.
            engageSnoozeFlowToDosForOthers: Optional[Any]. Permission to snooze Flow To-Dos for others in Engage.
            viewEngageAnalyticsActivity: Optional[Any]. Permission to view Engage analytics activity.
            viewEngageAnalyticsPerformance: Optional[Any]. Permission to view Engage analytics performance data.
            viewEngageAnalyticsFlows: Optional[Any]. Permission to view Engage analytics flows.
            manageGeneralBusinessSettings: Optional[Any]. Permission to manage general business settings.
            manageScorecards: Optional[Any]. Permission to manage scorecards.
            exportCallsAndCoachingDataToCSV: Optional[Any]. Permission to export calls and coaching data to CSV.
            crmDataInlineEditing: Optional[Any]. Permission for inline editing of CRM data.
            crmDataImport: Optional[Any]. Permission to import CRM data.
            viewRevenueAnalytics: Optional[Any]. Permission to view revenue analytics.
            manageRevenueAnalytics: Optional[Any]. Permission to manage revenue analytics.

        Returns:
            dict[str, Any]: The updated permission profile as a dictionary.

        Raises:
            ValueError: If the required parameter 'profileId' is missing.
            requests.HTTPError: If the HTTP request to update the profile fails.

        Tags:
            update, permission-profile, management, important
        """
        if profileId is None:
            raise ValueError("Missing required parameter 'profileId'")
        request_body = {
            "id": id,
            "name": name,
            "description": description,
            "callsAccess": callsAccess,
            "libraryFolderAccess": libraryFolderAccess,
            "dealsAccess": dealsAccess,
            "forecastPermissions": forecastPermissions,
            "coachingAccess": coachingAccess,
            "insightsAccess": insightsAccess,
            "usageAccess": usageAccess,
            "emailsAccess": emailsAccess,
            "scoreCalls": scoreCalls,
            "overrideScore": overrideScore,
            "downloadCallMedia": downloadCallMedia,
            "shareCallsWithCustomers": shareCallsWithCustomers,
            "manuallyScheduleAndUploadCalls": manuallyScheduleAndUploadCalls,
            "privateCalls": privateCalls,
            "deleteCalls": deleteCalls,
            "trimCalls": trimCalls,
            "listenInCalls": listenInCalls,
            "deleteEmails": deleteEmails,
            "callsAndSearch": callsAndSearch,
            "library": library,
            "deals": deals,
            "createEditAndDeleteDealsBoards": createEditAndDeleteDealsBoards,
            "dealsInlineEditing": dealsInlineEditing,
            "account": account,
            "coaching": coaching,
            "usage": usage,
            "teamStats": teamStats,
            "initiatives": initiatives,
            "market": market,
            "activity": activity,
            "forecast": forecast,
            "forecastManage": forecastManage,
            "engageManageCompanyTemplates": engageManageCompanyTemplates,
            "engageManageCompanySequences": engageManageCompanySequences,
            "engageCreateAndManageRulesets": engageCreateAndManageRulesets,
            "engageSnoozeFlowToDosForOthers": engageSnoozeFlowToDosForOthers,
            "viewEngageAnalyticsActivity": viewEngageAnalyticsActivity,
            "viewEngageAnalyticsPerformance": viewEngageAnalyticsPerformance,
            "viewEngageAnalyticsFlows": viewEngageAnalyticsFlows,
            "manageGeneralBusinessSettings": manageGeneralBusinessSettings,
            "manageScorecards": manageScorecards,
            "exportCallsAndCoachingDataToCSV": exportCallsAndCoachingDataToCSV,
            "crmDataInlineEditing": crmDataInlineEditing,
            "crmDataImport": crmDataImport,
            "viewRevenueAnalytics": viewRevenueAnalytics,
            "manageRevenueAnalytics": manageRevenueAnalytics,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/permission-profile"
        query_params = {k: v for k, v in [("profileId", profileId)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_permission_profile(
        self,
        workspaceId,
        id=None,
        name=None,
        description=None,
        callsAccess=None,
        libraryFolderAccess=None,
        dealsAccess=None,
        forecastPermissions=None,
        coachingAccess=None,
        insightsAccess=None,
        usageAccess=None,
        emailsAccess=None,
        scoreCalls=None,
        overrideScore=None,
        downloadCallMedia=None,
        shareCallsWithCustomers=None,
        manuallyScheduleAndUploadCalls=None,
        privateCalls=None,
        deleteCalls=None,
        trimCalls=None,
        listenInCalls=None,
        deleteEmails=None,
        callsAndSearch=None,
        library=None,
        deals=None,
        createEditAndDeleteDealsBoards=None,
        dealsInlineEditing=None,
        account=None,
        coaching=None,
        usage=None,
        teamStats=None,
        initiatives=None,
        market=None,
        activity=None,
        forecast=None,
        forecastManage=None,
        engageManageCompanyTemplates=None,
        engageManageCompanySequences=None,
        engageCreateAndManageRulesets=None,
        engageSnoozeFlowToDosForOthers=None,
        viewEngageAnalyticsActivity=None,
        viewEngageAnalyticsPerformance=None,
        viewEngageAnalyticsFlows=None,
        manageGeneralBusinessSettings=None,
        manageScorecards=None,
        exportCallsAndCoachingDataToCSV=None,
        crmDataInlineEditing=None,
        crmDataImport=None,
        viewRevenueAnalytics=None,
        manageRevenueAnalytics=None,
    ) -> dict[str, Any]:
        """
        Creates a new permission profile in the specified workspace with customizable access and permission settings.

        Args:
            workspaceId: str. The unique identifier of the workspace where the permission profile will be created. Required.
            id: str, optional. The unique identifier for the permission profile.
            name: str, optional. The name of the permission profile.
            description: str, optional. A description for the permission profile.
            callsAccess: Any, optional. Specifies calls access permissions.
            libraryFolderAccess: Any, optional. Specifies access permissions for library folders.
            dealsAccess: Any, optional. Specifies deals access permissions.
            forecastPermissions: Any, optional. Specifies forecast related permissions.
            coachingAccess: Any, optional. Specifies coaching access permissions.
            insightsAccess: Any, optional. Specifies insights access permissions.
            usageAccess: Any, optional. Specifies usage access permissions.
            emailsAccess: Any, optional. Specifies emails access permissions.
            scoreCalls: Any, optional. Permission to score calls.
            overrideScore: Any, optional. Permission to override call scores.
            downloadCallMedia: Any, optional. Permission to download call media.
            shareCallsWithCustomers: Any, optional. Permission to share calls with customers.
            manuallyScheduleAndUploadCalls: Any, optional. Permission to manually schedule and upload calls.
            privateCalls: Any, optional. Permission to mark calls as private.
            deleteCalls: Any, optional. Permission to delete calls.
            trimCalls: Any, optional. Permission to trim calls.
            listenInCalls: Any, optional. Permission to listen to calls.
            deleteEmails: Any, optional. Permission to delete emails.
            callsAndSearch: Any, optional. Additional calls and search permissions.
            library: Any, optional. Library specific permissions.
            deals: Any, optional. Deals specific permissions.
            createEditAndDeleteDealsBoards: Any, optional. Permission to create, edit, or delete deals boards.
            dealsInlineEditing: Any, optional. Permission for inline editing of deals.
            account: Any, optional. Account management permissions.
            coaching: Any, optional. Additional coaching permissions.
            usage: Any, optional. Additional usage permissions.
            teamStats: Any, optional. Permission to view team statistics.
            initiatives: Any, optional. Permission related to initiatives.
            market: Any, optional. Permission related to market features.
            activity: Any, optional. Permission related to activity features.
            forecast: Any, optional. Permission to view forecasts.
            forecastManage: Any, optional. Permission to manage forecasts.
            engageManageCompanyTemplates: Any, optional. Permission to manage company templates for engagement.
            engageManageCompanySequences: Any, optional. Permission to manage engagement company sequences.
            engageCreateAndManageRulesets: Any, optional. Permission to create and manage engagement rulesets.
            engageSnoozeFlowToDosForOthers: Any, optional. Permission to snooze engagement to-dos for others.
            viewEngageAnalyticsActivity: Any, optional. Permission to view engagement analytics activity.
            viewEngageAnalyticsPerformance: Any, optional. Permission to view engagement analytics performance.
            viewEngageAnalyticsFlows: Any, optional. Permission to view engagement analytics flows.
            manageGeneralBusinessSettings: Any, optional. Permission to manage general business settings.
            manageScorecards: Any, optional. Permission to manage scorecards.
            exportCallsAndCoachingDataToCSV: Any, optional. Permission to export calls and coaching data to CSV.
            crmDataInlineEditing: Any, optional. Permission for inline editing of CRM data.
            crmDataImport: Any, optional. Permission to import CRM data.
            viewRevenueAnalytics: Any, optional. Permission to view revenue analytics.
            manageRevenueAnalytics: Any, optional. Permission to manage revenue analytics.

        Returns:
            dict[str, Any]: The response containing details of the created permission profile.

        Raises:
            ValueError: Raised if the required 'workspaceId' parameter is missing.
            HTTPError: Raised if the HTTP request to create the permission profile fails (e.g., due to network issues or invalid input).

        Tags:
            create, permission-profile, management, api, important
        """
        if workspaceId is None:
            raise ValueError("Missing required parameter 'workspaceId'")
        request_body = {
            "id": id,
            "name": name,
            "description": description,
            "callsAccess": callsAccess,
            "libraryFolderAccess": libraryFolderAccess,
            "dealsAccess": dealsAccess,
            "forecastPermissions": forecastPermissions,
            "coachingAccess": coachingAccess,
            "insightsAccess": insightsAccess,
            "usageAccess": usageAccess,
            "emailsAccess": emailsAccess,
            "scoreCalls": scoreCalls,
            "overrideScore": overrideScore,
            "downloadCallMedia": downloadCallMedia,
            "shareCallsWithCustomers": shareCallsWithCustomers,
            "manuallyScheduleAndUploadCalls": manuallyScheduleAndUploadCalls,
            "privateCalls": privateCalls,
            "deleteCalls": deleteCalls,
            "trimCalls": trimCalls,
            "listenInCalls": listenInCalls,
            "deleteEmails": deleteEmails,
            "callsAndSearch": callsAndSearch,
            "library": library,
            "deals": deals,
            "createEditAndDeleteDealsBoards": createEditAndDeleteDealsBoards,
            "dealsInlineEditing": dealsInlineEditing,
            "account": account,
            "coaching": coaching,
            "usage": usage,
            "teamStats": teamStats,
            "initiatives": initiatives,
            "market": market,
            "activity": activity,
            "forecast": forecast,
            "forecastManage": forecastManage,
            "engageManageCompanyTemplates": engageManageCompanyTemplates,
            "engageManageCompanySequences": engageManageCompanySequences,
            "engageCreateAndManageRulesets": engageCreateAndManageRulesets,
            "engageSnoozeFlowToDosForOthers": engageSnoozeFlowToDosForOthers,
            "viewEngageAnalyticsActivity": viewEngageAnalyticsActivity,
            "viewEngageAnalyticsPerformance": viewEngageAnalyticsPerformance,
            "viewEngageAnalyticsFlows": viewEngageAnalyticsFlows,
            "manageGeneralBusinessSettings": manageGeneralBusinessSettings,
            "manageScorecards": manageScorecards,
            "exportCallsAndCoachingDataToCSV": exportCallsAndCoachingDataToCSV,
            "crmDataInlineEditing": crmDataInlineEditing,
            "crmDataImport": crmDataImport,
            "viewRevenueAnalytics": viewRevenueAnalytics,
            "manageRevenueAnalytics": manageRevenueAnalytics,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/permission-profile"
        query_params = {
            k: v for k, v in [("workspaceId", workspaceId)] if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def update_meeting(
        self,
        meetingId,
        startTime,
        endTime,
        invitees,
        organizerEmail,
        title=None,
        externalId=None,
    ) -> dict[str, Any]:
        """
        Updates the details of an existing meeting with new information such as time, invitees, and title.

        Args:
            meetingId: str. The unique identifier of the meeting to update.
            startTime: str. The updated start time of the meeting in ISO 8601 format.
            endTime: str. The updated end time of the meeting in ISO 8601 format.
            invitees: list. The updated list of invitees' email addresses.
            organizerEmail: str. The email address of the meeting organizer.
            title: str, optional. The new title of the meeting.
            externalId: str, optional. An external identifier for the meeting.

        Returns:
            dict. A dictionary representing the updated meeting details as returned by the server.

        Raises:
            ValueError: If any of the required parameters ('meetingId', 'startTime', 'endTime', 'invitees', or 'organizerEmail') are missing.

        Tags:
            update, meeting, management, important
        """
        if meetingId is None:
            raise ValueError("Missing required parameter 'meetingId'")
        if startTime is None:
            raise ValueError("Missing required parameter 'startTime'")
        if endTime is None:
            raise ValueError("Missing required parameter 'endTime'")
        if invitees is None:
            raise ValueError("Missing required parameter 'invitees'")
        if organizerEmail is None:
            raise ValueError("Missing required parameter 'organizerEmail'")
        request_body = {
            "startTime": startTime,
            "endTime": endTime,
            "title": title,
            "invitees": invitees,
            "externalId": externalId,
            "organizerEmail": organizerEmail,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/meetings/{meetingId}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_meeting(self, meetingId, organizerEmail=None) -> dict[str, Any]:
        """
        Deletes a meeting by its ID, optionally specifying the organizer's email.

        Args:
            meetingId: str. The unique identifier for the meeting to be deleted. Must not be None.
            organizerEmail: str, optional. The email address of the meeting organizer. If provided, it is included in the deletion request.

        Returns:
            dict. The response data from the delete operation, parsed from JSON.

        Raises:
            ValueError: Raised when 'meetingId' is None.
            HTTPError: Raised if the HTTP response indicates an unsuccessful delete operation.

        Tags:
            delete, meeting, api, important
        """
        if meetingId is None:
            raise ValueError("Missing required parameter 'meetingId'")
        request_body = {
            "organizerEmail": organizerEmail,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/meetings/{meetingId}"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def content_viewed(
        self,
        reportingSystem,
        eventTimestamp,
        contentId,
        contentUrl,
        contentTitle,
        eventId=None,
        viewActionTitle=None,
        shareId=None,
        viewInfoUrl=None,
        viewer=None,
        crmContext=None,
        contentProperties=None,
        eventProperties=None,
        userAgent=None,
        mobileAppId=None,
        agentPlatform=None,
        workspaceId=None,
        trackingId=None,
        nonCompanyParticipants=None,
        moreInfoUrl=None,
        actionName=None,
        sharer=None,
        sharingMessageSubject=None,
        sharingMessageBody=None,
    ) -> Any:
        """
        Reports a content view event to the customer engagement system with detailed metadata about the event and content.

        Args:
            reportingSystem: The identifier or name of the reporting system submitting the event. Required.
            eventTimestamp: The timestamp of when the content was viewed (in ISO 8601 format or as required). Required.
            contentId: A unique identifier for the content that was viewed. Required.
            contentUrl: The URL of the content that was viewed. Required.
            contentTitle: The title of the content that was viewed. Required.
            eventId: An optional unique identifier for the event.
            viewActionTitle: An optional descriptive title of the view action.
            shareId: An optional identifier indicating the sharing context, if any.
            viewInfoUrl: An optional URL for more information about the view event.
            viewer: An optional identifier or details about the viewer.
            crmContext: Optional CRM-related context or metadata.
            contentProperties: Optional additional properties describing the content.
            eventProperties: Optional additional properties describing the event.
            userAgent: Optional user agent string from the viewer's device.
            mobileAppId: Optional identifier for the mobile application.
            agentPlatform: Optional platform or environment information.
            workspaceId: Optional identifier for the associated workspace.
            trackingId: Optional tracking identifier for analytics.
            nonCompanyParticipants: Optional list or details about non-company viewers/participants.
            moreInfoUrl: Optional URL for further details about the event.
            actionName: Optional action name describing the type of view action.
            sharer: Optional identifier or details about the person who shared the content.
            sharingMessageSubject: Optional subject line of a sharing message.
            sharingMessageBody: Optional body/content of a sharing message.

        Returns:
            A dictionary representing the JSON response from the customer engagement API, containing the outcome of the reported event.

        Raises:
            ValueError: If any required parameter (reportingSystem, eventTimestamp, contentId, contentUrl, or contentTitle) is missing.
            requests.HTTPError: If the HTTP request to the customer engagement API fails with a response error status.

        Tags:
            report, content-view, event, customer-engagement, api, http, important
        """
        if reportingSystem is None:
            raise ValueError("Missing required parameter 'reportingSystem'")
        if eventTimestamp is None:
            raise ValueError("Missing required parameter 'eventTimestamp'")
        if contentId is None:
            raise ValueError("Missing required parameter 'contentId'")
        if contentUrl is None:
            raise ValueError("Missing required parameter 'contentUrl'")
        if contentTitle is None:
            raise ValueError("Missing required parameter 'contentTitle'")
        request_body = {
            "reportingSystem": reportingSystem,
            "eventTimestamp": eventTimestamp,
            "eventId": eventId,
            "contentId": contentId,
            "contentUrl": contentUrl,
            "contentTitle": contentTitle,
            "viewActionTitle": viewActionTitle,
            "shareId": shareId,
            "viewInfoUrl": viewInfoUrl,
            "viewer": viewer,
            "crmContext": crmContext,
            "contentProperties": contentProperties,
            "eventProperties": eventProperties,
            "userAgent": userAgent,
            "mobileAppId": mobileAppId,
            "agentPlatform": agentPlatform,
            "workspaceId": workspaceId,
            "trackingId": trackingId,
            "nonCompanyParticipants": nonCompanyParticipants,
            "moreInfoUrl": moreInfoUrl,
            "actionName": actionName,
            "sharer": sharer,
            "sharingMessageSubject": sharingMessageSubject,
            "sharingMessageBody": sharingMessageBody,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/customer-engagement/content/viewed"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def content_shared(
        self,
        reportingSystem,
        eventTimestamp,
        contentId,
        contentUrl,
        contentTitle,
        eventId=None,
        shareId=None,
        shareInfoUrl=None,
        sharingMessageSubject=None,
        sharingMessageBody=None,
        sharer=None,
        recipients=None,
        crmContext=None,
        contentProperties=None,
        eventProperties=None,
        workspaceId=None,
        actionName=None,
        nonCompanyParticipants=None,
        moreInfoUrl=None,
        trackingId=None,
        mobileAppId=None,
        agentPlatform=None,
        userAgent=None,
    ) -> Any:
        """
        Reports a content sharing event to the customer engagement system with detailed metadata about the shared content, sharer, and recipients.

        Args:
            reportingSystem: Identifier of the reporting system initiating the content sharing event. Required.
            eventTimestamp: Timestamp of when the share event occurred, in ISO 8601 format. Required.
            contentId: Unique identifier of the shared content. Required.
            contentUrl: URL of the content being shared. Required.
            contentTitle: Title of the shared content. Required.
            eventId: Optional unique identifier for the share event.
            shareId: Optional unique identifier for the share action.
            shareInfoUrl: Optional URL providing more context or information about the share.
            sharingMessageSubject: Optional subject line of the sharing message.
            sharingMessageBody: Optional body text of the sharing message.
            sharer: Optional identifier or object representing the user who shared the content.
            recipients: Optional list or object representing the intended recipients of the shared content.
            crmContext: Optional metadata providing context or references for related CRM objects or processes.
            contentProperties: Optional dictionary of additional properties or attributes for the shared content.
            eventProperties: Optional dictionary of additional properties for the share event.
            workspaceId: Optional identifier for the workspace or environment of the event.
            actionName: Optional string specifying the action or event type.
            nonCompanyParticipants: Optional list of participants not affiliated with the company.
            moreInfoUrl: Optional URL for more information about the content or event.
            trackingId: Optional tracking identifier for analytics or logging.
            mobileAppId: Optional identifier of the mobile application involved, if any.
            agentPlatform: Optional platform or system used by the agent.
            userAgent: Optional user agent string describing the client device or environment.

        Returns:
            A dictionary containing the server's JSON response with the recorded event details or status.

        Raises:
            ValueError: Raised if any required parameter (reportingSystem, eventTimestamp, contentId, contentUrl, or contentTitle) is None.
            requests.HTTPError: Raised if the HTTP request to the reporting endpoint fails with a non-success status code.

        Tags:
            report, content, share, customer-engagement, event, api, important
        """
        if reportingSystem is None:
            raise ValueError("Missing required parameter 'reportingSystem'")
        if eventTimestamp is None:
            raise ValueError("Missing required parameter 'eventTimestamp'")
        if contentId is None:
            raise ValueError("Missing required parameter 'contentId'")
        if contentUrl is None:
            raise ValueError("Missing required parameter 'contentUrl'")
        if contentTitle is None:
            raise ValueError("Missing required parameter 'contentTitle'")
        request_body = {
            "reportingSystem": reportingSystem,
            "eventTimestamp": eventTimestamp,
            "eventId": eventId,
            "contentId": contentId,
            "contentUrl": contentUrl,
            "contentTitle": contentTitle,
            "shareId": shareId,
            "shareInfoUrl": shareInfoUrl,
            "sharingMessageSubject": sharingMessageSubject,
            "sharingMessageBody": sharingMessageBody,
            "sharer": sharer,
            "recipients": recipients,
            "crmContext": crmContext,
            "contentProperties": contentProperties,
            "eventProperties": eventProperties,
            "workspaceId": workspaceId,
            "actionName": actionName,
            "nonCompanyParticipants": nonCompanyParticipants,
            "moreInfoUrl": moreInfoUrl,
            "trackingId": trackingId,
            "mobileAppId": mobileAppId,
            "agentPlatform": agentPlatform,
            "userAgent": userAgent,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/customer-engagement/content/shared"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def custom_action(
        self,
        reportingSystem,
        eventTimestamp,
        eventId=None,
        contentId=None,
        contentUrl=None,
        contentTitle=None,
        actionName=None,
        eventInfoUrl=None,
        actor=None,
        crmContext=None,
        contentProperties=None,
        eventProperties=None,
        userAgent=None,
        mobileAppId=None,
        agentPlatform=None,
        workspaceId=None,
        nonCompanyParticipants=None,
        moreInfoUrl=None,
        shareId=None,
        trackingId=None,
        sharer=None,
        sharingMessageSubject=None,
        sharingMessageBody=None,
    ) -> Any:
        """
        Submits a custom customer engagement action event with detailed reporting and context information to the server.

        Args:
            reportingSystem: The identifier or name of the reporting system sending the event. Required.
            eventTimestamp: The ISO 8601 timestamp representing when the event occurred. Required.
            eventId: A unique identifier for the event. Optional.
            contentId: The ID of the related content item. Optional.
            contentUrl: The URL of the related content item. Optional.
            contentTitle: The title of the related content item. Optional.
            actionName: The name describing the action performed (e.g., 'share', 'edit'). Optional.
            eventInfoUrl: A URL providing additional information about the event. Optional.
            actor: The actor (user or system) who triggered the event. Optional.
            crmContext: CRM context or identifiers relevant to the event. Optional.
            contentProperties: A dictionary of custom properties related to the content. Optional.
            eventProperties: A dictionary of additional properties about the event. Optional.
            userAgent: The user agent string of the client device, if available. Optional.
            mobileAppId: Identifier of the mobile application, if applicable. Optional.
            agentPlatform: The platform used by the agent (e.g., 'iOS', 'Android', 'Web'). Optional.
            workspaceId: Workspace or tenant ID associated with the event. Optional.
            nonCompanyParticipants: A list of participants in the event not affiliated with the company. Optional.
            moreInfoUrl: An additional URL for more details about the event. Optional.
            shareId: The identifier for a share or sharing action. Optional.
            trackingId: Unique identifier for tracking the event. Optional.
            sharer: User or entity who performed the sharing action. Optional.
            sharingMessageSubject: Subject line of a related sharing message, if any. Optional.
            sharingMessageBody: Body of a related sharing message, if any. Optional.

        Returns:
            A JSON-decoded response from the server containing the result of the action submission.

        Raises:
            ValueError: If required parameters 'reportingSystem' or 'eventTimestamp' are missing.
            requests.HTTPError: If the server response contains an HTTP error status.

        Tags:
            report, submit, action, customer-engagement, api, important
        """
        if reportingSystem is None:
            raise ValueError("Missing required parameter 'reportingSystem'")
        if eventTimestamp is None:
            raise ValueError("Missing required parameter 'eventTimestamp'")
        request_body = {
            "reportingSystem": reportingSystem,
            "eventTimestamp": eventTimestamp,
            "eventId": eventId,
            "contentId": contentId,
            "contentUrl": contentUrl,
            "contentTitle": contentTitle,
            "actionName": actionName,
            "eventInfoUrl": eventInfoUrl,
            "actor": actor,
            "crmContext": crmContext,
            "contentProperties": contentProperties,
            "eventProperties": eventProperties,
            "userAgent": userAgent,
            "mobileAppId": mobileAppId,
            "agentPlatform": agentPlatform,
            "workspaceId": workspaceId,
            "nonCompanyParticipants": nonCompanyParticipants,
            "moreInfoUrl": moreInfoUrl,
            "shareId": shareId,
            "trackingId": trackingId,
            "sharer": sharer,
            "sharingMessageSubject": sharingMessageSubject,
            "sharingMessageBody": sharingMessageBody,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/customer-engagement/action"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_generic_crm_integration(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves a list of generic CRM integrations from the API.

        Args:
            None: This function takes no arguments

        Returns:
            dict: A dictionary representing the JSON response containing available CRM integrations.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request to the CRM integrations endpoint fails or returns an unsuccessful status code.

        Tags:
            list, crm, integration, api, important
        """
        url = f"{self.base_url}/v2/crm/integrations"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def register_generic_crm_integration(self, ownerEmail, name) -> dict[str, Any]:
        """
        Registers a generic CRM integration for a given owner email and integration name.

        Args:
            ownerEmail: str. The email address of the owner of the CRM integration. Must not be None.
            name: str. The name of the CRM integration to register. Must not be None.

        Returns:
            dict. The response data from the CRM integration registration API as a dictionary.

        Raises:
            ValueError: If 'ownerEmail' or 'name' is None.
            HTTPError: If the API request returns an unsuccessful status code.

        Tags:
            register, crm, integration, api, important
        """
        if ownerEmail is None:
            raise ValueError("Missing required parameter 'ownerEmail'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "ownerEmail": ownerEmail,
            "name": name,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/crm/integrations"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_generic_crm_integration(
        self, integrationId, clientRequestId
    ) -> dict[str, Any]:
        """
        Deletes a generic CRM integration using the provided integration and client request IDs.

        Args:
            integrationId: str. The unique identifier of the CRM integration to delete.
            clientRequestId: str. A unique client-assigned identifier for tracking the request.

        Returns:
            dict[str, Any]: The parsed JSON response from the API after attempting deletion.

        Raises:
            ValueError: If 'integrationId' or 'clientRequestId' is None.
            requests.HTTPError: If the HTTP response indicates an unsuccessful status code.

        Tags:
            delete, crm, integration, api, important
        """
        if integrationId is None:
            raise ValueError("Missing required parameter 'integrationId'")
        if clientRequestId is None:
            raise ValueError("Missing required parameter 'clientRequestId'")
        url = f"{self.base_url}/v2/crm/integrations"
        query_params = {
            k: v
            for k, v in [
                ("integrationId", integrationId),
                ("clientRequestId", clientRequestId),
            ]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_users_access_to_calls(self, callAccessList=None) -> dict[str, Any]:
        """
        Updates user access permissions for calls by sending a PUT request with the specified access list.

        Args:
            callAccessList: Optional. A list of user access configurations to be applied to calls. If None, no access list is provided.

        Returns:
            dict: The server's response as a JSON-decoded dictionary containing the result of the access update operation.

        Raises:
            HTTPError: Raised if the server returns an unsuccessful status code, indicating a failure in updating user access.

        Tags:
            update, calls, users-access, api, management, important
        """
        request_body = {
            "callAccessList": callAccessList,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/calls/users-access"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_access_to_calls(self, filter) -> dict[str, Any]:
        """
        Retrieves user access information for calls based on the provided filter criteria.

        Args:
            filter: dict. The filter criteria used to determine which users' access to calls will be retrieved. Must not be None.

        Returns:
            dict. The JSON response containing user access details matching the given filter.

        Raises:
            ValueError: If the 'filter' parameter is None.
            requests.HTTPError: If the HTTP request fails or returns an unsuccessful status code.

        Tags:
            get, calls, users-access, filter, api, important
        """
        if filter is None:
            raise ValueError("Missing required parameter 'filter'")
        request_body = {
            "filter": filter,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/calls/users-access"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_users_access_to_calls(self, callAccessList=None) -> dict[str, Any]:
        """
        Deletes a list of users' access permissions to calls.

        Args:
            callAccessList: Optional list of user access objects specifying which users' call access should be deleted. If None, no specific user access is targeted.

        Returns:
            A dictionary containing the server's response data from the delete operation.

        Raises:
            HTTPError: If the HTTP request to delete users' access fails, an HTTPError will be raised.

        Tags:
            delete, access-management, calls, important
        """
        request_body = {
            "callAccessList": callAccessList,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/calls/users-access"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_multiple_users(self, filter, cursor=None) -> dict[str, Any]:
        """
        Retrieves a list of users based on a provided filter and optional pagination cursor.

        Args:
            filter: The filter criteria for selecting users. Required.
            cursor: An optional pagination cursor indicating where to start retrieving users. Defaults to None.

        Returns:
            A dictionary containing the list of users and associated metadata in JSON format.

        Raises:
            ValueError: Raised if the required 'filter' parameter is missing.
            requests.HTTPError: Raised if the HTTP request fails or returns an error status.

        Tags:
            list, users, async_job, batch, management, important
        """
        if filter is None:
            raise ValueError("Missing required parameter 'filter'")
        request_body = {
            "cursor": cursor,
            "filter": filter,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/users/extensive"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_interaction_stats(self, filter, cursor=None) -> dict[str, Any]:
        """
        Retrieves interaction statistics based on specified filter criteria, with optional pagination support.

        Args:
            filter: The filter criteria used to select which interaction statistics to retrieve. Must not be None.
            cursor: An optional pagination cursor indicating the starting point for fetching the next set of results. Defaults to None.

        Returns:
            A dictionary containing the interaction statistics data returned by the API.

        Raises:
            ValueError: Raised if the 'filter' parameter is None.
            HTTPError: Raised if the HTTP request to the backend service fails.

        Tags:
            list, interaction-stats, api, batch, important
        """
        if filter is None:
            raise ValueError("Missing required parameter 'filter'")
        request_body = {
            "cursor": cursor,
            "filter": filter,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/stats/interaction"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_answered_scorecards(self, filter, cursor=None) -> dict[str, Any]:
        """
        Retrieves a paginated list of answered scorecards based on the provided filter criteria.

        Args:
            filter: A dictionary specifying the filtering conditions for the scorecards. This parameter is required.
            cursor: An optional string for pagination. If provided, retrieves the next page of results starting from this cursor.

        Returns:
            A dictionary containing the JSON response with the list of answered scorecards and pagination details.

        Raises:
            ValueError: Raised if the 'filter' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the scorecards endpoint returns an unsuccessful status code.

        Tags:
            list, scorecards, management, stats, paginated, important
        """
        if filter is None:
            raise ValueError("Missing required parameter 'filter'")
        request_body = {
            "cursor": cursor,
            "filter": filter,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/stats/activity/scorecards"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_multiple_users_day_by_day_activity(
        self, filter, cursor=None
    ) -> dict[str, Any]:
        """
        Retrieves day-by-day activity statistics for multiple users based on a provided filter.

        Args:
            filter: dict. The filter criteria specifying users or activity attributes to include in the statistics.
            cursor: str or None. An optional pagination cursor for retrieving the next set of results.

        Returns:
            dict: A JSON-decoded dictionary containing the day-by-day activity statistics for the matching users.

        Raises:
            ValueError: Raised if the required 'filter' parameter is not provided.
            HTTPError: Raised if the HTTP request to the server fails or returns an error status.

        Tags:
            list, activity, user-management, stats, important
        """
        if filter is None:
            raise ValueError("Missing required parameter 'filter'")
        request_body = {
            "cursor": cursor,
            "filter": filter,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/stats/activity/day-by-day"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_multiple_users_aggregate_activity(
        self, filter, cursor=None
    ) -> dict[str, Any]:
        """
        Aggregates and returns activity statistics for multiple users based on specified filters.

        Args:
            filter: dict or compatible object specifying criteria to select users and activity types for aggregation. Required.
            cursor: Optional pagination token (str) to retrieve the next page of results. Default is None.

        Returns:
            dict: A dictionary containing aggregated user activity statistics matching the specified filter and pagination settings.

        Raises:
            ValueError: Raised if the 'filter' parameter is not provided.
            requests.HTTPError: Propagated if the underlying HTTP POST request fails with an HTTP error response.

        Tags:
            list, aggregate, activity, user-management, batch, important
        """
        if filter is None:
            raise ValueError("Missing required parameter 'filter'")
        request_body = {
            "cursor": cursor,
            "filter": filter,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/stats/activity/aggregate"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_multiple_users_aggregate_by_period(
        self, filter, aggregationPeriod, cursor=None
    ) -> dict[str, Any]:
        """
        Aggregates activity statistics for multiple users over a specified period using given filter criteria.

        Args:
            filter: dict. Dictionary specifying the filtering criteria for selecting users whose activities will be aggregated.
            aggregationPeriod: str. Time period over which to aggregate user activity data (e.g., 'daily', 'weekly', 'monthly').
            cursor: Optional[str]. Pagination cursor to retrieve the next set of results; defaults to None.

        Returns:
            dict. JSON response containing the aggregated user activity statistics by the specified period.

        Raises:
            ValueError: Raised if 'filter' or 'aggregationPeriod' is None.
            HTTPError: Raised if the HTTP request to the aggregation endpoint fails.

        Tags:
            list, aggregate, activity, users, batch, important
        """
        if filter is None:
            raise ValueError("Missing required parameter 'filter'")
        if aggregationPeriod is None:
            raise ValueError("Missing required parameter 'aggregationPeriod'")
        request_body = {
            "cursor": cursor,
            "filter": filter,
            "aggregationPeriod": aggregationPeriod,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/stats/activity/aggregate-by-period"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_meeting(
        self, startTime, endTime, invitees, organizerEmail, title=None, externalId=None
    ) -> dict[str, Any]:
        """
        Creates a new meeting with the specified details and returns the server's response as a dictionary.

        Args:
            startTime: The start time of the meeting, typically in ISO 8601 format (str or datetime). Required.
            endTime: The end time of the meeting, typically in ISO 8601 format (str or datetime). Required.
            invitees: A list of invitee email addresses or attendee objects for the meeting. Required.
            organizerEmail: The email address of the meeting organizer. Required.
            title: The title or subject of the meeting. Optional.
            externalId: An optional external identifier for the meeting, used for integrations or reference. Optional.

        Returns:
            A dictionary containing the JSON response from the server with the details of the created meeting.

        Raises:
            ValueError: If any required parameter ('startTime', 'endTime', 'invitees', or 'organizerEmail') is missing.
            requests.HTTPError: If the HTTP request to create the meeting fails (e.g., due to network error or server-side issue).

        Tags:
            add, meeting, create, management, api, important
        """
        if startTime is None:
            raise ValueError("Missing required parameter 'startTime'")
        if endTime is None:
            raise ValueError("Missing required parameter 'endTime'")
        if invitees is None:
            raise ValueError("Missing required parameter 'invitees'")
        if organizerEmail is None:
            raise ValueError("Missing required parameter 'organizerEmail'")
        request_body = {
            "startTime": startTime,
            "endTime": endTime,
            "title": title,
            "invitees": invitees,
            "externalId": externalId,
            "organizerEmail": organizerEmail,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/meetings"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def integration_status(self, emails=None) -> dict[str, Any]:
        """
        Retrieves the integration status for specified email addresses via the meetings API.

        Args:
            emails: Optional sequence of email addresses (list or similar) to check integration status for. If None, integration status for all accessible users may be returned.

        Returns:
            A dictionary containing the integration status information for the given email addresses.

        Raises:
            requests.HTTPError: If the HTTP request to the integration status endpoint returns an unsuccessful status code.

        Tags:
            integration-status, status, check, api, async-job, important
        """
        request_body = {
            "emails": emails,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/meetings/integration/status"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def integration_settings(self, integrationTypeSettings) -> dict[str, Any]:
        """
        Sends integration type settings to the integration settings API endpoint and returns the server's response as a dictionary.

        Args:
            integrationTypeSettings: A dictionary or object containing the integration type settings to be submitted to the integration settings API.

        Returns:
            A dictionary containing the JSON response from the integration settings API endpoint.

        Raises:
            ValueError: Raised if 'integrationTypeSettings' is None.
            requests.HTTPError: Raised if the HTTP request to the integration settings API fails.

        Tags:
            integration-settings, submit, api, management, important
        """
        if integrationTypeSettings is None:
            raise ValueError("Missing required parameter 'integrationTypeSettings'")
        request_body = {
            "integrationTypeSettings": integrationTypeSettings,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/integration-settings"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_flows_for_prospects(self, crmProspectsIds) -> dict[str, Any]:
        """
        Fetches flow data for the specified CRM prospect IDs from the API.

        Args:
            crmProspectsIds: A list of CRM prospect IDs for which flow data should be retrieved.

        Returns:
            A dictionary containing the flow information for the provided CRM prospect IDs as returned by the API.

        Raises:
            ValueError: Raised if 'crmProspectsIds' is None.
            requests.HTTPError: Raised if the HTTP request to the API fails with a bad status code.

        Tags:
            get, flows, prospect-management, api, important
        """
        if crmProspectsIds is None:
            raise ValueError("Missing required parameter 'crmProspectsIds'")
        request_body = {
            "crmProspectsIds": crmProspectsIds,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/flows/prospects"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def assign_prospects(
        self, crmProspectsIds, flowId, flowInstanceOwnerEmail
    ) -> dict[str, Any]:
        """
        Assigns a list of CRM prospect IDs to a specified flow instance and owner via an API POST request.

        Args:
            crmProspectsIds: List of prospect IDs from the CRM to assign.
            flowId: Identifier of the target flow instance.
            flowInstanceOwnerEmail: Email address of the flow instance's owner.

        Returns:
            Dictionary containing the API response data after assigning prospects.

        Raises:
            ValueError: Raised if any of the required parameters ('crmProspectsIds', 'flowId', or 'flowInstanceOwnerEmail') is None.
            HTTPError: Raised if the API POST request returns an unsuccessful status code.

        Tags:
            assign, prospects, api, batch, important, management
        """
        if crmProspectsIds is None:
            raise ValueError("Missing required parameter 'crmProspectsIds'")
        if flowId is None:
            raise ValueError("Missing required parameter 'flowId'")
        if flowInstanceOwnerEmail is None:
            raise ValueError("Missing required parameter 'flowInstanceOwnerEmail'")
        request_body = {
            "crmProspectsIds": crmProspectsIds,
            "flowId": flowId,
            "flowInstanceOwnerEmail": flowInstanceOwnerEmail,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/flows/prospects/assign"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_digital_interaction(
        self,
        eventId,
        timestamp,
        eventType,
        content,
        sourceSystemName=None,
        sessionId=None,
        device=None,
        person=None,
        customFields=None,
        trackingId=None,
    ) -> dict[str, Any]:
        """
        Submits a digital interaction event record to the API with required metadata and content.

        Args:
            eventId: str. Unique identifier of the event. Required.
            timestamp: str. ISO 8601 formatted date/time string for when the event occurred. Required.
            eventType: str. The type/category of the digital event. Required.
            content: dict. The main content or payload of the digital interaction. Required.
            sourceSystemName: str, optional. Name of the originating system for the event.
            sessionId: str, optional. Identifier for the user's session.
            device: str, optional. Description or ID of the user's device.
            person: dict, optional. Information about the person involved in the interaction.
            customFields: dict, optional. Additional custom fields associated with the event.
            trackingId: str, optional. Identifier for tracking the event across systems.

        Returns:
            dict. Parsed JSON response from the API representing the stored digital interaction.

        Raises:
            ValueError: If any of the required parameters ('eventId', 'timestamp', 'eventType', 'content') are missing.
            requests.HTTPError: If the API response status indicates an HTTP error.

        Tags:
            add, digital-interaction, api, event, important
        """
        if eventId is None:
            raise ValueError("Missing required parameter 'eventId'")
        if timestamp is None:
            raise ValueError("Missing required parameter 'timestamp'")
        if eventType is None:
            raise ValueError("Missing required parameter 'eventType'")
        if content is None:
            raise ValueError("Missing required parameter 'content'")
        request_body = {
            "eventId": eventId,
            "timestamp": timestamp,
            "eventType": eventType,
            "sourceSystemName": sourceSystemName,
            "sessionId": sessionId,
            "device": device,
            "content": content,
            "person": person,
            "customFields": customFields,
            "trackingId": trackingId,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/digital-interaction"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def purge_phone_number(self, phoneNumber) -> dict[str, Any]:
        """
        Erases all data associated with the specified phone number via the data privacy API.

        Args:
            phoneNumber: str. The phone number for which data should be purged.

        Returns:
            dict. The JSON response from the API after requesting data erasure for the provided phone number.

        Raises:
            ValueError: If the 'phoneNumber' parameter is None.
            requests.HTTPError: If the API request fails or returns an unsuccessful status code.

        Tags:
            purge, data-privacy, erase, important
        """
        if phoneNumber is None:
            raise ValueError("Missing required parameter 'phoneNumber'")
        url = f"{self.base_url}/v2/data-privacy/erase-data-for-phone-number"
        query_params = {
            k: v for k, v in [("phoneNumber", phoneNumber)] if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def purge_email_address(self, emailAddress) -> dict[str, Any]:
        """
        Permanently erases all data associated with the specified email address from the system.

        Args:
            emailAddress: str. The email address whose data should be purged.

        Returns:
            dict[str, Any]: The JSON response from the data privacy API after the purge operation.

        Raises:
            ValueError: Raised if 'emailAddress' is None.
            requests.HTTPError: Raised if the underlying HTTP request fails or receives a non-success response status.

        Tags:
            purge, erase, data-privacy, email, important
        """
        if emailAddress is None:
            raise ValueError("Missing required parameter 'emailAddress'")
        url = f"{self.base_url}/v2/data-privacy/erase-data-for-email-address"
        query_params = {
            k: v for k, v in [("emailAddress", emailAddress)] if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_crm_schema_fields(self, integrationId, objectType) -> dict[str, Any]:
        """
        Retrieves the schema fields for a specified CRM object type associated with a given integration.

        Args:
            integrationId: str. The unique identifier of the CRM integration for which to fetch schema fields.
            objectType: str. The type of CRM object (e.g., 'contact', 'deal') whose schema fields are to be listed.

        Returns:
            dict[str, Any]: A dictionary containing the schema fields of the specified CRM object type.

        Raises:
            ValueError: If 'integrationId' or 'objectType' is None.
            requests.HTTPError: If the HTTP request to the CRM API fails.

        Tags:
            list, crm, schema, fields, integration, api, important
        """
        if integrationId is None:
            raise ValueError("Missing required parameter 'integrationId'")
        if objectType is None:
            raise ValueError("Missing required parameter 'objectType'")
        url = f"{self.base_url}/v2/crm/entity-schema"
        query_params = {
            k: v
            for k, v in [("integrationId", integrationId), ("objectType", objectType)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def upload_crm_schema_field(
        self, integrationId, objectType, items
    ) -> dict[str, Any]:
        """
        Uploads CRM entity schema fields to the integration service for the specified CRM object type.

        Args:
            integrationId: str. The identifier of the CRM integration to which the schema fields will be uploaded.
            objectType: str. The type of CRM object (e.g., 'contact', 'lead') whose schema fields are being uploaded.
            items: list. A list of schema field definitions to be uploaded for the specified CRM object type.

        Returns:
            dict. The JSON response from the integration service containing the result of the upload operation.

        Raises:
            ValueError: Raised if any of the required parameters ('integrationId', 'objectType', or 'items') are missing or None.
            requests.HTTPError: Raised if the HTTP request to the integration service fails or returns an error status.

        Tags:
            upload, crm, schema, fields, integration, important
        """
        if integrationId is None:
            raise ValueError("Missing required parameter 'integrationId'")
        if objectType is None:
            raise ValueError("Missing required parameter 'objectType'")
        if items is None:
            raise ValueError("Missing required parameter 'items'")
        request_body = items
        url = f"{self.base_url}/v2/crm/entity-schema"
        query_params = {
            k: v
            for k, v in [("integrationId", integrationId), ("objectType", objectType)]
            if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_crm_objects(
        self, integrationId, objectType, objectsCrmIds
    ) -> dict[str, Any]:
        """
        Retrieves CRM objects by their CRM IDs from a specified integration and object type.

        Args:
            integrationId: str. The unique identifier of the CRM integration. Required.
            objectType: str. The type of CRM object to retrieve (e.g., 'contact', 'deal'). Required.
            objectsCrmIds: str. Comma-separated list of CRM object IDs to fetch. Required.

        Returns:
            dict[str, Any]: A dictionary containing the retrieved CRM objects as returned by the API.

        Raises:
            ValueError: If any of 'integrationId', 'objectType', or 'objectsCrmIds' parameters are missing.

        Tags:
            get, crm, objects, integration, api, important
        """
        if integrationId is None:
            raise ValueError("Missing required parameter 'integrationId'")
        if objectType is None:
            raise ValueError("Missing required parameter 'objectType'")
        if objectsCrmIds is None:
            raise ValueError("Missing required parameter 'objectsCrmIds'")
        url = f"{self.base_url}/v2/crm/entities"
        query_params = {
            k: v
            for k, v in [
                ("integrationId", integrationId),
                ("objectType", objectType),
                ("objectsCrmIds", objectsCrmIds),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_call_transcripts(self, filter, cursor=None) -> dict[str, Any]:
        """
        Retrieves call transcripts based on the specified filter and optional pagination cursor.

        Args:
            filter: A dictionary specifying the filtering criteria to select relevant call transcripts.
            cursor: An optional string representing the pagination cursor to fetch a specific page of results.

        Returns:
            A dictionary containing the API response with the fetched call transcripts.

        Raises:
            ValueError: Raised if the required 'filter' parameter is missing.
            requests.HTTPError: Raised if the HTTP request made to retrieve call transcripts fails with a non-success status code.

        Tags:
            get, list, calls, transcripts, batch, management, important
        """
        if filter is None:
            raise ValueError("Missing required parameter 'filter'")
        request_body = {
            "cursor": cursor,
            "filter": filter,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v2/calls/transcript"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_workspaces(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves a list of all available workspaces from the API.

        Returns:
            dict[str, Any]: A dictionary containing the details of the available workspaces as returned by the API.

        Raises:
            requests.HTTPError: If the HTTP request to fetch the workspace list fails or returns an unsuccessful status code.

        Tags:
            list, workspaces, api, retrieve, important
        """
        url = f"{self.base_url}/v2/workspaces"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_users(self, cursor=None, includeAvatars=None) -> dict[str, Any]:
        """
        Retrieves a paginated list of users from the API, with optional filtering by cursor and inclusion of avatar data.

        Args:
            cursor: str or None. An optional pagination cursor to fetch the next set of users.
            includeAvatars: bool or None. Whether to include avatar data for each user in the response.

        Returns:
            dict: The JSON response from the API containing user data, typically including users and pagination information.

        Raises:
            requests.HTTPError: Raised if the HTTP request to the user listing endpoint returns an unsuccessful status code.

        Tags:
            list, users, api, management, important
        """
        url = f"{self.base_url}/v2/users"
        query_params = {
            k: v
            for k, v in [("cursor", cursor), ("includeAvatars", includeAvatars)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_user(self, id) -> dict[str, Any]:
        """
        Retrieves user information by user ID from the API.

        Args:
            id: The unique identifier of the user to retrieve.

        Returns:
            A dictionary containing user information returned by the API.

        Raises:
            ValueError: If the 'id' parameter is None.
            requests.HTTPError: If the HTTP request to the user endpoint fails with a non-2xx status code.

        Tags:
            get, user, api, fetch, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v2/users/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_user_history(self, id) -> dict[str, Any]:
        """
        Retrieves the settings history for a specific user by user ID.

        Args:
            id: The unique identifier of the user whose settings history is to be retrieved.

        Returns:
            A dictionary containing the user's settings history as returned by the API.

        Raises:
            ValueError: If the 'id' parameter is None.
            requests.HTTPError: If the HTTP request to the user settings history endpoint fails.

        Tags:
            get, user-history, fetch, api, important
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/v2/users/{id}/settings-history"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_trackers(self, workspaceId=None) -> dict[str, Any]:
        """
        Retrieves a list of trackers for the specified workspace from the API.

        Args:
            workspaceId: Optional; the ID of the workspace to filter trackers by. If None, retrieves trackers for all accessible workspaces.

        Returns:
            A dictionary containing the tracker data returned by the API.

        Raises:
            requests.HTTPError: Raised if the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            list, trackers, management, api, important
        """
        url = f"{self.base_url}/v2/settings/trackers"
        query_params = {
            k: v for k, v in [("workspaceId", workspaceId)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_scorecards(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves a list of scorecard settings from the API.

        Args:
            None: This function takes no arguments

        Returns:
            A dictionary containing the scorecard settings as returned by the API.

        Raises:
            HTTPError: If the HTTP request to the API fails or returns a non-success status code.

        Tags:
            list, scorecards, settings, api, important
        """
        url = f"{self.base_url}/v2/settings/scorecards"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_permission_profile_users(self, profileId) -> dict[str, Any]:
        """
        Retrieves a list of users associated with a specified permission profile.

        Args:
            profileId: The unique identifier of the permission profile for which to list associated users.

        Returns:
            A dictionary containing information about users assigned to the given permission profile.

        Raises:
            ValueError: Raised if the 'profileId' parameter is not provided.
            HTTPError: Raised if the HTTP request to the API endpoint fails due to an unsuccessful response status.

        Tags:
            list, permission-profile, users, management, important
        """
        if profileId is None:
            raise ValueError("Missing required parameter 'profileId'")
        url = f"{self.base_url}/v2/permission-profile/users"
        query_params = {k: v for k, v in [("profileId", profileId)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_logs(
        self, logType, fromDateTime, toDateTime=None, cursor=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of logs for the specified log type and time range, with optional cursor-based pagination.

        Args:
            logType: str. The type of logs to retrieve. Required.
            fromDateTime: str. The start date and time (ISO 8601 format) for filtering logs. Required.
            toDateTime: str or None. The end date and time (ISO 8601 format) for filtering logs. Optional.
            cursor: str or None. A pagination cursor returned from a previous call to continue fetching logs. Optional.

        Returns:
            dict. A dictionary containing the log records and pagination details as returned by the API.

        Raises:
            ValueError: If 'logType' or 'fromDateTime' is not provided.
            requests.HTTPError: If the HTTP request fails or the API returns an error status.

        Tags:
            list, logs, api, management, important
        """
        if logType is None:
            raise ValueError("Missing required parameter 'logType'")
        if fromDateTime is None:
            raise ValueError("Missing required parameter 'fromDateTime'")
        url = f"{self.base_url}/v2/logs"
        query_params = {
            k: v
            for k, v in [
                ("logType", logType),
                ("fromDateTime", fromDateTime),
                ("toDateTime", toDateTime),
                ("cursor", cursor),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_library_structure(self, workspaceId=None) -> dict[str, Any]:
        """
        Retrieves the hierarchical structure of library folders, optionally filtered by workspace ID.

        Args:
            workspaceId: Optional; a string representing the workspace identifier to filter the library folders. If None, retrieves folders across all available workspaces.

        Returns:
            A dictionary containing the JSON response with the structure of library folders.

        Raises:
            HTTPError: If the HTTP request to retrieve the library structure fails or an invalid response is received.

        Tags:
            get, library, structure, folders, management, important
        """
        url = f"{self.base_url}/v2/library/folders"
        query_params = {
            k: v for k, v in [("workspaceId", workspaceId)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_calls_in_specific_folder(self, folderId=None) -> dict[str, Any]:
        """
        Retrieves the list of calls contained within a specified folder from the remote library API.

        Args:
            folderId: Optional; The ID of the folder to filter the calls. If None, retrieves calls from the default or root folder.

        Returns:
            A dictionary containing the JSON response with the calls present in the specified folder.

        Raises:
            requests.HTTPError: If the HTTP request to the remote API fails or returns an unsuccessful status code.

        Tags:
            get, list, calls, folder, api, management, important
        """
        url = f"{self.base_url}/v2/library/folder-content"
        query_params = {k: v for k, v in [("folderId", folderId)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_flows(
        self, flowOwnerEmail, cursor=None, workspaceId=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of flows owned by the specified user, with optional pagination and workspace filtering.

        Args:
            flowOwnerEmail: str. The email address of the owner whose flows are to be listed. Required.
            cursor: str or None. A cursor for pagination to retrieve the next set of results. Optional.
            workspaceId: str or None. The workspace identifier to filter flows by workspace. Optional.

        Returns:
            dict. The JSON response from the API containing flow details and pagination information.

        Raises:
            ValueError: If 'flowOwnerEmail' is not provided.
            requests.HTTPError: If the API request fails or returns a non-successful status.

        Tags:
            list, flows, management, api, important
        """
        if flowOwnerEmail is None:
            raise ValueError("Missing required parameter 'flowOwnerEmail'")
        url = f"{self.base_url}/v2/flows"
        query_params = {
            k: v
            for k, v in [
                ("flowOwnerEmail", flowOwnerEmail),
                ("cursor", cursor),
                ("workspaceId", workspaceId),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def find_all_references_to_phone_number(self, phoneNumber) -> dict[str, Any]:
        """
        Fetches all references to a specified phone number from the data privacy API.

        Args:
            phoneNumber: str. The phone number for which to find all associated references. Must not be None.

        Returns:
            dict[str, Any]: A dictionary containing all data references associated with the provided phone number.

        Raises:
            ValueError: If the 'phoneNumber' parameter is None.
            HTTPError: If the HTTP request to the data privacy API fails, e.g., due to network issues or a non-2xx response.

        Tags:
            find, list, phone-number, data-privacy, reference, important
        """
        if phoneNumber is None:
            raise ValueError("Missing required parameter 'phoneNumber'")
        url = f"{self.base_url}/v2/data-privacy/data-for-phone-number"
        query_params = {
            k: v for k, v in [("phoneNumber", phoneNumber)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def find_all_references_to_email_address(self, emailAddress) -> dict[str, Any]:
        """
        Finds and returns all data references associated with a given email address.

        Args:
            emailAddress: str. The email address for which to search for data references.

        Returns:
            dict[str, Any]: A dictionary containing all data references related to the specified email address, as returned by the API.

        Raises:
            ValueError: If 'emailAddress' is None.
            HTTPError: If the HTTP request to the data privacy API fails or returns an error response.

        Tags:
            search, data-privacy, email, api, important
        """
        if emailAddress is None:
            raise ValueError("Missing required parameter 'emailAddress'")
        url = f"{self.base_url}/v2/data-privacy/data-for-email-address"
        query_params = {
            k: v for k, v in [("emailAddress", emailAddress)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_request_status(self, integrationId, clientRequestId) -> dict[str, Any]:
        """
        Retrieves the status of a CRM request using the provided integration and client request IDs.

        Args:
            integrationId: The unique identifier for the integration. Must not be None.
            clientRequestId: The unique identifier for the client request. Must not be None.

        Returns:
            A dictionary containing the status details of the specified CRM request as returned by the API.

        Raises:
            ValueError: Raised if either 'integrationId' or 'clientRequestId' is None.
            requests.HTTPError: Raised if the HTTP request to the CRM service returns an unsuccessful status code.

        Tags:
            get, status, crm, request, sync, important
        """
        if integrationId is None:
            raise ValueError("Missing required parameter 'integrationId'")
        if clientRequestId is None:
            raise ValueError("Missing required parameter 'clientRequestId'")
        url = f"{self.base_url}/v2/crm/request-status"
        query_params = {
            k: v
            for k, v in [
                ("integrationId", integrationId),
                ("clientRequestId", clientRequestId),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_crmcalls_manual_association(
        self, fromDateTime=None, cursor=None
    ) -> dict[str, Any]:
        """
        Retrieves a list of manually associated CRM call records, with optional filtering by date and pagination.

        Args:
            fromDateTime: Optional[str]. The starting ISO 8601 datetime string to filter calls created after this timestamp.
            cursor: Optional[str]. A pagination cursor for fetching the next page of results.

        Returns:
            dict[str, Any]: A dictionary containing the response data for manually associated CRM calls, typically including call records and pagination metadata.

        Raises:
            requests.HTTPError: Raised if the HTTP request to the remote API returns an unsuccessful status code.

        Tags:
            list, crmcalls, management, async_job, important
        """
        url = f"{self.base_url}/v2/calls/manual-crm-associations"
        query_params = {
            k: v
            for k, v in [("fromDateTime", fromDateTime), ("cursor", cursor)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_permission_profile(self, workspaceId) -> dict[str, Any]:
        """
        Retrieves the list of permission profiles for the specified workspace.

        Args:
            workspaceId: The unique identifier of the workspace for which to list permission profiles.

        Returns:
            A dictionary containing permission profile details for the given workspace.

        Raises:
            ValueError: If the 'workspaceId' parameter is missing or None.
            HTTPError: If the HTTP request to the remote service fails or returns an error status.

        Tags:
            list, permissions, profile-management, api, important
        """
        if workspaceId is None:
            raise ValueError("Missing required parameter 'workspaceId'")
        url = f"{self.base_url}/v2/all-permission-profiles"
        query_params = {
            k: v for k, v in [("workspaceId", workspaceId)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.list_calls,
            self.add_call,
            self.get_call,
            self.list_calls_extensive,
            self.get_permission_profile,
            self.update_permission_profile,
            self.create_permission_profile,
            self.update_meeting,
            self.delete_meeting,
            self.content_viewed,
            self.content_shared,
            self.custom_action,
            self.list_generic_crm_integration,
            self.register_generic_crm_integration,
            self.delete_generic_crm_integration,
            self.add_users_access_to_calls,
            self.get_users_access_to_calls,
            self.delete_users_access_to_calls,
            self.list_multiple_users,
            self.list_interaction_stats,
            self.list_answered_scorecards,
            self.list_multiple_users_day_by_day_activity,
            self.list_multiple_users_aggregate_activity,
            self.list_multiple_users_aggregate_by_period,
            self.add_meeting,
            self.integration_status,
            self.integration_settings,
            self.get_flows_for_prospects,
            self.assign_prospects,
            self.add_digital_interaction,
            self.purge_phone_number,
            self.purge_email_address,
            self.list_crm_schema_fields,
            self.upload_crm_schema_field,
            self.get_crm_objects,
            self.get_call_transcripts,
            self.list_workspaces,
            self.list_users,
            self.get_user,
            self.get_user_history,
            self.list_trackers,
            self.list_scorecards,
            self.list_permission_profile_users,
            self.list_logs,
            self.get_library_structure,
            self.get_calls_in_specific_folder,
            self.list_flows,
            self.find_all_references_to_phone_number,
            self.find_all_references_to_email_address,
            self.get_request_status,
            self.list_crmcalls_manual_association,
            self.list_permission_profile,
        ]
