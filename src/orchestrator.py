import json
import boto3
import joblib
from context_retriever import retrieve_context
from context_retriever import KNOWLEDGE_BASE_ID

BEDROCK_MODEL_ID = 'anthropic.claude-3-sonnet-20240229-v1:0'
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
source_uri_string = 'x-amz-bedrock-kb-source-uri'
model = joblib.load(".\..\models\decision_tree_classifier_small.joblib")
model_features = ['age','bmi','smoker','sex']
target_variable_name = 'Chronic Obstructive Pulmonary Disease'

def is_prediction_request(query):
    prompt = f"""
    You are an assistant.

    TASK 1 — Determine if the user query is asking for a prediction based on feature values.

    TASK 2 — If the query is a prediction query, extract these features if present:
    {model_features}

    Return ONLY valid JSON in the following format:
    {{
      "is_prediction": True or False,
      "features": {{
         "age": number or null,
         "bmi": number or null,
         "smoker": True | False | null,
         "sex": True if value is Male" | False if value is "Female" | null
      }}
    }}

    Query: "{query}"
    """
    [answer,_] = call_llm(prompt)
    try:
        result = json.loads(answer)
    except json.JSONDecodeError:
        result = {"is_prediction": False, "features": {}}
    return result

def call_llm(query):
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
    completion_reason = payload.get('stop_reason', 'unknown')
    return [response,completion_reason]

def orchestrate(query):
    task_context = is_prediction_request(query)
    if task_context.get('is_prediction'):
        features = task_context.get('features',{})
        missing = [f for f in model_features if features.get(f) in (None, "", "null")]
        if missing:
                return f"Missing required features: {missing}. Please provide them in your query."
        X = [[float(v) for (k,v) in features.items()]]
        pred = model.predict(X)
        return f"Model prediction for {target_variable_name}: Class {pred[0]}"

    context_size = 5
    context = retrieve_context(query,KNOWLEDGE_BASE_ID,context_size)
    system_query = (
        f"""You are an assistant. 
        Use information in the context to answer the question.
        If you use information from a document, include its document id and its s3 uri in your answer.
        If unsure, say you don't know."""
    )
    
    llm_query = system_query + "\nContext:\n"
    for i,c in enumerate(context,start=1):
        text = c['text']
        uri = c['metadata'][source_uri_string]
        llm_query += "[{}]: {} (source: {})\n".format(i,text,uri)

    llm_query += f"Question: {query}" + "\nAnswer:"
    [llm_response,completion_reason] = call_llm(llm_query)
    #while completion_reason != 'FINISH':
        #do necessary actions
        #update llm_query
        #query again
    return llm_response

