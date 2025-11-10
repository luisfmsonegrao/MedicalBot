from .intent_classifier import get_task
#.copd_classifier import get_prediction, validate_features
from .llm_caller import call_llm
from .data_retriever import get_data
from .context_retriever import contextualize_query, retrieve_context
from .interaction_saver import save_interaction
from .custom_errors import AthenaQueryError, ModelPredictionError

def orchestrate(query,query_id):
    """
    Orchestrate DataDoctor agent
    """
    task_status = True
    error_name = ''
    task = get_task(query)#maybe this step can use smaller model specialized to text classification
    features = task.get('features',{})
    context = []
    task = task.get('task')
    if task == 'prediction':
        #status, message = validate_features(features)
        #if status:
            #try:
                #pred = get_prediction(features)
            #except ModelPredictionError as e:
            #    answer = str(e)
            #    task_status = False
            #    error_name = type(e).__name__
            #else:
            #    answer = f"Model prediction: {pred[0]}"
        #else:
            #answer = message
        answer = f"Model prediction are not supported in AWS Lambda due to layer size limit. Agent will be containerized soon."
        task_status = False

    elif task == 'question_answering':
        context = retrieve_context(query)
        llm_query = contextualize_query(query,context)
        answer = call_llm(llm_query)
    
    elif task == 'db_query':
        try:
            answer = get_data(features)
        except AthenaQueryError as e:
            answer = str(e)
            task_status = False
            error_name = type(e).__name__

    save_interaction(query,answer,context,task,query_id,features,task_status,error_name)
    return answer
