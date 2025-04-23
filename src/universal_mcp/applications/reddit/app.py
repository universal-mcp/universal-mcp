import httpx
from loguru import logger

from universal_mcp.applications.application import APIApplication
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations import Integration


class RedditApp(APIApplication):
    def __init__(self, integration: Integration) -> None:
        super().__init__(name="reddit", integration=integration)
        self.base_api_url = "https://oauth.reddit.com"

    def _post(self, url, data):
        try:
            headers = self._get_headers()
            response = httpx.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response
        except NotAuthorizedError as e:
            logger.warning(f"Authorization needed: {e.message}")
            raise e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                return e.response.text or "Rate limit exceeded. Please try again later."
            else:
                raise e
        except Exception as e:
            logger.error(f"Error posting {url}: {e}")
            raise e

    def _get_headers(self):
        if not self.integration:
            raise ValueError("Integration not configured for RedditApp")
        credentials = self.integration.get_credentials()
        if "access_token" not in credentials:
            logger.error("Reddit credentials found but missing 'access_token'.")
            raise ValueError("Invalid Reddit credentials format.")

        return {
            "Authorization": f"Bearer {credentials['access_token']}",
            "User-Agent": "agentr-reddit-app/0.1 by AgentR",
        }

    def get_subreddit_posts(
        self, subreddit: str, limit: int = 5, timeframe: str = "day"
    ) -> str:
        """
        Retrieves and formats top posts from a specified subreddit within a given timeframe using the Reddit API

        Args:
            subreddit: The name of the subreddit (e.g., 'python', 'worldnews') without the 'r/' prefix
            limit: The maximum number of posts to return (default: 5, max: 100)
            timeframe: The time period for top posts. Valid options: 'hour', 'day', 'week', 'month', 'year', 'all' (default: 'day')

        Returns:
            A formatted string containing a numbered list of top posts, including titles, authors, scores, and URLs, or an error message if the request fails

        Raises:
            RequestException: When the HTTP request to the Reddit API fails
            JSONDecodeError: When the API response contains invalid JSON

        Tags:
            fetch, reddit, api, list, social-media, important, read-only
        """
        valid_timeframes = ["hour", "day", "week", "month", "year", "all"]
        if timeframe not in valid_timeframes:
            return f"Error: Invalid timeframe '{timeframe}'. Please use one of: {', '.join(valid_timeframes)}"
        if not 1 <= limit <= 100:
            return (
                f"Error: Invalid limit '{limit}'. Please use a value between 1 and 100."
            )
        url = f"{self.base_api_url}/r/{subreddit}/top"
        params = {"limit": limit, "t": timeframe}
        logger.info(
            f"Requesting top {limit} posts from r/{subreddit} for timeframe '{timeframe}'"
        )
        response = self._get(url, params=params)
        data = response.json()
        if "error" in data:
            logger.error(
                f"Reddit API error: {data['error']} - {data.get('message', '')}"
            )
            return f"Error from Reddit API: {data['error']} - {data.get('message', '')}"
        posts = data.get("data", {}).get("children", [])
        if not posts:
            return (
                f"No top posts found in r/{subreddit} for the timeframe '{timeframe}'."
            )
        result_lines = [
            f"Top {len(posts)} posts from r/{subreddit} (timeframe: {timeframe}):\n"
        ]
        for i, post_container in enumerate(posts):
            post = post_container.get("data", {})
            title = post.get("title", "No Title")
            score = post.get("score", 0)
            author = post.get("author", "Unknown Author")
            permalink = post.get("permalink", "")
            full_url = f"https://www.reddit.com{permalink}" if permalink else "No Link"

            result_lines.append(f'{i + 1}. "{title}" by u/{author} (Score: {score})')
            result_lines.append(f"   Link: {full_url}")
        return "\n".join(result_lines)

    def search_subreddits(
        self, query: str, limit: int = 5, sort: str = "relevance"
    ) -> str:
        """
        Searches Reddit for subreddits matching a given query string and returns a formatted list of results including subreddit names, subscriber counts, and descriptions.

        Args:
            query: The text to search for in subreddit names and descriptions
            limit: The maximum number of subreddits to return, between 1 and 100 (default: 5)
            sort: The order of results, either 'relevance' or 'activity' (default: 'relevance')

        Returns:
            A formatted string containing a list of matching subreddits with their names, subscriber counts, and descriptions, or an error message if the search fails or parameters are invalid

        Raises:
            RequestException: When the HTTP request to Reddit's API fails
            JSONDecodeError: When the API response contains invalid JSON

        Tags:
            search, important, reddit, api, query, format, list, validation
        """
        valid_sorts = ["relevance", "activity"]
        if sort not in valid_sorts:
            return f"Error: Invalid sort option '{sort}'. Please use one of: {', '.join(valid_sorts)}"
        if not 1 <= limit <= 100:
            return (
                f"Error: Invalid limit '{limit}'. Please use a value between 1 and 100."
            )
        url = f"{self.base_api_url}/subreddits/search"
        params = {
            "q": query,
            "limit": limit,
            "sort": sort,
            # Optionally include NSFW results? Defaulting to false for safety.
            # "include_over_18": "false"
        }
        logger.info(
            f"Searching for subreddits matching '{query}' (limit: {limit}, sort: {sort})"
        )
        response = self._get(url, params=params)
        data = response.json()
        if "error" in data:
            logger.error(
                f"Reddit API error during subreddit search: {data['error']} - {data.get('message', '')}"
            )
            return f"Error from Reddit API during search: {data['error']} - {data.get('message', '')}"
        subreddits = data.get("data", {}).get("children", [])
        if not subreddits:
            return f"No subreddits found matching the query '{query}'."
        result_lines = [
            f"Found {len(subreddits)} subreddits matching '{query}' (sorted by {sort}):\n"
        ]
        for i, sub_container in enumerate(subreddits):
            sub_data = sub_container.get("data", {})
            display_name = sub_data.get("display_name", "N/A")  # e.g., 'python'
            title = sub_data.get(
                "title", "No Title"
            )  # Often the same as display_name or slightly longer
            subscribers = sub_data.get("subscribers", 0)
            # Use public_description if available, fallback to title
            description = sub_data.get("public_description", "").strip() or title

            # Format subscriber count nicely
            subscriber_str = f"{subscribers:,}" if subscribers else "Unknown"

            result_lines.append(
                f"{i + 1}. r/{display_name} ({subscriber_str} subscribers)"
            )
            if description:
                result_lines.append(f"   Description: {description}")
        return "\n".join(result_lines)

    def get_post_flairs(self, subreddit: str):
        """
        Retrieves a list of available post flairs for a specified subreddit using the Reddit API.

        Args:
            subreddit: The name of the subreddit (e.g., 'python', 'worldnews') without the 'r/' prefix

        Returns:
            A list of dictionaries containing flair details if flairs exist, or a string message indicating no flairs are available

        Raises:
            RequestException: When the API request fails or network connectivity issues occur
            JSONDecodeError: When the API response contains invalid JSON data

        Tags:
            fetch, get, reddit, flair, api, read-only
        """
        url = f"{self.base_api_url}/r/{subreddit}/api/link_flair_v2"
        logger.info(f"Fetching post flairs for subreddit: r/{subreddit}")
        response = self._get(url)
        flairs = response.json()
        if not flairs:
            return f"No post flairs available for r/{subreddit}."
        return flairs

    def create_post(
        self,
        subreddit: str,
        title: str,
        kind: str = "self",
        text: str = None,
        url: str = None,
        flair_id: str = None,
    ):
        """
        Creates a new Reddit post in a specified subreddit with support for text posts, link posts, and image posts

        Args:
            subreddit: The name of the subreddit (e.g., 'python', 'worldnews') without the 'r/'
            title: The title of the post
            kind: The type of post; either 'self' (text post) or 'link' (link or image post)
            text: The text content of the post; required if kind is 'self'
            url: The URL of the link or image; required if kind is 'link'. Must end with valid image extension for image posts
            flair_id: The ID of the flair to assign to the post

        Returns:
            The JSON response from the Reddit API, or an error message as a string if the API returns an error

        Raises:
            ValueError: Raised when kind is invalid or when required parameters (text for self posts, url for link posts) are missing

        Tags:
            create, post, social-media, reddit, api, important
        """
        if kind not in ["self", "link"]:
            raise ValueError("Invalid post kind. Must be one of 'self' or 'link'.")
        if kind == "self" and not text:
            raise ValueError("Text content is required for text posts.")
        if kind == "link" and not url:
            raise ValueError("URL is required for link posts (including images).")
        data = {
            "sr": subreddit,
            "title": title,
            "kind": kind,
            "text": text,
            "url": url,
            "flair_id": flair_id,
        }
        data = {k: v for k, v in data.items() if v is not None}
        url_api = f"{self.base_api_url}/api/submit"
        logger.info(f"Submitting a new post to r/{subreddit}")
        response = self._post(url_api, data=data)
        response_json = response.json()
        if (
            response_json
            and "json" in response_json
            and "errors" in response_json["json"]
        ):
            errors = response_json["json"]["errors"]
            if errors:
                error_message = ", ".join(
                    [f"{code}: {message}" for code, message in errors]
                )
                return f"Reddit API error: {error_message}"
        return response_json

    def get_comment_by_id(self, comment_id: str) -> dict:
        """
        Retrieves a specific Reddit comment using its unique identifier.

        Args:
            comment_id: The full unique identifier of the comment (prefixed with 't1_', e.g., 't1_abcdef')

        Returns:
            A dictionary containing the comment data including attributes like author, body, score, etc. If the comment is not found, returns a dictionary with an error message.

        Raises:
            HTTPError: When the Reddit API request fails due to network issues or invalid authentication
            JSONDecodeError: When the API response cannot be parsed as valid JSON

        Tags:
            retrieve, get, reddit, comment, api, fetch, single-item, important
        """
        url = f"https://oauth.reddit.com/api/info.json?id={comment_id}"
        response = self._get(url)
        data = response.json()
        comments = data.get("data", {}).get("children", [])
        if comments:
            return comments[0]["data"]
        else:
            return {"error": "Comment not found."}

    def post_comment(self, parent_id: str, text: str) -> dict:
        """
        Posts a comment to a Reddit post or comment using the Reddit API

        Args:
            parent_id: The full ID of the parent comment or post (e.g., 't3_abc123' for a post, 't1_def456' for a comment)
            text: The text content of the comment to be posted

        Returns:
            A dictionary containing the Reddit API response with details about the posted comment

        Raises:
            RequestException: If the API request fails or returns an error status code
            JSONDecodeError: If the API response cannot be parsed as JSON

        Tags:
            post, comment, social, reddit, api, important
        """
        url = f"{self.base_api_url}/api/comment"
        data = {
            "parent": parent_id,
            "text": text,
        }
        logger.info(f"Posting comment to {parent_id}")
        response = self._post(url, data=data)
        return response.json()

    def edit_content(self, content_id: str, text: str) -> dict:
        """
        Edits the text content of an existing Reddit post or comment using the Reddit API

        Args:
            content_id: The full ID of the content to edit (e.g., 't3_abc123' for a post, 't1_def456' for a comment)
            text: The new text content to replace the existing content

        Returns:
            A dictionary containing the API response with details about the edited content

        Raises:
            RequestException: When the API request fails or network connectivity issues occur
            ValueError: When invalid content_id format or empty text is provided

        Tags:
            edit, update, content, reddit, api, important
        """
        url = f"{self.base_api_url}/api/editusertext"
        data = {
            "thing_id": content_id,
            "text": text,
        }
        logger.info(f"Editing content {content_id}")
        response = self._post(url, data=data)
        return response.json()

    def delete_content(self, content_id: str) -> dict:
        """
        Deletes a specified Reddit post or comment using the Reddit API.

        Args:
            content_id: The full ID of the content to delete (e.g., 't3_abc123' for a post, 't1_def456' for a comment)

        Returns:
            A dictionary containing a success message with the deleted content ID

        Raises:
            HTTPError: When the API request fails or returns an error status code
            RequestException: When there are network connectivity issues or API communication problems

        Tags:
            delete, content-management, api, reddit, important
        """
        url = f"{self.base_api_url}/api/del"
        data = {
            "id": content_id,
        }
        logger.info(f"Deleting content {content_id}")
        response = self._post(url, data=data)
        response.raise_for_status()
        return {"message": f"Content {content_id} deleted successfully."}

    def list_tools(self):
        return [
            self.get_subreddit_posts,
            self.search_subreddits,
            self.get_post_flairs,
            self.create_post,
            self.get_comment_by_id,
            self.post_comment,
            self.edit_content,
            self.delete_content,
        ]
