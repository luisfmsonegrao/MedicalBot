import json
import boto3
from context_retriever import retrieve_context
from context_retriever import KNOWLEDGE_BASE_ID

BEDROCK_MODEL_ID = 'amazon.titan-text-lite-v1'
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
source_uri_string = 'x-amz-bedrock-kb-source-uri'

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
    completion_reason = payload['results'][0]['completionReason']
    return [response,completion_reason]

def orchestrate(query):
    print('HERE')
    context_size = 5
    context = retrieve_context(query,KNOWLEDGE_BASE_ID,context_size)
    system_query = (
        f"""You are an assistant. 
        Use information in the context to answer the question.
        If you use information from a source, include the source in your answer.
        If unsure, say you don't know."""
    )
    llm_query = system_query + "\nQuestion: " + query + "\nContext:\n"
    for (i,c) in enumerate(context):
        llm_query += f"[{i}]: {c['text']} (source: {c['metadata'][source_uri_string]})\n\n"

    [llm_response,completion_reason] = call_llm(llm_query)
    #while completion_reason != 'FINISH':
        #do necessary actions
        #update llm_query
        #reprompt
    return llm_response

