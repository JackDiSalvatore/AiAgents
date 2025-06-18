from dotenv import load_dotenv
from pprint import pprint
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_text_to_file_tool

load_dotenv()

# Prompt Template
class LlmResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

# LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
parser = PydanticOutputParser(pydantic_object=LlmResponse)

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research assistant that will help generate an in-depth multi-paragraph research paper.
            Use formal academic grammar and formatting.
            Answer the user query and use the necessary tools and save the summary to a file.
            Wrap the output in this format and provide no other text.\n{format_instructions}
            """
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}")
    ]
).partial(format_instructions=parser.get_format_instructions())

# Agent Tools
tools = [search_tool, wiki_tool, save_text_to_file_tool]

# Agent
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

query = input("What can I help you research? ")

try:
    raw_response = agent_executor.invoke({"query": query})
    output_text = raw_response.get("output")

    if output_text is not None:
        structured_response = parser.parse(output_text)
        print("Topic: ", structured_response.topic)
        print("Summary: ", structured_response.summary)
    else:
        print("No output received from agent executor.")
except Exception as e:
    print(e)
