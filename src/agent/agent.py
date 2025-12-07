from langchain.agents import create_agent
from langchain_aws import ChatBedrock
from .copd_classifier import get_prediction
from .data_retriever import get_data

model = ChatBedrock(
    model = "anthropic.claude-3-sonnet-20240229-v1:0",
    max_tokens = 4000,
    temperature = 0.0,
    top_p = 0.9
)

tools = [get_prediction,get_data]

agent = create_agent(
    model = model,
    tools = tools,
    system_prompt = """
    You are a medical assistant.
    Answer the user query, using the tools available to you if needed.
    """
)