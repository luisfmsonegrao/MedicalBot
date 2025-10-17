import json
import boto3
import joblib
import pandas as pd
import time
from context_retriever import retrieve_context
from context_retriever import KNOWLEDGE_BASE_ID
from table_schema_retriever import get_table_schema

BEDROCK_MODEL_ID = 'anthropic.claude-3-sonnet-20240229-v1:0'
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
s3_bucket = 'lneg-loka'
ATHENA_DATABASE = 'patient_data'
ATHENA_OUTPUT = f"s3://{s3_bucket}/datadoctor-query-results/"
TABLE_NAME = 'patient_data'
table_schema = get_table_schema(ATHENA_DATABASE,TABLE_NAME)
athena = boto3.client('athena',region_name = 'us-east-1')
model = joblib.load(".\..\models\decision_tree_classifier_small.joblib")
model_features = ['age','bmi','smoker','sex']
target_variable_name = 'Chronic Obstructive Pulmonary Disease'
source_uri_string = 'x-amz-bedrock-kb-source-uri'



def orchestrate(query):
    """Orchestrate DataDoctor agent"""

    task = get_task(query)#maybe this step can use smaller model specialized to text classification
    features = task.get('features',{})
    if task.get('task') == 'prediction':
        pred = _get_prediction(features)
        return f"Model prediction for {target_variable_name} class: {pred}"

    if task.get('task') == 'question_answering':
        llm_query = _prepare_qa_query(query)
        answer = call_llm(llm_query)
        return answer
    
    if task.get('task') == 'db_query':
        data = _get_data(features)
        return data

def get_task(query):
    """Classify intent of user's query"""

    prompt = f"""
    You are an assistant. Execute the following steps:

    Step 1 — Classify the query into one of 3 task classes: 'prediction', 'database query' or 'question answering'.
    
    Step 2 - return only valid JSON format according to the task class:
    
    Question Answering - use the following JSON format:
    {{
      "task": 'question_answering',
      "features": {{}}
    }}

    Prediction - extract features {model_features} from the query, if present. Use the following JSON format:
    {{
      "task": 'prediction',
      "features": {{
         "age": number or null,
         "bmi": number or null,
         "smoker": true | false | null,
         "sex": true if value is "Male" | false if value is "Female" | null
      }}
    }}

    Database query - convert query to SQL query for table {TABLE_NAME} using the table schema: {table_schema}.\n Use the following JSON format:
    {{
        "task": 'db_query'.
        "features":  SQL statement
    }}
    If the query is an aggregation operation, give the appropriate name to the new column.
    Note that the table is anonymized, it does not contain patient names.

    Query: "{query}"
    """
    answer = call_llm(prompt)
    print(answer)
    task = json.loads(answer)
    return task

def _get_prediction(features):
    """Predict Chronic Obstructive Pulmonary Disease outcome based on user's query"""

    missing = [f for f in model_features if features.get(f) in (None, "", "null")]
    if missing:
            return f"Missing required features: {missing}. Please provide them in your query."
    X = [[float(v) for (k,v) in features.items()]]
    pred = model.predict(X)
    return pred

def _prepare_qa_query(query):
    """Adapt user query for question answering with RAG from foundation model"""

    context_size=5
    context = retrieve_context(query,KNOWLEDGE_BASE_ID,context_size)
    system_query = (
        f"""You are an assistant. 
        Use information in the context to answer the question.
        If you use information from a document, include its document number and its s3 uri in your answer.
        If unsure, say you don't know."""
    )
    
    llm_query = system_query + "\nContext:\n"
    for i,c in enumerate(context,start=1):
        text = c['text']
        uri = c['metadata'][source_uri_string]
        llm_query += "[{}]: {} (source: {})\n".format(i,text,uri)

    llm_query += f"Question: {query}" + "\nAnswer:"
    return llm_query

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


def _get_data(query):
    """Query patient data from Amazon Athena database"""

    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': ATHENA_DATABASE},
        ResultConfiguration={'OutputLocation': ATHENA_OUTPUT}
    )
    execution_id = response['QueryExecutionId']

    while True:
        status = athena.get_query_execution(QueryExecutionId=execution_id)
        state = status['QueryExecution']['Status']['State']
        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(0.5)

    if state != 'SUCCEEDED':
        raise Exception(f"Athena query failed: {state}")

    results = athena.get_query_results(QueryExecutionId=execution_id)
    columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    rows = [
        [field.get('VarCharValue', None) for field in row['Data']]
        for row in results['ResultSet']['Rows'][1:]
    ]
    df = pd.DataFrame(rows, columns=columns)
    return df