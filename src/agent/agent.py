from langchain.agents import create_agent
from langchain_aws import ChatBedrock
from .copd_classifier import make_prediction
from .data_retriever import query_athena_database
from .context_retriever import get_context_information
from .agent_config import BEDROCK_MODEL_ID

#model_advanced = "anthropic.claude-3-5-sonnet-20240620-v1:0"

model = ChatBedrock(
    model = BEDROCK_MODEL_ID,
    max_tokens = 4000,
    temperature = 0.0,
)

tools = [make_prediction,query_athena_database,get_context_information]

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

