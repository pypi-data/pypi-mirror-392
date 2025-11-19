"""
Endercom Agent Functions for Python

This module provides a simple interface for creating agent functions
for the Endercom platform using the new function-based model.
"""

import json
import logging
import signal
import sys
import time
from typing import Dict, Any, List, Callable, Optional

try:
    from flask import Flask, request, jsonify
except ImportError:
    raise ImportError(
        "flask is required for AgentFunction. Install it with: pip install flask"
    )

try:
    import requests
except ImportError:
    raise ImportError(
        "requests is required for AgentFunction. Install it with: pip install requests"
    )


class AgentFunction:
    """
    Simple agent function that exposes HTTP endpoints for the Endercom platform.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        capabilities: List[str] = None,
        platform_url: str = "http://localhost:3000",
        auto_register: bool = True,
        debug: bool = False
    ):
        """
        Initialize the agent function.

        Args:
            name: Human-readable name for your function
            description: What this function does
            capabilities: List of capabilities (e.g., ["analyze", "process"])
            platform_url: URL of the Endercom platform
            auto_register: Automatically register with platform on startup
            debug: Enable debug logging
        """
        self.name = name
        self.description = description
        self.capabilities = capabilities or []
        self.platform_url = platform_url
        self.auto_register = auto_register
        self.debug = debug

        # Function handler
        self._handler: Optional[Callable] = None

        # Flask app for HTTP server
        self.app = Flask(__name__)
        self.app.logger.disabled = not debug

        # Setup logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        self.logger = logging.getLogger(__name__)

        # Setup routes
        self._setup_routes()

        # Function metadata
        self.function_id: Optional[str] = None
        self.endpoint_url: Optional[str] = None

        # Graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def handler(self, func: Callable) -> Callable:
        """
        Decorator to set the function handler.

        @function.handler
        def my_handler(input_data):
            return {"result": "success"}
        """
        self._handler = func
        return func

    def set_handler(self, func: Callable) -> None:
        """
        Set the function handler programmatically.
        """
        self._handler = func

    def _setup_routes(self):
        """Setup Flask routes for the function endpoints."""

        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({"status": "ok", "name": self.name})

        @self.app.route('/execute', methods=['POST'])
        def execute():
            """Function execution endpoint."""
            try:
                if not self._handler:
                    return jsonify({
                        "error": "No handler defined for this function"
                    }), 500

                # Get input data
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No JSON data provided"}), 400

                input_data = data.get('input', data)

                self.logger.info(f"Executing function with input: {input_data}")

                # Execute the handler
                result = self._handler(input_data)

                self.logger.info(f"Function execution completed: {result}")

                return jsonify(result)

            except Exception as e:
                self.logger.error(f"Function execution error: {str(e)}")
                return jsonify({
                    "error": f"Function execution failed: {str(e)}"
                }), 500

        @self.app.route('/info', methods=['GET'])
        def info():
            """Function information endpoint."""
            return jsonify({
                "name": self.name,
                "description": self.description,
                "capabilities": self.capabilities,
                "status": "running"
            })

    def register_with_platform(self, host: str = "localhost", port: int = 3001) -> Dict[str, Any]:
        """
        Register this function with the Endercom platform.

        Args:
            host: Host where this function is running
            port: Port where this function is running

        Returns:
            Registration response from platform
        """
        if not self.endpoint_url:
            self.endpoint_url = f"http://{host}:{port}/execute"

        registration_data = {
            "name": self.name,
            "description": self.description,
            "endpoint": self.endpoint_url,
            "capabilities": self.capabilities
        }

        try:
            response = requests.post(
                f"{self.platform_url}/api/agent-functions",
                json=registration_data,
                timeout=10
            )

            if response.status_code == 201:
                result = response.json()
                if result.get('success') and result.get('data'):
                    self.function_id = result['data']['id']
                    self.logger.info(f"Successfully registered function '{self.name}' with ID: {self.function_id}")
                    return result
                else:
                    raise Exception(f"Registration failed: {result.get('error', 'Unknown error')}")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

        except requests.RequestException as e:
            self.logger.error(f"Failed to register with platform: {str(e)}")
            raise Exception(f"Platform registration failed: {str(e)}")

    def unregister_from_platform(self) -> bool:
        """
        Unregister this function from the Endercom platform.
        """
        if not self.function_id:
            self.logger.warning("No function ID available, cannot unregister")
            return False

        try:
            response = requests.delete(
                f"{self.platform_url}/api/agent-functions/{self.function_id}",
                timeout=10
            )

            if response.status_code == 200:
                self.logger.info(f"Successfully unregistered function '{self.name}'")
                return True
            else:
                self.logger.error(f"Failed to unregister: HTTP {response.status_code}")
                return False

        except requests.RequestException as e:
            self.logger.error(f"Failed to unregister from platform: {str(e)}")
            return False

    def run(self, host: str = "localhost", port: int = 3001, **kwargs) -> None:
        """
        Start the agent function server.

        Args:
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional arguments for Flask.run()
        """
        if not self._handler:
            raise ValueError("No handler defined. Use @function.handler or set_handler()")

        # Auto-register if enabled
        if self.auto_register:
            try:
                self.register_with_platform(host, port)
            except Exception as e:
                self.logger.warning(f"Auto-registration failed: {str(e)}")
                self.logger.info("Function will still run, but won't be registered with platform")

        self.logger.info(f"Starting {self.name} on {host}:{port}")
        self.logger.info(f"Health check: http://{host}:{port}/health")
        self.logger.info(f"Execute endpoint: http://{host}:{port}/execute")
        self.logger.info(f"Function info: http://{host}:{port}/info")

        # Start Flask server
        self.app.run(
            host=host,
            port=port,
            debug=self.debug,
            **kwargs
        )

    def _signal_handler(self, signum, frame):
        """Handle graceful shutdown."""
        self.logger.info("Shutting down agent function...")

        if self.auto_register:
            try:
                self.unregister_from_platform()
            except:
                pass

        sys.exit(0)


def create_function(name: str, handler: Callable, **kwargs) -> AgentFunction:
    """
    Create and return a configured AgentFunction.

    Example:
        def my_handler(input_data):
            return {"result": "success"}

        function = create_function("My Function", my_handler)
        function.run()
    """
    function = AgentFunction(name=name, **kwargs)
    function.set_handler(handler)
    return function