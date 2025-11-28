from .intent_classifier import get_task
from .llm_caller import call_llm
from .data_retriever import get_data
from .context_retriever import contextualize_query, retrieve_context
from .custom_errors import AthenaQueryError, IntentClassificationError, ModelPredictionError
from .copd_classifier import get_prediction, validate_features
from .agent_config import MODEL_METADATA
from .time_decorator import measure_duration
import time

@measure_duration
def orchestrate(query,query_id,session_id):
    """
    Orchestrate MedicalBot agent
    """
    task_status = True
    error_name = ''
    context = []
    intent_duration = pred_duration = context_duration = qa_duration = dbquery_duration = 0

    try:
        task, intent_duration = get_task(query) # maybe this step can use smaller model specialized to text classification

    except IntentClassificationError as e:
        answer = {'text': str(e), 'data': ''}
        task_status = False
        error_name = type(e).__name__
        task = e.task_type
        features = e.features
    
    if task_status:
        features = task.get('features',{})
        task = task.get('task')
        if task == 'prediction':
            feature_status, missing_features = validate_features(features)
            if feature_status:
                try:
                    pred, pred_duration = get_prediction(features)
                except ModelPredictionError as e:
                    answer = {'text': str(e), 'data': ''}
                    task_status = False
                    error_name = type(e).__name__
                else:
                    answer = {'text': f"Model prediction: {pred[0]}; Feature values: {features}", 'data': ''}
            else:
                answer = {'text': f"Missing required features: {missing_features}. Please provide them in your query.", 'data': ''}

        elif task == 'question_answering':
            context, context_duration = retrieve_context(query)
            llm_query = contextualize_query(query,context)
            answer_text, qa_duration = call_llm(llm_query)
            answer = {'text': answer_text, 'data': ''}
        
        elif task == 'db_query':
            try:
                data, dbquery_duration = get_data(features)
                answer = {'text': f"Here's the data for query {features}:", 'data': data}
            except AthenaQueryError as e:
                answer = {'text': str(e), 'data': ''}
                task_status = False
                error_name = type(e).__name__
        
    durations_dict = {'intent_duration': intent_duration,
                      'pred_duration': pred_duration,
                      'context_duration': context_duration,
                      'qa_duration': qa_duration,
                      'dbquery_duration': dbquery_duration
                      }
    
    metadata = {
        "query":query,
        "results":answer,
        "timestamp":int(time.time()),
        "context":context,
        "task":task,
        "query_id":query_id,
        "session_id":session_id,
        "features":features,
        "task_status":task_status,
        "durations_dict":durations_dict,
        "error_name":error_name,
        "model_metadata":MODEL_METADATA
    }

    return answer, metadata
