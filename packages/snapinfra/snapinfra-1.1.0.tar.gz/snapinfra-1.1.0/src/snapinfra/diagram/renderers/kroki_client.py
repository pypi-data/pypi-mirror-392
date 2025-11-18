"""Kroki client for rendering diagrams."""

import base64
import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Literal, Optional, Dict, Any
import httpx
from rich.console import Console

console = Console()


class KrokiServerManager:
    """Manages Kroki server lifecycle using Docker."""

    KROKI_IMAGE = "yuzutech/kroki"
    KROKI_TAG = "latest"
    CONTAINER_NAME = "snapinfra-kroki"
    DEFAULT_PORT = 8000

    @classmethod
    def is_docker_available(cls) -> bool:
        """Check if Docker is available.

        Returns:
            True if Docker is available
        """
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @classmethod
    def is_kroki_running(cls, port: int = DEFAULT_PORT) -> bool:
        """Check if Kroki server is running.

        Args:
            port: Port number to check

        Returns:
            True if Kroki is responding
        """
        try:
            import httpx
            response = httpx.get(f"http://localhost:{port}/health", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    @classmethod
    def start_kroki(cls, port: int = DEFAULT_PORT) -> bool:
        """Start Kroki Docker container.

        Args:
            port: Port to bind to

        Returns:
            True if started successfully
        """
        if not cls.is_docker_available():
            console.print("Docker is not available", style="red")
            return False

        if cls.is_kroki_running(port):
            console.print(f"Kroki is already running on port {port}", style="green")
            return True

        try:
            # Stop existing container if any
            subprocess.run(
                ["docker", "stop", cls.CONTAINER_NAME],
                capture_output=True,
                timeout=10
            )
            subprocess.run(
                ["docker", "rm", cls.CONTAINER_NAME],
                capture_output=True,
                timeout=10
            )

            # Start new container
            console.print(f"Starting Kroki server on port {port}...", style="cyan")

            result = subprocess.run(
                [
                    "docker", "run",
                    "-d",
                    "--name", cls.CONTAINER_NAME,
                    "-p", f"{port}:8000",
                    f"{cls.KROKI_IMAGE}:{cls.KROKI_TAG}"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                console.print(f"Failed to start Kroki: {result.stderr}", style="red")
                return False

            # Wait for Kroki to be ready
            console.print("Waiting for Kroki to be ready...", style="cyan")
            for _ in range(30):  # Wait up to 30 seconds
                if cls.is_kroki_running(port):
                    console.print("Kroki server started successfully", style="green")
                    return True
                time.sleep(1)

            console.print("Kroki server did not start in time", style="red")
            return False

        except subprocess.TimeoutExpired:
            console.print("Timeout while starting Kroki", style="red")
            return False
        except Exception as e:
            console.print(f"Error starting Kroki: {e}", style="red")
            return False

    @classmethod
    def stop_kroki(cls) -> bool:
        """Stop Kroki Docker container.

        Returns:
            True if stopped successfully
        """
        try:
            result = subprocess.run(
                ["docker", "stop", cls.CONTAINER_NAME],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                subprocess.run(
                    ["docker", "rm", cls.CONTAINER_NAME],
                    capture_output=True,
                    timeout=10
                )
                console.print("Kroki server stopped", style="green")
                return True
            else:
                console.print("Kroki container not found", style="yellow")
                return False

        except Exception as e:
            console.print(f"Error stopping Kroki: {e}", style="red")
            return False


class KrokiClient:
    """Client for rendering diagrams using Kroki API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        auto_start: bool = True,
        cache_dir: Optional[Path] = None
    ):
        """Initialize Kroki client.

        Args:
            base_url: Base URL of Kroki server
            auto_start: Automatically start Kroki if not running
            cache_dir: Directory for caching rendered diagrams
        """
        self.base_url = base_url.rstrip("/")
        self.auto_start = auto_start
        self.cache_dir = cache_dir

        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)

        # Ensure Kroki is running
        if auto_start:
            self._ensure_kroki_running()

    def _ensure_kroki_running(self) -> None:
        """Ensure Kroki server is running."""
        # Extract port from base URL
        import re
        match = re.search(r':(\d+)', self.base_url)
        port = int(match.group(1)) if match else 8000

        if not KrokiServerManager.is_kroki_running(port):
            KrokiServerManager.start_kroki(port)

    async def render(
        self,
        diagram_source: str,
        diagram_type: Literal[
            "mermaid", "d2", "plantuml", "graphviz", "structurizr",
            "c4plantuml", "bpmn", "excalidraw", "svgbob"
        ],
        output_format: Literal["svg", "png", "pdf", "jpeg"] = "svg",
        use_cache: bool = True
    ) -> bytes:
        """Render diagram using Kroki API (GET method).

        Args:
            diagram_source: Diagram source code
            diagram_type: Type of diagram
            output_format: Output format
            use_cache: Use cache if available

        Returns:
            Rendered diagram as bytes
        """
        # Check cache first
        if use_cache and self.cache_dir:
            cached_result = self._get_from_cache(diagram_source, diagram_type, output_format)
            if cached_result:
                return cached_result

        # Encode diagram source for URL
        compressed = self._compress_diagram(diagram_source)
        encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')

        url = f"{self.base_url}/{diagram_type}/{output_format}/{encoded}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()

                result = response.content

                # Cache the result
                if use_cache and self.cache_dir:
                    self._save_to_cache(diagram_source, diagram_type, output_format, result)

                return result

            except httpx.HTTPStatusError as e:
                raise Exception(f"Kroki rendering failed: {e.response.text}")
            except httpx.RequestError as e:
                raise Exception(f"Failed to connect to Kroki: {e}")

    async def render_json(
        self,
        diagram_source: str,
        diagram_type: str,
        output_format: str = "svg",
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Render diagram using Kroki API (POST method for large diagrams).

        Args:
            diagram_source: Diagram source code
            diagram_type: Type of diagram
            output_format: Output format
            options: Additional rendering options

        Returns:
            Rendered diagram as bytes
        """
        url = f"{self.base_url}"

        payload = {
            "diagram_source": diagram_source,
            "diagram_type": diagram_type,
            "output_format": output_format
        }

        if options:
            payload["diagram_options"] = options

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.content

            except httpx.HTTPStatusError as e:
                raise Exception(f"Kroki rendering failed: {e.response.text}")
            except httpx.RequestError as e:
                raise Exception(f"Failed to connect to Kroki: {e}")

    def _compress_diagram(self, source: str) -> bytes:
        """Compress diagram source using zlib.

        Args:
            source: Diagram source code

        Returns:
            Compressed bytes
        """
        import zlib
        return zlib.compress(source.encode('utf-8'), level=9)

    def _get_cache_key(self, diagram_source: str, diagram_type: str, output_format: str) -> str:
        """Generate cache key for diagram.

        Args:
            diagram_source: Diagram source
            diagram_type: Diagram type
            output_format: Output format

        Returns:
            Cache key
        """
        content = f"{diagram_type}:{output_format}:{diagram_source}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _get_from_cache(
        self,
        diagram_source: str,
        diagram_type: str,
        output_format: str
    ) -> Optional[bytes]:
        """Get rendered diagram from cache.

        Args:
            diagram_source: Diagram source
            diagram_type: Diagram type
            output_format: Output format

        Returns:
            Cached result or None
        """
        if not self.cache_dir:
            return None

        cache_key = self._get_cache_key(diagram_source, diagram_type, output_format)
        cache_file = self.cache_dir / f"{cache_key}.{output_format}"

        if cache_file.exists():
            try:
                return cache_file.read_bytes()
            except Exception:
                return None

        return None

    def _save_to_cache(
        self,
        diagram_source: str,
        diagram_type: str,
        output_format: str,
        content: bytes
    ) -> None:
        """Save rendered diagram to cache.

        Args:
            diagram_source: Diagram source
            diagram_type: Diagram type
            output_format: Output format
            content: Rendered content
        """
        if not self.cache_dir:
            return

        cache_key = self._get_cache_key(diagram_source, diagram_type, output_format)
        cache_file = self.cache_dir / f"{cache_key}.{output_format}"

        try:
            cache_file.write_bytes(content)
        except Exception:
            pass  # Ignore cache write failures

    async def health_check(self) -> bool:
        """Check if Kroki server is healthy.

        Returns:
            True if healthy
        """
        url = f"{self.base_url}/health"

        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(url)
                return response.status_code == 200
            except Exception:
                return False

    async def get_supported_formats(self, diagram_type: str) -> list:
        """Get supported output formats for a diagram type.

        Args:
            diagram_type: Diagram type

        Returns:
            List of supported formats
        """
        # Kroki supports different formats for different diagram types
        common_formats = ["svg", "png", "pdf"]

        # Some diagram types support additional formats
        if diagram_type in ["mermaid", "plantuml", "graphviz"]:
            common_formats.append("jpeg")

        return common_formats
