from .intent_classifier import get_task
#.copd_classifier import get_prediction
from .llm_caller import call_llm
from .data_retriever import get_data
from .context_retriever import contextualize_query, retrieve_context
from .interaction_saver import save_interaction
from .custom_errors import AthenaQueryError

def orchestrate(query,query_id):
    """Orchestrate DataDoctor agent"""
    task_status = True
    task = get_task(query)#maybe this step can use smaller model specialized to text classification
    features = task.get('features',{})
    context = []
    task = task.get('task')
    if task == 'prediction':
        #pred = get_prediction(features)
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


    save_interaction(query,answer,context,task,query_id,features, task_status)
    return answer
