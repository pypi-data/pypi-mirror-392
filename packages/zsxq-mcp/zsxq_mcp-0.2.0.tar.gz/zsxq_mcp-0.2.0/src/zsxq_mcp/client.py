"""ZSXQ API Client for interacting with Zhishixingqiu API"""

import httpx
from typing import Optional, Dict, Any
from pathlib import Path


class ZSXQClient:
    """Client for ZSXQ API operations"""

    BASE_URL = "https://api.zsxq.com"

    def __init__(self, cookie: str):
        """
        Initialize ZSXQ client

        Args:
            cookie: Authentication cookie from browser
        """
        self.cookie = cookie
        self.headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "X-Version": "2.84.0",
            "X-Request-Id": "uuid-" + str(__import__('uuid').uuid4()),
        }

    async def upload_image(self, image_path: str) -> Dict[str, Any]:
        """
        Upload an image to ZSXQ using the correct 3-step process

        Args:
            image_path: Path to the image file

        Returns:
            Dict containing image_id

        Raises:
            httpx.HTTPError: If upload fails
        """
        file_path = Path(image_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Get file size
        file_size = file_path.stat().st_size

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Get upload token from ZSXQ API
            token_response = await client.post(
                f"{self.BASE_URL}/v2/uploads",
                headers=self.headers,
                json={
                    "req_data": {
                        "type": "image",
                        "size": file_size,
                        "name": "",
                        "hash": ""
                    }
                }
            )
            token_response.raise_for_status()
            token_data = token_response.json()

            if not token_data.get("succeeded"):
                raise Exception(f"Failed to get upload token: {token_data}")

            upload_token = token_data["resp_data"]["upload_token"]

            # Step 2: Upload to Qiniu Cloud
            with open(file_path, "rb") as f:
                files = {
                    "file": (file_path.name, f, "image/jpeg")
                }
                data = {
                    "token": upload_token
                }

                # Upload to Qiniu (remove ZSXQ headers)
                qiniu_headers = {
                    "Accept": "application/json, text/plain, */*",
                    "Origin": "https://wx.zsxq.com",
                    "Referer": "https://wx.zsxq.com/",
                    "User-Agent": self.headers["User-Agent"],
                }

                upload_response = await client.post(
                    "https://upload-z1.qiniup.com/",
                    headers=qiniu_headers,
                    files=files,
                    data=data
                )
                upload_response.raise_for_status()
                upload_result = upload_response.json()

                if not upload_result.get("succeeded"):
                    raise Exception(f"Failed to upload to Qiniu: {upload_result}")

                # Step 3: Return image_id
                image_id = upload_result["resp_data"]["image_id"]

                return {
                    "image_id": image_id
                }

    async def publish_topic(
        self,
        group_id: str,
        content: str,
        image_ids: Optional[list[str]] = None,
        mentioned_user_ids: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """
        Publish a topic to ZSXQ group

        Args:
            group_id: Target group ID
            content: Text content to publish
            image_ids: Optional list of uploaded image IDs
            mentioned_user_ids: Optional list of user IDs to mention

        Returns:
            API response data

        Raises:
            httpx.HTTPError: If publish fails
        """
        req_data: Dict[str, Any] = {
            "req_data": {
                "type": "topic",
                "text": content,
                "image_ids": image_ids if image_ids else [],
                "file_ids": [],
                "mentioned_user_ids": mentioned_user_ids if mentioned_user_ids else []
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/v2/groups/{group_id}/topics",
                headers=self.headers,
                json=req_data,
            )
            response.raise_for_status()
            result = response.json()

            if not result.get("succeeded"):
                raise Exception(f"Failed to publish topic: {result}")

            return result["resp_data"]

    async def get_group_info(self, group_id: str) -> Dict[str, Any]:
        """
        Get group information

        Args:
            group_id: Group ID to query

        Returns:
            Group information

        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/v2/groups/{group_id}", headers=self.headers
            )
            response.raise_for_status()
            result = response.json()

            if not result.get("succeeded"):
                raise Exception(f"Failed to get group info: {result}")

            return result["resp_data"]["group"]

    async def schedule_topic(
        self,
        group_id: str,
        content: str,
        scheduled_time: str,
        image_ids: Optional[list[str]] = None,
        mentioned_user_ids: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """
        Schedule a topic to be published at a specific time

        Args:
            group_id: Target group ID
            content: Text content to publish
            scheduled_time: Scheduled time in ISO format with timezone (e.g., "2025-11-15T09:53:00.000+0800")
            image_ids: Optional list of uploaded image IDs
            mentioned_user_ids: Optional list of user IDs to mention

        Returns:
            API response data

        Raises:
            httpx.HTTPError: If scheduling fails
        """
        req_data: Dict[str, Any] = {
            "req_data": {
                "topic": {
                    "text": content,
                    "image_ids": image_ids if image_ids else [],
                    "file_ids": [],
                    "mentioned_user_ids": mentioned_user_ids if mentioned_user_ids else []
                },
                "scheduled_time": scheduled_time
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/v2/groups/{group_id}/scheduled_jobs",
                headers=self.headers,
                json=req_data,
            )
            response.raise_for_status()
            result = response.json()

            if not result.get("succeeded"):
                raise Exception(f"Failed to schedule topic: {result}")

            return result["resp_data"]

    async def get_scheduled_jobs(self, group_id: str) -> Dict[str, Any]:
        """
        Get list of scheduled jobs/topics for a group

        Args:
            group_id: Group ID to query

        Returns:
            API response data with scheduled jobs

        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/v2/groups/{group_id}/scheduled_jobs",
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()

            if not result.get("succeeded"):
                raise Exception(f"Failed to get scheduled jobs: {result}")

            return result["resp_data"]
