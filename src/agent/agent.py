from langchain.agents import create_agent
from langchain_aws import ChatBedrock
from .copd_classifier import get_prediction
from .data_retriever import query_database
from .context_retriever import retrieve_context


model = ChatBedrock(
    model = "anthropic.claude-3-sonnet-20240229-v1:0",
    max_tokens = 4000,
    temperature = 0.0,
)

tools = [get_prediction,retrieve_context]

system_prompt = """
    You are a medical assistant.
    Answer the user query, using the tools available to you if needed.
    Give short answers.
    """

agent = create_agent(
    model = model,
    tools = tools,
    system_prompt = system_prompt,
    debug=True
)