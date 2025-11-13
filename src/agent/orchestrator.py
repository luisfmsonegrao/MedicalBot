from .intent_classifier import get_task
#.copd_classifier import get_prediction, validate_features
from .llm_caller import call_llm
from .data_retriever import get_data
from .context_retriever import contextualize_query, retrieve_context
from .interaction_saver import save_interaction
from .custom_errors import AthenaQueryError, IntentClassificationError, ModelPredictionError

def orchestrate(query,query_id,session_id):
    """
    Orchestrate MedicalBot agent
    """
    task_status = True
    error_name = ''
    context = []
    try:
        task = get_task(query) # maybe this step can use smaller model specialized to text classification
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
            #feature_status, missing_features = validate_features(features)
            #if feature_status:
                #try:
                    #pred = get_prediction(features)
                #except ModelPredictionError as e:
                #    answer = {'text': str(e), 'data': ''}
                #    task_status = False
                #    error_name = type(e).__name__
                #else:
                #    answer = {'text': f"Model prediction: {pred[0]}; Feature values: {features}", 'data': ''}
            #else:
                #answer = {'text': f"Missing required features: {missing_features}. Please provide them in your query.", 'data': ''}

            answer = {'text': f"Model prediction are not supported in AWS Lambda due to layer size limit. Agent will be containerized soon.", 'data': ''}
            task_status = False

        elif task == 'question_answering':
            context = retrieve_context(query)
            llm_query = contextualize_query(query,context)
            answer = {'text': call_llm(llm_query), 'data': ''}
        
        elif task == 'db_query':
            try:
                data = get_data(features)
                answer = {'text': features, 'data': data}
            except AthenaQueryError as e:
                answer = {'text': str(e), 'data': ''}
                task_status = False
                error_name = type(e).__name__
        
    save_interaction(
        query,
        answer,
        context,
        task,
        query_id,
        session_id,
        features,
        task_status,
        error_name
    )
    return answer
