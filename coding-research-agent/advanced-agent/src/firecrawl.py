import os
from typing import Any
from firecrawl import FirecrawlApp, ScrapeOptions
from firecrawl import SearchResponse, ScrapeResponse
from dotenv import load_dotenv

load_dotenv()

class FireCrawlService:

    def __init__(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")

        if not api_key:
            raise ValueError("Missing FIRECRAWL_API_KEY")
        
        self.app = FirecrawlApp(api_key)

    # Searching Web (like Google search)
    def search_companies(self, query: str, num_results: int = 5) -> SearchResponse:
        try:
            result = self.app.search(
                query=f"{query} company pricing",
                limit=num_results,
                scrape_options=ScrapeOptions(
                    formats=["markdown"]
                )
            )

            return result
        except Exception as e:
            print(e)
            return SearchResponse(data=[])

    # Search within a Website (scape)
    def scrape_company_page(self, url: str) -> ScrapeResponse[Any]:
        try:
            result = self.app.scrape_url(
                url,
                formats=["markdown"]
            )

            return result
        except Exception as e:
            print(e)
            return ScrapeResponse(data=None)

    # Other functions could include:
    # - map
    # - crawl