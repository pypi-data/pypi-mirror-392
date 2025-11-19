from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

from webquest.base.base_scraper import BaseScraper

TRequest = TypeVar("TRequest", bound=BaseModel)
TRaw = TypeVar("TRaw")
TResponse = TypeVar("TResponse", bound=BaseModel)


class BaseRunner(ABC):
    """Abstract base class for runners that execute scrapers."""

    @abstractmethod
    async def run_multiple(
        self,
        scraper: BaseScraper[TRequest, TRaw, TResponse],
        requests: list[TRequest],
    ) -> list[TResponse]: ...

    async def run(
        self,
        scraper: BaseScraper[TRequest, TRaw, TResponse],
        request: TRequest,
    ) -> TResponse:
        responses = await self.run_multiple(scraper, [request])
        return responses[0]
