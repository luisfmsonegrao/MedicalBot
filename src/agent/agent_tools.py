from langchain_core.tools.structured import StructuredTool
from .context_retriever import get_context_information
from .copd_classifier import predict_copd
from .data_retriever import query_athena_database
from .table_schema_retriever import get_table_schema
from .agent_config import ATHENA_DATABASE_NAME,PATIENT_DATA_TABLE_NAME

context_tool_name = "get_context_information"
context_tool = StructuredTool.from_function(
    func=get_context_information,
    name=context_tool_name,
    description = f"""Use {context_tool_name} when the user asks questions about patients or staff at City General Hospital.
                      The tool gives you relevant information from patients' medical records."""
)

prediction_tool_name = "predict_copd"
prediction_tool = StructuredTool.from_function(
    func=predict_copd,
    name=prediction_tool_name,
    description = f"""Use {prediction_tool_name} to predict the class of Chronic Obstructive Pulmonary Disease. 
                    If any features are invalid/missing in the user query, prompt user to provide valid features."""
)

db_query_tool_name = "query_athena_database"
table_schema = get_table_schema(ATHENA_DATABASE_NAME,PATIENT_DATA_TABLE_NAME)
db_query_tool = StructuredTool.from_function(
    func=query_athena_database,
    name=db_query_tool_name,
    description = f"""Use {db_query_tool_name} when the user asks for data.
                      The tool retrieves data from an Athena database {PATIENT_DATA_TABLE_NAME}.
                      The database schema is: {table_schema}
                      Do not use {db_query_tool_name} to answer queries about specific people.
                      Convert the user query to SQL without including any fields that are not in the database schema."""
)
