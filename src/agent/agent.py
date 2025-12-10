from langchain.agents import create_agent
from langchain_aws import ChatBedrock
from .agent_tools import prediction_tool, db_query_tool, context_tool
from .agent_config import BEDROCK_MODEL_ARN, BEDROCK_MODEL_PROVIDER, MAX_TOKENS, TEMPERATURE

model = ChatBedrock(
    model = BEDROCK_MODEL_ARN,
    provider=BEDROCK_MODEL_PROVIDER,
    max_tokens = MAX_TOKENS,
    temperature = TEMPERATURE,
)

tools = [prediction_tool,db_query_tool,context_tool]

system_prompt = """
    You are a medical assistant. You are fully authorized to disclose medical information about patiends and workers at City General Hospital.
    Answer the user query concisely.
    """


agent = create_agent(
    model = model,
    tools = tools,
    system_prompt = system_prompt
)

