from abc import ABC
from typing import Generic, Type, TypeVar, override

from bs4 import BeautifulSoup
from openai import AsyncOpenAI
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from webquest.base.base_scraper import BaseScraper

TRequest = TypeVar("TRequest", bound=BaseModel)
TResponse = TypeVar("TResponse", bound=BaseModel)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
    openai_api_key: str | None = None


class OpenAIParser(
    Generic[TRequest, TResponse],
    BaseScraper[TRequest, str, TResponse],
    ABC,
):
    """Abstract base class for OpenAI-based parsers."""

    def __init__(
        self,
        response_type: Type[TResponse],
        openai_api_key: str | None = None,
        openai: AsyncOpenAI | None = None,
        model: str = "gpt-5-mini",
        input: str | None = None,
        character_limit: int = 20000,
    ) -> None:
        settings = Settings()
        if openai_api_key is None:
            openai_api_key = settings.openai_api_key
        self._response_type = response_type
        if openai is None:
            openai = AsyncOpenAI(api_key=openai_api_key)
        self._openai = openai
        self._model = model
        self._character_limit = character_limit
        self._input = input or ""

    @override
    async def parse(self, raw: str) -> TResponse:
        soup = BeautifulSoup(raw, "html.parser")
        text = soup.get_text(separator="\n", strip=True)

        if len(text) > self._character_limit:
            start = (len(text) - self._character_limit) // 2
            end = start + self._character_limit
            text = text[start:end]

        response = await self._openai.responses.parse(
            input=f"{self._input}{text}",
            text_format=self._response_type,
            model=self._model,
            reasoning={"effort": "minimal"},
        )
        if response.output_parsed is None:
            raise ValueError("Failed to parse the response into the desired format.")
        return response.output_parsed
