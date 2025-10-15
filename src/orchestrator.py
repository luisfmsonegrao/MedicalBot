import json
import boto3
import joblib
import re
from context_retriever import retrieve_context
from context_retriever import KNOWLEDGE_BASE_ID
from enum import Enum

BEDROCK_MODEL_ID = 'amazon.titan-text-lite-v1'
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
source_uri_string = 'x-amz-bedrock-kb-source-uri'
model = joblib.load(".\..\models\decision_tree_classifier_small.joblib")
model_features = ['age','bmi','smoker','sex']
target_variable_name = 'Chronic Obstructive Pulmonary Disease'

class Sex(Enum):
    MALE = True
    FEMALE = False

class Smoker(Enum):
    YES=True
    NO=False

def extract_features(query):
    matches = re.findall(r'(\w+)\s*=\s*([\w\d.]+)', query)
    features = {k: v for k, v in matches}
    return features

def transform_features(features):
    try:
        features['sex']=Sex[features['sex'].upper()].value
    except KeyError as e:
       raise RuntimeError("Sex must be Male or Female")
    try:
        features['smoker']=Smoker[features['smoker'].upper()].value
    except KeyError as e:
        raise RuntimeError("Smoker must be YES or NO")
    return features

def get_feature_values(features):
    vals = [[features.get(f) for f in model_features]]
    return vals

def is_prediction_request(query):
    prediction_query = f"""
    You are a classification assistant.
    The user query is:
    "{query}"

    You must say if the user query is asking for a prediction. You must answer only one word:
    YES, if the user query is asking for a prediction.
    NO, if the user query does not ask for a prediction.

    Below are a few Examples to help you understand your task:
    "Can you predict lung cancer for a male patient with BMI=40, age=65 and active smoker."
    Answer: "YES"

    "Is a man with BMI=25, age=19 who does not smoke likely to have a heart attack?"
    Answer: "YES"

    "How many times has Paul Platt been admitted to the hospital?
    Answer: "No"

    Don't forget, answer only YES or NO.
    """
    [answer,_] = call_llm(prediction_query)
    return "YES" in answer

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
    if is_prediction_request(query):
        features = extract_features(query)
        if not all(feature in features for feature in model_features):
            return f"Please provide feature values for {model_features} in the format feature_name=value"
        features = transform_features(features)
        X = get_feature_values(features)
        pred = model.predict(X)
        return f"Model prediction for {target_variable_name}: Class {pred[0]}"

    context_size = 5
    context = retrieve_context(query,KNOWLEDGE_BASE_ID,context_size)
    system_query = (
        f"""You are an assistant. 
        Use information in the context to answer the question.
        If you use information from a document, cite it using its document id.
        If unsure, say you don't know."""
    )
    
    llm_query = system_query + "\nContext:\n"
    for i,c in enumerate(context,start=1):
        text = c['text']
        uri = c['metadata'][source_uri_string]
        llm_query += "ref.{}: {} (source: {})\n".format(i,text,uri)

    llm_query += f"Question: {query}" + "\nAnswer:"
    [llm_response,completion_reason] = call_llm(llm_query)
    #while completion_reason != 'FINISH':
        #do necessary actions
        #update llm_query
        #query again
    return llm_response

