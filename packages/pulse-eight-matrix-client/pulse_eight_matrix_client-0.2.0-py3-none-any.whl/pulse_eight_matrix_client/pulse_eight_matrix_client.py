"""Pulse8 HDBaseT Matrix Client."""

import asyncio
import logging
import time
from typing import List, Optional
import aiohttp

from .exceptions import Pulse8ConnectionError, Pulse8APIError
from .models import (
    SystemDetails,
    SystemFeatures,
    Port,
    PortListResponse,
    PortDetails,
    SetPortResponse,
)

_LOGGER = logging.getLogger(__name__)


class PulseEightMatrixClient:
    """Async client for Pulse8 HDBaseT Matrix."""

    def __init__(
        self,
        host: str,
        port: int = 80,
        timeout: int = 10,
    ):
        """
        Initialize the Pulse8 Matrix client.

        Args:
            host: IP address or hostname of the matrix
            port: HTTP port (default: 80)
            timeout: Request timeout in seconds (default: 10)
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def connect(self):
        """Create HTTP session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)

    async def close(self):
        """Close HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None

    def _get_timestamp(self) -> int:
        """Generate cache-busting timestamp."""
        return int(time.time() * 1000)

    async def _request(self, endpoint: str) -> dict:
        """
        Make an HTTP GET request to the matrix.

        Args:
            endpoint: API endpoint path

        Returns:
            JSON response as dictionary

        Raises:
            Pulse8ConnectionError: If connection fails
            Pulse8APIError: If API returns an error
        """
        if self._session is None:
            await self.connect()

        url = f"{self.base_url}{endpoint}"
        timestamp = self._get_timestamp()

        # Add cache-busting parameter
        separator = "&" if "?" in url else "?"
        url_with_timestamp = f"{url}{separator}_={timestamp}"

        try:
            async with self._session.get(url_with_timestamp) as response:
                if response.status != 200:
                    raise Pulse8APIError(
                        f"API returned status {response.status}",
                        status_code=response.status
                    )

                data = await response.json()

                # Check if Result is False
                if isinstance(data, dict) and not data.get("Result", True):
                    raise Pulse8APIError(
                        f"API returned Result=false: {data.get('Message', 'Unknown error')}"
                    )

                return data

        except aiohttp.ClientError as e:
            raise Pulse8ConnectionError(f"Failed to connect to matrix: {e}") from e
        except Exception as e:
            if isinstance(e, (Pulse8ConnectionError, Pulse8APIError)):
                raise
            raise Pulse8APIError(f"Unexpected error: {e}") from e

    async def get_system_details(self) -> SystemDetails:
        """
        Get system details including model, version, and serial number.

        Returns:
            SystemDetails object with system information
        """
        data = await self._request("/System/Details")
        return SystemDetails.from_dict(data)

    async def get_system_features(self) -> SystemFeatures:
        """
        Get system features and capabilities.

        Returns:
            SystemFeatures object with feature information
        """
        data = await self._request("/system/features")
        return SystemFeatures.from_dict(data)

    async def get_ports(self) -> List[Port]:
        """
        Get list of all ports (inputs and outputs).

        Returns:
            List of Port objects
        """
        data = await self._request("/Port/List")
        port_list = PortListResponse.from_dict(data)
        return port_list.ports

    async def get_input_ports(self) -> List[Port]:
        """
        Get list of input ports only.

        Returns:
            List of input Port objects
        """
        ports = await self.get_ports()
        return [p for p in ports if p.mode == "Input"]

    async def get_output_ports(self) -> List[Port]:
        """
        Get list of output ports only.

        Returns:
            List of output Port objects
        """
        ports = await self.get_ports()
        return [p for p in ports if p.mode == "Output"]

    async def get_input_details(self, bay: int) -> PortDetails:
        """
        Get detailed information about an input port.

        Args:
            bay: Input bay number (0-7 typically)

        Returns:
            PortDetails object with detailed port information
        """
        data = await self._request(f"/Port/Details/Input/{bay}")
        return PortDetails.from_dict(data)

    async def get_output_details(self, bay: int) -> PortDetails:
        """
        Get detailed information about an output port.

        Args:
            bay: Output bay number

        Returns:
            PortDetails object with detailed port information
        """
        data = await self._request(f"/Port/Details/Output/{bay}")
        return PortDetails.from_dict(data)

    async def set_port(self, input_bay: int, output_bay: int) -> SetPortResponse:
        """
        Route an input to an output.

        Args:
            input_bay: Input bay number to route from
            output_bay: Output bay number to route to

        Returns:
            SetPortResponse indicating success

        Example:
            # Route input 7 to output 5
            response = await client.set_port(7, 5)
        """
        data = await self._request(f"/Port/Set/{input_bay}/{output_bay}")
        result = SetPortResponse.from_dict(data)
        return result

    async def get_port_by_name(self, name: str) -> Optional[Port]:
        """
        Find a port by its name.

        Args:
            name: Port name to search for

        Returns:
            Port object if found, None otherwise
        """
        ports = await self.get_ports()
        for port in ports:
            if port.name.lower() == name.lower():
                return port
        return None

    async def route_by_name(self, input_name: str, output_name: str) -> SetPortResponse:
        """
        Route an input to an output using port names.

        Args:
            input_name: Name of the input port
            output_name: Name of the output port

        Returns:
            SetPortResponse indicating success

        Raises:
            ValueError: If input or output port not found
        """
        ports = await self.get_ports()

        input_port = None
        output_port = None

        for port in ports:
            if not input_port and port.mode == "Input" and port.name.lower() == input_name.lower():
                input_port = port
            elif not output_port and port.mode == "Output" and port.name.lower() == output_name.lower():
                output_port = port

            if input_port and output_port:
                break

        if input_port is None:
            raise ValueError(f"Input port '{input_name}' not found")
        if output_port is None:
            raise ValueError(f"Output port '{output_name}' not found")

        result = await self.set_port(input_port.bay, output_port.bay)
        return result