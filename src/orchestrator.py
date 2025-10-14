import json
import boto3
from context_retriever import retrieve_context
from context_retriever import KNOWLEDGE_BASE_ID

BEDROCK_MODEL_ID = 'amazon.titan-text-lite-v1'
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def call_llm(query):
    body = json.dumps({
        "inputText": query,
        "textGenerationConfig": {
            "maxTokenCount": 4000,
            "temperature": 0.0,
            "topP": 0.9,      
    }
    })
    output = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json"
    )
    payload = json.loads(output['body'].read())
    response = payload['results'][0]["outputText"]
    return response

def orchestrate(query):
    context_size = 5
    context = retrieve_context(query,KNOWLEDGE_BASE_ID,context_size)
    system_query = (
        "You are an assistant that uses the provided context to answer questions. You answer in natural English language. If you don't know the answer to a question you say you dont know."
    )
    llm_query = system_query + "\nUser query: " + query + "\nContext:\n"
    for c in context:
        llm_query += f"{c['text']}\n\n"
    
    print(llm_query)
    llm_response = call_llm(llm_query)
    return llm_response



