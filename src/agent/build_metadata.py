from .interaction_saver import embed_query
from decimal import Decimal
from .agent_config import TEXT_EMBEDDING_MODEL_ID, CACHE_TTL,MODEL_METADATA, BEDROCK_MODEL_ID
import time


def build_metadata(
        session_id,
        query_id,
        lambda_version,
        query,
        answer,
        total_duration,
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
    metadata['total_duration'] = total_duration
    metadata['lambda_version'] = lambda_version
    metadata['query'] = query
    metadata['results'] = answer
    metadata['feedback'] = "NA"
    metadata['task_type'] = task_type
    metadata['model_metadata'] = MODEL_METADATA
    metadata['llm_model'] = BEDROCK_MODEL_ID
    metadata['text_embedding_model_id'] = TEXT_EMBEDDING_MODEL_ID
    query_embedding = embed_query(query)
    metadata['embedding'] = [Decimal(str(x)) for x in query_embedding]

    return metadata