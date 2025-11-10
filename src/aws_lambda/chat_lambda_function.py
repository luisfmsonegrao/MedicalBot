import json
import uuid
from src.agent.orchestrator import orchestrate 

def lambda_handler(event, context):
    """
    Handle requests to AWS Lambda function
    """
    try:
        body = json.loads(event.get("body", "{}"))
        user_query = body.get("query", "")
        if not user_query:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'query' field"})
            }
        query_id = str(uuid.uuid4())
        answer = orchestrate(user_query,query_id)
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            },
            "body": json.dumps({"answer": answer, "query_id": query_id})
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }