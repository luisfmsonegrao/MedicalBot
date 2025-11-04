import boto3
import joblib
import pandas as pd
import time
from intent_classifier import get_task
from copd_classifier import get_prediction
from llm_caller import call_llm
from data_retriever import get_data
from context_retriever import contextualize_query
from src.config import TARGET_NAME


def orchestrate(query):
    """Orchestrate DataDoctor agent"""

    task = get_task(query)#maybe this step can use smaller model specialized to text classification
    features = task.get('features',{})
    if task.get('task') == 'prediction':
        pred = get_prediction(features)
        return f"Model prediction for {TARGET_NAME} class: {pred}"

    if task.get('task') == 'question_answering':
        llm_query = contextualize_query(query)
        answer = call_llm(llm_query)
        return answer
    
    if task.get('task') == 'db_query':
        data = get_data(features)
        return data
