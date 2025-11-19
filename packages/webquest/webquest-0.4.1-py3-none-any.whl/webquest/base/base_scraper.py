from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from playwright.async_api import BrowserContext
from pydantic import BaseModel

TRequest = TypeVar("TRequest", bound=BaseModel)
TRaw = TypeVar("TRaw")
TResponse = TypeVar("TResponse", bound=BaseModel)


class BaseScraper(ABC, Generic[TRequest, TRaw, TResponse]):
    """Abstract base class for web scrapers."""

    Request: Type[TRequest]
    Response: Type[TResponse]

    @abstractmethod
    async def fetch(self, context: BrowserContext, request: TRequest) -> TRaw: ...

    @abstractmethod
    async def parse(self, raw: TRaw) -> TResponse: ...

    async def scrape(self, context: BrowserContext, request: TRequest) -> TResponse:
        raw = await self.fetch(context, request)
        response = await self.parse(raw)
        return response
