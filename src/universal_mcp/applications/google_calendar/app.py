from datetime import datetime, timedelta

from loguru import logger

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class GoogleCalendarApp(APIApplication):
    def __init__(self, integration: Integration) -> None:
        super().__init__(name="google-calendar", integration=integration)
        self.base_api_url = "https://www.googleapis.com/calendar/v3/calendars/primary"

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
        """
        Retrieves and formats events from Google Calendar for today or a specified number of future days, with optional result limiting and timezone specification.

        Args:
            days: Number of days to retrieve events for (default: 1, which is just today)
            max_results: Maximum number of events to return (optional)
            time_zone: Time zone used in the response (optional, default is calendar's time zone)

        Returns:
            A formatted string containing a list of calendar events with their times and IDs, or a message indicating no events were found

        Raises:
            HTTPError: Raised when the API request fails or returns an error status code

        Tags:
            fetch, list, calendar, events, date-time, important, api, formatting
        """
        today = datetime.utcnow().date()
        end_date = today + timedelta(days=days)
        time_min = f"{today.isoformat()}T00:00:00Z"
        time_max = f"{end_date.isoformat()}T00:00:00Z"
        url = f"{self.base_api_url}/events"
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
        """
        Retrieves and formats detailed information about a specific Google Calendar event by its ID

        Args:
            event_id: The unique identifier of the calendar event to retrieve
            max_attendees: Optional. The maximum number of attendees to include in the response. If None, includes all attendees
            time_zone: Optional. The time zone to use for formatting dates in the response. If None, uses the calendar's default time zone

        Returns:
            A formatted string containing comprehensive event details including summary, time, location, description, creator, organizer, recurrence status, and attendee information

        Raises:
            HTTPError: Raised when the API request fails or returns an error status code
            JSONDecodeError: Raised when the API response cannot be parsed as JSON

        Tags:
            retrieve, calendar, event, format, api, important
        """
        url = f"{self.base_api_url}/events/{event_id}"
        params = {}
        if max_attendees is not None:
            params["maxAttendees"] = max_attendees
        if time_zone:
            params["timeZone"] = time_zone
        logger.info(f"Retrieving calendar event with ID: {event_id}")
        response = self._get(url, params=params)
        response.raise_for_status()
        event = response.json()
        summary = event.get("summary", "Untitled event")
        description = event.get("description", "No description")
        location = event.get("location", "No location specified")
        start = event.get("start", {})
        end = event.get("end", {})
        start_time = start.get("dateTime", start.get("date", "Unknown"))
        end_time = end.get("dateTime", end.get("date", "Unknown"))
        start_formatted = self._format_datetime(start_time)
        end_formatted = self._format_datetime(end_time)
        creator = event.get("creator", {}).get("email", "Unknown")
        organizer = event.get("organizer", {}).get("email", "Unknown")
        recurrence = "Yes" if "recurrence" in event else "No"
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
        """
        Retrieves and formats a list of events from Google Calendar with customizable filtering, sorting, and pagination options

        Args:
            max_results: Maximum number of events to return (default: 10, max: 2500)
            time_min: Start time in ISO format (e.g., '2023-12-01T00:00:00Z'). Defaults to current time if not specified
            time_max: End time in ISO format (e.g., '2023-12-31T23:59:59Z')
            q: Free text search terms to filter events (searches across summary, description, location, attendees)
            order_by: Sort order for results - either 'startTime' (default) or 'updated'
            single_events: Whether to expand recurring events into individual instances (default: True)
            time_zone: Time zone for response formatting (defaults to calendar's time zone)
            page_token: Token for retrieving a specific page of results in paginated responses

        Returns:
            A formatted string containing the list of events with details including summary, ID, start time, and location, or a message if no events are found

        Raises:
            HTTPError: Raised when the API request fails or returns an error status code

        Tags:
            list, calendar, events, search, filter, pagination, format, important
        """
        url = f"{self.base_api_url}/events"
        params = {
            "maxResults": max_results,
            "singleEvents": str(single_events).lower(),
            "orderBy": order_by,
        }
        if time_min:
            params["timeMin"] = time_min
        else:
            # Default to current time if not specified
            now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
            params["timeMin"] = now
        if time_max:
            params["timeMax"] = time_max
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
        calendar_summary = data.get("summary", "Your Calendar")
        time_zone_info = data.get("timeZone", "Unknown")
        result = f"Events from {calendar_summary} (Time Zone: {time_zone_info}):\n\n"
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
        if "nextPageToken" in data:
            next_token = data.get("nextPageToken")
            result += (
                f"\nMore events available. Use page_token='{next_token}' to see more."
            )
        return result

    def quick_add_event(self, text: str, send_updates: str = "none") -> str:
        """
        Creates a calendar event using natural language text input and returns a formatted confirmation message with event details.

        Args:
            text: Natural language text describing the event (e.g., 'Meeting with John at Coffee Shop tomorrow 3pm-4pm')
            send_updates: Specifies who should receive event notifications: 'all', 'externalOnly', or 'none' (default)

        Returns:
            A formatted string containing the confirmation message with event details including summary, time, location, and event ID

        Raises:
            HTTPError: Raised when the API request fails or returns an error status code

        Tags:
            create, calendar, event, quick-add, natural-language, important
        """
        url = f"{self.base_api_url}/events/quickAdd"
        params = {"text": text, "sendUpdates": send_updates}
        logger.info(f"Creating event via quickAdd: '{text}'")
        response = self._post(url, data=None, params=params)
        response.raise_for_status()
        event = response.json()
        event_id = event.get("id", "Unknown")
        summary = event.get("summary", "Untitled event")
        start = event.get("start", {})
        end = event.get("end", {})
        start_time = start.get("dateTime", start.get("date", "Unknown"))
        end_time = end.get("dateTime", end.get("date", "Unknown"))
        start_formatted = self._format_datetime(start_time)
        end_formatted = self._format_datetime(end_time)
        location = event.get("location", "No location specified")
        result = "Successfully created event!\n\n"
        result += f"Summary: {summary}\n"
        result += f"When: {start_formatted}"
        if start_formatted != end_formatted:
            result += f" to {end_formatted}"
        result += f"\nWhere: {location}\n"
        result += f"Event ID: {event_id}\n"
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
        """
        Retrieves and formats all instances of a recurring calendar event within a specified time range, showing details like time, status, and modifications for each occurrence.

        Args:
            event_id: ID of the recurring event
            max_results: Maximum number of event instances to return (default: 25, max: 2500)
            time_min: Lower bound (inclusive) for event's end time in ISO format
            time_max: Upper bound (exclusive) for event's start time in ISO format
            time_zone: Time zone used in the response (defaults to calendar's time zone)
            show_deleted: Whether to include deleted instances (default: False)
            page_token: Token for retrieving a specific page of results

        Returns:
            A formatted string containing a list of event instances with details including time, status, instance ID, and modification information, plus pagination token if applicable.

        Raises:
            HTTPError: Raised when the API request fails or returns an error status code
            JSONDecodeError: Raised when the API response cannot be parsed as JSON

        Tags:
            list, retrieve, calendar, events, recurring, pagination, formatting, important
        """
        url = f"{self.base_api_url}/events/{event_id}/instances"
        params = {"maxResults": max_results, "showDeleted": str(show_deleted).lower()}
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
        parent_summary = instances[0].get("summary", "Untitled recurring event")
        result = f"Instances of recurring event: {parent_summary}\n\n"
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
