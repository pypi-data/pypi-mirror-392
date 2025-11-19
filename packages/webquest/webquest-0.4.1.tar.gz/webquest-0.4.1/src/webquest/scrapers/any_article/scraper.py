from typing import override

from openai import AsyncOpenAI
from playwright.async_api import BrowserContext

from webquest.base.openai_parser import OpenAIParser
from webquest.scrapers.any_article.schemas import AnyArticleRequest, AnyArticleResponse


class AnyArticle(OpenAIParser[AnyArticleRequest, AnyArticleResponse]):
    """Scraper to extract the main article from any web page using OpenAI."""

    Request = AnyArticleRequest
    Response = AnyArticleResponse

    def __init__(
        self,
        openai_api_key: str | None = None,
        openai: AsyncOpenAI | None = None,
        model: str = "gpt-5-mini",
    ) -> None:
        super().__init__(
            response_type=AnyArticleResponse,
            openai_api_key=openai_api_key,
            openai=openai,
            model=model,
            input="Parse the following web page and extract the main article:\n\n",
        )

    @override
    async def fetch(
        self,
        context: BrowserContext,
        request: AnyArticleRequest,
    ) -> str:
        page = await context.new_page()
        await page.goto(request.url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        html = await page.content()
        return html
