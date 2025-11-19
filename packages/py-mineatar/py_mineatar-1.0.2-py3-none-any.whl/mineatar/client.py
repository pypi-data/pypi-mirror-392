import aiohttp
import requests
from .exceptions import InvalidUUIDError, APIError, RateLimitError


class MineatarClient:
    """Client for interacting with the Mineatar API."""

    BASE_URL = "https://api.mineatar.io"

    def __init__(self, session: requests.Session = None):
        self.session = session or requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _handle_response(self, response: requests.Response):
        if response.status_code == 429:
            raise RateLimitError("API rate limit exceeded.")
        elif response.status_code == 400:
            raise InvalidUUIDError("Invalid UUID provided.")
        elif not response.ok:
            raise APIError(f"API error: {response.status_code} - {response.text}")

        return response

    def get_skin(self, uuid: str) -> bytes:
        """
        Fetch the skin image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
        Returns:
            bytes: The skin image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        url = f"{self.BASE_URL}/skin/{uuid}"
        response = self.session.get(url)
        response = self._handle_response(response)
        return response.content

    def get_head(self, uuid: str, scale: int = 4, overlay: bool = True) -> bytes:
        """
        Fetch the head image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the head image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The head image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/head/{uuid}{query_params}"
        response = self.session.get(url)
        response = self._handle_response(response)
        return response.content

    def get_face(self, uuid: str, scale: int = 4, overlay: bool = True) -> bytes:
        """
        Fetch the face image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the face image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The face image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/face/{uuid}{query_params}"
        response = self.session.get(url)
        response = self._handle_response(response)
        return response.content

    def get_fullbody(self, uuid: str, scale: int = 4, overlay: bool = True) -> bytes:
        """
        Fetch the full body image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the full body image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The full body image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/body/full/{uuid}{query_params}"
        response = self.session.get(url)
        response = self._handle_response(response)
        return response.content

    def get_frontbody(self, uuid: str, scale: int = 4, overlay: bool = True) -> bytes:
        """
        Fetch the front body image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the front body image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The front body image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/body/front/{uuid}{query_params}"
        response = self.session.get(url)
        response = self._handle_response(response)
        return response.content

    def get_backbody(self, uuid: str, scale: int = 4, overlay: bool = True) -> bytes:
        """
        Fetch the back body image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the back body image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The back body image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/body/back/{uuid}{query_params}"
        response = self.session.get(url)
        response = self._handle_response(response)
        return response.content

    def get_leftbody(self, uuid: str, scale: int = 4, overlay: bool = True) -> bytes:
        """
        Fetch the left body image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the left body image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The left body image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/body/left/{uuid}{query_params}"
        response = self.session.get(url)
        response = self._handle_response(response)
        return response.content

    def get_rightbody(self, uuid: str, scale: int = 4, overlay: bool = True) -> bytes:
        """
        Fetch the right body image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the right body image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The right body image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/body/right/{uuid}{query_params}"
        response = self.session.get(url)
        response = self._handle_response(response)
        return response.content

    def close(self):
        """Close the requests session."""
        self.session.close()


class AsyncMineatarClient:
    """Asynchronous client for interacting with the Mineatar API."""

    BASE_URL = "https://api.mineatar.io"

    def __init__(self, session: aiohttp.ClientSession = None):
        self.session = session or aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def _handle_response(self, response: aiohttp.ClientResponse):
        if response.status == 429:
            raise RateLimitError("API rate limit exceeded.")
        elif response.status == 400:
            raise InvalidUUIDError("Invalid UUID provided.")
        elif response.status >= 400:
            text = await response.text()
            raise APIError(f"API error: {response.status} - {text}")

        return response

    async def get_skin(self, uuid: str) -> bytes:
        """
        Fetch the skin image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
        Returns:
            bytes: The skin image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        url = f"{self.BASE_URL}/skin/{uuid}"
        async with self.session.get(url) as response:
            response = await self._handle_response(response)
            return await response.read()

    async def get_head(self, uuid: str, scale: int = 4, overlay: bool = True) -> bytes:
        """
        Fetch the head image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the head image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The head image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/head/{uuid}{query_params}"
        async with self.session.get(url) as response:
            response = await self._handle_response(response)
            return await response.read()

    async def get_face(self, uuid: str, scale: int = 4, overlay: bool = True) -> bytes:
        """
        Fetch the face image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the face image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The face image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/face/{uuid}{query_params}"
        async with self.session.get(url) as response:
            response = await self._handle_response(response)
            return await response.read()

    async def get_fullbody(
        self, uuid: str, scale: int = 4, overlay: bool = True
    ) -> bytes:
        """
        Fetch the full body image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the full body image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The full body image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/body/full/{uuid}{query_params}"
        async with self.session.get(url) as response:
            response = await self._handle_response(response)
            return await response.read()

    async def get_frontbody(
        self, uuid: str, scale: int = 4, overlay: bool = True
    ) -> bytes:
        """
        Fetch the front body image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the front body image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The front body image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/body/front/{uuid}{query_params}"
        async with self.session.get(url) as response:
            response = await self._handle_response(response)
            return await response.read()

    async def get_backbody(
        self, uuid: str, scale: int = 4, overlay: bool = True
    ) -> bytes:
        """
        Fetch the back body image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the back body image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The back body image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/body/back/{uuid}{query_params}"
        async with self.session.get(url) as response:
            response = await self._handle_response(response)
            return await response.read()

    async def get_leftbody(
        self, uuid: str, scale: int = 4, overlay: bool = True
    ) -> bytes:
        """
        Fetch the left body image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the left body image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The left body image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/body/left/{uuid}{query_params}"
        async with self.session.get(url) as response:
            response = await self._handle_response(response)
            return await response.read()

    async def get_rightbody(
        self, uuid: str, scale: int = 4, overlay: bool = True
    ) -> bytes:
        """
        Fetch the right body image for a given Minecraft UUID.

        Args:
            uuid (str): The Minecraft UUID.
            scale (int): The scale of the right body image.
            overlay (bool): Whether to include the overlay layer.
        Returns:
            bytes: The right body image data.
        Raises:
            InvalidUUIDError: If the provided UUID is invalid.
            APIError: If there is an error with the Mineatar API.
            RateLimitError: If the API rate limit is exceeded.
        """
        overlay_str = "true" if overlay else "false"
        query_params = f"?scale={scale}&overlay={overlay_str}"
        url = f"{self.BASE_URL}/body/right/{uuid}{query_params}"
        async with self.session.get(url) as response:
            response = await self._handle_response(response)
            return await response.read()

    async def close(self):
        """Close the aiohttp session."""
        await self.session.close()
