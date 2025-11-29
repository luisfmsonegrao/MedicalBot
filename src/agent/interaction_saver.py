import boto3
import json
from decimal import Decimal
from .agent_config import TEXT_EMBEDDING_MODEL_ID, CACHE_TTL

dynamodb = boto3.resource("dynamodb")
interaction_cache = dynamodb.Table("medicalbot-cache")
bedrock = boto3.client("bedrock-runtime")


def save_interaction(*,
        query,
        results,
        context,
        timestamp,
        task,
        query_id,
        session_id,
        features,
        task_status,
        durations_dict,
        error_name='',
        model_metadata,
        lambda_version
        ):
    """
    Save interaction to DynamoDB
    """
    embedding = embed_query(query)
    embedding = [Decimal(str(x)) for x in embedding]
    durations_dict = {k: Decimal(str(v)) for k,v in durations_dict.items()}
    interaction_cache.put_item(
        Item={
            "query_id": query_id,
            "session_id": session_id,
            "timestamp": timestamp,
            "query": query,
            "embedding": embedding,
            "features": json.dumps(features),
            "results": json.dumps(results),
            "context": json.dumps(context),
            "feedback": "NA",
            "task_type": task,
            "task_status": task_status,
            "error_name": error_name,
            "model_metadata": json.dumps(model_metadata),
            "text_embedding_model_id": TEXT_EMBEDDING_MODEL_ID,
            "ttl": timestamp + CACHE_TTL,
            "lambda_version": lambda_version,
            **durations_dict
        }
    )

def embed_query(query):
    """
    Compute query embedding
    """
    response = bedrock.invoke_model(
        modelId=TEXT_EMBEDDING_MODEL_ID, body=json.dumps({"inputText": query})
    )
    response = json.loads(response["body"].read())["embedding"]
    return response