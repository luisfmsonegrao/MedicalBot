from .intent_classifier import get_task
#.copd_classifier import get_prediction, validate_features
from .llm_caller import call_llm
from .data_retriever import get_data
from .context_retriever import contextualize_query, retrieve_context
from .interaction_saver import save_interaction
from .custom_errors import AthenaQueryError, IntentClassificationError, ModelPredictionError
from .copd_classifier import get_prediction, validate_features
import time

def orchestrate(query,query_id,session_id):
    """
    Orchestrate MedicalBot agent
    """
    start_time = time.perf_counter()
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
        
    duration = time.perf_counter() - start_time
    durations_dict = {'total_duration': duration, 
                      'intent_duration': intent_duration,
                      'pred_duration': pred_duration,
                      'context_duration': context_duration,
                      'qa_duration': qa_duration,
                      'dbquery_duration': dbquery_duration
                      }
    
    save_interaction(
        query,
        answer,
        context,
        task,
        query_id,
        session_id,
        features,
        task_status,
        durations_dict,
        error_name
    )
    return answer
