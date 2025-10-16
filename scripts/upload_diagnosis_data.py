import os, sys
import boto3
import glob

folder = os.path.dirname(os.path.abspath(sys.argv[0]))
folder = os.path.abspath(os.path.join(folder,'../data/unique_markdowns'))

local_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
local_folder = os.path.abspath(os.path.join(local_folder,'../data/unique_markdowns'))
bucket_name = "lneg-loka"
s3 = boto3.client('s3')

def upload_to_s3(local_path, bucket):
    key = os.path.basename(local_path)
    key = f"unique_diagnosis-docs/{key}"
    s3.upload_file(local_path, bucket, key)
    return key

for md_file in glob.glob(os.path.join(local_folder,"*md")):
    upload_to_s3(md_file,bucket_name)


