"""Main Mogu SDK client"""

from typing import Any, Dict, Optional

from mogu_sdk.auth import BaseClient
from mogu_sdk.resources.wiki import WikiClient


class MoguClient:
    """
    Main client for Mogu Workflow Management Platform.

    This client provides access to all Mogu API resources through
    resource-specific clients.

    Example:
        >>> import asyncio
        >>> from mogu_sdk import MoguClient
        >>>
        >>> async def main():
        >>>     client = MoguClient(
        >>>         base_url="https://api.mogu.example.com",
        >>>         token="your-oauth-token"
        >>>     )
        >>>
        >>>     # Access wiki client
        >>>     result = await client.wiki.create_or_update_page(
        >>>         workspace_id="ws-123",
        >>>         path="docs/guide.md",
        >>>         content="# Guide",
        >>>         commit_message="Update guide"
        >>>     )
        >>>     print(f"Committed: {result.commit_id}")
        >>>
        >>>     await client.close()
        >>>
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        verify_ssl: bool = True,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize Mogu client.

        Args:
            base_url: Base URL of the Mogu API (default: from MOGU_BASE_URL env var)
            token: OAuth bearer token (default: from MOGU_TOKEN env var)
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts for failed requests
            verify_ssl: Whether to verify SSL certificates
            headers: Additional headers to include in all requests

        Raises:
            ValueError: If token is not provided and MOGU_TOKEN env var is not set
        """
        self._http_client = BaseClient(
            base_url=base_url,
            token=token,
            timeout=timeout,
            max_retries=max_retries,
            verify_ssl=verify_ssl,
            headers=headers,
        )

        # Initialize resource clients
        self._wiki = WikiClient(self._http_client)

    @property
    def wiki(self) -> WikiClient:
        """
        Access wiki operations.

        Returns:
            WikiClient instance for wiki operations
        """
        return self._wiki

    async def __aenter__(self) -> "MoguClient":
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit"""
        await self.close()

    async def close(self) -> None:
        """
        Close the HTTP client and clean up resources.

        This should be called when you're done using the client,
        or use the client as an async context manager.
        """
        await self._http_client.close()
