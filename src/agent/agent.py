from langchain.agents import create_agent
from langchain_aws import ChatBedrock
from .copd_classifier import make_prediction
from .data_retriever import get_tabular_data
from .context_retriever import get_context_information

model_base = "anthropic.claude-3-sonnet-20240229-v1:0"
model_advanced = "anthropic.claude-3-5-sonnet-20240620-v1:0"

model = ChatBedrock(
    model = model_base,
    max_tokens = 4000,
    temperature = 0.0,
)

tools = [make_prediction,get_tabular_data,get_context_information]

system_prompt = """
    You are a medical assistant.
    Answer the user query, using the tools available to you.
    Give short answers.
    """


agent = create_agent(
    model = model,
    tools = tools,
    system_prompt = system_prompt,
    debug=True
)

