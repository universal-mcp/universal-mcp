from datetime import datetime, timedelta

from loguru import logger

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class GoogleCalendarApp(APIApplication):
    def __init__(self, integration: Integration) -> None:
        super().__init__(name="google-calendar", integration=integration)
        self.base_api_url = "https://www.googleapis.com/calendar/v3/calendars/primary"

    def _get_headers(self):
        if not self.integration:
            raise ValueError("Integration not configured for GoogleCalendarApp")
        credentials = self.integration.get_credentials()
        if "headers" in credentials:
            return credentials["headers"]
        return {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Accept": "application/json",
        }

    def _format_datetime(self, dt_string: str) -> str:
        """Format a datetime string from ISO format to a human-readable format.

        Args:
            dt_string: A datetime string in ISO format (e.g., "2023-06-01T10:00:00Z")

        Returns:
            A formatted datetime string (e.g., "2023-06-01 10:00 AM") or the original string with
            "(All day)" appended if it's just a date
        """
        if not dt_string or dt_string == "Unknown":
            return "Unknown"

        # Check if it's just a date (all-day event) or a datetime
        if "T" in dt_string:
            # It's a datetime - parse and format it
            try:
                # Handle Z (UTC) suffix by replacing with +00:00 timezone
                if dt_string.endswith("Z"):
                    dt_string = dt_string.replace("Z", "+00:00")

                # Parse the ISO datetime string
                dt = datetime.fromisoformat(dt_string)

                # Format to a more readable form
                return dt.strftime("%Y-%m-%d %I:%M %p")
            except ValueError:
                # In case of parsing error, return the original
                logger.warning(f"Could not parse datetime string: {dt_string}")
                return dt_string
        else:
            # It's just a date (all-day event)
            return f"{dt_string} (All day)"

    def get_today_events(
        self, days: int = 1, max_results: int = None, time_zone: str = None
    ) -> str:
        """Get events from your Google Calendar for today or a specified number of days

        Args:
            days: Number of days to retrieve events for (default: 1, which is just today)
            max_results: Maximum number of events to return (optional)
            time_zone: Time zone used in the response (optional, default is calendar's time zone)

        Returns:
            A formatted list of events or an error message
        """
        # Get today's date in ISO format
        today = datetime.utcnow().date()
        end_date = today + timedelta(days=days)

        # Format dates for API
        time_min = f"{today.isoformat()}T00:00:00Z"
        time_max = f"{end_date.isoformat()}T00:00:00Z"

        url = f"{self.base_api_url}/events"

        # Build query parameters
        params = {
            "timeMin": time_min,
            "timeMax": time_max,
            "singleEvents": "true",
            "orderBy": "startTime",
        }

        if max_results is not None:
            params["maxResults"] = max_results

        if time_zone:
            params["timeZone"] = time_zone

        date_range = "today" if days == 1 else f"the next {days} days"
        logger.info(f"Retrieving calendar events for {date_range}")

        response = self._get(url, params=params)
        response.raise_for_status()

        events = response.json().get("items", [])
        if not events:
            return f"No events scheduled for {date_range}."

        result = f"Events for {date_range}:\n\n"
        for event in events:
            # Extract event date and time
            start = event.get("start", {})
            event_date = (
                start.get("date", start.get("dateTime", "")).split("T")[0]
                if "T" in start.get("dateTime", "")
                else start.get("date", "")
            )

            # Extract and format time
            start_time = start.get("dateTime", start.get("date", "All day"))

            # Format the time display
            if "T" in start_time:  # It's a datetime
                formatted_time = self._format_datetime(start_time)
                # For multi-day view, keep the date; for single day, just show time
                if days > 1:
                    time_display = formatted_time
                else:
                    # Extract just the time part
                    time_display = (
                        formatted_time.split(" ")[1]
                        + " "
                        + formatted_time.split(" ")[2]
                    )
            else:  # It's an all-day event
                time_display = f"{event_date} (All day)" if days > 1 else "All day"

            # Get event details
            summary = event.get("summary", "Untitled event")
            event_id = event.get("id", "No ID")

            result += f"- {time_display}: {summary} (ID: {event_id})\n"

        return result

    def get_event(
        self, event_id: str, max_attendees: int = None, time_zone: str = None
    ) -> str:
        """Get a specific event from your Google Calendar by ID

        Args:
            event_id: The ID of the event to retrieve
            max_attendees: Optional. The maximum number of attendees to include in the response
            time_zone: Optional. Time zone used in the response (default is calendar's time zone)

        Returns:
            A formatted event details or an error message
        """
        url = f"{self.base_api_url}/events/{event_id}"

        # Build query parameters
        params = {}
        if max_attendees is not None:
            params["maxAttendees"] = max_attendees
        if time_zone:
            params["timeZone"] = time_zone

        logger.info(f"Retrieving calendar event with ID: {event_id}")

        response = self._get(url, params=params)
        response.raise_for_status()

        event = response.json()

        # Extract event details
        summary = event.get("summary", "Untitled event")
        description = event.get("description", "No description")
        location = event.get("location", "No location specified")

        # Format dates
        start = event.get("start", {})
        end = event.get("end", {})

        start_time = start.get("dateTime", start.get("date", "Unknown"))
        end_time = end.get("dateTime", end.get("date", "Unknown"))

        # Format datetimes using the helper function
        start_formatted = self._format_datetime(start_time)
        end_formatted = self._format_datetime(end_time)

        # Get creator and organizer
        creator = event.get("creator", {}).get("email", "Unknown")
        organizer = event.get("organizer", {}).get("email", "Unknown")

        # Check if it's a recurring event
        recurrence = "Yes" if "recurrence" in event else "No"

        # Get attendees if any
        attendees = event.get("attendees", [])
        attendee_info = ""
        if attendees:
            attendee_info = "\nAttendees:\n"
            for i, attendee in enumerate(attendees, 1):
                email = attendee.get("email", "No email")
                name = attendee.get("displayName", email)
                response_status = attendee.get("responseStatus", "Unknown")

                status_mapping = {
                    "accepted": "Accepted",
                    "declined": "Declined",
                    "tentative": "Maybe",
                    "needsAction": "Not responded",
                }

                formatted_status = status_mapping.get(response_status, response_status)
                attendee_info += f"  {i}. {name} ({email}) - {formatted_status}\n"

        # Format the response
        result = f"Event: {summary}\n"
        result += f"ID: {event_id}\n"
        result += f"When: {start_formatted} to {end_formatted}\n"
        result += f"Where: {location}\n"
        result += f"Description: {description}\n"
        result += f"Creator: {creator}\n"
        result += f"Organizer: {organizer}\n"
        result += f"Recurring: {recurrence}\n"
        result += attendee_info

        return result

    def list_events(
        self,
        max_results: int = 10,
        time_min: str = None,
        time_max: str = None,
        q: str = None,
        order_by: str = "startTime",
        single_events: bool = True,
        time_zone: str = None,
        page_token: str = None,
    ) -> str:
        """List events from your Google Calendar with various filtering options

        Args:
            max_results: Maximum number of events to return (default: 10, max: 2500)
            time_min: Start time (ISO format, e.g. '2023-12-01T00:00:00Z') - defaults to now if not specified
            time_max: End time (ISO format, e.g. '2023-12-31T23:59:59Z')
            q: Free text search terms (searches summary, description, location, attendees, etc.)
            order_by: How to order results - 'startTime' (default) or 'updated'
            single_events: Whether to expand recurring events (default: True)
            time_zone: Time zone used in the response (default is calendar's time zone)
            page_token: Token for retrieving a specific page of results

        Returns:
            A formatted list of events or an error message
        """
        url = f"{self.base_api_url}/events"

        # Build query parameters
        params = {
            "maxResults": max_results,
            "singleEvents": str(single_events).lower(),
            "orderBy": order_by,
        }

        # Set time boundaries if provided, otherwise default to now for time_min
        if time_min:
            params["timeMin"] = time_min
        else:
            # Default to current time if not specified
            now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
            params["timeMin"] = now

        if time_max:
            params["timeMax"] = time_max

        # Add optional filters if provided
        if q:
            params["q"] = q

        if time_zone:
            params["timeZone"] = time_zone

        if page_token:
            params["pageToken"] = page_token

        logger.info(f"Retrieving calendar events with params: {params}")

        response = self._get(url, params=params)
        response.raise_for_status()

        data = response.json()
        events = data.get("items", [])

        if not events:
            return "No events found matching your criteria."

        # Extract calendar information
        calendar_summary = data.get("summary", "Your Calendar")
        time_zone_info = data.get("timeZone", "Unknown")

        result = f"Events from {calendar_summary} (Time Zone: {time_zone_info}):\n\n"

        # Process and format each event
        for i, event in enumerate(events, 1):
            # Get basic event details
            event_id = event.get("id", "No ID")
            summary = event.get("summary", "Untitled event")

            # Get event times and format them
            start = event.get("start", {})
            start_time = start.get("dateTime", start.get("date", "Unknown"))

            # Format the start time using the helper function
            start_formatted = self._format_datetime(start_time)

            # Get location if available
            location = event.get("location", "No location specified")

            # Check if it's a recurring event
            is_recurring = "recurrence" in event
            recurring_info = " (Recurring)" if is_recurring else ""

            # Format the event information
            result += f"{i}. {summary}{recurring_info}\n"
            result += f"   ID: {event_id}\n"
            result += f"   When: {start_formatted}\n"
            result += f"   Where: {location}\n"

            # Add a separator between events
            if i < len(events):
                result += "\n"

        # Add pagination info if available
        if "nextPageToken" in data:
            next_token = data.get("nextPageToken")
            result += (
                f"\nMore events available. Use page_token='{next_token}' to see more."
            )

        return result

    def quick_add_event(self, text: str, send_updates: str = "none") -> str:
        """Create a calendar event using natural language description

        This method allows you to quickly create an event using a simple text string,
        similar to how you would add events in the Google Calendar UI.

        Args:
            text: Text describing the event (e.g., "Meeting with John at Coffee Shop tomorrow 3pm-4pm")
            send_updates: Who should receive notifications - "all", "externalOnly", or "none" (default)

        Returns:
            A confirmation message with the created event details or an error message
        """
        url = f"{self.base_api_url}/events/quickAdd"

        # Use params argument instead of manually constructing URL
        params = {"text": text, "sendUpdates": send_updates}

        logger.info(f"Creating event via quickAdd: '{text}'")

        # Pass params to _post method
        response = self._post(url, data=None, params=params)
        response.raise_for_status()

        event = response.json()

        # Extract event details
        event_id = event.get("id", "Unknown")
        summary = event.get("summary", "Untitled event")

        # Format dates
        start = event.get("start", {})
        end = event.get("end", {})

        start_time = start.get("dateTime", start.get("date", "Unknown"))
        end_time = end.get("dateTime", end.get("date", "Unknown"))

        # Format datetimes using the helper function
        start_formatted = self._format_datetime(start_time)
        end_formatted = self._format_datetime(end_time)

        # Get location if available
        location = event.get("location", "No location specified")

        # Format the confirmation message
        result = "Successfully created event!\n\n"
        result += f"Summary: {summary}\n"
        result += f"When: {start_formatted}"

        # Only add end time if it's different from start (for all-day events they might be the same)
        if start_formatted != end_formatted:
            result += f" to {end_formatted}"

        result += f"\nWhere: {location}\n"
        result += f"Event ID: {event_id}\n"

        # Add a note about viewing the event
        result += f"\nUse get_event('{event_id}') to see full details."

        return result

    def get_event_instances(
        self,
        event_id: str,
        max_results: int = 25,
        time_min: str = None,
        time_max: str = None,
        time_zone: str = None,
        show_deleted: bool = False,
        page_token: str = None,
    ) -> str:
        """Get all instances of a recurring event

        This method retrieves all occurrences of a recurring event within a specified time range.

        Args:
            event_id: ID of the recurring event
            max_results: Maximum number of event instances to return (default: 25, max: 2500)
            time_min: Lower bound (inclusive) for event's end time (ISO format)
            time_max: Upper bound (exclusive) for event's start time (ISO format)
            time_zone: Time zone used in the response (default is calendar's time zone)
            show_deleted: Whether to include deleted instances (default: False)
            page_token: Token for retrieving a specific page of results

        Returns:
            A formatted list of event instances or an error message
        """
        url = f"{self.base_api_url}/events/{event_id}/instances"

        # Build query parameters
        params = {"maxResults": max_results, "showDeleted": str(show_deleted).lower()}

        # Add optional parameters if provided
        if time_min:
            params["timeMin"] = time_min

        if time_max:
            params["timeMax"] = time_max

        if time_zone:
            params["timeZone"] = time_zone

        if page_token:
            params["pageToken"] = page_token

        logger.info(f"Retrieving instances of recurring event with ID: {event_id}")

        response = self._get(url, params=params)
        response.raise_for_status()

        data = response.json()
        instances = data.get("items", [])

        if not instances:
            return f"No instances found for recurring event with ID: {event_id}"

        # Extract event summary from the first instance
        parent_summary = instances[0].get("summary", "Untitled recurring event")

        result = f"Instances of recurring event: {parent_summary}\n\n"

        # Process and format each instance
        for i, instance in enumerate(instances, 1):
            # Get instance ID and status
            instance_id = instance.get("id", "No ID")
            status = instance.get("status", "confirmed")

            # Format status for display
            status_display = ""
            if status == "cancelled":
                status_display = " [CANCELLED]"
            elif status == "tentative":
                status_display = " [TENTATIVE]"

            # Get instance time
            start = instance.get("start", {})
            original_start_time = instance.get("originalStartTime", {})

            # Determine if this is a modified instance
            is_modified = original_start_time and "dateTime" in original_start_time
            modified_indicator = " [MODIFIED]" if is_modified else ""

            # Get the time information
            start_time = start.get("dateTime", start.get("date", "Unknown"))

            # Format the time using the helper function
            formatted_time = self._format_datetime(start_time)

            # Format the instance information
            result += f"{i}. {formatted_time}{status_display}{modified_indicator}\n"
            result += f"   Instance ID: {instance_id}\n"

            # Show original start time if modified
            if is_modified:
                orig_time = original_start_time.get(
                    "dateTime", original_start_time.get("date", "Unknown")
                )
                orig_formatted = self._format_datetime(orig_time)
                result += f"   Original time: {orig_formatted}\n"

            # Add a separator between instances
            if i < len(instances):
                result += "\n"

        # Add pagination info if available
        if "nextPageToken" in data:
            next_token = data.get("nextPageToken")
            result += f"\nMore instances available. Use page_token='{next_token}' to see more."

        return result

    def list_tools(self):
        return [
            self.get_event,
            self.get_today_events,
            self.list_events,
            self.quick_add_event,
            self.get_event_instances,
        ]
