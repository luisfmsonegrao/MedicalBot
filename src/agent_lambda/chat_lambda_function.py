import json, time
import os
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
        body = json.loads(event.get("body"))
        session_id = body.get("session_id")
        query_id = body.get("query_id")
        user_query = body.get("query")
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid request"})
        }
    task_status = True
    error_name = error_description = answer = ""
    status_code = 200
    callback = LoggingCallback()
    try:
        start_time = time.perf_counter()
        answer = agent.invoke({"messages": [{"role": "user", "content":user_query}]}, config={"callbacks": [callback]})
        print(f"Ans1:{answer}")
        total_duration = time.perf_counter() - start_time
        answer = getattr(answer['messages'][-1],'content')
        print(f"Ans2:{answer}")
    except Exception as e:
        print(f"Error:{e}")
        task_status = False
        total_duration = 0
        callback.on_chain_end(chain=agent,outputs=None)
        error_name = e.__class__.__name__
        error_description = str(e)
        status_code = 500

    metadata = build_metadata(
        session_id,
        query_id,
        task_status,
        lambda_version,
        user_query,
        answer,
        total_duration,
        error_name,
        error_description,
        callback
        )
    save_interaction(**metadata)
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        },
        "body": json.dumps({"answer": answer, "error": error_description})
    }