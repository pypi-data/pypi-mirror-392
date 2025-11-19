"""Utility for retrieving system variables used by the MCP server."""

from __future__ import annotations

from typing import Any

import httpx
import structlog

DEFAULT_SYSTEM_VARIABLES_API_URL = "http://localhost:3001/api/system/prompt-variables"

logger = structlog.get_logger(__name__)


async def fetch_system_variables(
    api_url: str,
    auth_token: str,
    *,
    timeout_seconds: float = 5.0,
) -> dict[str, Any]:
    """Fetch system prompt variables from the local API.

    Args:
        api_url: Fully qualified URL to the system variables endpoint.
        auth_token: API key used for the Authorization header.
        timeout_seconds: Request timeout in seconds. Defaults to 5 seconds.

    Returns:
        A dictionary mapping variable keys to their values. Returns an empty
        dictionary if the API call fails for any reason or returns an unexpected
        payload.
    """

    if not auth_token:
        logger.warning(
            "System variables request skipped due to missing auth token",
            api_url=api_url,
        )
        return {}

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "X-App-Offline": "true",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.get(api_url, headers=headers)

        if response.status_code != httpx.codes.OK:
            logger.warning(
                "System variables request failed",
                status_code=response.status_code,
                api_url=api_url,
            )
            return {}

        try:
            payload = response.json()
        except ValueError as exc:
            logger.warning(
                "System variables response could not be parsed as JSON",
                api_url=api_url,
                error=str(exc),
            )
            return {}

        variables_payload = (
            payload.get("variables") if isinstance(payload, dict) else None
        )
        if not isinstance(variables_payload, list):
            logger.warning(
                "System variables response missing 'variables' list",
                api_url=api_url,
            )
            return {}

        variables: dict[str, Any] = {}
        for item in variables_payload:
            if not isinstance(item, dict):
                continue

            key = item.get("key")
            if not isinstance(key, str) or not key:
                continue

            variables[key] = item.get("value")

        logger.info(
            "System variables retrieved",
            variable_count=len(variables),
            api_url=api_url,
        )
        return variables

    except httpx.RequestError as exc:
        logger.warning(
            "System variables request encountered a network error",
            api_url=api_url,
            error=str(exc),
        )
        return {}
