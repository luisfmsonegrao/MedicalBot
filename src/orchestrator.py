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

def orchestrate(query):
    task = get_task(query)#maybe this step can use smaller model specialized to text classification
    if task.get('task') == 'prediction_task':
        pred = _get_prediction(task)
        return f"Model prediction for {target_variable_name} class: {pred[0]}"

    if task.get('task') == 'question_answering_task':
        answer = _get_answer(query)
        return answer
    
    if task.get('task') == 'db_query_task':
        return "Database queries are not supported yet."

def get_task(query):
    prompt = f"""
    You are an assistant.

    TASK 1 — Classify the query into one of the following 3 classes: prediction_task, db_query_task or question_answering_task.
    If the query is not a prediction task, return only valid JSON in the following format:
    {{
      "task": 'db_query_task' or 'question_answering_task',
      "features": {{}}
    }}

    TASK 2 — If the query is a prediction_task, extract these features if present:
    {model_features}
    Return ONLY valid JSON in the following format:
    {{
      "task": 'prediction_task',
      "features": {{
         "age": number or null,
         "bmi": number or null,
         "smoker": True | False | null,
         "sex": True if value is "Male" | False if value is "Female" | null
      }}
    }}

    Query: "{query}"
    """
    answer = call_llm(prompt)
    try:
        task = json.loads(answer)
    except json.JSONDecodeError:
        task = {"task": 'question_answering_task', "features": {}}
    return task

def _get_prediction(task):
    features = task.get('features',{})
    missing = [f for f in model_features if features.get(f) in (None, "", "null")]
    if missing:
            return f"Missing required features: {missing}. Please provide them in your query."
    X = [[float(v) for (k,v) in features.items()]]
    pred = model.predict(X)
    return pred

def _get_answer(query):
    context_size=5
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
    answer = call_llm(llm_query)
    return answer

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
    return response