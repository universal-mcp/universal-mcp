
# Spotify MCP Server

An MCP Server for the Spotify API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Spotify API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| get_an_album | Retrieves detailed information about a specific album by its ID from the API. |
| get_multiple_albums | Retrieves detailed information for multiple albums by their IDs from the API. |
| get_an_albums_tracks | Retrieves the list of tracks for a specified album from the API, with optional filtering and pagination. |
| get_an_artist | Retrieve detailed information about a specific artist by their unique identifier. |
| get_multiple_artists | Retrieves information for multiple artists using their IDs. |
| get_an_artists_albums | Retrieves a list of albums for the specified artist from the API. |
| get_an_artists_top_tracks | Retrieves the top tracks for a specified artist from the API. |
| get_an_artists_related_artists | Retrieves a list of artists related to the specified artist by their unique ID. |
| get_a_show | Retrieve detailed information about a show by its unique identifier. |
| get_multiple_shows | Retrieves information for multiple shows by their IDs, with optional market filtering. |
| get_a_shows_episodes | Retrieves episodes for a specific show from the API with optional market, limit, and offset parameters. |
| get_an_episode | Retrieves a single podcast episode's details by its unique identifier. |
| get_multiple_episodes | Retrieves details for multiple podcast episodes using their IDs, optionally filtered by market. |
| get_an_audiobook | Retrieves detailed information about a specific audiobook by ID, optionally filtered by market. |
| get_multiple_audiobooks | Fetches details for multiple audiobooks by their IDs, optionally filtered by market. |
| get_audiobook_chapters | Retrieves the chapters for a specified audiobook from the API. |
| get_users_saved_audiobooks | Retrieves the current user's saved audiobooks from the API with optional pagination. |
| save_audiobooks_user | Saves one or more audiobooks to the current user's library. |
| remove_audiobooks_user | Removes one or more audiobooks from the authenticated user's library. |
| check_users_saved_audiobooks | Checks if the specified audiobooks are saved in the current user's library. |
| get_a_chapter | Retrieves a specific chapter's details by ID from the API, optionally filtering by market. |
| get_several_chapters | Retrieve details for multiple chapters based on their IDs, optionally filtering by market. |
| get_track | Retrieves detailed information about a track by its unique identifier from the external API. |
| get_several_tracks | Retrieves metadata for multiple tracks based on their IDs from the API. |
| search | Performs a search query against the API and returns the matching results as a JSON object. |
| get_current_users_profile | Retrieves the current authenticated user's profile information from the API. |
| get_playlist | Retrieves a playlist from the API using the specified playlist ID. |
| change_playlist_details | Update the details of an existing playlist with the specified attributes. |
| get_playlists_tracks | Retrieves the tracks of a specified playlist from the API, applying optional filters and pagination parameters. |
| add_tracks_to_playlist | Adds one or more tracks to a specified playlist at an optional position. |
| reorder_or_replace_playlists_tracks | Reorders or replaces tracks in a playlist by moving, inserting, or replacing track entries using the specified parameters. |
| get_a_list_of_current_users_playlists | Retrieves a list of the current user's playlists with optional pagination controls. |
| get_users_saved_albums | Retrieves the current user's saved albums from the Spotify library with optional pagination and market filtering. |
| check_users_saved_albums | Checks if the specified albums are saved in the current user's Spotify library. |
| get_users_saved_tracks | Retrieves the current user's saved tracks from the Spotify library with optional filtering and pagination. |
| save_tracks_user | Saves one or more tracks to the current user's music library. |
| check_users_saved_tracks | Checks if the current user has saved specific tracks in their Spotify library. |
| get_users_saved_episodes | Retrieves the current user's saved podcast episodes from the service, with optional support for market, pagination, and result limits. |
| save_episodes_user | Saves episodes to the user's library using the provided list of episode IDs. |
| check_users_saved_episodes | Checks if the specified episodes are saved in the current user's library. |
| get_users_saved_shows | Retrieves the current user's saved shows from the Spotify API with optional pagination. |
| check_users_saved_shows | Checks if the specified shows are saved in the current user's library. |
| get_users_profile | Retrieves the profile information for a specific user by user ID. |
| get_list_users_playlists | Retrieves a list of playlists for a specified user. |
| create_playlist | Creates a new playlist for a specified user with optional visibility, collaboration, and description settings. |
| follow_playlist | Follows a Spotify playlist on behalf of the current user. |
| unfollow_playlist | Unfollows the specified playlist by deleting the current user's following relationship. |
| get_featured_playlists | Retrieves a list of Spotify's featured playlists with optional localization, result limiting, and pagination. |
| get_categories | Retrieves a list of category objects from the API with optional locale, limit, and offset filters. |
| get_a_category | Retrieve detailed information about a specific category by its ID, optionally localized to a given locale. |
| get_a_categories_playlists | Retrieves playlists associated with a specified category from the API. |
| get_playlist_cover | Retrieves the cover image(s) for a specified playlist by its unique ID. |
| get_new_releases | Retrieves a list of new music releases with optional pagination parameters. |
| get_followed | Retrieves the list of entities the current user is following, with support for pagination and limiting results. |
| follow_artists_users | Follows one or more artists or users on behalf of the current user. |
| check_current_user_follows | Check if the current user follows specific Spotify users or artists. |
| check_if_user_follows_playlist | Checks if one or more users follow a specified playlist. |
| get_several_audio_features | Retrieves audio feature information for multiple tracks using their IDs. |
| get_audio_features | Retrieves audio feature information for a given identifier from the API. |
| get_audio_analysis | Retrieves the audio analysis data for a specified audio ID from the API. |
| get_recommendations | Retrieves track recommendations based on a combination of seed values and audio feature constraints. |
| get_recommendation_genres | Retrieves a list of available genre seeds for recommendations from the remote API. |
| get_information_about_the_users_current_playback | Retrieves information about the user's current playback state from the music service. |
| transfer_a_users_playback | Transfers the playback of a user's current session to one or more specified devices. |
| get_a_users_available_devices | Retrieves the list of devices available to the current user for playback control. |
| get_the_users_currently_playing_track | Retrieves information about the track currently being played by the user. |
| start_a_users_playback | Starts or resumes playback of a user's Spotify player on the specified device, context, or track list. |
| pause_a_users_playback | Pauses the current playback for the authenticated user. |
| skip_users_playback_to_next_track | Skips the user's playback to the next track on the current or specified device. |
| skip_users_playback_to_previous_track | Skips the user's playback to the previous track on the active or specified device. |
| seek_to_position_in_currently_playing_track | Seeks to the specified position in the currently playing track for the user. |
| set_repeat_mode_on_users_playback | Sets the repeat mode for the current user's playback on Spotify, optionally targeting a specific device. |
| set_volume_for_users_playback | Set the playback volume for the current user's active device. |
| toggle_shuffle_for_users_playback | Toggles the shuffle state for the user's playback on the specified device. |
| get_recently_played | Retrieves the current user's recently played tracks from the Spotify API, optionally filtered by time or limited in count. |
| get_queue | Retrieves the current playback queue for the user from the music player API. |
| add_to_queue | Adds an item to the user's playback queue on the specified device using its URI. |
| get_available_markets | Retrieves a list of available markets from the API endpoint. |
| get_users_top_artists | Retrieves the current user's top artists from the API, supporting optional filtering by time range, result limit, and pagination offset. |
| get_users_top_tracks | Retrieves the current user's top tracks from the service within an optional time range, with pagination support. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Spotify app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
