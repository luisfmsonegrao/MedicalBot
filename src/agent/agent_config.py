import os,json

AWS_REGION = "us-east-1"

KNOWLEDGE_BASE_ID = "A3XBZT3D8Y"

BEDROCK_MODEL_ID = 'anthropic.claude-3-sonnet-20240229-v1:0'

S3_BUCKET = 'lneg-loka'

ATHENA_DATABASE_NAME = 'patient_data'

ATHENA_OUTPUT_PATH = f"s3://{S3_BUCKET}/datadoctor-query-results/"

PATIENT_DATA_TABLE_NAME = 'patient_data'

MODEL_FEATURES = ['age','bmi','smoker','sex']

TARGET_NAME = 'Chronic Obstructive Pulmonary Disease'

SOURCE_URI_STRING = 'x-amz-bedrock-kb-source-uri'

CONTEXT_WINDOW = 5

TEXT_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"

CACHE_TTL = 7200

model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
model_metadata_name = "model_metadata.json"
model_metadata_file = os.path.join(model_path,model_metadata_name)

with open(model_metadata_file,'r',encoding='utf-8') as f:
    MODEL_METADATA = json.load(f)