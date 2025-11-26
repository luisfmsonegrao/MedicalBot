import json
from src.agent.orchestrator import orchestrate 

def lambda_handler(event, context):
    """
    Handle requests to AWS Lambda function
    """
    try:
        body = json.loads(event.get("body", "{}"))
        session_id = body.get("session_id","")
        query_id = body.get("query_id","")
        user_query = body.get("query", "")
        if not user_query:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'query' field"})
            }
        answer = orchestrate(user_query,query_id,session_id)
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            },
            "body": json.dumps({"answer": answer})
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }