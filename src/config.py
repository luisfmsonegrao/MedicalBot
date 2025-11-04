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
