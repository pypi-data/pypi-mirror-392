"""Base HTTP client for Zaban API."""

from typing import Any, Dict, Optional, cast

import httpx

from ._exceptions import (
    APIError,
    AuthenticationError,
    ConnectionError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)


class BaseClient:
    """Base HTTP client for making requests to Zaban API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        """Initialize the base client.

        Args:
            api_key: Zaban API key (starts with 'sk-')
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Create httpx client
        self._client = httpx.Client(
            timeout=timeout,
            headers=self._get_headers(),
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for requests."""
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API.

        Args:
            response: HTTP response

        Raises:
            AuthenticationError: For 401 status codes
            RateLimitError: For 429 status codes
            ValidationError: For 400 status codes
            APIError: For other error status codes
        """
        status_code = response.status_code

        try:
            error_data = response.json()
            message = error_data.get("detail", str(error_data))
        except Exception:
            message = response.text or f"HTTP {status_code} error"

        if status_code == 401:
            raise AuthenticationError(message, status_code=status_code, response=response)
        elif status_code == 429:
            raise RateLimitError(message, status_code=status_code, response=response)
        elif status_code == 400:
            raise ValidationError(message, status_code=status_code, response=response)
        else:
            raise APIError(message, status_code=status_code, response=response)

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            json: JSON body for the request
            files: Files for multipart upload
            params: Query parameters

        Returns:
            Response data as dictionary

        Raises:
            Various exceptions based on response status
        """
        url = f"{self.base_url}/{path.lstrip('/')}"

        try:
            # For file uploads, don't set Content-Type (httpx will set it)
            headers = None
            if files:
                headers = {"X-API-Key": self.api_key}

            response = self._client.request(
                method=method,
                url=url,
                json=json,
                files=files,
                params=params,
                headers=headers,
            )

            # Check for errors
            if response.status_code >= 400:
                self._handle_error_response(response)

            # Return JSON response
            return cast(Dict[str, Any], response.json())

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out after {self.timeout}s") from e
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to {self.base_url}") from e
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error occurred: {str(e)}") from e

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class AsyncBaseClient:
    """Async HTTP client for making requests to Zaban API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        """Initialize the async base client.

        Args:
            api_key: Zaban API key (starts with 'sk-')
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Create async httpx client
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers=self._get_headers(),
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for requests."""
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API.

        Args:
            response: HTTP response

        Raises:
            AuthenticationError: For 401 status codes
            RateLimitError: For 429 status codes
            ValidationError: For 400 status codes
            APIError: For other error status codes
        """
        status_code = response.status_code

        try:
            error_data = response.json()
            message = error_data.get("detail", str(error_data))
        except Exception:
            message = response.text or f"HTTP {status_code} error"

        if status_code == 401:
            raise AuthenticationError(message, status_code=status_code, response=response)
        elif status_code == 429:
            raise RateLimitError(message, status_code=status_code, response=response)
        elif status_code == 400:
            raise ValidationError(message, status_code=status_code, response=response)
        else:
            raise APIError(message, status_code=status_code, response=response)

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an async request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            json: JSON body for the request
            files: Files for multipart upload
            params: Query parameters

        Returns:
            Response data as dictionary

        Raises:
            Various exceptions based on response status
        """
        url = f"{self.base_url}/{path.lstrip('/')}"

        try:
            # For file uploads, don't set Content-Type (httpx will set it)
            headers = None
            if files:
                headers = {"X-API-Key": self.api_key}

            response = await self._client.request(
                method=method,
                url=url,
                json=json,
                files=files,
                params=params,
                headers=headers,
            )

            # Check for errors
            if response.status_code >= 400:
                self._handle_error_response(response)

            # Return JSON response
            return cast(Dict[str, Any], response.json())

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out after {self.timeout}s") from e
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to {self.base_url}") from e
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error occurred: {str(e)}") from e

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
