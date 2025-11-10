import os
import boto3
import json

secrets_client = boto3.client("secretsmanager", region_name="us-east-1")


def get_secret(secret_name):
    """
    Fetch secret value from AWS Secrets Manager.
    """
    response = secrets_client.get_secret_value(SecretId=secret_name)
    secret_string = response.get("SecretString")
    if secret_string:
        return json.loads(secret_string)
    return None


def lambda_handler(event, context):
    secret_name = os.environ.get("SECRET_NAME")
    secret = get_secret(secret_name)
    api_key = secret.get("api-key") if secret else None
    token = event["headers"].get("api-key")
    if token == api_key:
        return {"isAuthorized": True, "context": {"user": "trusted-user"}}
    else:
        return {"isAuthorized": False}