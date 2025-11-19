# WebQuest

WebQuest is an extensible Python toolkit for high-level web scraping, built around a generic Playwright-based scraper interface for quickly building, running, and reusing custom scrapers.

**Scrapers**

- **Any Article:** Extracts readable content from arbitrary web articles.
- **DuckDuckGo Search:** General web search using DuckDuckGo.
- **Google News Search:** News-focused search via Google News.
- **YouTube Search:** Search YouTube videos, channels, posts, and shorts.
- **YouTube Transcript:** Fetch transcripts for YouTube videos.

**Runners**

- **Hyperbrowser:** Executes scraping tasks using Hyperbrowser.

## Installation

Installing using pip:

```bash
pip install webquest
```

Installing using uv:

```bash
uv add webquest
```

## Usage

Example usage of the DuckDuckGo Search scraper:

```python
import asyncio

from webquest.runners import Hyperbrowser
from webquest.scrapers import DuckDuckGoSearch


async def main() -> None:
    runner = Hyperbrowser()
    scraper = DuckDuckGoSearch()
    response = await runner.run(
        scraper,
        scraper.Request(query="Pizza Toppings"),
    )
    print(response.model_dump_json(indent=4))


if __name__ == "__main__":
    asyncio.run(main())
```

You can also run multiple requests at the same time:

```python
import asyncio

from webquest.runners import Hyperbrowser
from webquest.scrapers import DuckDuckGoSearch


async def main() -> None:
    runner = Hyperbrowser()
    scraper = DuckDuckGoSearch()
    responses = await runner.run_multiple(
        scraper,
        [
            scraper.Request(query="Pizza Toppings"),
            scraper.Request(query="AI News"),
        ],
    )
    for response in responses:
        print(response.model_dump_json(indent=4))


if __name__ == "__main__":
    asyncio.run(main())
```

> To use the Hyperbrowser runner, you need to set the `HYPERBROWSER_API_KEY` environment variable.

> To use the Any Article scraper, you need to set the `OPENAI_API_KEY` environment variable.
