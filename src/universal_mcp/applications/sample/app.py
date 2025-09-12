import datetime

import httpx
from loguru import logger

from universal_mcp.applications.application import BaseApplication


class SampleApp(BaseApplication):
    """A sample application providing basic utility tools."""

    def __init__(self, **kwargs):
        """Initializes the SampleToolApp with the name 'sample_tool_app'."""
        super().__init__(name="sample")

    def get_current_time(self):
        """Get the current system time as a formatted string.

        Returns:
            str: The current time in the format 'YYYY-MM-DD HH:MM:SS'.
        Tags:
            time, date, current, system, utility, important
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_current_date(self):
        """Get the current system date as a formatted string.

        Returns:
            str: The current date in the format 'YYYY-MM-DD'.
        Tags:
            time, date, current, system, utility, important
        """
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def calculate(self, expression: str):
        """Safely evaluate a mathematical expression.

        Args:
            expression (str): The mathematical expression to evaluate.

        Returns:
            str: The result of the calculation, or an error message if evaluation fails.
        Tags:
            math, calculation, utility, important
        """
        try:
            # Safe evaluation of mathematical expressions
            result = eval(expression, {"__builtins__": {}}, {})  # noqa: S102
            return f"Result: {result}"
        except Exception as e:
            return f"Error in calculation: {str(e)}"

    def read_file(self, filename: str):
        """Read content from a file.

        Args:
            filename (str): The name of the file to read from.

        Returns:
            str: The content of the file, or an error message if the operation fails.
        Tags:
            file, read, utility, important
        """
        try:
            with open(filename) as f:
                return f"File content:\n{f.read()}"
        except Exception as e:
            return f"File read error: {str(e)}"

    def write_file(self, filename: str, content: str):
        """Write content to a file.

        Args:
            filename (str): The name of the file to write to.
            content (str): The content to write to the file.

        Returns:
            str: Success message or an error message if the operation fails.
        Tags:
            file, write, utility, important
        """
        try:
            with open(filename, "w") as f:
                f.write(content)
            return f"Successfully wrote to {filename}"
        except Exception as e:
            return f"File write error: {str(e)}"

    def get_weather(
        self,
        latitude: float,
        longitude: float,
        current: list[str] | None = None,
        hourly: list[str] | None = None,
        daily: list[str] | None = None,
        timezone: str = "auto",
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
        precipitation_unit: str = "mm",
    ) -> dict:
        """
        Get weather data from Open-Meteo API.

        Args:
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            current (List[str], optional): Current weather parameters to fetch
            hourly (List[str], optional): Hourly weather parameters to fetch
            daily (List[str], optional): Daily weather parameters to fetch
            timezone (str): Timezone (default: "auto")
            temperature_unit (str): Temperature unit - "celsius" or "fahrenheit"
            wind_speed_unit (str): Wind speed unit - "kmh", "ms", "mph", "kn"
            precipitation_unit (str): Precipitation unit - "mm" or "inch"

        Returns:
            Dict: Weather data from the API

        Raises:
            httpx.RequestError: If API request fails
            ValueError: If coordinates are invalid
        """
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")

        # Base URL
        base_url = "https://api.open-meteo.com/v1/forecast"

        # Default parameters if none provided
        if current is None:
            current = ["temperature_2m", "relative_humidity_2m", "weather_code", "wind_speed_10m", "wind_direction_10m"]

        if daily is None:
            daily = ["temperature_2m_max", "temperature_2m_min", "weather_code", "precipitation_sum"]

        # Build parameters
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "temperature_unit": temperature_unit,
            "wind_speed_unit": wind_speed_unit,
            "precipitation_unit": precipitation_unit,
        }

        # Add weather parameters
        if current:
            params["current"] = ",".join(current)
        if hourly:
            params["hourly"] = ",".join(hourly)
        if daily:
            params["daily"] = ",".join(daily)

        try:
            # Make API request
            with httpx.Client(timeout=10) as client:
                response = client.get(base_url, params=params)
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException as e:
            raise httpx.RequestError("Request timed out") from e
        except httpx.ConnectError as e:
            raise httpx.RequestError("Connection error") from e
        except httpx.HTTPStatusError as e:
            raise httpx.RequestError(f"HTTP error: {e}") from e
        except httpx.RequestError as e:
            raise httpx.RequestError(f"Request failed: {e}") from e

    def get_simple_weather(self, latitude: float, longitude: float) -> dict:
        """
        Get simplified current weather data.

        Args:
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate

        Returns:
            Dict: Simplified weather data with current conditions
        """

        try:
            weather_data = self.get_weather(
                latitude=latitude,
                longitude=longitude,
                current=[
                    "temperature_2m",
                    "relative_humidity_2m",
                    "weather_code",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "precipitation",
                ],
            )

            # Weather code descriptions (WMO Weather interpretation codes)
            weather_codes = {
                0: "Clear sky",
                1: "Mainly clear",
                2: "Partly cloudy",
                3: "Overcast",
                45: "Fog",
                48: "Depositing rime fog",
                51: "Light drizzle",
                53: "Moderate drizzle",
                55: "Dense drizzle",
                61: "Slight rain",
                63: "Moderate rain",
                65: "Heavy rain",
                71: "Slight snow fall",
                73: "Moderate snow fall",
                75: "Heavy snow fall",
                80: "Slight rain showers",
                81: "Moderate rain showers",
                82: "Violent rain showers",
                95: "Thunderstorm",
                96: "Thunderstorm with slight hail",
                99: "Thunderstorm with heavy hail",
            }

            current = weather_data.get("current", {})
            weather_code = current.get("weather_code", 0)

            simplified = {
                "location": {
                    "latitude": weather_data.get("latitude"),
                    "longitude": weather_data.get("longitude"),
                    "timezone": weather_data.get("timezone"),
                },
                "current": {
                    "time": current.get("time"),
                    "temperature": current.get("temperature_2m"),
                    "temperature_unit": weather_data.get("current_units", {}).get("temperature_2m", "°C"),
                    "humidity": current.get("relative_humidity_2m"),
                    "weather_description": weather_codes.get(weather_code, "Unknown"),
                    "weather_code": weather_code,
                    "wind_speed": current.get("wind_speed_10m"),
                    "wind_speed_unit": weather_data.get("current_units", {}).get("wind_speed_10m", "km/h"),
                    "wind_direction": current.get("wind_direction_10m"),
                    "precipitation": current.get("precipitation", 0),
                },
            }

            return simplified

        except Exception as e:
            return {"error": str(e)}

    def generate_image(self, prompt: str):
        """Generate an image based on a prompt.
        A
        Args:
            prompt (str): The prompt to generate an image from.

        Returns:
            dict: The generated image.
        Tags:
            image, generate, utility, important
        """
        import base64
        import io

        from PIL import Image, ImageDraw, ImageFont

        # Create a simple placeholder image
        img = Image.new("RGB", (600, 400), color="lightblue")
        draw = ImageDraw.Draw(img)

        # Add text to the image
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except Exception as e:
            logger.error(f"Error loading font: {e}")
            font = None

        text = f"Generated: {prompt[:50]}..."
        draw.text((50, 200), text, fill="black", font=font)

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {"type": "image", "data": img_base64, "mime_type": "image/png", "file_name": "sample.png"}

    def list_tools(self):
        """List all available tool methods in this application.

        Returns:
            list: A list of callable tool methods.
        """
        return [
            self.get_current_time,
            self.get_current_date,
            self.calculate,
            self.read_file,
            self.write_file,
            self.get_simple_weather,
            self.generate_image,
        ]
