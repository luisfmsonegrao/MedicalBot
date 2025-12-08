import json, time
import os
from src.agent.orchestrator import orchestrate
from src.agent.agent import agent
from src.agent.logging_callback import LoggingCallback
from src.agent.interaction_saver import save_interaction
from src.agent.build_metadata import build_metadata

def lambda_handler(event, context):
    """
    Handle requests to AWS Lambda function
    """
    lambda_version = os.environ["AWS_LAMBDA_FUNCTION_VERSION"]
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
        #(answer,metadata),time = orchestrate(user_query,query_id,session_id)
        callback = LoggingCallback()
        start_time = time.perf_counter()
        answer = agent.invoke({"messages": [{"role": "user", "content":user_query}]}, config={"callbacks": [callback]})
        total_duration = time.perf_counter() - start_time
        metadata = build_metadata(session_id,query_id,lambda_version,user_query,answer,total_duration,callback)
        save_interaction(**metadata)
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