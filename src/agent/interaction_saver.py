import boto3
import uuid
import time
import json
from decimal import Decimal
from .agent_config import TEXT_EMBEDDING_MODEL_ID, CACHE_TTL, MODEL_METADATA

dynamodb = boto3.resource("dynamodb")
interaction_cache = dynamodb.Table("medicalbot-cache")
bedrock = boto3.client("bedrock-runtime")


def save_interaction(query,results,context,task,query_id,features):
    """
    Save interaction to DynamoDB
    """
    embedding = embed_query(query)
    embedding = [Decimal(str(x)) for x in embedding]
    init_time = int(time.time())
    interaction_cache.put_item(
        Item={
            "query_id": query_id,
            "timestamp": init_time,
            "query_text": query,
            "embedding": embedding,
            "extracted_features": json.dumps(features),
            "results": json.dumps(results),
            "context": json.dumps(context),
            "feedback": "NA",
            "task_type": task,
            "model_metadata": json.dumps(MODEL_METADATA),
            "text_embedding_model_id": TEXT_EMBEDDING_MODEL_ID,
            "ttl": init_time + CACHE_TTL,
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