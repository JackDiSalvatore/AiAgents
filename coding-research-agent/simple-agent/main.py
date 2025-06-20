from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
import os
from pydantic import SecretStr

load_dotenv()

openai_api_key = SecretStr(os.getenv("OPENAI_API_KEY") or "")
firecrawl_api_key = SecretStr(os.getenv("FIRECRAWL_API_KEY") or "")

# LLM
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    api_key=openai_api_key
)

# MCP Server Connection
# This spawns a background process, I think
server_params = StdioServerParameters(
    command="npx",
    env={
        "FIRECRAWL_API_KEY": firecrawl_api_key.get_secret_value(),
    },
    args=["firecrawl-mcp"]
)

# Main
async def main():
    # Connect to MCP server
    async with stdio_client(server_params) as (read, write):

        # Create client session
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)

            # Message state
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can scrape websites, crawl pages, and extract data using the provided tools. Think step by step and use the appropriate tools to help the user."
                }
            ]

            print("Available tools - ", *[tool.name for tool in tools])
            print("-" * 60)

            # Loop chat with agent
            while True:
                user_input = input("\nYou: ")
                if user_input == "quit":
                    print("Goodbye")
                    break
                
                messages.append(
                    {
                        "role": "user",
                        "content": user_input,   # limit user character input
                    }
                )

                try:
                    # Async invoke
                    agent_response = await agent.ainvoke({"messages": messages})
                    agent_message = agent_response["messages"][-1].content

                    print("\nAgent: ", agent_message)

                except Exception as e:
                    print(e)

# Run
if __name__ == "__main__":
    asyncio.run(main())
