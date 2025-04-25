from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class SpotifyApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="spotify", integration=integration, **kwargs)
        self.base_url = "https://api.spotify.com/v1"

    def get_an_album(self, id, market=None) -> Any:
        """
        Retrieves detailed information about a specific album by its ID from the API.

        Args:
            id: str. The unique identifier for the album to retrieve. Must not be None.
            market: Optional[str]. An ISO 3166-1 alpha-2 country code to filter the album's availability. Defaults to None.

        Returns:
            dict. A JSON-decoded dictionary containing album details as returned by the API.

        Raises:
            ValueError: If the 'id' parameter is None.
            HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            get, album, api, fetch
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/albums/{id}"
        query_params = {k: v for k, v in [("market", market)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_multiple_albums(self, ids, market=None) -> Any:
        """
        Retrieves detailed information for multiple albums by their IDs from the API.

        Args:
            ids: A comma-separated string or list of album IDs to retrieve.
            market: (Optional) An ISO 3166-1 alpha-2 country code to filter the results based on market availability.

        Returns:
            A JSON-serializable object containing details of the requested albums.

        Raises:
            ValueError: If the 'ids' parameter is not provided.
            requests.HTTPError: If the HTTP request to the API fails with a status error.

        Tags:
            get, albums, api, list
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/albums"
        query_params = {
            k: v for k, v in [("ids", ids), ("market", market)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_an_albums_tracks(self, id, market=None, limit=None, offset=None) -> Any:
        """
        Retrieves the list of tracks for a specified album from the API, with optional filtering and pagination.

        Args:
            id: str. The unique identifier for the album. Required.
            market: Optional[str]. An ISO 3166-1 alpha-2 country code to filter track availability. Defaults to None.
            limit: Optional[int]. The maximum number of tracks to return. Defaults to None.
            offset: Optional[int]. The index of the first track to return. Useful for pagination. Defaults to None.

        Returns:
            Any. A JSON object containing the album's tracks and related pagination information as returned by the API.

        Raises:
            ValueError: If the 'id' parameter is None.
            HTTPError: If the HTTP request to the API fails (e.g., due to network issues or an invalid album ID).

        Tags:
            get, list, tracks, album, api
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/albums/{id}/tracks"
        query_params = {
            k: v
            for k, v in [("market", market), ("limit", limit), ("offset", offset)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_an_artist(self, id) -> Any:
        """
        Retrieve detailed information about a specific artist by their unique identifier.

        Args:
            id: The unique identifier of the artist to retrieve. Must not be None.

        Returns:
            A JSON object containing the artist's details as returned by the API.

        Raises:
            ValueError: Raised if the 'id' parameter is None.
            requests.exceptions.HTTPError: Raised if the HTTP request to fetch the artist fails (e.g., non-2xx status code).

        Tags:
            get, artist, api, fetch
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/artists/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_multiple_artists(self, ids) -> Any:
        """
        Retrieves information for multiple artists using their IDs.

        Args:
            ids: A comma-separated string or list of artist IDs to retrieve information for.

        Returns:
            A JSON object containing details for the specified artists.

        Raises:
            ValueError: Raised if the 'ids' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the artists endpoint fails.

        Tags:
            get, artists, api, list
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/artists"
        query_params = {k: v for k, v in [("ids", ids)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_an_artists_albums(
        self, id, include_groups=None, market=None, limit=None, offset=None
    ) -> Any:
        """
        Retrieves a list of albums for the specified artist from the API.

        Args:
            id: str. The unique identifier of the artist whose albums are to be retrieved.
            include_groups: Optional[str]. A comma-separated list of keywords to filter the album types (e.g., 'album', 'single', 'appears_on', 'compilation').
            market: Optional[str]. An ISO 3166-1 alpha-2 country code to filter the albums for a specific market.
            limit: Optional[int]. The maximum number of album objects to return. Default is determined by the API.
            offset: Optional[int]. The index of the first album to return. Useful for pagination.

        Returns:
            dict. A JSON object containing the artist's albums, as returned by the API.

        Raises:
            ValueError: If the 'id' parameter is not provided.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status code.

        Tags:
            get, list, albums, artist, api
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/artists/{id}/albums"
        query_params = {
            k: v
            for k, v in [
                ("include_groups", include_groups),
                ("market", market),
                ("limit", limit),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_an_artists_top_tracks(self, id, market=None) -> Any:
        """
        Retrieves the top tracks for a specified artist from the API.

        Args:
            id: str. The Spotify ID of the artist whose top tracks are to be retrieved.
            market: Optional[str]. An ISO 3166-1 alpha-2 country code to filter the top tracks for a specific market. Defaults to None.

        Returns:
            dict. A JSON object containing the artist's top tracks data as returned by the API.

        Raises:
            ValueError: Raised if the required 'id' parameter is not provided.
            requests.HTTPError: Raised if the HTTP request to the API is unsuccessful.

        Tags:
            get, artist, top-tracks, api, music
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/artists/{id}/top-tracks"
        query_params = {k: v for k, v in [("market", market)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_an_artists_related_artists(self, id) -> Any:
        """
        Retrieves a list of artists related to the specified artist by their unique ID.

        Args:
            id: str. The unique identifier of the artist for whom related artists are to be fetched.

        Returns:
            dict. A JSON-decoded dictionary containing data about artists related to the specified artist.

        Raises:
            ValueError: Raised if the required 'id' parameter is missing or None.
            HTTPError: Raised if the HTTP request to fetch related artists fails (non-success response).

        Tags:
            fetch, related-artists, ai, api
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/artists/{id}/related-artists"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_a_show(self, id, market=None) -> Any:
        """
        Retrieve detailed information about a show by its unique identifier.

        Args:
            id: str. The unique identifier of the show to retrieve. Must not be None.
            market: Optional[str]. An ISO 3166-1 alpha-2 country code. If provided, restricts the show details to the specified market.

        Returns:
            dict. A dictionary containing the show's information as returned by the API.

        Raises:
            ValueError: Raised if the 'id' parameter is None.
            requests.HTTPError: Raised if the HTTP request for the show details fails.

        Tags:
            get, show, api, fetch
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/shows/{id}"
        query_params = {k: v for k, v in [("market", market)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_multiple_shows(self, ids, market=None) -> Any:
        """
        Retrieves information for multiple shows by their IDs, with optional market filtering.

        Args:
            ids: str or list of str. A comma-separated list or sequence of show IDs to retrieve information for. This parameter is required.
            market: Optional[str]. An optional ISO 3166-1 alpha-2 country code to filter show availability.

        Returns:
            dict. The JSON response containing show details for the specified IDs.

        Raises:
            ValueError: Raised if the 'ids' parameter is not provided.
            requests.HTTPError: Raised if an HTTP error occurs during the API request.

        Tags:
            get, list, shows, api, batch
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/shows"
        query_params = {
            k: v for k, v in [("market", market), ("ids", ids)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_a_shows_episodes(self, id, market=None, limit=None, offset=None) -> Any:
        """
        Retrieves episodes for a specific show from the API with optional market, limit, and offset parameters.

        Args:
            id: str. The unique identifier of the show whose episodes are to be retrieved.
            market: Optional[str]. An ISO 3166-1 alpha-2 country code to filter episodes available in a particular market.
            limit: Optional[int]. The maximum number of episodes to return. Optional.
            offset: Optional[int]. The index of the first episode to return. Optional.

        Returns:
            Any. A JSON-decoded object containing the episodes information for the specified show.

        Raises:
            ValueError: If the required 'id' parameter is None.
            HTTPError: If the HTTP request to the API fails (non-2xx status code).

        Tags:
            get, episodes, api, list, management
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/shows/{id}/episodes"
        query_params = {
            k: v
            for k, v in [("market", market), ("limit", limit), ("offset", offset)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_an_episode(self, id, market=None) -> Any:
        """
        Retrieves a single podcast episode's details by its unique identifier.

        Args:
            id: str. Unique identifier of the episode to retrieve. Required.
            market: Optional[str]. An ISO 3166-1 alpha-2 country code to filter the episode for a specific market. Defaults to None.

        Returns:
            dict. The JSON-decoded response containing episode details.

        Raises:
            ValueError: Raised if the 'id' parameter is None.
            requests.exceptions.HTTPError: Raised if the HTTP request to retrieve the episode fails.

        Tags:
            get, episode, api, fetch, single-item
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/episodes/{id}"
        query_params = {k: v for k, v in [("market", market)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_multiple_episodes(self, ids, market=None) -> Any:
        """
        Retrieves details for multiple podcast episodes using their IDs, optionally filtered by market.

        Args:
            ids: str. A comma-separated list of episode IDs to retrieve.
            market: Optional[str]. An ISO 3166-1 alpha-2 country code to filter the episodes based on market (defaults to None).

        Returns:
            Any. The response JSON containing details of the requested episodes.

        Raises:
            ValueError: Raised if the required parameter 'ids' is not provided.
            requests.HTTPError: Raised if the HTTP request to the API endpoint returns an unsuccessful status code.

        Tags:
            get, episodes, batch, podcast, api
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/episodes"
        query_params = {
            k: v for k, v in [("ids", ids), ("market", market)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_an_audiobook(self, id, market=None) -> Any:
        """
        Retrieves detailed information about a specific audiobook by ID, optionally filtered by market.

        Args:
            id: str. The unique identifier of the audiobook to retrieve.
            market: Optional[str]. An ISO 3166-1 alpha-2 country code to filter audiobook availability. Defaults to None.

        Returns:
            dict. A dictionary containing audiobook details as returned from the API.

        Raises:
            ValueError: Raised if the 'id' parameter is not provided.
            requests.HTTPError: Raised if the HTTP request to the audiobook API fails (non-2xx status code).

        Tags:
            get, audiobook, api, details, fetch
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/audiobooks/{id}"
        query_params = {k: v for k, v in [("market", market)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_multiple_audiobooks(self, ids, market=None) -> Any:
        """
        Fetches details for multiple audiobooks by their IDs, optionally filtered by market.

        Args:
            ids: A list or comma-separated string of audiobook IDs to retrieve.
            market: Optional; a string specifying the market to filter results by.

        Returns:
            A dictionary containing details of the requested audiobooks as parsed from the JSON API response.

        Raises:
            ValueError: Raised if 'ids' is not provided.
            requests.exceptions.HTTPError: Raised if the API response contains a failed HTTP status.

        Tags:
            get, audiobook, batch, api
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/audiobooks"
        query_params = {
            k: v for k, v in [("ids", ids), ("market", market)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_audiobook_chapters(self, id, market=None, limit=None, offset=None) -> Any:
        """
        Retrieves the chapters for a specified audiobook from the API.

        Args:
            id: str. The unique identifier of the audiobook whose chapters are to be retrieved.
            market: Optional[str]. An ISO 3166-1 alpha-2 country code specifying the market for the chapters. Defaults to None.
            limit: Optional[int]. The maximum number of chapters to return. Defaults to None.
            offset: Optional[int]. The index of the first chapter to return. Used for pagination. Defaults to None.

        Returns:
            dict. A JSON response containing audiobook chapter details as returned by the API.

        Raises:
            ValueError: If the 'id' parameter is not provided.
            requests.HTTPError: If the API request fails with a non-successful HTTP status code.

        Tags:
            get, audiobook, chapters, api, fetch
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/audiobooks/{id}/chapters"
        query_params = {
            k: v
            for k, v in [("market", market), ("limit", limit), ("offset", offset)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_saved_audiobooks(self, limit=None, offset=None) -> Any:
        """
        Retrieves the current user's saved audiobooks from the API with optional pagination.

        Args:
            limit: Optional; int or None. The maximum number of audiobooks to return. If None, the API default is used.
            offset: Optional; int or None. The index of the first audiobook to retrieve. If None, the API default is used.

        Returns:
            dict: A JSON-decoded dictionary containing the user's saved audiobooks.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            get, list, audiobooks, user-data, api
        """
        url = f"{self.base_url}/me/audiobooks"
        query_params = {
            k: v for k, v in [("limit", limit), ("offset", offset)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def save_audiobooks_user(self, ids) -> Any:
        """
        Saves one or more audiobooks to the current user's library.

        Args:
            ids: A comma-separated string or list of audiobook IDs to add to the user's library. Must not be None.

        Returns:
            The JSON-decoded response from the API, typically containing the result of the save operation.

        Raises:
            ValueError: If 'ids' is None.
            HTTPError: If the API request fails due to an unsuccessful HTTP response status.

        Tags:
            save, audiobooks, user, management, api
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/me/audiobooks"
        query_params = {k: v for k, v in [("ids", ids)] if v is not None}
        response = self._put(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def remove_audiobooks_user(self, ids) -> Any:
        """
        Removes one or more audiobooks from the authenticated user's library.

        Args:
            ids: The identifier or list of identifiers of the audiobooks to remove.

        Returns:
            The API response as a parsed JSON object containing the result of the deletion operation.

        Raises:
            ValueError: If the 'ids' parameter is None.
            requests.HTTPError: If the HTTP request to delete audiobooks does not succeed.

        Tags:
            remove, audiobooks, user-library, management
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/me/audiobooks"
        query_params = {k: v for k, v in [("ids", ids)] if v is not None}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def check_users_saved_audiobooks(self, ids) -> Any:
        """
        Checks if the specified audiobooks are saved in the current user's library.

        Args:
            ids: A string or list of audiobook IDs to check. Each ID should correspond to an audiobook in the catalog.

        Returns:
            A JSON-serializable object (typically a list of booleans) indicating whether each audiobook is saved by the user.

        Raises:
            ValueError: Raised if the 'ids' parameter is None.
            HTTPError: Raised if the HTTP request to the API fails with an error status.

        Tags:
            check, audiobooks, user-library, api
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/me/audiobooks/contains"
        query_params = {k: v for k, v in [("ids", ids)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_a_chapter(self, id, market=None) -> Any:
        """
        Retrieves a specific chapter's details by ID from the API, optionally filtering by market.

        Args:
            id: The unique identifier of the chapter to retrieve. Must not be None.
            market: Optional; a string specifying a market code to filter the chapter details.

        Returns:
            A JSON-decoded object containing the details of the requested chapter.

        Raises:
            ValueError: Raised when the required 'id' parameter is missing (None).
            HTTPError: Raised if the HTTP request to the API fails or returns an unsuccessful status.

        Tags:
            get, chapter, api, data-retrieval
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/chapters/{id}"
        query_params = {k: v for k, v in [("market", market)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_several_chapters(self, ids, market=None) -> Any:
        """
        Retrieve details for multiple chapters based on their IDs, optionally filtering by market.

        Args:
            ids: List or string of chapter IDs to retrieve. This parameter is required.
            market: Optional market code to filter the chapters by region or market. Defaults to None.

        Returns:
            A JSON-decoded response containing details for the specified chapters.

        Raises:
            ValueError: If the 'ids' parameter is None.
            HTTPError: If the HTTP request to the chapters endpoint returns an error response.

        Tags:
            get, chapters, batch, api
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/chapters"
        query_params = {
            k: v for k, v in [("ids", ids), ("market", market)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_track(self, id, market=None) -> Any:
        """
        Retrieves detailed information about a track by its unique identifier from the external API.

        Args:
            id: str. The unique identifier for the track to retrieve. Must not be None.
            market: Optional[str]. An ISO 3166-1 alpha-2 country code to filter the track's availability (default is None).

        Returns:
            dict. The JSON response containing track details from the API.

        Raises:
            ValueError: If the required 'id' parameter is None.
            HTTPError: If the API request returns an unsuccessful HTTP status code.

        Tags:
            get, track, api, fetch
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/tracks/{id}"
        query_params = {k: v for k, v in [("market", market)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_several_tracks(self, ids, market=None) -> Any:
        """
        Retrieves metadata for multiple tracks based on their IDs from the API.

        Args:
            ids: A comma-separated list or iterable of track IDs to retrieve metadata for. This parameter is required.
            market: An optional ISO 3166-1 alpha-2 country code to filter the track data. Defaults to None.

        Returns:
            A dictionary containing the metadata of the requested tracks as returned by the API.

        Raises:
            ValueError: If 'ids' is not provided (None), indicating that required parameter is missing.
            requests.HTTPError: If the HTTP request to the API fails or returns a non-success status code.

        Tags:
            get, tracks, api, metadata
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/tracks"
        query_params = {
            k: v for k, v in [("market", market), ("ids", ids)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def search(
        self, q, type, market=None, limit=None, offset=None, include_external=None
    ) -> Any:
        """
        Performs a search query against the API and returns the matching results as a JSON object.

        Args:
            q: str. The search query string. Required.
            type: str or list of str. The type(s) of item to search for (e.g., 'track', 'artist'). Required.
            market: Optional[str]. An ISO 3166-1 alpha-2 country code or 'from_token'. Optional.
            limit: Optional[int]. Maximum number of results to return. Optional.
            offset: Optional[int]. The index of the first result to return. Optional.
            include_external: Optional[str]. If 'audio', the response will include any relevant audio content. Optional.

        Returns:
            dict. The JSON response containing search results.

        Raises:
            ValueError: If the required parameter 'q' or 'type' is missing.
            requests.HTTPError: If the HTTP request fails or the server returns an error status.

        Tags:
            search, api, query, async-job, important
        """
        if q is None:
            raise ValueError("Missing required parameter 'q'")
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        url = f"{self.base_url}/search"
        query_params = {
            k: v
            for k, v in [
                ("q", q),
                ("type", type),
                ("market", market),
                ("limit", limit),
                ("offset", offset),
                ("include_external", include_external),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_current_users_profile(
        self,
    ) -> Any:
        """
        Retrieves the current authenticated user's profile information from the API.

        Args:
            None: This function takes no arguments

        Returns:
            dict: A dictionary containing the user's profile data as returned by the API.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.

        Tags:
            get, profile, user, api
        """
        url = f"{self.base_url}/me"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_playlist(
        self, playlist_id, market=None, fields=None, additional_types=None
    ) -> Any:
        """
        Retrieves a playlist from the API using the specified playlist ID.

        Args:
            playlist_id: The ID of the playlist to retrieve. Required.
            market: Optional. An ISO 3166-1 alpha-2 country code or the string 'from_token' to specify the market to get content for.
            fields: Optional. Filters for the query: a comma-separated list of the fields to return. If omitted, all fields are returned.
            additional_types: Optional. A comma-separated list of item types that your client supports besides the default track type.

        Returns:
            A dictionary containing the playlist data in JSON format.

        Raises:
            ValueError: If the required playlist_id parameter is None or not provided.
            HTTPError: If the API request fails (through raise_for_status()).

        Tags:
            retrieve, get, playlist, api, important
        """
        if playlist_id is None:
            raise ValueError("Missing required parameter 'playlist_id'")
        url = f"{self.base_url}/playlists/{playlist_id}"
        query_params = {
            k: v
            for k, v in [
                ("market", market),
                ("fields", fields),
                ("additional_types", additional_types),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def change_playlist_details(
        self, playlist_id, name=None, public=None, collaborative=None, description=None
    ) -> Any:
        """
        Update the details of an existing playlist with the specified attributes.

        Args:
            playlist_id: str. The unique identifier of the playlist to update. Must not be None.
            name: Optional[str]. New name for the playlist. If None, the name is not changed.
            public: Optional[bool]. Whether the playlist should be public. If None, the setting is unchanged.
            collaborative: Optional[bool]. Whether the playlist should be collaborative. If None, the setting is unchanged.
            description: Optional[str]. New description for the playlist. If None, the description is not changed.

        Returns:
            dict. The JSON response containing the updated playlist details.

        Raises:
            ValueError: Raised if 'playlist_id' is None.
            requests.HTTPError: Raised if the API request returns an unsuccessful status code.

        Tags:
            change, update, playlist, management, api
        """
        if playlist_id is None:
            raise ValueError("Missing required parameter 'playlist_id'")
        request_body = {
            "name": name,
            "public": public,
            "collaborative": collaborative,
            "description": description,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/playlists/{playlist_id}"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_playlists_tracks(
        self,
        playlist_id,
        market=None,
        fields=None,
        limit=None,
        offset=None,
        additional_types=None,
    ) -> Any:
        """
        Retrieves the tracks of a specified playlist from the API, applying optional filters and pagination parameters.

        Args:
            playlist_id: str. The unique identifier of the playlist to retrieve tracks from.
            market: Optional[str]. An ISO 3166-1 alpha-2 country code, or 'from_token'. Filters the response to a specific market.
            fields: Optional[str]. Comma-separated list of Spotify fields to include in the response.
            limit: Optional[int]. The maximum number of items to return (default and maximum are API-dependent).
            offset: Optional[int]. The index of the first item to return for pagination.
            additional_types: Optional[str]. Types of items to return, e.g., 'track', 'episode'.

        Returns:
            dict. JSON response containing the playlist's tracks and associated metadata.

        Raises:
            ValueError: If 'playlist_id' is None.
            requests.HTTPError: If the API request fails due to a client or server error.

        Tags:
            get, list, playlist, tracks, api, management, important
        """
        if playlist_id is None:
            raise ValueError("Missing required parameter 'playlist_id'")
        url = f"{self.base_url}/playlists/{playlist_id}/tracks"
        query_params = {
            k: v
            for k, v in [
                ("market", market),
                ("fields", fields),
                ("limit", limit),
                ("offset", offset),
                ("additional_types", additional_types),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_tracks_to_playlist(self, playlist_id, position=None, uris=None) -> Any:
        """
        Adds one or more tracks to a specified playlist at an optional position.

        Args:
            playlist_id: str. The unique identifier of the playlist to which tracks will be added.
            position: Optional[int]. The position in the playlist where the tracks should be inserted. If not specified, tracks will be added to the end.
            uris: Optional[List[str]]. A list of track URIs to add to the playlist. If not specified, no tracks will be added.

        Returns:
            dict: The JSON response from the API containing information about the operation result.

        Raises:
            ValueError: If 'playlist_id' is not provided.
            requests.HTTPError: If the HTTP request to the external API fails or returns an error status code.

        Tags:
            add, playlist-management, tracks, api, important
        """
        if playlist_id is None:
            raise ValueError("Missing required parameter 'playlist_id'")
        request_body = {
            "uris": uris,
            "position": position,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/playlists/{playlist_id}/tracks"
        query_params = {
            k: v for k, v in [("position", position), ("uris", uris)] if v is not None
        }
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def reorder_or_replace_playlists_tracks(
        self,
        playlist_id,
        uris=None,
        range_start=None,
        insert_before=None,
        range_length=None,
        snapshot_id=None,
    ) -> Any:
        """
        Reorders or replaces tracks in a playlist by moving, inserting, or replacing track entries using the specified parameters.

        Args:
            playlist_id: str. The Spotify ID of the playlist to be modified. Required.
            uris: Optional[list of str]. The new track URIs to replace the playlist's tracks. If provided, replaces tracks instead of reordering.
            range_start: Optional[int]. The position of the first track to be reordered. Required for reordering.
            insert_before: Optional[int]. The position where the reordered tracks should be inserted. Required for reordering.
            range_length: Optional[int]. The number of tracks to be reordered. Defaults to 1 if not specified.
            snapshot_id: Optional[str]. The playlist's snapshot ID against which to apply changes, used for concurrency control.

        Returns:
            dict. The JSON response from the Spotify API containing the new snapshot ID of the playlist.

        Raises:
            ValueError: If 'playlist_id' is None.
            requests.HTTPError: If the HTTP request to the API fails (e.g., due to invalid parameters or network issues).

        Tags:
            reorder, replace, playlist, tracks, management, api
        """
        if playlist_id is None:
            raise ValueError("Missing required parameter 'playlist_id'")
        request_body = {
            "uris": uris,
            "range_start": range_start,
            "insert_before": insert_before,
            "range_length": range_length,
            "snapshot_id": snapshot_id,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/playlists/{playlist_id}/tracks"
        query_params = {k: v for k, v in [("uris", uris)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_a_list_of_current_users_playlists(self, limit=None, offset=None) -> Any:
        """
        Retrieves a list of the current user's playlists with optional pagination controls.

        Args:
            limit: int or None. The maximum number of playlists to return. If None, the default set by the API is used.
            offset: int or None. The index of the first playlist to return. If None, the default set by the API is used.

        Returns:
            dict. A JSON response containing the playlists of the current user.

        Raises:
            requests.HTTPError: If the HTTP request to the API fails or returns a non-success status code.

        Tags:
            list, playlists, user, api
        """
        url = f"{self.base_url}/me/playlists"
        query_params = {
            k: v for k, v in [("limit", limit), ("offset", offset)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_saved_albums(self, limit=None, offset=None, market=None) -> Any:
        """
        Retrieves the current user's saved albums from the Spotify library with optional pagination and market filtering.

        Args:
            limit: Optional; maximum number of albums to return. If not specified, the default set by the API is used.
            offset: Optional; the index of the first album to return. Used for pagination.
            market: Optional; an ISO 3166-1 alpha-2 country code to filter albums by market availability.

        Returns:
            A JSON object containing the list of the user's saved albums and related pagination details as returned by the Spotify API.

        Raises:
            requests.HTTPError: If the HTTP request to the Spotify API fails or returns an unsuccessful status code.

        Tags:
            get, list, albums, user-library, spotify, api
        """
        url = f"{self.base_url}/me/albums"
        query_params = {
            k: v
            for k, v in [("limit", limit), ("offset", offset), ("market", market)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def check_users_saved_albums(self, ids) -> Any:
        """
        Checks if the specified albums are saved in the current user's Spotify library.

        Args:
            ids: A comma-separated string or list of Spotify album IDs to check for saved status.

        Returns:
            A list of boolean values indicating whether each album specified in 'ids' is saved in the user's library.

        Raises:
            ValueError: If the 'ids' parameter is None.
            requests.HTTPError: If the HTTP request to the Spotify API fails.

        Tags:
            check, spotify, albums, user-library
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/me/albums/contains"
        query_params = {k: v for k, v in [("ids", ids)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_saved_tracks(self, market=None, limit=None, offset=None) -> Any:
        """
        Retrieves the current user's saved tracks from the Spotify library with optional filtering and pagination.

        Args:
            market: Optional; an ISO 3166-1 alpha-2 country code. Filters the results to tracks available in the specified market.
            limit: Optional; maximum number of items to return (usually between 1 and 50).
            offset: Optional; the index of the first item to return, used for pagination.

        Returns:
            A JSON object containing a paginated list of the user's saved tracks and associated metadata.

        Raises:
            requests.HTTPError: Raised if the HTTP request to the Spotify API fails or returns a non-success status code.

        Tags:
            list, get, user-data, spotify, tracks, batch
        """
        url = f"{self.base_url}/me/tracks"
        query_params = {
            k: v
            for k, v in [("market", market), ("limit", limit), ("offset", offset)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def save_tracks_user(self, ids) -> Any:
        """
        Saves one or more tracks to the current user's music library.

        Args:
            ids: A list or comma-separated string of track IDs to save to the user's library. Must not be None.

        Returns:
            The JSON response from the API as a Python object, typically confirming the successful saving of tracks.

        Raises:
            ValueError: If the 'ids' parameter is None.
            HTTPError: If the HTTP request to save tracks fails (raised by response.raise_for_status()).

        Tags:
            save, user-library, tracks, api
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        request_body = {
            "ids": ids,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/me/tracks"
        query_params = {k: v for k, v in [("ids", ids)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def check_users_saved_tracks(self, ids) -> Any:
        """
        Checks if the current user has saved specific tracks in their Spotify library.

        Args:
            ids: A comma-separated string of Spotify track IDs to check for saved status.

        Returns:
            A list of boolean values indicating whether each track ID is saved by the current user.

        Raises:
            ValueError: Raised when the 'ids' parameter is None.
            HTTPError: Raised if the HTTP request to the Spotify API fails.

        Tags:
            check, user-library, spotify, status
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/me/tracks/contains"
        query_params = {k: v for k, v in [("ids", ids)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_saved_episodes(self, market=None, limit=None, offset=None) -> Any:
        """
        Retrieves the current user's saved podcast episodes from the service, with optional support for market, pagination, and result limits.

        Args:
            market: Optional; a string specifying the market (country code) to filter episode availability.
            limit: Optional; an integer specifying the maximum number of episodes to return.
            offset: Optional; an integer specifying the index of the first episode to return for pagination.

        Returns:
            A JSON-decoded response containing the user's saved episodes and associated metadata.

        Raises:
            requests.HTTPError: If the HTTP request fails or the API returns a non-success status code.

        Tags:
            get, list, user-content, episodes, ai
        """
        url = f"{self.base_url}/me/episodes"
        query_params = {
            k: v
            for k, v in [("market", market), ("limit", limit), ("offset", offset)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def save_episodes_user(self, ids) -> Any:
        """
        Saves episodes to the user's library using the provided list of episode IDs.

        Args:
            ids: A list of episode IDs to be saved to the user's library.

        Returns:
            The JSON response from the server confirming successful saving of episodes.

        Raises:
            ValueError: Raised if the 'ids' parameter is None.
            HTTPError: Raised if the HTTP PUT request to the server fails.

        Tags:
            save, episodes, user-management, async-job
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        request_body = {
            "ids": ids,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/me/episodes"
        query_params = {k: v for k, v in [("ids", ids)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def check_users_saved_episodes(self, ids) -> Any:
        """
        Checks if the specified episodes are saved in the current user's library.

        Args:
            ids: A list or comma-separated string of episode IDs to check for presence in the user's saved episodes. Must not be None.

        Returns:
            A JSON-compatible object (typically a list of booleans) indicating whether each episode ID is present in the user's saved episodes.

        Raises:
            ValueError: Raised if the 'ids' parameter is None.
            HTTPError: Raised if the HTTP request to the remote service fails with a non-success status code.

        Tags:
            check, status, async_job, ai, management
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/me/episodes/contains"
        query_params = {k: v for k, v in [("ids", ids)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_saved_shows(self, limit=None, offset=None) -> Any:
        """
        Retrieves the current user's saved shows from the Spotify API with optional pagination.

        Args:
            limit: Optional; maximum number of shows to return. Must be a positive integer or None for default behavior.
            offset: Optional; the index of the first show to return. Must be a non-negative integer or None for default behavior.

        Returns:
            A JSON-decoded object containing the list of saved shows and associated metadata.

        Raises:
            HTTPError: Raised if the HTTP request to the Spotify API returns an unsuccessful status code.

        Tags:
            get, list, shows, spotify, user-content
        """
        url = f"{self.base_url}/me/shows"
        query_params = {
            k: v for k, v in [("limit", limit), ("offset", offset)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def check_users_saved_shows(self, ids) -> Any:
        """
        Checks if the specified shows are saved in the current user's library.

        Args:
            ids: A comma-separated string or list of show IDs to check for presence in the user's library.

        Returns:
            A JSON-compatible object (typically a list of booleans) indicating, for each show ID, whether it is saved in the user's library.

        Raises:
            ValueError: If the required 'ids' parameter is not provided.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status code.

        Tags:
            check, library, status, async-job, ai
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/me/shows/contains"
        query_params = {k: v for k, v in [("ids", ids)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_profile(self, user_id) -> Any:
        """
        Retrieves the profile information for a specific user by user ID.

        Args:
            user_id: The unique identifier of the user whose profile information is to be retrieved.

        Returns:
            A JSON-decoded object containing the user's profile information.

        Raises:
            ValueError: Raised if the 'user_id' parameter is not provided (i.e., is None).
            requests.exceptions.HTTPError: Raised if the HTTP request to fetch the user's profile fails (non-success status code).

        Tags:
            get, profile, user, api
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        url = f"{self.base_url}/users/{user_id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_list_users_playlists(self, user_id, limit=None, offset=None) -> Any:
        """
        Retrieves a list of playlists for a specified user.

        Args:
            user_id: The ID of the user whose playlists to retrieve. Required.
            limit: The maximum number of playlists to return. Optional.
            offset: The index of the first playlist to return. Used for pagination. Optional.

        Returns:
            A JSON object containing the user's playlists data.

        Raises:
            ValueError: Raised when the required parameter 'user_id' is None.
            HTTPError: Raised when the HTTP request fails.

        Tags:
            retrieve, list, playlists, user, pagination, api
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        url = f"{self.base_url}/users/{user_id}/playlists"
        query_params = {
            k: v for k, v in [("limit", limit), ("offset", offset)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_playlist(
        self, user_id, name, public=None, collaborative=None, description=None
    ) -> Any:
        """
        Creates a new playlist for a specified user with optional visibility, collaboration, and description settings.

        Args:
            user_id: str. The unique identifier of the user for whom the playlist is to be created.
            name: str. The name of the new playlist.
            public: Optional[bool]. If True, the playlist is public; if False, it is private. If None, the default visibility is used.
            collaborative: Optional[bool]. If True, the playlist can be edited by other users. If None, the playlist is not collaborative.
            description: Optional[str]. An optional description for the playlist.

        Returns:
            dict. A dictionary containing the created playlist's details as returned by the API.

        Raises:
            ValueError: If either 'user_id' or 'name' is not provided.
            requests.HTTPError: If the HTTP request to create the playlist fails.

        Tags:
            create, playlist, api, management, important
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user_id'")
        if name is None:
            raise ValueError("Missing required parameter 'name'")
        request_body = {
            "name": name,
            "public": public,
            "collaborative": collaborative,
            "description": description,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/users/{user_id}/playlists"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def follow_playlist(self, playlist_id, public=None) -> Any:
        """
        Follows a Spotify playlist on behalf of the current user.

        Args:
            playlist_id: str. The Spotify ID of the playlist to follow. Must not be None.
            public: Optional[bool]. Whether the playlist should be public (visible on the user's profile). If None, defaults to the server-side default.

        Returns:
            Any. The JSON response from the Spotify API confirming the follow action.

        Raises:
            ValueError: If 'playlist_id' is None.
            HTTPError: If the HTTP request fails or the API returns an error status.

        Tags:
            follow, playlist, api, async-job
        """
        if playlist_id is None:
            raise ValueError("Missing required parameter 'playlist_id'")
        request_body = {
            "public": public,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/playlists/{playlist_id}/followers"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def unfollow_playlist(self, playlist_id) -> Any:
        """
        Unfollows the specified playlist by deleting the current user's following relationship.

        Args:
            playlist_id: The unique identifier of the playlist to unfollow. Must not be None.

        Returns:
            The API response as a JSON-compatible object containing details of the unfollow operation.

        Raises:
            ValueError: If 'playlist_id' is None.
            requests.HTTPError: If the API request fails and returns an unsuccessful HTTP status code.

        Tags:
            unfollow, playlist-management, delete, async-job
        """
        if playlist_id is None:
            raise ValueError("Missing required parameter 'playlist_id'")
        url = f"{self.base_url}/playlists/{playlist_id}/followers"
        query_params = {}
        response = self._delete(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_featured_playlists(self, locale=None, limit=None, offset=None) -> Any:
        """
        Retrieves a list of Spotify's featured playlists with optional localization, result limiting, and pagination.

        Args:
            locale: Optional; a string specifying the language and country (e.g., 'en_US') to localize the playlist names and descriptions. If None, the server default is used.
            limit: Optional; an integer specifying the maximum number of playlists to return. If None, the server default is used.
            offset: Optional; an integer specifying the index of the first playlist to return (for pagination). If None, the server default is used.

        Returns:
            A dictionary containing the JSON response from the Spotify Web API with details about the featured playlists.

        Raises:
            requests.HTTPError: If the HTTP request to the Spotify API fails or returns an unsuccessful status code.

        Tags:
            get, list, playlists, featured, api, music
        """
        url = f"{self.base_url}/browse/featured-playlists"
        query_params = {
            k: v
            for k, v in [("locale", locale), ("limit", limit), ("offset", offset)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_categories(self, locale=None, limit=None, offset=None) -> Any:
        """
        Retrieves a list of category objects from the API with optional locale, limit, and offset filters.

        Args:
            locale: Optional; str. Locale identifier (e.g., 'en_US') to localize the category names returned.
            limit: Optional; int. Maximum number of categories to return in the response.
            offset: Optional; int. The index of the first category to return, used for pagination.

        Returns:
            dict. The JSON response from the API containing category data.

        Raises:
            requests.HTTPError: If the HTTP request to the API endpoint returns an unsuccessful status code.

        Tags:
            get, list, categories, api
        """
        url = f"{self.base_url}/browse/categories"
        query_params = {
            k: v
            for k, v in [("locale", locale), ("limit", limit), ("offset", offset)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_a_category(self, category_id, locale=None) -> Any:
        """
        Retrieve detailed information about a specific category by its ID, optionally localized to a given locale.

        Args:
            category_id: str. The unique identifier of the category to retrieve.
            locale: Optional[str]. The locale code to use for localization of the category information. If None, the default locale is used.

        Returns:
            dict. A JSON object containing the category details as returned by the API.

        Raises:
            ValueError: If 'category_id' is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an unsuccessful status code.

        Tags:
            get, category, api
        """
        if category_id is None:
            raise ValueError("Missing required parameter 'category_id'")
        url = f"{self.base_url}/browse/categories/{category_id}"
        query_params = {k: v for k, v in [("locale", locale)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_a_categories_playlists(self, category_id, limit=None, offset=None) -> Any:
        """
        Retrieves playlists associated with a specified category from the API.

        Args:
            category_id: str. The unique identifier for the category whose playlists are to be fetched.
            limit: Optional[int]. The maximum number of playlists to return. If None, the default API value is used.
            offset: Optional[int]. The index of the first playlist to return. Used for pagination. If None, the default API value is used.

        Returns:
            dict. The JSON response containing playlist data for the specified category.

        Raises:
            ValueError: If 'category_id' is None.
            requests.HTTPError: If the API request fails or returns a non-success status code.

        Tags:
            get, list, playlists, categories, api, management
        """
        if category_id is None:
            raise ValueError("Missing required parameter 'category_id'")
        url = f"{self.base_url}/browse/categories/{category_id}/playlists"
        query_params = {
            k: v for k, v in [("limit", limit), ("offset", offset)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_playlist_cover(self, playlist_id) -> Any:
        """
        Retrieves the cover image(s) for a specified playlist by its unique ID.

        Args:
            playlist_id: The unique identifier of the playlist for which to fetch cover images.

        Returns:
            The JSON response containing playlist cover image metadata as returned by the API.

        Raises:
            ValueError: Raised when the required parameter 'playlist_id' is None.
            HTTPError: Raised if the HTTP request to retrieve the cover images fails.

        Tags:
            get, playlist, cover-image, api
        """
        if playlist_id is None:
            raise ValueError("Missing required parameter 'playlist_id'")
        url = f"{self.base_url}/playlists/{playlist_id}/images"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_new_releases(self, limit=None, offset=None) -> Any:
        """
        Retrieves a list of new music releases with optional pagination parameters.

        Args:
            limit: Optional; int. The maximum number of items to return. If not specified, the server default is used.
            offset: Optional; int. The index of the first item to return. Used for pagination. If not specified, the server default is used.

        Returns:
            dict. A JSON object containing metadata and a list of new releases.

        Raises:
            requests.HTTPError: If the HTTP request to fetch new releases returns an unsuccessful status code.

        Tags:
            get, list, browse, music, async-job, api
        """
        url = f"{self.base_url}/browse/new-releases"
        query_params = {
            k: v for k, v in [("limit", limit), ("offset", offset)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_followed(self, type, after=None, limit=None) -> Any:
        """
        Retrieves the list of entities the current user is following, with support for pagination and limiting results.

        Args:
            type: str. The type of entity to return (e.g., 'artist', 'user'). Required.
            after: str or None. The cursor value to fetch items after a specific entity for pagination. Optional.
            limit: int or None. The maximum number of items to return. Optional.

        Returns:
            dict. A JSON-decoded response containing the list of followed entities and pagination details.

        Raises:
            ValueError: If the 'type' parameter is not provided.
            HTTPError: If the HTTP request to the API fails (raised by requests.Response.raise_for_status()).

        Tags:
            get, list, follow-management, api
        """
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        url = f"{self.base_url}/me/following"
        query_params = {
            k: v
            for k, v in [("type", type), ("after", after), ("limit", limit)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def follow_artists_users(self, type, ids) -> Any:
        """
        Follows one or more artists or users on behalf of the current user.

        Args:
            type: str. The type of entity to follow. Valid values are typically 'artist' or 'user'.
            ids: str or list of str. The Spotify IDs of the artists or users to follow. Can be a single ID or a comma-separated/list of IDs.

        Returns:
            dict. The response from the API as a parsed JSON object containing the result of the follow operation.

        Raises:
            ValueError: If 'type' or 'ids' is None, indicating a missing required parameter.
            HTTPError: If the API request fails or returns an error status code.

        Tags:
            follow, users, artists, api
        """
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        request_body = {
            "ids": ids,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/me/following"
        query_params = {
            k: v for k, v in [("type", type), ("ids", ids)] if v is not None
        }
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def check_current_user_follows(self, type, ids) -> Any:
        """
        Check if the current user follows specific Spotify users or artists.

        Args:
            type: str. The type of entity to check, either 'artist' or 'user'.
            ids: str or list of str. The Spotify IDs of the users or artists to check, separated by commas if a string.

        Returns:
            list of bool. A list indicating, for each provided ID, whether the current user is following the corresponding user or artist.

        Raises:
            ValueError: If the 'type' or 'ids' parameter is missing or None.
            requests.HTTPError: If the HTTP request to the API fails or returns an error status.

        Tags:
            check, follows, spotify, user, artist, api
        """
        if type is None:
            raise ValueError("Missing required parameter 'type'")
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/me/following/contains"
        query_params = {
            k: v for k, v in [("type", type), ("ids", ids)] if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def check_if_user_follows_playlist(self, playlist_id, ids) -> Any:
        """
        Checks if one or more users follow a specified playlist.

        Args:
            playlist_id: The unique identifier of the playlist to check.
            ids: A comma-separated list or iterable of user IDs to be checked for following the playlist.

        Returns:
            A JSON-compatible object indicating, for each user ID, whether that user is following the playlist.

        Raises:
            ValueError: If 'playlist_id' or 'ids' is None.
            requests.HTTPError: If the API request fails or returns an error response.

        Tags:
            check, playlist, followers, api
        """
        if playlist_id is None:
            raise ValueError("Missing required parameter 'playlist_id'")
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/playlists/{playlist_id}/followers/contains"
        query_params = {k: v for k, v in [("ids", ids)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_several_audio_features(self, ids) -> Any:
        """
        Retrieves audio feature information for multiple tracks using their IDs.

        Args:
            ids: A comma-separated string or list of track IDs for which to retrieve audio features.

        Returns:
            A JSON-decoded object containing audio features for the specified tracks.

        Raises:
            ValueError: If the 'ids' parameter is None.
            requests.HTTPError: If the HTTP request to the audio features endpoint fails.

        Tags:
            get, audio-features, batch, ai
        """
        if ids is None:
            raise ValueError("Missing required parameter 'ids'")
        url = f"{self.base_url}/audio-features"
        query_params = {k: v for k, v in [("ids", ids)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_audio_features(self, id) -> Any:
        """
        Retrieves audio feature information for a given identifier from the API.

        Args:
            id: The identifier of the audio resource for which to fetch features.

        Returns:
            A dictionary containing the audio feature data for the specified resource.

        Raises:
            ValueError: Raised if the 'id' parameter is None.
            requests.HTTPError: Raised if the HTTP request to the API fails with a bad status code.

        Tags:
            get, audio-features, api, fetch
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/audio-features/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_audio_analysis(self, id) -> Any:
        """
        Retrieves the audio analysis data for a specified audio ID from the API.

        Args:
            id: The unique identifier of the audio resource to analyze. Must not be None.

        Returns:
            A JSON object containing audio analysis data for the specified audio ID.

        Raises:
            ValueError: If the 'id' parameter is None.
            requests.HTTPError: If the HTTP request to the audio analysis endpoint fails (e.g., network error or non-2xx response).

        Tags:
            get, audio-analysis, api, fetch
        """
        if id is None:
            raise ValueError("Missing required parameter 'id'")
        url = f"{self.base_url}/audio-analysis/{id}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_recommendations(
        self,
        limit=None,
        market=None,
        seed_artists=None,
        seed_genres=None,
        seed_tracks=None,
        min_acousticness=None,
        max_acousticness=None,
        target_acousticness=None,
        min_danceability=None,
        max_danceability=None,
        target_danceability=None,
        min_duration_ms=None,
        max_duration_ms=None,
        target_duration_ms=None,
        min_energy=None,
        max_energy=None,
        target_energy=None,
        min_instrumentalness=None,
        max_instrumentalness=None,
        target_instrumentalness=None,
        min_key=None,
        max_key=None,
        target_key=None,
        min_liveness=None,
        max_liveness=None,
        target_liveness=None,
        min_loudness=None,
        max_loudness=None,
        target_loudness=None,
        min_mode=None,
        max_mode=None,
        target_mode=None,
        min_popularity=None,
        max_popularity=None,
        target_popularity=None,
        min_speechiness=None,
        max_speechiness=None,
        target_speechiness=None,
        min_tempo=None,
        max_tempo=None,
        target_tempo=None,
        min_time_signature=None,
        max_time_signature=None,
        target_time_signature=None,
        min_valence=None,
        max_valence=None,
        target_valence=None,
    ) -> Any:
        """
        Retrieves track recommendations based on a combination of seed values and audio feature constraints.

        Args:
            limit: Optional; maximum number of recommendations to return.
            market: Optional; an ISO 3166-1 alpha-2 country code to filter the response.
            seed_artists: Optional; list or comma-separated string of artist IDs to use as seeds.
            seed_genres: Optional; list or comma-separated string of genre names to use as seeds.
            seed_tracks: Optional; list or comma-separated string of track IDs to use as seeds.
            min_acousticness: Optional; minimum acousticness value (float) of tracks to return.
            max_acousticness: Optional; maximum acousticness value (float) of tracks to return.
            target_acousticness: Optional; target acousticness value (float) for recommended tracks.
            min_danceability: Optional; minimum danceability value (float) of tracks to return.
            max_danceability: Optional; maximum danceability value (float) of tracks to return.
            target_danceability: Optional; target danceability value (float) for recommended tracks.
            min_duration_ms: Optional; minimum duration (in milliseconds) for tracks to return.
            max_duration_ms: Optional; maximum duration (in milliseconds) for tracks to return.
            target_duration_ms: Optional; target duration (in milliseconds) for recommended tracks.
            min_energy: Optional; minimum energy value (float) of tracks to return.
            max_energy: Optional; maximum energy value (float) of tracks to return.
            target_energy: Optional; target energy value (float) for recommended tracks.
            min_instrumentalness: Optional; minimum instrumentalness value (float) of tracks to return.
            max_instrumentalness: Optional; maximum instrumentalness value (float) of tracks to return.
            target_instrumentalness: Optional; target instrumentalness value (float) for recommended tracks.
            min_key: Optional; minimum key value (int) for tracks to return.
            max_key: Optional; maximum key value (int) for tracks to return.
            target_key: Optional; target key value (int) for recommended tracks.
            min_liveness: Optional; minimum liveness value (float) of tracks to return.
            max_liveness: Optional; maximum liveness value (float) of tracks to return.
            target_liveness: Optional; target liveness value (float) for recommended tracks.
            min_loudness: Optional; minimum loudness value (float, in dB) of tracks to return.
            max_loudness: Optional; maximum loudness value (float, in dB) of tracks to return.
            target_loudness: Optional; target loudness value (float, in dB) for recommended tracks.
            min_mode: Optional; minimum mode value (int: 0 for minor, 1 for major) for tracks to return.
            max_mode: Optional; maximum mode value (int: 0 for minor, 1 for major) for tracks to return.
            target_mode: Optional; target mode value (int: 0 for minor, 1 for major) for recommended tracks.
            min_popularity: Optional; minimum popularity (int) of tracks to return.
            max_popularity: Optional; maximum popularity (int) of tracks to return.
            target_popularity: Optional; target popularity (int) for recommended tracks.
            min_speechiness: Optional; minimum speechiness value (float) of tracks to return.
            max_speechiness: Optional; maximum speechiness value (float) of tracks to return.
            target_speechiness: Optional; target speechiness value (float) for recommended tracks.
            min_tempo: Optional; minimum tempo (float, BPM) of tracks to return.
            max_tempo: Optional; maximum tempo (float, BPM) of tracks to return.
            target_tempo: Optional; target tempo (float, BPM) for recommended tracks.
            min_time_signature: Optional; minimum time signature (int) for tracks to return.
            max_time_signature: Optional; maximum time signature (int) for tracks to return.
            target_time_signature: Optional; target time signature (int) for recommended tracks.
            min_valence: Optional; minimum valence value (float) of tracks to return.
            max_valence: Optional; maximum valence value (float) of tracks to return.
            target_valence: Optional; target valence value (float) for recommended tracks.

        Returns:
            A JSON object containing a list of recommended tracks matching the provided seeds and filter criteria.

        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
            requests.RequestException: If a network-related error occurs during the request.

        Tags:
            get, recommendations, ai, music, filter
        """
        url = f"{self.base_url}/recommendations"
        query_params = {
            k: v
            for k, v in [
                ("limit", limit),
                ("market", market),
                ("seed_artists", seed_artists),
                ("seed_genres", seed_genres),
                ("seed_tracks", seed_tracks),
                ("min_acousticness", min_acousticness),
                ("max_acousticness", max_acousticness),
                ("target_acousticness", target_acousticness),
                ("min_danceability", min_danceability),
                ("max_danceability", max_danceability),
                ("target_danceability", target_danceability),
                ("min_duration_ms", min_duration_ms),
                ("max_duration_ms", max_duration_ms),
                ("target_duration_ms", target_duration_ms),
                ("min_energy", min_energy),
                ("max_energy", max_energy),
                ("target_energy", target_energy),
                ("min_instrumentalness", min_instrumentalness),
                ("max_instrumentalness", max_instrumentalness),
                ("target_instrumentalness", target_instrumentalness),
                ("min_key", min_key),
                ("max_key", max_key),
                ("target_key", target_key),
                ("min_liveness", min_liveness),
                ("max_liveness", max_liveness),
                ("target_liveness", target_liveness),
                ("min_loudness", min_loudness),
                ("max_loudness", max_loudness),
                ("target_loudness", target_loudness),
                ("min_mode", min_mode),
                ("max_mode", max_mode),
                ("target_mode", target_mode),
                ("min_popularity", min_popularity),
                ("max_popularity", max_popularity),
                ("target_popularity", target_popularity),
                ("min_speechiness", min_speechiness),
                ("max_speechiness", max_speechiness),
                ("target_speechiness", target_speechiness),
                ("min_tempo", min_tempo),
                ("max_tempo", max_tempo),
                ("target_tempo", target_tempo),
                ("min_time_signature", min_time_signature),
                ("max_time_signature", max_time_signature),
                ("target_time_signature", target_time_signature),
                ("min_valence", min_valence),
                ("max_valence", max_valence),
                ("target_valence", target_valence),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_recommendation_genres(
        self,
    ) -> Any:
        """
        Retrieves a list of available genre seeds for recommendations from the remote API.

        Args:
            None: This function takes no arguments

        Returns:
            dict: A JSON object containing available genre seeds for recommendations.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request to the API fails or returns an error status code.

        Tags:
            get, list, api, recommendation, genres
        """
        url = f"{self.base_url}/recommendations/available-genre-seeds"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_information_about_the_users_current_playback(
        self, market=None, additional_types=None
    ) -> Any:
        """
        Retrieves information about the user's current playback state from the music service.

        Args:
            market: Optional; a string specifying an ISO 3166-1 alpha-2 country code to filter the response content. Defaults to None.
            additional_types: Optional; a comma-separated string specifying additional item types to include in the response. Defaults to None.

        Returns:
            A JSON object containing the user's current playback information, such as track, device, and playback state.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request to the music service API fails or returns an error status code.

        Tags:
            get, playback, user, status, api
        """
        url = f"{self.base_url}/me/player"
        query_params = {
            k: v
            for k, v in [("market", market), ("additional_types", additional_types)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def transfer_a_users_playback(self, device_ids, play=None) -> Any:
        """
        Transfers the playback of a user's current session to one or more specified devices.

        Args:
            device_ids: list or str. A list of device IDs (or a single device ID) to which playback should be transferred. This parameter is required.
            play: bool or None. Whether playback should start on the new device(s) after transfer. If None, the playback state is not changed. Optional.

        Returns:
            dict. A JSON response from the server, typically containing the status or details of the playback transfer.

        Raises:
            ValueError: Raised if 'device_ids' is None.
            requests.HTTPError: Raised if the underlying HTTP request fails or returns an error status code.

        Tags:
            transfer, playback, management, api-call
        """
        if device_ids is None:
            raise ValueError("Missing required parameter 'device_ids'")
        request_body = {
            "device_ids": device_ids,
            "play": play,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/me/player"
        query_params = {}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_a_users_available_devices(
        self,
    ) -> Any:
        """
        Retrieves the list of devices available to the current user for playback control.

        Args:
            None: This function takes no arguments

        Returns:
            dict: A JSON object containing information about the user's available playback devices.

        Raises:
            requests.HTTPError: If the HTTP request to the devices endpoint fails or returns a non-success status code.

        Tags:
            get, list, devices, user, management
        """
        url = f"{self.base_url}/me/player/devices"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_the_users_currently_playing_track(
        self, market=None, additional_types=None
    ) -> Any:
        """
        Retrieves information about the track currently being played by the user.

        Args:
            market: Optional; a string specifying the market (country code) to filter the track data, ensuring results are relevant to a particular geographic location. Defaults to None.
            additional_types: Optional; a string or comma-separated list specifying additional item types (such as 'episode') to include in the response. Defaults to None.

        Returns:
            dict: A dictionary containing details about the currently playing track, or None if no data is available.

        Raises:
            requests.HTTPError: If the underlying HTTP request fails or returns an unsuccessful status code.

        Tags:
            get, track, player, user, async_job
        """
        url = f"{self.base_url}/me/player/currently-playing"
        query_params = {
            k: v
            for k, v in [("market", market), ("additional_types", additional_types)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def start_a_users_playback(
        self, device_id=None, context_uri=None, uris=None, offset=None, position_ms=None
    ) -> Any:
        """
        Starts or resumes playback of a user's Spotify player on the specified device, context, or track list.

        Args:
            device_id: Optional[str]. The Spotify device ID on which playback should start. If not specified, the user's current active device is used.
            context_uri: Optional[str]. Spotify URI of the context to play (album, playlist, or artist). Mutually exclusive with 'uris'.
            uris: Optional[list[str]]. List of Spotify track URIs to play. Mutually exclusive with 'context_uri'.
            offset: Optional[dict or int or str]. Indicates from which position in 'uris' or 'context_uri' playback should start. Can be a dict specifying 'position' or 'uri', or an integer index.
            position_ms: Optional[int]. Start playback at this position in milliseconds.

        Returns:
            Any. The JSON-parsed response from the Spotify Web API containing the result of the playback request.

        Raises:
            requests.HTTPError: If the underlying HTTP request fails or an error response is returned from the Spotify Web API.

        Tags:
            start, playback, ai, management, async_job
        """
        request_body = {
            "context_uri": context_uri,
            "uris": uris,
            "offset": offset,
            "position_ms": position_ms,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/me/player/play"
        query_params = {k: v for k, v in [("device_id", device_id)] if v is not None}
        response = self._put(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def pause_a_users_playback(self, device_id=None) -> Any:
        """
        Pauses the current playback for the authenticated user.

        Args:
            device_id: Optional string representing the Spotify device ID on which playback should be paused. If not provided, the user's currently active device is targeted.

        Returns:
            The JSON response from the Spotify API. This will typically be an empty object if the request was successful.

        Raises:
            HTTPError: Raised when the Spotify API returns an error response, such as when the user doesn't have an active device, the user doesn't have a premium account, or there's an authentication issue.

        Tags:
            pause, playback, control, spotify
        """
        url = f"{self.base_url}/me/player/pause"
        query_params = {k: v for k, v in [("device_id", device_id)] if v is not None}
        response = self._put(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def skip_users_playback_to_next_track(self, device_id=None) -> Any:
        """
        Skips the user's playback to the next track on the current or specified device.

        Args:
            device_id: Optional; the ID of the device on which to skip to the next track. If None, the currently active device is used.

        Returns:
            dict: The response from the API after attempting to skip to the next track.

        Raises:
            requests.HTTPError: If the HTTP request to skip to the next track fails with an unsuccessful status code.

        Tags:
            skip, playback-control, user, spotify-api
        """
        url = f"{self.base_url}/me/player/next"
        query_params = {k: v for k, v in [("device_id", device_id)] if v is not None}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def skip_users_playback_to_previous_track(self, device_id=None) -> Any:
        """
        Skips the user's playback to the previous track on the active or specified device.

        Args:
            device_id: Optional; string representing the device ID to control. If not provided, defaults to the user's currently active device.

        Returns:
            The JSON response from the API after attempting to skip to the previous track.

        Raises:
            requests.HTTPError: If the HTTP request to the playback API fails or returns an error status.

        Tags:
            playback-control, skip, previous-track, user, api
        """
        url = f"{self.base_url}/me/player/previous"
        query_params = {k: v for k, v in [("device_id", device_id)] if v is not None}
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def seek_to_position_in_currently_playing_track(
        self, position_ms, device_id=None
    ) -> Any:
        """
        Seeks to the specified position in the currently playing track for the user.

        Args:
            position_ms: int. The position in milliseconds to seek to within the currently playing track. Must not be None.
            device_id: Optional[str]. The ID of the target device on which to seek. If not specified, the currently active device is used.

        Returns:
            dict. The JSON response from the API after seeking to the specified position.

        Raises:
            ValueError: If 'position_ms' is None.
            requests.exceptions.HTTPError: If the HTTP request to seek fails with a bad status code.

        Tags:
            seek, player-control, api
        """
        if position_ms is None:
            raise ValueError("Missing required parameter 'position_ms'")
        url = f"{self.base_url}/me/player/seek"
        query_params = {
            k: v
            for k, v in [("position_ms", position_ms), ("device_id", device_id)]
            if v is not None
        }
        response = self._put(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def set_repeat_mode_on_users_playback(self, state, device_id=None) -> Any:
        """
        Sets the repeat mode for the current user's playback on Spotify, optionally targeting a specific device.

        Args:
            state: str. The desired repeat mode. Valid values include 'track', 'context', or 'off'.
            device_id: Optional[str]. The Spotify device ID to target. If not specified, applies to the user's currently active device.

        Returns:
            dict. The JSON response from the Spotify Web API after updating the repeat mode.

        Raises:
            ValueError: Raised if the required 'state' parameter is not provided.
            requests.HTTPError: Raised if the HTTP request to the Spotify API fails (e.g., due to a bad request or authorization error).

        Tags:
            set, playback, repeat, management
        """
        if state is None:
            raise ValueError("Missing required parameter 'state'")
        url = f"{self.base_url}/me/player/repeat"
        query_params = {
            k: v
            for k, v in [("state", state), ("device_id", device_id)]
            if v is not None
        }
        response = self._put(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def set_volume_for_users_playback(self, volume_percent, device_id=None) -> Any:
        """
        Set the playback volume for the current user's active device.

        Args:
            volume_percent: int. The desired volume level as a percentage (0-100).
            device_id: str, optional. The unique identifier for the target device. If not specified, the user's currently active device is used.

        Returns:
            dict. The JSON response from the API containing the result of the volume change operation.

        Raises:
            ValueError: If 'volume_percent' is None.
            requests.HTTPError: If the HTTP request to the API fails or returns an error response.

        Tags:
            set, volume, playback, user-management
        """
        if volume_percent is None:
            raise ValueError("Missing required parameter 'volume_percent'")
        url = f"{self.base_url}/me/player/volume"
        query_params = {
            k: v
            for k, v in [("volume_percent", volume_percent), ("device_id", device_id)]
            if v is not None
        }
        response = self._put(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def toggle_shuffle_for_users_playback(self, state, device_id=None) -> Any:
        """
        Toggles the shuffle state for the user's playback on the specified device.

        Args:
            state: bool. Whether to enable (True) or disable (False) shuffle playback.
            device_id: str or None. The Spotify device ID on which to set shuffle mode. If None, the active device is used.

        Returns:
            dict. The JSON response from the server containing the playback state information.

        Raises:
            ValueError: If the required parameter 'state' is None.
            HTTPError: If the server returns an unsuccessful status code.

        Tags:
            toggle, shuffle, playback, user, management, spotify
        """
        if state is None:
            raise ValueError("Missing required parameter 'state'")
        url = f"{self.base_url}/me/player/shuffle"
        query_params = {
            k: v
            for k, v in [("state", state), ("device_id", device_id)]
            if v is not None
        }
        response = self._put(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_recently_played(self, limit=None, after=None, before=None) -> Any:
        """
        Retrieves the current user's recently played tracks from the Spotify API, optionally filtered by time or limited in count.

        Args:
            limit: Optional; int or None. Maximum number of items to return (default set by API).
            after: Optional; int, Unix timestamp in milliseconds or None. Returns items played after this time.
            before: Optional; int, Unix timestamp in milliseconds or None. Returns items played before this time.

        Returns:
            dict: A JSON object containing the list of recently played track objects and related metadata.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.

        Tags:
            get, list, spotify-api, user-library, recently-played
        """
        url = f"{self.base_url}/me/player/recently-played"
        query_params = {
            k: v
            for k, v in [("limit", limit), ("after", after), ("before", before)]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_queue(
        self,
    ) -> Any:
        """
        Retrieves the current playback queue for the user from the music player API.

        Args:
            None: This function takes no arguments

        Returns:
            dict: The JSON response containing the user's current playback queue.

        Raises:
            requests.HTTPError: If the HTTP request to the player queue endpoint returns an unsuccessful status code.

        Tags:
            get, queue, api, player
        """
        url = f"{self.base_url}/me/player/queue"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def add_to_queue(self, uri, device_id=None) -> Any:
        """
        Adds an item to the user's playback queue on the specified device using its URI.

        Args:
            uri: str. The Spotify URI of the item to add to the queue. Must not be None.
            device_id: Optional[str]. The ID of the target device for playback. If None, uses the user's currently active device.

        Returns:
            dict. The JSON response from the Spotify API containing the result of the queue addition.

        Raises:
            ValueError: If the 'uri' parameter is None.
            requests.HTTPError: If the HTTP request to the Spotify API fails.

        Tags:
            add, queue, spotify, api, player
        """
        if uri is None:
            raise ValueError("Missing required parameter 'uri'")
        url = f"{self.base_url}/me/player/queue"
        query_params = {
            k: v for k, v in [("uri", uri), ("device_id", device_id)] if v is not None
        }
        response = self._post(url, data={}, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_available_markets(
        self,
    ) -> Any:
        """
        Retrieves a list of available markets from the API endpoint.

        Args:
            None: This function takes no arguments

        Returns:
            A JSON-decoded response containing information about available markets.

        Raises:
            requests.HTTPError: If the HTTP request to the API endpoint fails or an error status code is returned.

        Tags:
            get, markets, api, list, fetch
        """
        url = f"{self.base_url}/markets"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_top_artists(self, time_range=None, limit=None, offset=None) -> Any:
        """
        Retrieves the current user's top artists from the API, supporting optional filtering by time range, result limit, and pagination offset.

        Args:
            time_range: Optional; a string indicating the time range over which to retrieve top artists (e.g., 'short_term', 'medium_term', 'long_term'). If None, the API default is used.
            limit: Optional; an integer specifying the maximum number of artists to return. If None, the API default is used.
            offset: Optional; an integer specifying the index of the first artist to return for pagination. If None, the API default is used.

        Returns:
            A JSON-deserialized object containing the user's top artists and related metadata as returned by the API.

        Raises:
            requests.HTTPError: If the API request fails or returns an unsuccessful HTTP status code.

        Tags:
            get, list, artists, user, ai, batch
        """
        url = f"{self.base_url}/me/top/artists"
        query_params = {
            k: v
            for k, v in [
                ("time_range", time_range),
                ("limit", limit),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_users_top_tracks(self, time_range=None, limit=None, offset=None) -> Any:
        """
        Retrieves the current user's top tracks from the service within an optional time range, with pagination support.

        Args:
            time_range: Optional; str. Specifies the time range for top tracks (e.g., 'short_term', 'medium_term', 'long_term').
            limit: Optional; int. The maximum number of tracks to return.
            offset: Optional; int. The index of the first track to return, used for pagination.

        Returns:
            dict. The JSON response containing the user's top tracks and associated metadata.

        Raises:
            requests.HTTPError: If the HTTP request fails or returns an unsuccessful status code.

        Tags:
            get, list, user, tracks, ai
        """
        url = f"{self.base_url}/me/top/tracks"
        query_params = {
            k: v
            for k, v in [
                ("time_range", time_range),
                ("limit", limit),
                ("offset", offset),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.get_an_album,
            self.get_multiple_albums,
            self.get_an_albums_tracks,
            self.get_an_artist,
            self.get_multiple_artists,
            self.get_an_artists_albums,
            self.get_an_artists_top_tracks,
            self.get_an_artists_related_artists,
            self.get_a_show,
            self.get_multiple_shows,
            self.get_a_shows_episodes,
            self.get_an_episode,
            self.get_multiple_episodes,
            self.get_an_audiobook,
            self.get_multiple_audiobooks,
            self.get_audiobook_chapters,
            self.get_users_saved_audiobooks,
            self.save_audiobooks_user,
            self.remove_audiobooks_user,
            self.check_users_saved_audiobooks,
            self.get_a_chapter,
            self.get_several_chapters,
            self.get_track,
            self.get_several_tracks,
            self.search,
            self.get_current_users_profile,
            self.get_playlist,
            self.change_playlist_details,
            self.get_playlists_tracks,
            self.add_tracks_to_playlist,
            self.reorder_or_replace_playlists_tracks,
            self.get_a_list_of_current_users_playlists,
            self.get_users_saved_albums,
            self.check_users_saved_albums,
            self.get_users_saved_tracks,
            self.save_tracks_user,
            self.check_users_saved_tracks,
            self.get_users_saved_episodes,
            self.save_episodes_user,
            self.check_users_saved_episodes,
            self.get_users_saved_shows,
            self.check_users_saved_shows,
            self.get_users_profile,
            self.get_list_users_playlists,
            self.create_playlist,
            self.follow_playlist,
            self.unfollow_playlist,
            self.get_featured_playlists,
            self.get_categories,
            self.get_a_category,
            self.get_a_categories_playlists,
            self.get_playlist_cover,
            self.get_new_releases,
            self.get_followed,
            self.follow_artists_users,
            self.check_current_user_follows,
            self.check_if_user_follows_playlist,
            self.get_several_audio_features,
            self.get_audio_features,
            self.get_audio_analysis,
            self.get_recommendations,
            self.get_recommendation_genres,
            self.get_information_about_the_users_current_playback,
            self.transfer_a_users_playback,
            self.get_a_users_available_devices,
            self.get_the_users_currently_playing_track,
            self.start_a_users_playback,
            self.pause_a_users_playback,
            self.skip_users_playback_to_next_track,
            self.skip_users_playback_to_previous_track,
            self.seek_to_position_in_currently_playing_track,
            self.set_repeat_mode_on_users_playback,
            self.set_volume_for_users_playback,
            self.toggle_shuffle_for_users_playback,
            self.get_recently_played,
            self.get_queue,
            self.add_to_queue,
            self.get_available_markets,
            self.get_users_top_artists,
            self.get_users_top_tracks,
        ]
