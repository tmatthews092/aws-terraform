import json
import boto3
import logging
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.client('s3')
substring_to_search = 'AACGCT'

def lambda_handler(event, context):
    # retrieve bucket name and file_key from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    # get the object
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    #get lines of file
    file_content = obj['Body'].read().decode('utf-8')
    matches = file_content.count(substring_to_search)

    # Format all data to be inserted in s3 file
    match_data = {
        "file_name": file_key,
        "substring_to_search": substring_to_search,
        "matches": matches,
        "timestamp": datetime.now(timezone.utc)
    }
    
    encoded_string = json.dumps(
        match_data, 
        indent=4, 
        sort_keys=True, 
        default=str
    ).encode("utf-8")

    file_name = f"match_results_{file_key}.json"
    s3_path = "results/" + file_name

    # upload s3 file back to bucket in results folder
    s3.put_object(Bucket=bucket_name, Key=s3_path, Body=encoded_string)

    logger.info(matches)
    return {
        'statusCode': 200,
        'body': matches
    }
