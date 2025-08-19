#!/usr/bin/env python3
"""
Legend SDLC Client

Client for interacting with the Legend SDLC service.
"""

import logging
import aiohttp
from typing import Dict, Any

logger = logging.getLogger(__name__)


class LegendSDLCClient:
    """Client for interacting with the Legend SDLC service"""

    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = aiohttp.ClientSession()

    async def get_project_info(self, project_id: str) -> Dict[str, Any]:
        """Get information about a specific project"""
        url = f"{self.base_url}/api/projects/{project_id}/workspaces"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get project info: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error getting project info: {str(e)}")
            return {}

    async def close(self):
        """Close the client session"""
        await self.session.close()
