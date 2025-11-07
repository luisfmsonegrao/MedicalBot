import boto3
import json

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("medicalbot-cache")

def lambda_handler(event, context):
    body = json.loads(event["body"])
    feedback = body['feedback']
    query_id = body['query_id']
    table.update_item(
        Key={"query_id": query_id},
        UpdateExpression="set feedback = :f",
        ExpressionAttributeValues={":f": feedback}
    )
    return {"statusCode": 200, "body": json.dumps({"status": "feedback recorded"})}