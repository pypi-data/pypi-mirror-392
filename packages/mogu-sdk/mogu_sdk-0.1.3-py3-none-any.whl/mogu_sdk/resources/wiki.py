"""Wiki client for Mogu SDK"""

from typing import List, Optional

from mogu_sdk.auth import BaseClient
from mogu_sdk.exceptions import NotFoundError
from mogu_sdk.models import (
    CreateWikiFileRequest,
    UpdateWikiFileRequest,
    WikiContent,
    WikiFile,
    WikiSearchMatch,
    WikiSearchResponse,
    WikiSearchResult,
    WikiUpdateResponse,
)


class WikiClient:
    """Client for wiki operations"""

    def __init__(self, client: BaseClient) -> None:
        """
        Initialize wiki client.

        Args:
            client: Base HTTP client for making requests
        """
        self._client = client

    async def list_files(
        self,
        workspace_id: str,
        folder_path: Optional[str] = None,
        recursive: bool = True,
    ) -> List[WikiFile]:
        """
        List markdown files in the workspace wiki.

        Args:
            workspace_id: Workspace identifier
            folder_path: Optional subfolder path within docs folder
            recursive: Whether to list files recursively

        Returns:
            List of wiki files and folders

        Raises:
            NotFoundError: If workspace not found
            PermissionDeniedError: If user lacks access
            MoguAPIError: On other API errors
        """
        params = {"recursive": str(recursive).lower()}
        if folder_path:
            params["folder_path"] = folder_path

        response = await self._client.get(
            f"/api/v1/wiki/workspaces/{workspace_id}/files",
            params=params,
        )

        data = response.json()
        return [WikiFile(**file_data) for file_data in data["files"]]

    async def get_content(
        self,
        workspace_id: str,
        path: str,
    ) -> WikiContent:
        """
        Get the content of a markdown file from the wiki.

        Args:
            workspace_id: Workspace identifier
            path: Path to the markdown file within the repository

        Returns:
            Wiki file content

        Raises:
            NotFoundError: If workspace or file not found
            PermissionDeniedError: If user lacks access
            MoguAPIError: On other API errors
        """
        response = await self._client.get(
            f"/api/v1/wiki/workspaces/{workspace_id}/content",
            params={"path": path},
        )

        data = response.json()
        return WikiContent(**data)

    async def create_file(
        self,
        workspace_id: str,
        path: str,
        content: str = "",
        commit_message: str = "Create new wiki file",
    ) -> WikiUpdateResponse:
        """
        Create a new wiki file.

        Args:
            workspace_id: Workspace identifier
            path: File path relative to repository root
            content: Initial file content
            commit_message: Commit message for the Git commit

        Returns:
            Update response with commit ID

        Raises:
            PermissionDeniedError: If user lacks edit permission
            ValidationError: If input validation fails
            MoguAPIError: On other API errors
        """
        request_data = CreateWikiFileRequest(
            path=path,
            content=content,
            commit_message=commit_message,
        )

        response = await self._client.post(
            f"/api/v1/wiki/workspaces/{workspace_id}/content",
            json=request_data.model_dump(),
        )

        data = response.json()
        return WikiUpdateResponse(**data)

    async def update_file(
        self,
        workspace_id: str,
        path: str,
        content: str,
        commit_message: str = "Update wiki file",
    ) -> WikiUpdateResponse:
        """
        Update an existing wiki file.

        Args:
            workspace_id: Workspace identifier
            path: File path relative to repository root
            content: Updated file content
            commit_message: Commit message for the Git commit

        Returns:
            Update response with commit ID

        Raises:
            NotFoundError: If file not found
            PermissionDeniedError: If user lacks edit permission
            ValidationError: If input validation fails
            MoguAPIError: On other API errors
        """
        request_data = UpdateWikiFileRequest(
            path=path,
            content=content,
            commit_message=commit_message,
        )

        response = await self._client.put(
            f"/api/v1/wiki/workspaces/{workspace_id}/content",
            json=request_data.model_dump(),
        )

        data = response.json()
        return WikiUpdateResponse(**data)

    async def create_or_update_page(
        self,
        workspace_id: str,
        path: str,
        content: str,
        commit_message: Optional[str] = None,
    ) -> WikiUpdateResponse:
        """
        Create or update a wiki page intelligently.

        This method automatically detects if the file exists and either creates
        or updates it accordingly. This is the recommended method for page management.

        Args:
            workspace_id: Workspace identifier
            path: File path relative to repository root
            content: Page content
            commit_message: Optional commit message (auto-generated if not provided)

        Returns:
            Update response with commit ID and operation message

        Raises:
            PermissionDeniedError: If user lacks edit permission
            ValidationError: If input validation fails
            MoguAPIError: On other API errors
        """
        # Try to get existing content to determine if file exists
        file_exists = False
        try:
            await self.get_content(workspace_id=workspace_id, path=path)
            file_exists = True
        except NotFoundError:
            file_exists = False

        # Generate default commit message if not provided
        if not commit_message:
            action = "Update" if file_exists else "Create"
            commit_message = f"{action} {path}"

        # Create or update based on existence
        if file_exists:
            return await self.update_file(
                workspace_id=workspace_id,
                path=path,
                content=content,
                commit_message=commit_message,
            )
        else:
            return await self.create_file(
                workspace_id=workspace_id,
                path=path,
                content=content,
                commit_message=commit_message,
            )

    async def delete_file(
        self,
        workspace_id: str,
        path: str,
        commit_message: str = "Delete wiki file",
    ) -> WikiUpdateResponse:
        """
        Delete a wiki file.

        Args:
            workspace_id: Workspace identifier
            path: Path to the file to delete
            commit_message: Commit message for the Git commit

        Returns:
            Update response with commit ID

        Raises:
            NotFoundError: If file not found
            PermissionDeniedError: If user lacks delete permission
            MoguAPIError: On other API errors
        """
        response = await self._client.delete(
            f"/api/v1/wiki/workspaces/{workspace_id}/content",
            params={"path": path, "commit_message": commit_message},
        )

        data = response.json()
        return WikiUpdateResponse(**data)

    def _extract_snippet(
        self,
        full_content: str,
        match_line_number: int,
        char_offset: int,
        match_length: int,
        snippet_chars: int,
    ) -> tuple[str, int, int]:
        """
        Extract character-based snippet around a match.

        Args:
            full_content: Full content of the file
            match_line_number: Line number of the match (1-indexed)
            char_offset: Character offset within the line
            match_length: Length of the match
            snippet_chars: Total characters to extract around match

        Returns:
            Tuple of (snippet_text, match_start_in_snippet, match_end_in_snippet)
        """
        # Convert line-based position to absolute character position
        lines = full_content.splitlines(keepends=True)
        
        # Calculate absolute character position of the match
        char_position = sum(len(line) for line in lines[: match_line_number - 1])
        char_position += char_offset

        # Calculate snippet boundaries (centered on match)
        half_snippet = snippet_chars // 2
        start_pos = max(0, char_position - half_snippet)
        end_pos = min(
            len(full_content), char_position + match_length + half_snippet
        )

        # Extract raw snippet
        snippet = full_content[start_pos:end_pos]

        # Smart boundary adjustment - don't cut words awkwardly
        # Adjust start boundary
        if start_pos > 0 and snippet:
            # Find first whitespace or newline to start from
            whitespace_chars = {' ', chr(10), chr(9)}  # space, newline, tab
            for i, char in enumerate(snippet[:50]):  # Look within first 50 chars
                if char in whitespace_chars:
                    snippet = snippet[i + 1 :]
                    start_pos += i + 1
                    break

        # Adjust end boundary
        if end_pos < len(full_content) and snippet:
            # Find last whitespace or newline to end at
            whitespace_chars = {' ', chr(10), chr(9)}  # space, newline, tab
            for i in range(len(snippet) - 1, max(0, len(snippet) - 50), -1):
                if snippet[i] in whitespace_chars:
                    snippet = snippet[: i + 1]
                    break

        # Add ellipsis indicators
        leading_ellipsis = ""
        trailing_ellipsis = ""
        
        if start_pos > 0:
            leading_ellipsis = "..."
            snippet = leading_ellipsis + snippet
        
        if end_pos < len(full_content):
            trailing_ellipsis = "..."
            snippet = snippet + trailing_ellipsis

        # Calculate match position within the snippet
        match_start_in_snippet = char_position - start_pos + len(leading_ellipsis)
        match_end_in_snippet = match_start_in_snippet + match_length

        return snippet, match_start_in_snippet, match_end_in_snippet

    async def search(
        self,
        workspace_id: str,
        query: str,
        max_results: int = 50,
        context_lines: int = 3,
        snippet_chars: int = 0,
    ) -> WikiSearchResponse:
        """
        Search wiki content with context extraction.

        Performs full-text search across all markdown files in the wiki.
        Returns matched files with highlighted snippets and configurable context.

        Args:
            workspace_id: Workspace identifier
            query: Search query string
            max_results: Maximum number of results to return (1-100)
            context_lines: Number of lines to fetch before/after each match (0-10)
            snippet_chars: Number of characters to extract around match (0-5000, 0=disabled)
            snippet_chars: Number of characters to extract around match (0-5000, 0=disabled)

        Returns:
            Search response with results and context

        Raises:
            NotFoundError: If workspace not found
            PermissionDeniedError: If user lacks access
            ValidationError: If query is invalid
            MoguAPIError: On other API errors
        """
        # Validate parameters
        if max_results < 1 or max_results > 100:
            raise ValueError("max_results must be between 1 and 100")
        if context_lines < 0 or context_lines > 10:
            raise ValueError("context_lines must be between 0 and 10")
        if snippet_chars < 0 or snippet_chars > 5000:
            raise ValueError("snippet_chars must be between 0 and 5000")
        if snippet_chars < 0 or snippet_chars > 5000:
            raise ValueError("snippet_chars must be between 0 and 5000")

        response = await self._client.get(
            f"/api/v1/wiki/workspaces/{workspace_id}/search",
            params={"query": query, "max_results": max_results},
        )

        data = response.json()

        # Process results and add context extraction
        results = []
        for result_data in data["results"]:
            # Fetch full file content to extract context
            try:
                file_content = await self.get_content(
                    workspace_id=workspace_id,
                    path=result_data["path"],
                )
                content_lines = file_content.content.splitlines()

                # If backend didn't provide matches, search for them in content
                backend_matches = result_data["matches"]
                if not backend_matches:
                    # Search for query in content and create matches
                    query_lower = query.lower()
                    for line_idx, line in enumerate(content_lines):
                        line_lower = line.lower()
                        offset = 0
                        while True:
                            pos = line_lower.find(query_lower, offset)
                            if pos == -1:
                                break
                            
                            # Create a match entry
                            backend_matches.append({
                                "line_number": line_idx + 1,
                                "line_content": line,
                                "char_offset": pos,
                                "length": len(query),
                            })
                            offset = pos + 1

                # Enhance matches with context
                matches = []
                for match_data in backend_matches:
                    line_number = match_data["line_number"]

                    # Extract context lines
                    context_before = []
                    context_after = []

                    if context_lines > 0:
                        # Lines before (line_number is 1-indexed)
                        start_idx = max(0, line_number - 1 - context_lines)
                        context_before = content_lines[start_idx : line_number - 1]

                        # Lines after
                        end_idx = min(len(content_lines), line_number + context_lines)
                        context_after = content_lines[line_number:end_idx]

                    # Extract text snippet if requested
                    text_snippet = None
                    snippet_match_start = None
                    snippet_match_end = None

                    if snippet_chars > 0:
                        text_snippet, snippet_match_start, snippet_match_end = (
                            self._extract_snippet(
                                full_content=file_content.content,
                                match_line_number=match_data["line_number"],
                                char_offset=match_data["char_offset"],
                                match_length=match_data["length"],
                                snippet_chars=snippet_chars,
                            )
                        )

                    match = WikiSearchMatch(
                        line_number=match_data["line_number"],
                        line_content=match_data["line_content"],
                        char_offset=match_data["char_offset"],
                        length=match_data["length"],
                        context_before=context_before if context_before else None,
                        context_after=context_after if context_after else None,
                        text_snippet=text_snippet,
                        snippet_match_start=snippet_match_start,
                        snippet_match_end=snippet_match_end,
                    )
                    matches.append(match)

                result = WikiSearchResult(
                    path=result_data["path"],
                    name=result_data["name"],
                    matches=matches,
                    score=result_data["score"],
                )
                results.append(result)

            except Exception:
                # If context extraction fails, return match without context
                matches = [WikiSearchMatch(**m) for m in result_data["matches"]]
                result = WikiSearchResult(
                    path=result_data["path"],
                    name=result_data["name"],
                    matches=matches,
                    score=result_data["score"],
                )
                results.append(result)

        return WikiSearchResponse(
            results=results,
            total_count=len(results),
            query=query,
        )
