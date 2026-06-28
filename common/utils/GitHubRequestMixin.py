import time
from random import uniform
from typing import Any

import requests

from common.config import Config


class GitHubRequestMixin:
    API = "https://api.github.com"

    HEADERS = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {Config.GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    REQUEST_TIMEOUT = 30
    SLEEP_BASE = 1.2
    SLEEP_JITTER = (1.2, 2.8)

    @classmethod
    def sleep(cls) -> None:
        time.sleep(cls.SLEEP_BASE + uniform(*cls.SLEEP_JITTER))

    @classmethod
    def request(
        cls,
        path_or_url: str,
        *,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        success_codes: tuple[int, ...] | None = None,
        fail_codes: tuple[int, ...] = (),
    ) -> requests.Response | None:
        url = cls._make_url(path_or_url)

        while True:
            response = requests.request(
                method=method,
                url=url,
                headers=cls.HEADERS,
                params=params,
                json=json,
                timeout=cls.REQUEST_TIMEOUT,
            )

            if cls._handle_rate_limit(response):
                continue

            if success_codes and response.status_code in success_codes:
                return response

            if response.status_code in fail_codes:
                return None

            response.raise_for_status()
            return response

    @classmethod
    def get_json(
        cls,
        path_or_url: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> tuple[Any, requests.structures.CaseInsensitiveDict[str]]:
        response = cls.request(path_or_url, params=params)

        if response is None:
            raise RuntimeError("GitHub request failed")

        return response.json(), response.headers

    @classmethod
    def _make_url(cls, path_or_url: str) -> str:
        if path_or_url.startswith("http"):
            return path_or_url

        return f"{cls.API}{path_or_url}"

    @classmethod
    def _handle_rate_limit(cls, response: requests.Response) -> bool:
        if response.status_code != 403:
            return False

        if "rate limit" not in response.text.lower():
            return False

        reset = int(response.headers.get("x-ratelimit-reset", "0") or 0)
        wait = max(0, reset - int(time.time())) + 2

        logger = getattr(cls, "logger", None)

        if logger:
            logger.warning(f"[rate-limit] sleep {wait}s")
        else:
            print(f"[rate-limit] sleep {wait}s")

        time.sleep(wait)
        return True

    @staticmethod
    def next_link(headers: requests.structures.CaseInsensitiveDict[str]) -> str | None:
        link = headers.get("Link", "")

        next_links = [
            part.split(";")[0].strip("<> ")
            for part in link.split(",")
            if 'rel="next"' in part
        ]

        return next_links[0] if next_links else None
