
# Elevenlabs MCP Server

An MCP Server for the Elevenlabs API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Elevenlabs API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| get_generated_items_v1_history_get | Retrieves a paginated history of generated items from the API, optionally filtered by page size, starting history item, or voice ID. |
| get_history_item_by_id_v1_history__history_item_id__get | Retrieves a specific history item by its unique identifier. |
| delete_history_item_v1_history__history_item_id__delete | Deletes a specific history item by its unique identifier. |
| get_audio_from_history_item_v1_history__history_item_id__audio_get | Retrieves the audio data associated with a specific history item by its unique identifier. |
| download_history_items_v1_history_download_post | Downloads specified history items in the given output format via a POST request. |
| delete_sample_v1_voices__voice_id__samples__sample_id__delete | Deletes a specific voice sample identified by voice_id and sample_id from the API. |
| get_audio_from_sample_v1_voices__voice_id__samples__sample_id__audio_get | Retrieves audio data for a specific sample from a given voice using provided identifiers. |
| text_to_speech_v1_text_to_speech__voice_id__post | Converts input text to speech using the specified voice configuration via a POST request to the text-to-speech API endpoint. |
| text_to_speech_v1_text_to_speech__voice_id__stream_post | Streams synthesized speech audio for given text using a specified voice ID and customizable options. |
| voice_generation_parameters_v1_voice_generation_generate_voice_parameters_get | Retrieves available parameter options for voice generation from the API. |
| generate_a_random_voice_v1_voice_generation_generate_voice_post | Generates a synthetic voice audio based on specified demographics and text input by sending a POST request to the voice generation API. |
| create_a_previously_generated_voice_v1_voice_generation_create_voice_post | Creates a new voice entry using data from a previously generated voice. |
| get_user_subscription_info_v1_user_subscription_get | Retrieves the current user's subscription information from the API. |
| get_user_info_v1_user_get | Retrieves information about the current authenticated user from the API. |
| get_voices_v1_voices_get | Retrieves a list of available voices from the v1 API endpoint. |
| get_default_voice_settings__v1_voices_settings_default_get | Retrieves the default voice settings from the API endpoint. |
| get_voice_settings_v1_voices__voice_id__settings_get | Retrieves the settings for a specific voice using the provided voice ID. |
| get_voice_v1_voices__voice_id__get | Retrieves details for a specific voice, optionally including voice settings, by making a GET request to the API. |
| delete_voice_v1_voices__voice_id__delete | Deletes a voice resource identified by the given voice ID using the v1 API endpoint. |
| add_sharing_voice_v1_voices_add__public_user_id___voice_id__post | Adds a shared voice for a public user by sending a POST request with a new name for the specified voice. |
| get_projects_v1_projects_get | Retrieves a list of projects from the API using a GET request to the '/v1/projects' endpoint. |
| get_project_by_id_v1_projects__project_id__get | Retrieve project details by project ID using the v1 projects API. |
| delete_project_v1_projects__project_id__delete | Deletes a project by its ID using a DELETE HTTP request to the v1/projects endpoint. |
| convert_project_v1_projects__project_id__convert_post | Converts the specified project by sending a POST request to the appropriate API endpoint. |
| get_project_snapshots_v1_projects__project_id__snapshots_get | Retrieves a list of snapshots for the specified project using the v1 projects API. |
| stream_project_audio_v1_projects__project_id__snapshots__project_snapshot_id__stream_post | Streams audio data for a specific project snapshot, with optional conversion to MPEG format. |
| streams_archive_with_project_audio_v1_projects__project_id__snapshots__project_snapshot_id__archive_post | Creates an audio archive for the specified project snapshot by making a POST request to the project's archive endpoint. |
| get_chapters_v1_projects__project_id__chapters_get | Retrieves the list of chapters for a specific project by project ID. |
| get_chapter_by_id_v1_projects__project_id__chapters__chapter_id__get | Retrieves a specific chapter resource by its ID from a given project using the API. |
| delete_chapter_v1_projects__project_id__chapters__chapter_id__delete | Deletes a specific chapter from a project by its project and chapter IDs. |
| convert_chapter_v1_projects__project_id__chapters__chapter_id__convert_post | Initiates a conversion operation for a specified chapter within a project and returns the result as JSON. |
| get_chapter_snapshots_v1_projects__project_id__chapters__chapter_id__snapshots_get | Retrieves the list of chapter snapshots for a specific chapter within a project. |
| stream_chapter_audio_v1_projects__project_id__chapters__chapter_id__snapshots__chapter_snapshot_id__stream_post | Streams the audio for a specific chapter snapshot in a project, with optional conversion to MPEG format. |
| update_pronunciation_dictionaries_v1_projects__project_id__update_pronunciation_dictionaries_post | Updates the pronunciation dictionaries for a specific project by sending the provided dictionary locators to the server. |
| get_dubbing_project_metadata_v1_dubbing__dubbing_id__get | Retrieves metadata for a dubbing project by its unique identifier. |
| delete_dubbing_project_v1_dubbing__dubbing_id__delete | Deletes a dubbing project identified by its ID via the v1 API endpoint. |
| get_dubbed_file_v1_dubbing__dubbing_id__audio__language_code__get | Retrieves the dubbed audio file for a given dubbing ID and language code from the API. |
| get_transcript_for_dub_v1_dubbing__dubbing_id__transcript__language_code__get | Retrieves the transcript for a specific dubbing in the requested language. |
| get_sso_provider_admin_admin__admin_url_prefix__sso_provider_get | Retrieves SSO provider information for a specific admin URL prefix and workspace. |
| get_models_v1_models_get | Retrieves a list of available models from the v1 API endpoint. |
| get_voices_v1_shared_voices_get | Retrieves a list of shared voice resources, filtered and paginated according to the specified criteria. |
| add_rules_to_the_pronunciation_dictionary_v1_pronunciation_dictionaries__pronunciation_dictionary_id__add_rules_post | Adds new pronunciation rules to a specified pronunciation dictionary by making a POST request to the backend service. |
| remove_rules_from_the_pronunciation_dictionary_v1_pronunciation_dictionaries__pronunciation_dictionary_id__remove_rules_post | Removes specified pronunciation rules from a pronunciation dictionary via a POST request to the API. |
| get_pls_file_with_a_pronunciation_dictionary_version_rules_v1_pronunciation_dictionaries__dictionary_id___version_id__download_get | Downloads a pronunciation lexicon (PLS) file for a specific pronunciation dictionary version. |
| get_metadata_for_a_pronunciation_dictionary_v1_pronunciation_dictionaries__pronunciation_dictionary_id___get | Retrieves metadata for a specific pronunciation dictionary by its ID. |
| get_pronunciation_dictionaries_v1_pronunciation_dictionaries__get | Retrieve a paginated list of pronunciation dictionaries from the v1 API endpoint. |
| get_a_profile_page_profile__handle__get | Retrieves a user's profile data as a dictionary using their unique handle. |
| redirect_to_mintlify_docs_get | Fetches the Mintlify documentation by sending a GET request and returns the parsed JSON response. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Elevenlabs app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
