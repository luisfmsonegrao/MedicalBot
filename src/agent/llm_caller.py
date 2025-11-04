import json
import boto3
from src.config import BEDROCK_MODEL_ID

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def call_llm(query):
    """Query foundation LLM"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {"role": "user", "content": query}
        ],
        "max_tokens": 4000,
        "temperature": 0.0,
        "top_p": 0.9
    })
    output = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json"
    )
    payload = json.loads(output['body'].read())
    response = payload['content'][0]['text']
    return response