from pydantic import BaseModel, Field, StrictInt,StrictFloat, StrictStr
from typing import Literal

class ContextInput(BaseModel):
    query: StrictStr

class PredictionInput(BaseModel):
    age: StrictInt = Field(...)
    sex: Literal["Male","Female"]
    smoker: Literal["Yes","No"]
    bmi: StrictFloat = Field(...)

class QueryInput(BaseModel):
    sql: StrictStr