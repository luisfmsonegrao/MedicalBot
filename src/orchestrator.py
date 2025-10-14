import json
import boto3
from context_retriever import retrieve_context
from context_retriever import KNOWLEDGE_BASE_ID

BEDROCK_MODEL_ID = 'amazon.titan-text-lite-v1'
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def call_llm(query):
    print('CALL-LLM')
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
    completion_reason = payload['results'][0]['completionReason']
    return [response,completion_reason]

def orchestrate(query):
    print('HERE')
    context_size = 5
    context = retrieve_context(query,KNOWLEDGE_BASE_ID,context_size)
    system_query = (
        f"You are an assistant. Use the information in the context to answer the question. If unsure, say you don't know."
    )
    llm_query = system_query + "\nQuestion: " + query + "\nContext:\n"
    for c in context:
        llm_query += f"{c['text']}\n\n"
    print(llm_query)
    [llm_response,completion_reason] = call_llm(llm_query)
    #while completion_reason != 'FINISH':
        #do necessary actions
        #update llm_query
        #reprompt
    return llm_response

