from pydantic import BaseModel


class GoogleNewsSearchRequest(BaseModel):
    query: str
    locale: str | None = None


class Article(BaseModel):
    site: str
    url: str
    title: str
    published_at: str


class GoogleNewsSearchResponse(BaseModel):
    articles: list[Article]
