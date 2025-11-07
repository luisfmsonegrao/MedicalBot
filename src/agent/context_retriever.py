import boto3
from .agent_config import AWS_REGION, KNOWLEDGE_BASE_ID, CONTEXT_WINDOW, SOURCE_URI_STRING


bedrock_agent = boto3.client('bedrock-agent-runtime',region_name=AWS_REGION)

def contextualize_query(query,context):
    """Adapt user query for question answering with RAG from foundation model"""

    system_query = (
        f"""You are an assistant. 
        Use information in the context to answer the question.
        If you use information from a document, include its document number and its s3 uri in your answer.
        If unsure, say you don't know."""
    )
    
    llm_query = system_query + "\nContext:\n"
    for i,c in enumerate(context,start=1):
        text = c['text']
        uri = c['metadata'][SOURCE_URI_STRING]
        llm_query += "[{}]: {} (source: {})\n".format(i,text,uri)

    llm_query += f"Question: {query}" + "\nAnswer:"
    return llm_query

def retrieve_context(query,top_k=5):
    """Retrieve relevant context from Amazon Bedrock Knowledge database"""
    response = bedrock_agent.retrieve(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
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




