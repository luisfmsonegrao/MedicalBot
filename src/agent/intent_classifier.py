import json
from json import JSONDecodeError
from .custom_errors import IntentClassificationError
from .table_schema_retriever import get_table_schema
from .agent_config import MODEL_FEATURES, ATHENA_DATABASE_NAME, PATIENT_DATA_TABLE_NAME
from .llm_caller import call_llm

table_schema = get_table_schema(ATHENA_DATABASE_NAME,PATIENT_DATA_TABLE_NAME)


def get_task(query):
    """
    Classify intent of user's query
    """

    prompt = f"""
    You are an assistant. Execute the following steps:

    Step 1 — Classify the query into one of 3 task classes: 'prediction', 'database query' or 'question answering'.
    
    Step 2 - return only valid JSON format according to the task class:
    
    Question Answering - use the following JSON format:
    {{
      "task": 'question_answering',
      "features": {{}}
    }}

    Prediction - extract features {MODEL_FEATURES} from the query, if present. Use the following JSON format:
    {{
      "task": 'prediction',
      "features": {{
         "age": number or null,
         "bmi": number or null,
         "smoker": "Yes" | "No" | null,
         "sex": "Male" | "Female" | null
      }}
    }}

    Database query - convert query to SQL query for table {PATIENT_DATA_TABLE_NAME}. Strictly obey the table schema: {table_schema}.\n Use the following JSON format:
    {{
        "task": 'db_query'.
        "features":  SQL statement
    }}
    If the query is an aggregation operation, give the appropriate name to the new column.
    Note that the table is anonymized, it does not contain patient names.

    Query: "{query}"
    """
    answer = call_llm(prompt)
    try:
        task = json.loads(answer)
    except JSONDecodeError as e:
        task_type = answer.split('"task":')[1].split(",")[0].strip()
        features = answer.split('"features":')[1].split("}")[0].strip()
        raise IntentClassificationError(task_type,features,e)
    return task