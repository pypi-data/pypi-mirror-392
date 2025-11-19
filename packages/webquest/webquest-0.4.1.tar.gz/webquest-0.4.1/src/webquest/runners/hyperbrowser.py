import asyncio
from typing import TypeVar, override

from hyperbrowser import AsyncHyperbrowser
from playwright.async_api import async_playwright
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from webquest.base.base_runner import BaseRunner
from webquest.base.base_scraper import BaseScraper

TRequest = TypeVar("TRequest", bound=BaseModel)
TRaw = TypeVar("TRaw")
TResponse = TypeVar("TResponse", bound=BaseModel)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
    hyperbrowser_api_key: str | None = None


class Hyperbrowser(BaseRunner):
    """Runner that uses Hyperbrowser to execute scrapers."""

    def __init__(
        self,
        hyperbrowser_api_key: str | None = None,
        hyperbrowser_client: AsyncHyperbrowser | None = None,
    ):
        settings = Settings()
        if hyperbrowser_api_key is None:
            hyperbrowser_api_key = settings.hyperbrowser_api_key
        if hyperbrowser_client is None:
            hyperbrowser_client = AsyncHyperbrowser(api_key=hyperbrowser_api_key)
        self._hyperbrowser_client = hyperbrowser_client

    @override
    async def run_multiple(
        self,
        scraper: BaseScraper[TRequest, TRaw, TResponse],
        requests: list[TRequest],
    ) -> list[TResponse]:
        session = await self._hyperbrowser_client.sessions.create()
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(session.ws_endpoint)
            context = browser.contexts[0]
            raw_items = await asyncio.gather(
                *[scraper.fetch(context, request) for request in requests]
            )
        await self._hyperbrowser_client.sessions.stop(session.id)

        responses = await asyncio.gather(
            *[scraper.parse(raw_item) for raw_item in raw_items]
        )
        return responses
