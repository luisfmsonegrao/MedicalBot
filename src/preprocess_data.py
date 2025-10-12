import pandas as pd
import os
import boto3
import io
import numpy as np

bucket_name = "lneg-loka"
file_name = "patient_data_raw.csv"
processed_file_name = "patient_data_processed.csv"

#load data from s3
s3 = boto3.client('s3')
obj = s3.get_object(Bucket=bucket_name, Key=file_name)
csv_string = obj['Body'].read().decode('utf-8')
df = pd.read_csv(io.StringIO(csv_string))

#copy data into new dataframe
df_new = df.copy()

#drop columns with NaN values since their class-conditional distributions are virtually independent of the target class
df_new = df_new.drop('exercise_frequency',axis=1)
df_new = df_new.drop('education_level',axis=1)

#alanine_aminotransferase is virtually collinear with BMI. Perhaps data is corrupted. In any case, at least one of them should be dropped.
df_new = df_new.drop("alanine_aminotransferase",axis=1)


buffer = io.StringIO()
df_new.to_csv(buffer)
s3.put_object(Bucket = bucket_name, Key = processed_file_name, Body = buffer.getvalue())




