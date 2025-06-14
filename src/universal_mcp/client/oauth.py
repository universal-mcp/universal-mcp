import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from universal_mcp.utils.singleton import Singleton


class CallbackHandler(BaseHTTPRequestHandler):
    """Handles the HTTP GET request for an OAuth 2.0 callback.

    This handler is designed to capture the authorization code and state
    (or an error) returned by an OAuth 2.0 authorization server as query
    parameters in the redirect URI. It stores these values in a shared
    `callback_data` dictionary.

    It sends a simple HTML response to the user's browser indicating
    success or failure of the authorization attempt.
    """

    def __init__(self, request, client_address, server, callback_data: dict):
        """Initializes the CallbackHandler.

        Args:
            request: The HTTP request.
            client_address: The client's address.
            server: The server instance.
            callback_data (dict): A dictionary shared with the `CallbackServer`
                to store the captured OAuth parameters (e.g.,
                `authorization_code`, `state`, `error`).
        """
        self.callback_data = callback_data
        super().__init__(request, client_address, server)

    def do_GET(self):
        """Handles the GET request from the OAuth authorization server's redirect.

        Parses the URL query parameters to find 'code' and 'state', or 'error'.
        Stores these values into the `self.callback_data` dictionary.
        Responds to the browser with a success or failure HTML page.
        """
        parsed = urlparse(self.path)
        query_params = parse_qs(parsed.query)

        if "code" in query_params:
            self.callback_data["authorization_code"] = query_params["code"][0]
            self.callback_data["state"] = query_params.get("state", [None])[0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
            <html>
            <body>
                <h1>Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
                <script>setTimeout(() => window.close(), 2000);</script>
            </body>
            </html>
            """)
        elif "error" in query_params:
            self.callback_data["error"] = query_params["error"][0]
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                f"""
            <html>
            <body>
                <h1>Authorization Failed</h1>
                <p>Error: {query_params["error"][0]}</p>
                <p>You can close this window and return to the terminal.</p>
            </body>
            </html>
            """.encode()
            )
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: Any):
        """Suppresses the default logging of HTTP requests.

        Overrides the base class method to prevent request logs from being
        printed to stderr, keeping the console cleaner during the OAuth flow.
        """
        pass


class CallbackServer(metaclass=Singleton):
    """A singleton HTTP server to manage OAuth 2.0 redirect callbacks.

    This server runs in a background thread, listening on a specified
    localhost port. It uses the `CallbackHandler` to capture the
    authorization code or error returned by an OAuth 2.0 provider
    after user authentication.

    Being a Singleton, only one instance of this server will run per
    application, even if instantiated multiple times.

    Attributes:
        port (int): The port number on localhost where the server listens.
        server (HTTPServer | None): The underlying `HTTPServer` instance.
            None if the server is not running.
        thread (threading.Thread | None): The background thread in which
            the server runs. None if the server is not running.
        callback_data (dict): A dictionary to store data received from the
            OAuth callback (e.g., `authorization_code`, `state`, `error`).
            This is shared with the `CallbackHandler`.
        _running (bool): A flag indicating whether the server is currently
            started and listening.
    """

    def __init__(self, port: int = 3000):
        """Initializes the CallbackServer.

        Args:
            port (int, optional): The port number on localhost for the server
                to listen on. Defaults to 3000.
        """
        self.port = port
        self.server = None
        self.thread = None
        self.callback_data = {"authorization_code": None, "state": None, "error": None}
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def _create_handler_with_data(self):
        """Creates a `CallbackHandler` subclass with shared `callback_data`.

        This method dynamically defines a new handler class that inherits from
        `CallbackHandler`. The purpose is to allow the handler instances
        to access and modify the `self.callback_data` dictionary of this
        `CallbackServer` instance, enabling communication of OAuth parameters
        from the handler back to the server logic.

        Returns:
            type: A new class, subclass of `CallbackHandler`.
        """
        callback_data = self.callback_data

        class DataCallbackHandler(CallbackHandler):
            def __init__(self, request, client_address, server):
                super().__init__(request, client_address, server, callback_data)

        return DataCallbackHandler

    def start(self):
        """Starts the HTTP callback server in a background daemon thread.

        If the server is not already running, it initializes an `HTTPServer`
        with a specialized `CallbackHandler` and starts it in a new
        daemon thread. This allows the main application flow to continue
        while waiting for the OAuth callback.
        """
        if self._running:
            return
        handler_class = self._create_handler_with_data()
        self.server = HTTPServer(("localhost", self.port), handler_class)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"🖥️  Started callback server on http://localhost:{self.port}")
        self._running = True

    def stop(self):
        """Stops the HTTP callback server and cleans up resources.

        Shuts down the `HTTPServer` and waits for its background thread
        to complete.
        """
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread:
            self.thread.join(timeout=1)

    def wait_for_callback(self, timeout: int = 300) -> str:
        """Waits for the OAuth callback to provide an authorization code.

        This method polls the `self.callback_data` dictionary until an
        authorization code is received or an error is reported by the
        `CallbackHandler`, or until the timeout is reached.

        Args:
            timeout (int, optional): The maximum time in seconds to wait
                for the callback. Defaults to 300 seconds (5 minutes).

        Returns:
            str: The received authorization code.

        Raises:
            Exception: If an error is reported in the callback
                       (e.g., "OAuth error: <error_message>").
            Exception: If the timeout is reached before a code or error
                       is received (e.g., "Timeout waiting for OAuth callback").
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.callback_data["authorization_code"]:
                return self.callback_data["authorization_code"]
            elif self.callback_data["error"]:
                raise Exception(f"OAuth error: {self.callback_data['error']}")
            time.sleep(0.1)
        raise Exception("Timeout waiting for OAuth callback")

    def get_state(self) -> str | None:
        """Retrieves the 'state' parameter received during the OAuth callback.

        The state parameter is often used to prevent cross-site request forgery (CSRF)
        attacks by matching its value with one sent in the initial authorization request.

        Returns:
            str | None: The 'state' parameter value if received, otherwise None.
        """
        return self.callback_data["state"]
