import base64
from dataclasses import dataclass
from typing import Optional, BinaryIO, Any

import requests


@dataclass
class SupportbotEliteQuery:
    message: str
    file: Optional[BinaryIO] = None  # e.g. an open file object
    session_id: Optional[str] = None


class SupportbotElite:
    def __init__(self, user_id: str, api_key: str) -> None:
        self.user_id = user_id
        self.api_key = api_key

    def query(self, params: SupportbotEliteQuery) -> Any:
        """
        Synchronous version of the TypeScript `query` method.
        Returns the `requests.Response` object.
        """
        # Prepare multipart form fields
        data = {"message": params.message}
        if params.session_id:
            data["session_id"] = params.session_id

        files = None
        if params.file is not None:
            # ('filename', fileobj) — you can customize the filename
            files = {
                "file": (
                    getattr(params.file, "name", "file"),
                    params.file,
                )
            }

        # Build Basic auth token: base64("userId:apiKey")
        token_bytes = f"{self.user_id}:{self.api_key}".encode("utf-8")
        auth_token = base64.b64encode(token_bytes).decode("ascii")

        headers = {
            "Authorization": f"Basic {auth_token}",
        }

        response = requests.post(
            "https://api.bizagenthub.ai/supportbot-elite",
            headers=headers,
            data=data,
            files=files,
        )
        return response