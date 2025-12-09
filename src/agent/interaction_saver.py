import boto3

dynamodb = boto3.resource("dynamodb")
interaction_cache = dynamodb.Table("medicalbot-cache")

def save_interaction(*,
        session_id,
        query_id,
        timestamp,
        total_duration,
        lambda_version,
        query,
        results,
        error_name,
        error_description,
        logs,
        feedback,
        task_type,
        task_status,
        model_metadata,
        llm_model,
        text_embedding_model_id,
        embedding,
        ttl,
        **kwargs
        ):
    """
    Save interaction to DynamoDB
    """

    interaction_cache.put_item(
        Item={
            "query_id": query_id,
            "session_id": session_id,
            "timestamp": timestamp,
            "query": query,
            "embedding": embedding,
            "results": results,
            "logs":logs,
            "total_duration":total_duration,
            "feedback": feedback,
            "task_type": task_type,
            "task_status": task_status,
            "error_name": error_name,
            "error_description": error_description,
            "model_metadata": model_metadata,
            "text_embedding_model_id": text_embedding_model_id,
            "llm_model":llm_model,
            "ttl": ttl,
            "lambda_version": lambda_version,
            **kwargs
        }
    )
