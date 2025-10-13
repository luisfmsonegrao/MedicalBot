import pandas as pd
import os
import boto3
import io
import numpy as np
from sklearn.preprocessing import LabelEncoder

#Load raw data
bucket_name = "lneg-loka"
file_name = "patient_data_raw.csv"
processed_file_name = "patient_data_processed.csv"
s3 = boto3.client('s3')
obj = s3.get_object(Bucket=bucket_name, Key=file_name)
csv_string = obj['Body'].read().decode('utf-8')
df = pd.read_csv(io.StringIO(csv_string))

df_new = df.copy()

#clean & transform data
# Should make preprocessing a part of model pipeline to avoid having to preprocess test data at inference time
df_new = df_new.drop('exercise_frequency',axis=1)
df_new = df_new.drop('education_level',axis=1)
df_new = df_new.drop('patient_id',axis=1)
df_new = df_new.drop("alanine_aminotransferase",axis=1)
label_encoder = LabelEncoder()
df_new['diet_quality'] = label_encoder.fit_transform(df['diet_quality'])
df_new['income_bracket'] = label_encoder.fit_transform(df['income_bracket'])
multinomial_categories = ['diagnosis_code']
multinomial_df = pd.get_dummies(df_new[multinomial_categories],drop_first=False)
binomial_categories =['sex','smoker']
binomial_df = pd.get_dummies(df_new[binomial_categories],drop_first=True)
df_new = df_new.drop(multinomial_categories,axis=1)
df_new = df_new.drop(binomial_categories,axis=1)
df_new = pd.concat([df_new,binomial_df],axis=1)
df_new = pd.concat([df_new,multinomial_df],axis=1)
df_new

#upload data
buffer = io.StringIO()
df_new.to_csv(buffer)
s3.put_object(Bucket = bucket_name, Key = processed_file_name, Body = buffer.getvalue())




