import boto3
from datetime import datetime, timezone
import logging

# init logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# init s3 client
s3 = boto3.client('s3')

# ----------------------------------------------------------------------------------------------------------------------
# UPLOAD FILE
# ----------------------------------------------------------------------------------------------------------------------

def upload_results_s3_object(match_data, file_key, bucket_name):
    file_name = f"results_{file_key}.json"
    s3_path = "results/" + file_name

    # upload s3 file back to bucket in results folder
    s3.put_object(Bucket=bucket_name, Key=s3_path, Body=match_data)
    logger.info(f'***Uploaded {file_name} to the results folder in {bucket_name}***')

def upload_errors_s3_object(file_key, bucket_name, error_msg):
    file_name = f"error_{file_key}_{datetime.now(timezone.utc)}.json"
    s3_path = "errors/" + file_name
    # upload s3 file back to bucket in error folder
    s3.put_object(Bucket=bucket_name, Key=s3_path, Body=error_msg)
    logger.info(f'***Uploaded Error file to error folder {file_name} in {bucket_name}***')

# ----------------------------------------------------------------------------------------------------------------------
# GET FILE
# ----------------------------------------------------------------------------------------------------------------------

def get_s3_object(event):
    # retrieve bucket name and file_key from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    # get the object
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    # get lines of file
    file_content = obj['Body'].read().decode('utf-8').splitlines()
    logger.info(f'***Fasta File {file_key} was uploaded***')
    return bucket_name, file_key, file_content
