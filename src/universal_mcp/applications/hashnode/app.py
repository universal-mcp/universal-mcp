from gql import gql

from universal_mcp.applications import GraphQLApplication
from universal_mcp.integrations import Integration


class HashnodeApp(GraphQLApplication):
    def __init__(self, integration: Integration | None = None, **kwargs) -> None:
        super().__init__(name="hashnode", base_url="https://gql.hashnode.com", **kwargs)
        self.integration = integration

    def publish_post(
        self,
        publication_id: str,
        title: str,
        content: str,
        tags: list[str] = None,
        slug: str = None,
        subtitle: str = None,
        cover_image: str = None,
    ) -> str:
        """
        Publishes a post to Hashnode using the GraphQL API.

        Args:
            publication_id: The ID of the publication to publish the post to
            title: The title of the post
            content: The markdown content of the post
            tags: Optional list of tag names to add to the post. Example: ["blog", "release-notes", "python", "ai"]
            slug: Optional custom URL slug for the post. Example: "my-post"
            subtitle: Optional subtitle for the post. Example: "A subtitle for my post"
            cover_image: Optional cover image for the post. Example: "https://example.com/cover-image.jpg"
        Returns:
            The URL of the published post

        Raises:
            GraphQLError: If the API request fails

        Tags:
            publish, post, hashnode, api, important
        """
        publish_post_mutation = gql("""
        mutation PublishPost($input: PublishPostInput!) {
          publishPost(input: $input) {
            post {
              url
            }
          }
        }
        """)

        variables = {
            "input": {
                "publicationId": publication_id,
                "title": title,
                "contentMarkdown": content,
            }
        }

        if tags:
            variables["input"]["tags"] = [
                {"name": tag, "slug": tag.replace(" ", "-").lower()} for tag in tags
            ]

        if slug:
            variables["input"]["slug"] = slug

        if subtitle:
            variables["input"]["subtitle"] = subtitle

        if cover_image:
            variables["input"]["bannerImageOptions"] = {
                "url": cover_image,
                "potrait": False,
            }

        result = self.mutate(publish_post_mutation, variables)
        return result["publishPost"]["post"]["url"]

    def list_tools(self):
        return [self.publish_post]
