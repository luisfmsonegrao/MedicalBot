from decimal import Decimal
from .agent_config import TEXT_EMBEDDING_MODEL_ID, CACHE_TTL,MODEL_METADATA, BEDROCK_MODEL_ARN
import time, json, boto3

bedrock = boto3.client("bedrock-runtime")

def build_metadata(
        session_id,
        query_id,
        task_status,
        lambda_version,
        query,
        answer,
        total_duration,
        error_name,
        error_description,
        agent_logs
        ):
    
    metrics = agent_logs.metrics
    logs = agent_logs.logs
    task_type = agent_logs.task_type
    timestamp = int(time.time())
    metadata = {}
    metadata['session_id'] = session_id
    metadata['query_id'] = query_id
    metadata['timestamp'] = timestamp
    metadata['total_duration'] = Decimal(str(total_duration))
    metadata['lambda_version'] = lambda_version
    metadata['query'] = query
    metadata['results'] = answer
    metadata['error_name'] = error_name
    metadata['error_description'] = error_description
    metadata['logs'] = json.dumps(logs)
    metadata['feedback'] = "NA"
    metadata['task_type'] = task_type
    metadata['task_status'] = task_status
    metadata['model_metadata'] = json.dumps(MODEL_METADATA)
    metadata['llm_model'] = BEDROCK_MODEL_ARN
    metadata['text_embedding_model_id'] = TEXT_EMBEDDING_MODEL_ID
    query_embedding = embed_query(query)
    metadata['embedding'] = [Decimal(str(x)) for x in query_embedding]
    metadata['ttl'] = timestamp + CACHE_TTL
    for (k,v) in metrics.items():
        metadata[k] = json.dumps(v)

    return metadata

def embed_query(query):
    """
    Compute query embedding
    """
    response = bedrock.invoke_model(
        modelId=TEXT_EMBEDDING_MODEL_ID, body=json.dumps({"inputText": query})
    )
    response = json.loads(response["body"].read())["embedding"]
    return response