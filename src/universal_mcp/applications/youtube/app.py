from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class YoutubeApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        """
        Initializes an instance of a YouTube application integration.

        Args:
            integration: An optional Integration object to be used with the YouTube application integration.
            kwargs: Additional keyword arguments to be passed to the parent class initializer.

        Returns:
            None
        """
        super().__init__(name="youtube", integration=integration, **kwargs)
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def get_jobs_job_reports(
        self,
        jobId,
        createdAfter=None,
        onBehalfOfContentOwner=None,
        pageSize=None,
        pageToken=None,
        startTimeAtOrAfter=None,
        startTimeBefore=None,
    ) -> Any:
        """
        Retrieves job reports for a specific job based on provided filters and parameters.

        Args:
            self: The instance of the class on which the method is being called.
            jobId: The unique identifier for the job whose reports are to be retrieved.
            createdAfter: Optional; filter to include only reports created after this date (ISO 8601 format).
            onBehalfOfContentOwner: Optional; for content owners wanting to access reports on behalf of another user.
            pageSize: Optional; the maximum number of report entries to return per page.
            pageToken: Optional; a token identifying the page of results to return.
            startTimeAtOrAfter: Optional; filter to include only reports starting at or after this date-time (ISO 8601 format).
            startTimeBefore: Optional; filter to include only reports with a start time before this date-time (ISO 8601 format).

        Returns:
            A JSON object containing the job reports matching the provided criteria.
        """
        if jobId is None:
            raise ValueError("Missing required parameter 'jobId'")
        url = f"{self.base_url}/v1/jobs/{jobId}/reports"
        query_params = {
            k: v
            for k, v in [
                ("createdAfter", createdAfter),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
                ("pageSize", pageSize),
                ("pageToken", pageToken),
                ("startTimeAtOrAfter", startTimeAtOrAfter),
                ("startTimeBefore", startTimeBefore),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_jobs_job_reports_report(
        self, jobId, reportId, onBehalfOfContentOwner=None
    ) -> Any:
        """
        Retrieves a report for a specified job using the jobId and reportId.

        Args:
            self: The instance of the class on which this method is called.
            jobId: The unique identifier for the job associated with the report.
            reportId: The unique identifier for the report to retrieve.
            onBehalfOfContentOwner: Optional; if specified, the request is performed on behalf of the content owner associated with this parameter.

        Returns:
            A JSON object containing the details of the requested report.
        """
        if jobId is None:
            raise ValueError("Missing required parameter 'jobId'")
        if reportId is None:
            raise ValueError("Missing required parameter 'reportId'")
        url = f"{self.base_url}/v1/jobs/{jobId}/reports/{reportId}"
        query_params = {
            k: v
            for k, v in [("onBehalfOfContentOwner", onBehalfOfContentOwner)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_jobs_job(self, jobId, onBehalfOfContentOwner=None) -> Any:
        """
        Deletes a job with the specified job ID, optionally acting on behalf of a content owner.

        Args:
            jobId: The unique identifier of the job to be deleted. Must not be None.
            onBehalfOfContentOwner: Optional. The ID of the content owner on whose behalf the request is made.

        Returns:
            Returns the JSON response of the delete operation as a Python dictionary.
        """
        if jobId is None:
            raise ValueError("Missing required parameter 'jobId'")
        url = f"{self.base_url}/v1/jobs/{jobId}"
        query_params = {
            k: v
            for k, v in [("onBehalfOfContentOwner", onBehalfOfContentOwner)]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_jobs(
        self,
        includeSystemManaged=None,
        onBehalfOfContentOwner=None,
        pageSize=None,
        pageToken=None,
    ) -> Any:
        """
        Retrieves a list of jobs from the server, optionally filtering by specified query parameters.

        Args:
            includeSystemManaged: Optional; a boolean indicating whether to include system managed jobs in the result.
            onBehalfOfContentOwner: Optional; a string representing the content owner on behalf of which the request is made.
            pageSize: Optional; an integer specifying the number of jobs to return per page.
            pageToken: Optional; a string representing the token to specify the start of the page for paginated results.

        Returns:
            A JSON-decoded response containing the list of jobs and related metadata.
        """
        url = f"{self.base_url}/v1/jobs"
        query_params = {
            k: v
            for k, v in [
                ("includeSystemManaged", includeSystemManaged),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
                ("pageSize", pageSize),
                ("pageToken", pageToken),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_media_resource_name(self, resourceName) -> Any:
        """
        Retrieves a media resource by name and returns its JSON representation.

        Args:
            resourceName: The name of the media resource to be retrieved. Cannot be None.

        Returns:
            The JSON representation of the media resource.
        """
        if resourceName is None:
            raise ValueError("Missing required parameter 'resourceName'")
        url = f"{self.base_url}/v1/media/{resourceName}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_reporttypes(
        self,
        includeSystemManaged=None,
        onBehalfOfContentOwner=None,
        pageSize=None,
        pageToken=None,
    ) -> Any:
        """
        Retrieves a list of report types from the API with optional filtering and pagination.

        Args:
            includeSystemManaged: Optional; a boolean flag indicating if system-managed report types should be included.
            onBehalfOfContentOwner: Optional; a string that specifies the content owner for whom the user is acting on behalf of.
            pageSize: Optional; an integer that defines the number of results to return per page.
            pageToken: Optional; a string token that indicates a specific page of results to retrieve.

        Returns:
            A JSON object containing the list of report types available from the API.
        """
        url = f"{self.base_url}/v1/reportTypes"
        query_params = {
            k: v
            for k, v in [
                ("includeSystemManaged", includeSystemManaged),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
                ("pageSize", pageSize),
                ("pageToken", pageToken),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_captions(
        self, id=None, onBehalfOf=None, onBehalfOfContentOwner=None
    ) -> Any:
        """
        Deletes captions from a specified resource.

        Args:
            id: Optional; the unique identifier for the caption resource to delete.
            onBehalfOf: Optional; a parameter to identify the user for whom the request is made.
            onBehalfOfContentOwner: Optional; a parameter to specify the content owner for whom the request is made.

        Returns:
            Returns the response JSON object after deleting the caption resource.
        """
        url = f"{self.base_url}/captions"
        query_params = {
            k: v
            for k, v in [
                ("id", id),
                ("onBehalfOf", onBehalfOf),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
            ]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_captions(
        self, id, onBehalfOf=None, onBehalfOfContentOwner=None, tfmt=None, tlang=None
    ) -> Any:
        """
        Retrieves captions for a specified video by its ID, optionally allowing additional query customizations.

        Args:
            id: The unique identifier for the video whose captions are to be retrieved. This parameter is mandatory.
            onBehalfOf: The ID of the user on whose behalf the request is made. Defaults to None.
            onBehalfOfContentOwner: The ID of the content owner on whose behalf the request is made. Defaults to None.
            tfmt: The format of the caption track, such as 'srt' or 'ttml'. Defaults to None.
            tlang: The language of the caption track, specified as a language code. Defaults to None.

        Returns:
            A JSON object containing the captions data for the specified video.
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/captions/{id}"
        query_params = {
            k: v
            for k, v in [
                ("onBehalfOf", onBehalfOf),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
                ("tfmt", tfmt),
                ("tlang", tlang),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_comments(self, id=None) -> Any:
        """
        Deletes a comment or comments from the server based on the specified ID.

        Args:
            id: Optional ID of the comment to be deleted. If not provided, and based on implementation, all comments may be deleted.

        Returns:
            The JSON response from the server after attempting to delete the comment(s).
        """
        url = f"{self.base_url}/comments"
        query_params = {k: v for k, v in [("id", id)] if v is not None}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_comments_mark_as_spam(self, id=None) -> Any:
        """
        Marks a comment as spam by sending a POST request to the specified API endpoint.

        Args:
            id: Optional; the unique identifier of the comment to be marked as spam. If not provided, no specific comment ID is included in the request parameters.

        Returns:
            The JSON response from the API containing the result of the mark-as-spam operation.
        """
        url = f"{self.base_url}/comments/markAsSpam"
        query_params = {k: v for k, v in [("id", id)] if v is not None}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_comments_set_moderation_status(
        self, banAuthor=None, id=None, moderationStatus=None
    ) -> Any:
        """
        Sets the moderation status for a comment and optionally bans the author.

        Args:
            banAuthor: Optional; a boolean indicating whether to ban the author of the comment.
            id: Optional; a string representing the unique identifier of the comment to be moderated.
            moderationStatus: Optional; a string specifying the desired moderation status for the comment, such as 'approved', 'rejected', etc.

        Returns:
            A JSON object containing the response from the server after attempting to set the moderation status for the specified comment.
        """
        url = f"{self.base_url}/comments/setModerationStatus"
        query_params = {
            k: v
            for k, v in [
                ("banAuthor", banAuthor),
                ("id", id),
                ("moderationStatus", moderationStatus),
            ]
            if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_live_broadcasts(
        self, id=None, onBehalfOfContentOwner=None, onBehalfOfContentOwnerChannel=None
    ) -> Any:
        """
        Deletes live broadcasts from a platform using specified query parameters.

        Args:
            id: Optional; The unique identifier for the live broadcast to delete.
            onBehalfOfContentOwner: Optional; The content owner on whose behalf the API request is being made.
            onBehalfOfContentOwnerChannel: Optional; The channel ID associated with the content owner.

        Returns:
            A JSON object containing the server's response to the delete request.
        """
        url = f"{self.base_url}/liveBroadcasts"
        query_params = {
            k: v
            for k, v in [
                ("id", id),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
                ("onBehalfOfContentOwnerChannel", onBehalfOfContentOwnerChannel),
            ]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_live_broadcasts_bind(
        self,
        id=None,
        onBehalfOfContentOwner=None,
        onBehalfOfContentOwnerChannel=None,
        part=None,
        streamId=None,
    ) -> Any:
        """
        Binds a live broadcast to a stream on YouTube, using specified parameters to authenticate and identify the broadcast and stream.

        Args:
            id: Optional; str. The id of the live broadcast to bind.
            onBehalfOfContentOwner: Optional; str. The YouTube CMS content owner on behalf of whom the operation is performed.
            onBehalfOfContentOwnerChannel: Optional; str. The YouTube channel ID for which the live broadcast is operated, on behalf of a content owner.
            part: Optional; str. The part parameter specifies a comma-separated list of one or more liveBroadcast resource properties that the API response will include.
            streamId: Optional; str. The id of the stream to which the live broadcast is to be bound.

        Returns:
            The JSON response object from the YouTube API after attempting to bind the live broadcast to the stream.
        """
        url = f"{self.base_url}/liveBroadcasts/bind"
        query_params = {
            k: v
            for k, v in [
                ("id", id),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
                ("onBehalfOfContentOwnerChannel", onBehalfOfContentOwnerChannel),
                ("part", part),
                ("streamId", streamId),
            ]
            if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_live_broadcasts_control(
        self,
        displaySlate=None,
        id=None,
        offsetTimeMs=None,
        onBehalfOfContentOwner=None,
        onBehalfOfContentOwnerChannel=None,
        part=None,
        walltime=None,
    ) -> Any:
        """
        Controls a live broadcast by sending a POST request with specified parameters.

        Args:
            displaySlate: Optional; Specifies whether or not to show a slate during the broadcast.
            id: Optional; The ID of the live broadcast to control.
            offsetTimeMs: Optional; The offset time in milliseconds for the broadcast control action.
            onBehalfOfContentOwner: Optional; Indicates that the request is made on behalf of a content owner.
            onBehalfOfContentOwnerChannel: Optional; The channel owned by the content owner.
            part: Optional; Specifies a comma-separated list of one or more broadcasts resource properties.
            walltime: Optional; An RFC 3339 timestamp that represents the time at which the action takes place.

        Returns:
            The JSON response from the server after controlling the live broadcast.
        """
        url = f"{self.base_url}/liveBroadcasts/control"
        query_params = {
            k: v
            for k, v in [
                ("displaySlate", displaySlate),
                ("id", id),
                ("offsetTimeMs", offsetTimeMs),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
                ("onBehalfOfContentOwnerChannel", onBehalfOfContentOwnerChannel),
                ("part", part),
                ("walltime", walltime),
            ]
            if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_live_broadcasts_transition(
        self,
        broadcastStatus=None,
        id=None,
        onBehalfOfContentOwner=None,
        onBehalfOfContentOwnerChannel=None,
        part=None,
    ) -> Any:
        """
        Transitions a live broadcast to a specified status for a given broadcast ID.

        Args:
            broadcastStatus: Optional; The status to which the live broadcast should be transitioned.
            id: Optional; The unique identifier of the broadcast that needs to be transitioned.
            onBehalfOfContentOwner: Optional; The YouTube content owner on whose behalf the API request is being made.
            onBehalfOfContentOwnerChannel: Optional; The YouTube channel ID of the channel associated with the specified content owner.
            part: Optional; A comma-separated list of one or more liveBroadcast resource properties that the API response will include.

        Returns:
            The JSON response from the API containing the details of the transitioned live broadcast.
        """
        url = f"{self.base_url}/liveBroadcasts/transition"
        query_params = {
            k: v
            for k, v in [
                ("broadcastStatus", broadcastStatus),
                ("id", id),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
                ("onBehalfOfContentOwnerChannel", onBehalfOfContentOwnerChannel),
                ("part", part),
            ]
            if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_live_chat_bans(self, id=None) -> Any:
        """
        Deletes a live chat ban identified by the given ID from the server.

        Args:
            id: Optional; The unique identifier of the live chat ban to be deleted. If None, no specific ban is targeted.

        Returns:
            The JSON response from the server after the delete operation, which may include details of the deletion.
        """
        url = f"{self.base_url}/liveChat/bans"
        query_params = {k: v for k, v in [("id", id)] if v is not None}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_live_chat_messages(self, id=None) -> Any:
        """
        Deletes live chat messages based on the specified message ID.

        Args:
            id: Optional; The identifier of the specific live chat message to be deleted. If not provided, it defaults to None.

        Returns:
            A JSON object containing the server's response to the deletion request. It includes details about the operation's success or failure.
        """
        url = f"{self.base_url}/liveChat/messages"
        query_params = {k: v for k, v in [("id", id)] if v is not None}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_live_chat_moderators(self, id=None) -> Any:
        """
        Deletes a live chat moderator by ID.

        Args:
            id: The ID of the live chat moderator to delete. If None, no moderator is deleted.

        Returns:
            The JSON response from the server after attempting to delete the moderator.
        """
        url = f"{self.base_url}/liveChat/moderators"
        query_params = {k: v for k, v in [("id", id)] if v is not None}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_videos(self, id=None, onBehalfOfContentOwner=None) -> Any:
        """
        Deletes videos based on specified criteria from a video platform.

        Args:
            id: Optional; A string representing the unique identifier of the video to be deleted. If not provided, no video ID will be specified for deletion.
            onBehalfOfContentOwner: Optional; A string representing the content owner on whose behalf the operation is being performed. If omitted, the operation is performed on behalf of the authenticated user.

        Returns:
            Returns a JSON object containing the response from the API after attempting to delete the video(s), including any relevant status or error information.
        """
        url = f"{self.base_url}/videos"
        query_params = {
            k: v
            for k, v in [("id", id), ("onBehalfOfContentOwner", onBehalfOfContentOwner)]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_videos_get_rating(self, id=None, onBehalfOfContentOwner=None) -> Any:
        """
        Retrieves the rating of a video using video ID and optional content owner specification.

        Args:
            id: Optional; The ID of the video for which the rating is to be retrieved. If None, no specific video ID is used in the request.
            onBehalfOfContentOwner: Optional; Identifies the content owner for whom the request is being made. Used for API requests made on behalf of a content owner.

        Returns:
            A JSON object containing the video rating information returned by the API.
        """
        url = f"{self.base_url}/videos/getRating"
        query_params = {
            k: v
            for k, v in [("id", id), ("onBehalfOfContentOwner", onBehalfOfContentOwner)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_videos_rate(self, id=None, rating=None) -> Any:
        """
        Submit a rating for a video on the server using the provided video ID and rating value.

        Args:
            id: Optional; The unique identifier of the video to rate. If None, the video ID is not included in the request.
            rating: Optional; The rating value to assign to the video. If None, the rating is not included in the request.

        Returns:
            The JSON response from the server after submitting the rating.
        """
        url = f"{self.base_url}/videos/rate"
        query_params = {
            k: v for k, v in [("id", id), ("rating", rating)] if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_videos_report_abuse(self, onBehalfOfContentOwner=None) -> Any:
        """
        Sends a report to YouTube indicating a video's potential abuse.

        Args:
            self: The instance of the class containing this method.
            onBehalfOfContentOwner: Optional; The YouTube content owner on whose behalf the abuse report is being sent.

        Returns:
            The JSON response from the YouTube API after reporting the abuse.
        """
        url = f"{self.base_url}/videos/reportAbuse"
        query_params = {
            k: v
            for k, v in [("onBehalfOfContentOwner", onBehalfOfContentOwner)]
            if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_watermarks_set(self, channelId=None, onBehalfOfContentOwner=None) -> Any:
        """
        Sets watermarks on a specified YouTube channel using optional content owner credentials.

        Args:
            channelId: Optional; The ID of the YouTube channel on which to set the watermark.
            onBehalfOfContentOwner: Optional; The content owner's ID that the request is made on behalf of, allowing authenticated channel actions.

        Returns:
            The JSON response from the API call, which includes details about the watermark setting operation.
        """
        url = f"{self.base_url}/watermarks/set"
        query_params = {
            k: v
            for k, v in [
                ("channelId", channelId),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
            ]
            if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_watermarks_unset(self, channelId=None, onBehalfOfContentOwner=None) -> Any:
        """
        Removes watermarks from a YouTube channel specified by channel ID.

        Args:
            channelId: Optional; The unique identifier of the YouTube channel from which to remove watermarks.
            onBehalfOfContentOwner: Optional; The content owner that the request is on behalf of, used by YouTube content partners.

        Returns:
            The JSON response from the YouTube API after attempting to remove the watermarks.
        """
        url = f"{self.base_url}/watermarks/unset"
        query_params = {
            k: v
            for k, v in [
                ("channelId", channelId),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
            ]
            if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_activities(
        self,
        channelId=None,
        home=None,
        maxResults=None,
        mine=None,
        pageToken=None,
        part=None,
        publishedAfter=None,
        publishedBefore=None,
        regionCode=None,
    ) -> Any:
        """
        Get YouTube channel activities.

        Args:
            channelId: Channel ID
            home: User's feed
            maxResults: Results limit
            mine: User's activities
            pageToken: Page token
            part: Response parts
            publishedAfter: After date
            publishedBefore: Before date
            regionCode: Region code

        Returns:
            JSON with activities
        """
        url = f"{self.base_url}/activities"
        query_params = {
            k: v
            for k, v in [
                ("channelId", channelId),
                ("home", home),
                ("maxResults", maxResults),
                ("mine", mine),
                ("pageToken", pageToken),
                ("part", part),
                ("publishedAfter", publishedAfter),
                ("publishedBefore", publishedBefore),
                ("regionCode", regionCode),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_channel_banners_insert(
        self, channelId=None, onBehalfOfContentOwner=None
    ) -> Any:
        """
        Inserts a new channel banner for a specified YouTube channel using YouTube Data API.

        Args:
            channelId: Optional; A string representing the unique identifier of the YouTube channel for which the banner is being inserted.
            onBehalfOfContentOwner: Optional; A string indicating that the request is on behalf of an authenticated content owner and specifies the content owner's external ID.

        Returns:
            A JSON object containing the response from the YouTube Data API with details about the newly inserted channel banner.
        """
        url = f"{self.base_url}/channelBanners/insert"
        query_params = {
            k: v
            for k, v in [
                ("channelId", channelId),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
            ]
            if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_channel_sections(self, id=None, onBehalfOfContentOwner=None) -> Any:
        """
        Deletes channel sections from a platform specified by the base URL.

        Args:
            id: Optional; A string representing the unique identifier of the channel section to be deleted.
            onBehalfOfContentOwner: Optional; A string indicating that the request is being made on behalf of the content owner specified by this parameter.

        Returns:
            Returns a JSON-decoded response object from the server after attempting to delete the specified channel section.
        """
        url = f"{self.base_url}/channelSections"
        query_params = {
            k: v
            for k, v in [("id", id), ("onBehalfOfContentOwner", onBehalfOfContentOwner)]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_channels(
        self,
        categoryId=None,
        forUsername=None,
        hl=None,
        id=None,
        managedByMe=None,
        maxResults=None,
        mine=None,
        mySubscribers=None,
        onBehalfOfContentOwner=None,
        pageToken=None,
        part=None,
    ) -> Any:
        """
        Get YouTube channels.

        Args:
            categoryId: Category ID
            forUsername: Username
            hl: Language code
            id: Channel IDs
            managedByMe: Managed channels
            maxResults: Results limit
            mine: Own channels
            mySubscribers: Subscribed channels
            onBehalfOfContentOwner: Owner ID
            pageToken: Page token
            part: Response parts

        Returns:
            JSON with channels
        """
        url = f"{self.base_url}/channels"
        query_params = {
            k: v
            for k, v in [
                ("categoryId", categoryId),
                ("forUsername", forUsername),
                ("hl", hl),
                ("id", id),
                ("managedByMe", managedByMe),
                ("maxResults", maxResults),
                ("mine", mine),
                ("mySubscribers", mySubscribers),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
                ("pageToken", pageToken),
                ("part", part),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_comment_threads(
        self,
        allThreadsRelatedToChannelId=None,
        channelId=None,
        id=None,
        maxResults=None,
        moderationStatus=None,
        order=None,
        pageToken=None,
        part=None,
        searchTerms=None,
        textFormat=None,
        videoId=None,
    ) -> Any:
        """
        Get YouTube comment threads.

        Args:
            allThreadsRelatedToChannelId: Threads for channel
            channelId: Channel ID
            id: Comment thread IDs
            maxResults: Results limit
            moderationStatus: Moderation status
            order: Sort order
            pageToken: Pagination token
            part: Response parts
            searchTerms: Search terms
            textFormat: Text format
            videoId: Video ID

        Returns:
            JSON with comment threads
        """
        url = f"{self.base_url}/commentThreads"
        query_params = {
            k: v
            for k, v in [
                ("allThreadsRelatedToChannelId", allThreadsRelatedToChannelId),
                ("channelId", channelId),
                ("id", id),
                ("maxResults", maxResults),
                ("moderationStatus", moderationStatus),
                ("order", order),
                ("pageToken", pageToken),
                ("part", part),
                ("searchTerms", searchTerms),
                ("textFormat", textFormat),
                ("videoId", videoId),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_fanfundingevents(
        self, hl=None, maxResults=None, pageToken=None, part=None
    ) -> Any:
        """
        Retrieves fan funding events based on specified filter criteria.

        Args:
            hl: Optional; a string representing the language for text values. If not specified, the default language will be used.
            maxResults: Optional; an integer specifying the maximum number of results to return. If not specified, a server-determined default will be used.
            pageToken: Optional; a string token to retrieve a specific page in a paginated set of results. Useful for navigating through large sets of data.
            part: Optional; a comma-separated list of one or more 'fanFundingEvent' resource properties that the API response will include.

        Returns:
            The function returns the JSON-decoded response of the fan funding events data retrieved from the API.
        """
        url = f"{self.base_url}/fanFundingEvents"
        query_params = {
            k: v
            for k, v in [
                ("hl", hl),
                ("maxResults", maxResults),
                ("pageToken", pageToken),
                ("part", part),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_guecategories(self, hl=None, id=None, part=None, regionCode=None) -> Any:
        """
        Fetches guide categories from a remote service based on specified parameters.

        Args:
            hl: Optional; a string that specifies the language localization.
            id: Optional; a string representing the ID of the guide category.
            part: Optional; a string indicating which parts of the guide category resource to return.
            regionCode: Optional; a string that denotes the region of interest.

        Returns:
            A dictionary containing the JSON response representing guide categories from the service.
        """
        url = f"{self.base_url}/guideCategories"
        query_params = {
            k: v
            for k, v in [
                ("hl", hl),
                ("id", id),
                ("part", part),
                ("regionCode", regionCode),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_languages(self, hl=None, part=None) -> Any:
        """
        Fetches a list of supported languages from the internationalization API.

        Args:
            hl: Optional; The language code to localize the language names, e.g., 'en' for English.
            part: Optional; The part parameter specifies a comma-separated list of one or more i18nLanguage resource properties that the API response will include.

        Returns:
            A JSON object containing the API response with the list of supported languages.
        """
        url = f"{self.base_url}/i18nLanguages"
        query_params = {k: v for k, v in [("hl", hl), ("part", part)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_regions(self, hl=None, part=None) -> Any:
        """
        Retrieves a list of i18n regions from a specified API endpoint.

        Args:
            hl: Optional; a string representing the language code for which the regions are requested.
            part: Optional; a string specifying a comma-separated list of one or more i18nRegion resource parts to include in the API response.

        Returns:
            The JSON response from the API containing the list of i18n regions.
        """
        url = f"{self.base_url}/i18nRegions"
        query_params = {k: v for k, v in [("hl", hl), ("part", part)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_livestreams(
        self, id=None, onBehalfOfContentOwner=None, onBehalfOfContentOwnerChannel=None
    ) -> Any:
        """
        Deletes a livestream resource from the YouTube Data API using optional filtering parameters.

        Args:
            id: Optional; A comma-separated list of YouTube livestream IDs that identify the resources to be deleted.
            onBehalfOfContentOwner: Optional; YouTube content owner who is channel owner of the livestream and makes this API call.
            onBehalfOfContentOwnerChannel: Optional; The YouTube channel ID on behalf of which the API call is being made.

        Returns:
            A JSON object containing the API's response to the delete request.
        """
        url = f"{self.base_url}/liveStreams"
        query_params = {
            k: v
            for k, v in [
                ("id", id),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
                ("onBehalfOfContentOwnerChannel", onBehalfOfContentOwnerChannel),
            ]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_play_list_items(self, id=None, onBehalfOfContentOwner=None) -> Any:
        """
        Deletes playlist items identified by the given id or on behalf of the specified content owner.

        Args:
            id: Optional; The ID of the playlist item to be deleted.
            onBehalfOfContentOwner: Optional; The content owner on whose behalf the playlist item is being deleted.

        Returns:
            The JSON response from the server indicating the result of the deletion operation.
        """
        url = f"{self.base_url}/playlistItems"
        query_params = {
            k: v
            for k, v in [("id", id), ("onBehalfOfContentOwner", onBehalfOfContentOwner)]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_playlists(self, id=None, onBehalfOfContentOwner=None) -> Any:
        """
        Deletes playlists based on specified criteria.

        Args:
            id: Optional; A string representing the ID of the playlist to delete. Default is None.
            onBehalfOfContentOwner: Optional; A string representing the content owner in whose behalf the operation is being performed. Default is None.

        Returns:
            The JSON response from the server as a result of the delete operation.
        """
        url = f"{self.base_url}/playlists"
        query_params = {
            k: v
            for k, v in [("id", id), ("onBehalfOfContentOwner", onBehalfOfContentOwner)]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_search(
        self,
        channelId=None,
        channelType=None,
        eventType=None,
        forContentOwner=None,
        forDeveloper=None,
        forMine=None,
        location=None,
        locationRadius=None,
        maxResults=None,
        onBehalfOfContentOwner=None,
        order=None,
        pageToken=None,
        part=None,
        publishedAfter=None,
        publishedBefore=None,
        q=None,
        regionCode=None,
        relatedToVideoId=None,
        relevanceLanguage=None,
        safeSearch=None,
        topicId=None,
        type=None,
        videoCaption=None,
        videoCategoryId=None,
        videoDefinition=None,
        videoDimension=None,
        videoDuration=None,
        videoEmbeddable=None,
        videoLicense=None,
        videoSyndicated=None,
        videoType=None,
    ) -> Any:
        """
        Search YouTube Data API with filters.

        Args:
            channelId: Channel filter
            channelType: Channel type
            eventType: Event type
            forContentOwner: Content owner search
            forDeveloper: Developer search
            forMine: User's videos
            location: Location filter
            locationRadius: Location radius
            maxResults: Results limit
            onBehalfOfContentOwner: Owner ID
            order: Results order
            pageToken: Page token
            part: Response parts
            publishedAfter: After date
            publishedBefore: Before date
            q: Search query
            regionCode: Region code
            relatedToVideoId: Related videos
            relevanceLanguage: Language
            safeSearch: Safe search
            topicId: Topic filter
            type: Resource type
            videoCaption: Caption filter
            videoCategoryId: Category
            videoDefinition: Definition
            videoDimension: Dimension
            videoDuration: Duration
            videoEmbeddable: Embeddable
            videoLicense: License
            videoSyndicated: Syndicated
            videoType: Video type

        Returns:
            JSON with search results
        """
        url = f"{self.base_url}/search"
        query_params = {
            k: v
            for k, v in [
                ("channelId", channelId),
                ("channelType", channelType),
                ("eventType", eventType),
                ("forContentOwner", forContentOwner),
                ("forDeveloper", forDeveloper),
                ("forMine", forMine),
                ("location", location),
                ("locationRadius", locationRadius),
                ("maxResults", maxResults),
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
                ("order", order),
                ("pageToken", pageToken),
                ("part", part),
                ("publishedAfter", publishedAfter),
                ("publishedBefore", publishedBefore),
                ("q", q),
                ("regionCode", regionCode),
                ("relatedToVideoId", relatedToVideoId),
                ("relevanceLanguage", relevanceLanguage),
                ("safeSearch", safeSearch),
                ("topicId", topicId),
                ("type", type),
                ("videoCaption", videoCaption),
                ("videoCategoryId", videoCategoryId),
                ("videoDefinition", videoDefinition),
                ("videoDimension", videoDimension),
                ("videoDuration", videoDuration),
                ("videoEmbeddable", videoEmbeddable),
                ("videoLicense", videoLicense),
                ("videoSyndicated", videoSyndicated),
                ("videoType", videoType),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_sponsors(
        self, filter=None, maxResults=None, pageToken=None, part=None
    ) -> Any:
        """
        Fetches a list of sponsors from a server, applying optional filtering and pagination.

        Args:
            filter: Optional; A string containing filtering criteria for the sponsors.
            maxResults: Optional; An integer limiting the number of sponsors returned.
            pageToken: Optional; A token string used to retrieve a specific page of results.
            part: Optional; A string specifying which parts of the sponsor details to fetch.

        Returns:
            The JSON response containing the list of sponsors, potentially filtered and paginated, as returned by the server.
        """
        url = f"{self.base_url}/sponsors"
        query_params = {
            k: v
            for k, v in [
                ("filter", filter),
                ("maxResults", maxResults),
                ("pageToken", pageToken),
                ("part", part),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_subscriptions(self, id=None) -> Any:
        """
        Deletes subscriptions by sending a DELETE request to the API.

        Args:
            id: Optional; An identifier for a specific subscription to delete. If None, deletes all subscriptions.

        Returns:
            The JSON response from the API after attempting to delete the subscription(s).
        """
        url = f"{self.base_url}/subscriptions"
        query_params = {k: v for k, v in [("id", id)] if v is not None}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_superchatevents(
        self, hl=None, maxResults=None, pageToken=None, part=None
    ) -> Any:
        """
        Fetches a list of super chat events from the YouTube API with optional filtering parameters.

        Args:
            hl: Optional; the language code to select localized resource information.
            maxResults: Optional; the maximum number of items that should be returned in the result set.
            pageToken: Optional; the token to identify a specific page in the result set.
            part: Optional; the parameter specifying which super chat event resource parts to include in the response.

        Returns:
            A JSON object containing the super chat events data returned by the YouTube API.
        """
        url = f"{self.base_url}/superChatEvents"
        query_params = {
            k: v
            for k, v in [
                ("hl", hl),
                ("maxResults", maxResults),
                ("pageToken", pageToken),
                ("part", part),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_thumbnails_set(self, onBehalfOfContentOwner=None, videoId=None) -> Any:
        """
        Sets a thumbnail for a specified video on behalf of a content owner using the YouTube API.

        Args:
            onBehalfOfContentOwner: Optional; str. The YouTube content owner ID on whose behalf the request is being made.
            videoId: Optional; str. The ID of the video for which the thumbnails are being set.

        Returns:
            dict. The response from the YouTube API as a JSON object, containing details of the updated video thumbnail.
        """
        url = f"{self.base_url}/thumbnails/set"
        query_params = {
            k: v
            for k, v in [
                ("onBehalfOfContentOwner", onBehalfOfContentOwner),
                ("videoId", videoId),
            ]
            if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_video_abuse_report_reasons(self, hl=None, part=None) -> Any:
        """
        Fetches a list of video abuse report reasons with optional localization and response filtering.

        Args:
            hl: An optional parameter specifying the language for localizing the response. This is typically a BCP-47 language code, such as 'en' or 'fr'.
            part: An optional parameter specifying which parts of the abuse report reasons to include in the response. This could specify fields like 'id' or 'snippet'.

        Returns:
            The function returns a JSON object containing the list of video abuse report reasons, or filtered parts of it, if specified.
        """
        url = f"{self.base_url}/videoAbuseReportReasons"
        query_params = {k: v for k, v in [("hl", hl), ("part", part)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_veocategories(self, hl=None, id=None, part=None, regionCode=None) -> Any:
        """
        Fetches video categories from an external API using specified query parameters.

        Args:
            hl: Optional; the language code for localized video category names, e.g., 'en'.
            id: Optional; a comma-separated list of video category IDs to filter the results.
            part: Optional; a list of properties to include in the response, e.g., 'snippet'.
            regionCode: Optional; an ISO 3166-1 alpha-2 country code to filter the categories for a specific region.

        Returns:
            The JSON response from the API containing video category information.
        """
        url = f"{self.base_url}/videoCategories"
        query_params = {
            k: v
            for k, v in [
                ("hl", hl),
                ("id", id),
                ("part", part),
                ("regionCode", regionCode),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_groupitems(self, id=None, onBehalfOfContentOwner=None) -> Any:
        """
        Deletes group items based on specified parameters.

        Args:
            id: Optional; A string that identifies the group item to be deleted. If not provided, all group items may be affected depending on other parameters.
            onBehalfOfContentOwner: Optional; A string representing the content owner on whose behalf the request is being made. This is typically used for partners or channels managed by the content owner.

        Returns:
            A JSON object containing the response from the deletion request, which includes the results of the delete operation.
        """
        url = f"{self.base_url}/groupItems"
        query_params = {
            k: v
            for k, v in [("id", id), ("onBehalfOfContentOwner", onBehalfOfContentOwner)]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def delete_groups(self, id=None, onBehalfOfContentOwner=None) -> Any:
        """
        Deletes groups specified by their ID, optionally on behalf of a content owner.

        Args:
            id: Optional; The unique identifier for the group to be deleted. If not provided, no specific group ID will be targeted.
            onBehalfOfContentOwner: Optional; The content owner that the group deletion is being performed on behalf of.

        Returns:
            A JSON-decoded response from the server indicating the success or failure of the delete operation.
        """
        url = f"{self.base_url}/groups"
        query_params = {
            k: v
            for k, v in [("id", id), ("onBehalfOfContentOwner", onBehalfOfContentOwner)]
            if v is not None
        }
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_reports(
        self,
        currency=None,
        dimensions=None,
        end=None,
        filters=None,
        ids=None,
        include=None,
        max=None,
        metrics=None,
        sort=None,
        start=None,
    ) -> Any:
        """
        Fetches and returns report data based on specified filtering and sorting criteria.

        Args:
            currency: Optional; Specifies the currency format for the report.
            dimensions: Optional; List of dimensions to include in the report.
            end: Optional; End date for the report data range.
            filters: Optional; Filters to apply to the report data.
            ids: Optional; Specific identifiers to include in the report.
            include: Optional; Additional entities to include in the report's output.
            max: Optional; Maximum number of results to return.
            metrics: Optional; List of metrics to include in the report.
            sort: Optional; Order by which to sort the report results.
            start: Optional; Start date for the report data range.

        Returns:
            The response containing the report data in JSON format.
        """
        url = f"{self.base_url}/reports"
        query_params = {
            k: v
            for k, v in [
                ("currency", currency),
                ("dimensions", dimensions),
                ("end", end),
                ("filters", filters),
                ("ids", ids),
                ("include", include),
                ("max", max),
                ("metrics", metrics),
                ("sort", sort),
                ("start", start),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        """
        Returns a list of tool methods available in the class instance.

        Args:
            None: This function does not accept any parameters.

        Returns:
            list: A list containing references to various tool methods associated with job reports, media resources, comments, broadcasts, videos, activities, channels, etc.
        """
        return [
            self.get_jobs_job_reports,
            self.get_jobs_job_reports_report,
            self.delete_jobs_job,
            self.get_jobs,
            self.get_media_resource_name,
            self.get_reporttypes,
            self.delete_captions,
            self.get_captions,
            self.delete_comments,
            self.add_comments_mark_as_spam,
            self.add_comments_set_moderation_status,
            self.delete_live_broadcasts,
            self.add_live_broadcasts_bind,
            self.add_live_broadcasts_control,
            self.add_live_broadcasts_transition,
            self.delete_live_chat_bans,
            self.delete_live_chat_messages,
            self.delete_live_chat_moderators,
            self.delete_videos,
            self.get_videos_get_rating,
            self.add_videos_rate,
            self.add_videos_report_abuse,
            self.add_watermarks_set,
            self.add_watermarks_unset,
            self.get_activities,
            self.add_channel_banners_insert,
            self.delete_channel_sections,
            self.get_channels,
            self.get_comment_threads,
            self.get_fanfundingevents,
            self.get_guecategories,
            self.get_languages,
            self.get_regions,
            self.delete_livestreams,
            self.delete_play_list_items,
            self.delete_playlists,
            self.get_search,
            self.get_sponsors,
            self.delete_subscriptions,
            self.get_superchatevents,
            self.add_thumbnails_set,
            self.get_video_abuse_report_reasons,
            self.get_veocategories,
            self.delete_groupitems,
            self.delete_groups,
            self.get_reports,
        ]
