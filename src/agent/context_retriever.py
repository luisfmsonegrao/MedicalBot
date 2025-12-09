import boto3
from .agent_config import AWS_REGION, KNOWLEDGE_BASE_ID, CONTEXT_WINDOW
from langchain_core.tools.structured import StructuredTool
from pydantic import BaseModel, StrictStr

bedrock_agent = boto3.client('bedrock-agent-runtime',region_name=AWS_REGION)

class ContextInput(BaseModel):
    query: StrictStr

tool_name = "get_context_information"
def get_context_information(query: ContextInput):
    """
    Retrieve relevant context from Amazon Bedrock Knowledge database
    """
    user_query = query.query
    response = bedrock_agent.retrieve(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        retrievalQuery={"text": user_query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": CONTEXT_WINDOW
            }
        }
    )
    contexts = []
    for r in response.get("retrievalResults",[]):
        contexts.append({
            "text": r.get("content", {}).get("text", ""),
            "score": r.get("score"),
            "metadata": r.get("metadata")
        })
    return contexts

context_tool = StructuredTool.from_function(
    func=get_context_information,
    name=tool_name,
    description = f"""Use {tool_name} when the user asks questions about patients or staff at City General Hospital.
                      The tool gives you relevant context from patients' medical records."""
)



