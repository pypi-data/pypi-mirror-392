"""
Java Edition server icon information.

This module fetches the server icon for a Minecraft Java Edition server.
"""
import base64
import requests
import aiohttp
import asyncio
from .constants import DEFAULT_TIMEOUT, BASE_URL
from .exceptions import McstatusioHTTPError, McstatusioTimeoutError
class JavaIcon:
    """
    A class to represent a Minecraft Java Edition server icon.
    """
    
    def __init__(self, hostname: str, port: int = 25565, timeout: int = DEFAULT_TIMEOUT):
        self.hostname = hostname
        self.port = port
        self.timeout = timeout

    def _parse_hostname(self) -> tuple[str, int]:
        """
        Parse the hostname to extract host and port if specified.
        """
        if ':' in self.hostname:
            host, port_str = self.hostname.split(':', 1)
            return host, int(port_str)
        return self.hostname, self.port
    
    def fetch_icon(self) -> bytes:
        """
        Fetch the server icon synchronously.

        Returns:
            The base64 encoded server icon string or None if not found.
        """
        host, port = self._parse_hostname()
        url = f"{BASE_URL}/v2/icon/{host}:{port}?timeout={self.timeout}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.content
            return data
        except requests.RequestException:
            raise McstatusioHTTPError("Failed to fetch server icon.")
        except requests.Timeout:
            raise McstatusioTimeoutError("Request timed out while fetching server icon.")

    async def fetch_icon_async(self) -> bytes:
        """
        Fetch the server icon asynchronously.

        Returns:
            The base64 encoded server icon string or None if not found.
        """
        host, port = self._parse_hostname()
        url = f"{BASE_URL}/v2/icon/{host}:{port}?timeout={self.timeout}"
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.read()
                    return data
        except aiohttp.ClientError:
            raise McstatusioHTTPError("Failed to fetch server icon.")
        except asyncio.TimeoutError:
            raise McstatusioTimeoutError("Request timed out while fetching server icon.")


