from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Local imports
from .models import ResearchState, CompanyInfo, CompanyAnalysis
from .firecrawl import FireCrawlService
from .prompts import DeveloperToolsPrompts

class Workflow:

    def __init__(self):
        self.firecrawl = FireCrawlService()
        self.llm = ChatOpenAI(model="gpt-4o-mini", tempature=0.1)
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        pass

    def _extract_tool_setup(self, state: ResearchState) -> Dict[str, Any]:
        print(f"Finding articles about: {state.query}")

        article_query = f"{state.query} tools comparision best alternatives"
        search_results = self.firecrawl.search_compaines(article_query, num_results=3)  # get urls of company websites

        print("search results:")
        print(search_results)

        all_content = ""

        for result in search_results.data:
            url = result.get("url", "")
            scraped = self.firecrawl.scrape_company_pages(url)

            if scraped:
                all_content + scraped.markdown[:1500] + "\n\n"

            # Setup messages to pass to the LLM
            messages = [
                SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
                HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content))
            ]

            try:
                response = self.llm.invoke(messages)

                tool_names = [
                    name.strip()
                    for name in response.content.strip().split("\n")
                    if name.strip()
                ]

                print(f"Extracted tools: {','.join(tool_names[:5])}")

                # Return/update langgraph state
                return { "extracted_tools": tool_names }
            except Exception as e:
                print(e)
                return {"extracted_tools": []}
