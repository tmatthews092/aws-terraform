import json
import boto3
import logging
import re
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.client('s3')
substring_to_search = 'AACGCT'

def lambda_handler(event, context):
    logger.info('Launching Fasta File Parser')

    bucket_name, file_key, file_content = get_file_details_from_s3(event)
    sequence_data = set_sequence_data(file_content)
    # Format all data to be inserted in s3 file
    match_data = {
        "file_name": file_key,
        "substring_to_search": substring_to_search,
        "sequences_data": sequence_data,
        "timestamp": datetime.now(timezone.utc)
    }
    
    upload_results_file_to_s3(file_key, bucket_name, match_data)

    logger.info(match_data)
    return {
        'statusCode': 200,
        'body': match_data
    }

def upload_results_file_to_s3(file_key, bucket_name, match_data):
    encoded_string = json.dumps(
        match_data, 
        indent=4, 
        sort_keys=True, 
        default=str
    ).encode("utf-8")

    file_name = f"results_{file_key}.json"
    s3_path = "results/" + file_name

    # upload s3 file back to bucket in results folder
    s3.put_object(Bucket=bucket_name, Key=s3_path, Body=encoded_string)

def get_file_details_from_s3(event):
    # retrieve bucket name and file_key from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    # get the object
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    #get lines of file
    file_content = obj['Body'].read().decode('utf-8').splitlines()
    return bucket_name, file_key, file_content

def set_sequence_data(fc):
    sd = []
    for name, seq in extract_name_seq(fc):
        matches = 0
        match_start_positions = []
        for match in re.finditer(substring_to_search, seq):
            matches += 1
            match_start_positions.append(match.start())
        sd.append({
            'identifier': name,
            'sequence': seq,
            'matches': matches,
            'match_start_positions': match_start_positions
        })
    return sd

# https://stackoverflow.com/questions/29805642/learning-to-parse-a-fasta-file-with-python
def extract_name_seq(fc):
    name, seq = None, []
    for line in fc:
        line = line.rstrip()
        if line.startswith(">"):
            if name: yield (name, ''.join(seq))
            name, seq = line, []
        else:
            seq.append(line)
    if name: yield (name, ''.join(seq))
