import boto3
from .agent_config import AWS_REGION, KNOWLEDGE_BASE_ID, CONTEXT_WINDOW
from .tool_input_models import ContextInput

bedrock_agent = boto3.client('bedrock-agent-runtime',region_name=AWS_REGION)


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


