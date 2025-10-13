import boto3
import json

REGION = "us-east-1"
KNOWLEDGE_BASE_ID = "A3XBZT3D8Y"

bedrock_agent = boto3.client('bedrock-agent-runtime',region_name=REGION)

def retrieve_context(query,kb_id,top_k=5):
    response = bedrock_agent.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": top_k
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




