import base64
from email.message import EmailMessage

from loguru import logger

from universal_mcp.applications.application import APIApplication
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations import Integration


class GoogleMailApp(APIApplication):
    def __init__(self, integration: Integration) -> None:
        super().__init__(name="google-mail", integration=integration)
        self.base_api_url = "https://gmail.googleapis.com/gmail/v1/users/me"

    def send_email(self, to: str, subject: str, body: str) -> str:
        """
        Sends an email using the Gmail API and returns a confirmation or error message.

        Args:
            to: The email address of the recipient
            subject: The subject line of the email
            body: The main content of the email message

        Returns:
            A string containing either a success confirmation message or an error description

        Raises:
            NotAuthorizedError: When Gmail API authentication is not valid or has expired
            KeyError: When required configuration keys are missing
            Exception: For any other unexpected errors during the email sending process

        Tags:
            send, email, api, communication, important
        """
        try:
            url = f"{self.base_api_url}/messages/send"

            # Create email in base64 encoded format
            raw_message = self._create_message(to, subject, body)

            # Format the data as expected by Gmail API
            email_data = {"raw": raw_message}

            logger.info(f"Sending email to {to}")

            response = self._post(url, email_data)

            if response.status_code == 200:
                return f"Successfully sent email to {to}"
            else:
                logger.error(
                    f"Gmail API Error: {response.status_code} - {response.text}"
                )
                return f"Error sending email: {response.status_code} - {response.text}"
        except NotAuthorizedError as e:
            # Return the authorization message directly
            logger.warning(f"Gmail authorization required: {e.message}")
            return e.message
        except KeyError as key_error:
            logger.error(f"Missing key error: {str(key_error)}")
            return f"Configuration error: Missing required key - {str(key_error)}"
        except Exception as e:
            logger.exception(f"Error sending email: {type(e).__name__} - {str(e)}")
            return f"Error sending email: {type(e).__name__} - {str(e)}"

    def _create_message(self, to, subject, body):
        try:
            message = EmailMessage()
            message["to"] = to
            message["subject"] = subject
            message.set_content(body)

            # Use "me" as the default sender
            message["from"] = "me"

            # Encode as base64 string
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            return raw
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            raise

    def create_draft(self, to: str, subject: str, body: str) -> str:
        """
        Creates a draft email message in Gmail using the Gmail API and returns a confirmation status.

        Args:
            to: The email address of the recipient
            subject: The subject line of the draft email
            body: The main content/message of the draft email

        Returns:
            A string containing either a success message with the draft ID or an error message describing the failure

        Raises:
            NotAuthorizedError: When the user's Gmail API authorization is invalid or expired
            KeyError: When required configuration keys are missing
            Exception: For general API errors, network issues, or other unexpected problems

        Tags:
            create, email, draft, gmail, api, important
        """
        try:
            url = f"{self.base_api_url}/drafts"

            raw_message = self._create_message(to, subject, body)

            draft_data = {"message": {"raw": raw_message}}

            logger.info(f"Creating draft email to {to}")

            response = self._post(url, draft_data)

            if response.status_code == 200:
                draft_id = response.json().get("id", "unknown")
                return f"Successfully created draft email with ID: {draft_id}"
            else:
                logger.error(
                    f"Gmail API Error: {response.status_code} - {response.text}"
                )
                return f"Error creating draft: {response.status_code} - {response.text}"
        except NotAuthorizedError as e:
            logger.warning(f"Gmail authorization required: {e.message}")
            return e.message
        except KeyError as key_error:
            logger.error(f"Missing key error: {str(key_error)}")
            return f"Configuration error: Missing required key - {str(key_error)}"
        except Exception as e:
            logger.exception(f"Error creating draft: {type(e).__name__} - {str(e)}")
            return f"Error creating draft: {type(e).__name__} - {str(e)}"

    def send_draft(self, draft_id: str) -> str:
        """
        Sends an existing draft email using the Gmail API and returns a confirmation message.

        Args:
            draft_id: The unique identifier of the Gmail draft to be sent

        Returns:
            A string containing either a success message with the sent message ID or an error message detailing the failure reason

        Raises:
            NotAuthorizedError: When the user's Gmail API authorization is invalid or expired
            KeyError: When required configuration keys are missing from the API response
            Exception: For other unexpected errors during the API request or response handling

        Tags:
            send, email, api, communication, important, draft
        """
        try:
            url = f"{self.base_api_url}/drafts/send"

            draft_data = {"id": draft_id}

            logger.info(f"Sending draft email with ID: {draft_id}")

            response = self._post(url, draft_data)

            if response.status_code == 200:
                message_id = response.json().get("id", "unknown")
                return f"Successfully sent draft email. Message ID: {message_id}"
            else:
                logger.error(
                    f"Gmail API Error: {response.status_code} - {response.text}"
                )
                return f"Error sending draft: {response.status_code} - {response.text}"
        except NotAuthorizedError as e:
            logger.warning(f"Gmail authorization required: {e.message}")
            return e.message
        except KeyError as key_error:
            logger.error(f"Missing key error: {str(key_error)}")
            return f"Configuration error: Missing required key - {str(key_error)}"
        except Exception as e:
            logger.exception(f"Error sending draft: {type(e).__name__} - {str(e)}")
            return f"Error sending draft: {type(e).__name__} - {str(e)}"

    def get_draft(self, draft_id: str, format: str = "full") -> str:
        """
        Retrieves and formats a specific draft email from Gmail by its ID

        Args:
            draft_id: String identifier of the draft email to retrieve
            format: Output format of the draft (options: minimal, full, raw, metadata). Defaults to 'full'

        Returns:
            A formatted string containing the draft email details (ID, recipient, subject) or an error message if retrieval fails

        Raises:
            NotAuthorizedError: When the user's Gmail authorization is invalid or expired
            KeyError: When required configuration keys or response data fields are missing
            Exception: For any other unexpected errors during draft retrieval

        Tags:
            retrieve, email, gmail, draft, api, format, important
        """
        try:
            url = f"{self.base_api_url}/drafts/{draft_id}"

            # Add format parameter as query param
            params = {"format": format}

            logger.info(f"Retrieving draft with ID: {draft_id}")

            response = self._get(url, params=params)

            if response.status_code == 200:
                draft_data = response.json()

                # Format the response in a readable way
                message = draft_data.get("message", {})
                headers = {}

                # Extract headers if they exist
                for header in message.get("payload", {}).get("headers", []):
                    name = header.get("name", "")
                    value = header.get("value", "")
                    headers[name] = value

                to = headers.get("To", "Unknown recipient")
                subject = headers.get("Subject", "No subject")

                result = f"Draft ID: {draft_id}\nTo: {to}\nSubject: {subject}\n"

                return result
            else:
                logger.error(
                    f"Gmail API Error: {response.status_code} - {response.text}"
                )
                return (
                    f"Error retrieving draft: {response.status_code} - {response.text}"
                )
        except NotAuthorizedError as e:
            logger.warning(f"Gmail authorization required: {e.message}")
            return e.message
        except KeyError as key_error:
            logger.error(f"Missing key error: {str(key_error)}")
            return f"Configuration error: Missing required key - {str(key_error)}"
        except Exception as e:
            logger.exception(f"Error retrieving draft: {type(e).__name__} - {str(e)}")
            return f"Error retrieving draft: {type(e).__name__} - {str(e)}"

    def list_drafts(
        self, max_results: int = 20, q: str = None, include_spam_trash: bool = False
    ) -> str:
        """
        Retrieves and formats a list of email drafts from the user's Gmail mailbox with optional filtering and pagination.

        Args:
            max_results: Maximum number of drafts to return (max 500, default 20)
            q: Search query string to filter drafts using Gmail search syntax (default None)
            include_spam_trash: Boolean flag to include drafts from spam and trash folders (default False)

        Returns:
            A formatted string containing the list of draft IDs and count information, or an error message if the request fails

        Raises:
            NotAuthorizedError: When the Gmail API authentication is missing or invalid
            KeyError: When required configuration keys are missing
            Exception: For general errors during API communication or data processing

        Tags:
            list, email, drafts, gmail, api, search, query, pagination, important
        """
        try:
            url = f"{self.base_api_url}/drafts"

            # Build query parameters
            params = {"maxResults": max_results}

            if q:
                params["q"] = q

            if include_spam_trash:
                params["includeSpamTrash"] = "true"

            logger.info(f"Retrieving drafts list with params: {params}")

            response = self._get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                drafts = data.get("drafts", [])
                result_size = data.get("resultSizeEstimate", 0)

                if not drafts:
                    return "No drafts found."

                result = (
                    f"Found {len(drafts)} drafts (estimated total: {result_size}):\n\n"
                )

                for i, draft in enumerate(drafts, 1):
                    draft_id = draft.get("id", "Unknown ID")
                    # The message field only contains id and threadId at this level
                    result += f"{i}. Draft ID: {draft_id}\n"

                if "nextPageToken" in data:
                    result += "\nMore drafts available. Use page token to see more."

                return result
            else:
                logger.error(
                    f"Gmail API Error: {response.status_code} - {response.text}"
                )
                return f"Error listing drafts: {response.status_code} - {response.text}"
        except NotAuthorizedError as e:
            logger.warning(f"Gmail authorization required: {e.message}")
            return e.message
        except KeyError as key_error:
            logger.error(f"Missing key error: {str(key_error)}")
            return f"Configuration error: Missing required key - {str(key_error)}"
        except Exception as e:
            logger.exception(f"Error listing drafts: {type(e).__name__} - {str(e)}")
            return f"Error listing drafts: {type(e).__name__} - {str(e)}"

    def get_message(self, message_id: str) -> str:
        """
        Retrieves and formats a specific email message from Gmail API by its ID, including sender, recipient, date, subject, and message preview.

        Args:
            message_id: The unique identifier of the Gmail message to retrieve

        Returns:
            A formatted string containing the message details (ID, From, To, Date, Subject, Preview) or an error message if the retrieval fails

        Raises:
            NotAuthorizedError: When the request lacks proper Gmail API authorization
            KeyError: When required configuration keys or message fields are missing
            Exception: For general API communication errors or unexpected issues

        Tags:
            retrieve, email, format, api, gmail, message, important
        """
        try:
            url = f"{self.base_api_url}/messages/{message_id}"

            logger.info(f"Retrieving message with ID: {message_id}")

            response = self._get(url)

            if response.status_code == 200:
                message_data = response.json()

                # Extract basic message metadata
                headers = {}

                # Extract headers if they exist
                for header in message_data.get("payload", {}).get("headers", []):
                    name = header.get("name", "")
                    value = header.get("value", "")
                    headers[name] = value

                from_addr = headers.get("From", "Unknown sender")
                to = headers.get("To", "Unknown recipient")
                subject = headers.get("Subject", "No subject")
                date = headers.get("Date", "Unknown date")

                # Format the result
                result = (
                    f"Message ID: {message_id}\n"
                    f"From: {from_addr}\n"
                    f"To: {to}\n"
                    f"Date: {date}\n"
                    f"Subject: {subject}\n\n"
                )

                # Include snippet as preview of message content
                if "snippet" in message_data:
                    result += f"Preview: {message_data['snippet']}\n"

                return result
            else:
                logger.error(
                    f"Gmail API Error: {response.status_code} - {response.text}"
                )
                return f"Error retrieving message: {response.status_code} - {response.text}"
        except NotAuthorizedError as e:
            logger.warning(f"Gmail authorization required: {e.message}")
            return e.message
        except KeyError as key_error:
            logger.error(f"Missing key error: {str(key_error)}")
            return f"Configuration error: Missing required key - {str(key_error)}"
        except Exception as e:
            logger.exception(f"Error retrieving message: {type(e).__name__} - {str(e)}")
            return f"Error retrieving message: {type(e).__name__} - {str(e)}"

    def list_messages(
        self, max_results: int = 20, q: str = None, include_spam_trash: bool = False
    ) -> str:
        """
        Retrieves and formats a list of messages from the user's Gmail mailbox with optional filtering and pagination support.

        Args:
            max_results: Maximum number of messages to return (max 500, default 20)
            q: Search query string to filter messages using Gmail search syntax
            include_spam_trash: Boolean flag to include messages from spam and trash folders (default False)

        Returns:
            A formatted string containing the list of message IDs and thread IDs, or an error message if the operation fails

        Raises:
            NotAuthorizedError: When the Gmail API authentication is invalid or missing
            KeyError: When required configuration keys are missing
            Exception: For general API errors, network issues, or other unexpected problems

        Tags:
            list, messages, gmail, search, query, pagination, important
        """
        try:
            url = f"{self.base_api_url}/messages"

            # Build query parameters
            params = {"maxResults": max_results}

            if q:
                params["q"] = q

            if include_spam_trash:
                params["includeSpamTrash"] = "true"

            logger.info(f"Retrieving messages list with params: {params}")

            response = self._get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                result_size = data.get("resultSizeEstimate", 0)

                if not messages:
                    return "No messages found matching the criteria."

                result = f"Found {len(messages)} messages (estimated total: {result_size}):\n\n"

                # Just list message IDs without fetching additional details
                for i, msg in enumerate(messages, 1):
                    message_id = msg.get("id", "Unknown ID")
                    thread_id = msg.get("threadId", "Unknown Thread")
                    result += f"{i}. Message ID: {message_id} (Thread: {thread_id})\n"

                # Add a note about how to get message details
                result += "\nUse get_message(message_id) to view the contents of a specific message."

                if "nextPageToken" in data:
                    result += "\nMore messages available. Use page token to see more."

                return result
            else:
                logger.error(
                    f"Gmail API Error: {response.status_code} - {response.text}"
                )
                return (
                    f"Error listing messages: {response.status_code} - {response.text}"
                )
        except NotAuthorizedError as e:
            logger.warning(f"Gmail authorization required: {e.message}")
            return e.message
        except KeyError as key_error:
            logger.error(f"Missing key error: {str(key_error)}")
            return f"Configuration error: Missing required key - {str(key_error)}"
        except Exception as e:
            logger.exception(f"Error listing messages: {type(e).__name__} - {str(e)}")
            return f"Error listing messages: {type(e).__name__} - {str(e)}"

    def list_labels(self) -> str:
        """
        Retrieves and formats a list of all labels (both system and user-created) from the user's Gmail account, organizing them by type and sorting them alphabetically.

        Args:
            None: This method takes no arguments

        Returns:
            A formatted string containing a list of Gmail labels categorized by type (system and user), with their IDs, or an error message if the operation fails.

        Raises:
            NotAuthorizedError: Raised when the user's Gmail authorization is invalid or missing
            Exception: Raised when any other unexpected error occurs during the API request or data processing

        Tags:
            list, gmail, labels, fetch, organize, important, management
        """
        try:
            url = f"{self.base_api_url}/labels"

            logger.info("Retrieving Gmail labels")

            response = self._get(url)

            if response.status_code == 200:
                data = response.json()
                labels = data.get("labels", [])

                if not labels:
                    return "No labels found in your Gmail account."

                # Sort labels by type (system first, then user) and then by name
                system_labels = []
                user_labels = []

                for label in labels:
                    label_id = label.get("id", "Unknown ID")
                    label_name = label.get("name", "Unknown Name")
                    label_type = label.get("type", "Unknown Type")

                    if label_type == "system":
                        system_labels.append((label_id, label_name))
                    else:
                        user_labels.append((label_id, label_name))

                # Sort by name within each category
                system_labels.sort(key=lambda x: x[1])
                user_labels.sort(key=lambda x: x[1])

                result = f"Found {len(labels)} Gmail labels:\n\n"

                # System labels
                if system_labels:
                    result += "System Labels:\n"
                    for label_id, label_name in system_labels:
                        result += f"- {label_name} (ID: {label_id})\n"
                    result += "\n"

                # User labels
                if user_labels:
                    result += "User Labels:\n"
                    for label_id, label_name in user_labels:
                        result += f"- {label_name} (ID: {label_id})\n"

                # Add note about using labels
                result += "\nThese label IDs can be used with list_messages to filter emails by label."

                return result
            else:
                logger.error(
                    f"Gmail API Error: {response.status_code} - {response.text}"
                )
                return f"Error listing labels: {response.status_code} - {response.text}"
        except NotAuthorizedError as e:
            logger.warning(f"Gmail authorization required: {e.message}")
            return e.message
        except Exception as e:
            logger.exception(f"Error listing labels: {type(e).__name__} - {str(e)}")
            return f"Error listing labels: {type(e).__name__} - {str(e)}"

    def create_label(self, name: str) -> str:
        """
        Creates a new Gmail label with specified visibility settings and returns creation status details.

        Args:
            name: The display name of the label to create

        Returns:
            A formatted string containing the creation status, including the new label's name and ID if successful, or an error message if the creation fails

        Raises:
            NotAuthorizedError: Raised when the request lacks proper Gmail API authorization
            Exception: Raised for any other unexpected errors during label creation

        Tags:
            create, label, gmail, management, important
        """
        try:
            url = f"{self.base_api_url}/labels"

            # Create the label data with just the essential fields
            label_data = {
                "name": name,
                "labelListVisibility": "labelShow",  # Show in label list
                "messageListVisibility": "show",  # Show in message list
            }

            logger.info(f"Creating new Gmail label: {name}")

            response = self._post(url, label_data)

            if response.status_code in [200, 201]:
                new_label = response.json()
                label_id = new_label.get("id", "Unknown")
                label_name = new_label.get("name", name)

                result = "Successfully created new label:\n"
                result += f"- Name: {label_name}\n"
                result += f"- ID: {label_id}\n"

                return result
            else:
                logger.error(
                    f"Gmail API Error: {response.status_code} - {response.text}"
                )
                return f"Error creating label: {response.status_code} - {response.text}"
        except NotAuthorizedError as e:
            logger.warning(f"Gmail authorization required: {e.message}")
            return e.message
        except Exception as e:
            logger.exception(f"Error creating label: {type(e).__name__} - {str(e)}")
            return f"Error creating label: {type(e).__name__} - {str(e)}"

    def get_profile(self) -> str:
        """
        Retrieves and formats the user's Gmail profile information including email address, message count, thread count, and history ID.

        Args:
            None: This method takes no arguments besides self

        Returns:
            A formatted string containing the user's Gmail profile information or an error message if the request fails

        Raises:
            NotAuthorizedError: Raised when the user's credentials are invalid or authorization is required
            Exception: Raised for any other unexpected errors during the API request or data processing

        Tags:
            fetch, profile, gmail, user-info, api-request, important
        """
        try:
            url = f"{self.base_api_url}/profile"

            logger.info("Retrieving Gmail user profile")

            response = self._get(url)

            if response.status_code == 200:
                profile_data = response.json()

                # Extract profile information
                email_address = profile_data.get("emailAddress", "Unknown")
                messages_total = profile_data.get("messagesTotal", 0)
                threads_total = profile_data.get("threadsTotal", 0)
                history_id = profile_data.get("historyId", "Unknown")

                # Format the response
                result = "Gmail Profile Information:\n"
                result += f"- Email Address: {email_address}\n"
                result += f"- Total Messages: {messages_total:,}\n"
                result += f"- Total Threads: {threads_total:,}\n"
                result += f"- History ID: {history_id}\n"

                return result
            else:
                logger.error(
                    f"Gmail API Error: {response.status_code} - {response.text}"
                )
                return f"Error retrieving profile: {response.status_code} - {response.text}"
        except NotAuthorizedError as e:
            logger.warning(f"Gmail authorization required: {e.message}")
            return e.message
        except Exception as e:
            logger.exception(f"Error retrieving profile: {type(e).__name__} - {str(e)}")
            return f"Error retrieving profile: {type(e).__name__} - {str(e)}"

    def list_tools(self):
        return [
            self.send_email,
            self.create_draft,
            self.send_draft,
            self.get_draft,
            self.list_drafts,
            self.get_message,
            self.list_messages,
            self.list_labels,
            self.create_label,
            self.get_profile,
        ]
