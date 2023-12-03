# imports
import boto3
from datetime import datetime, timezone
import json
import logging
import os
import re
import sys
import traceback

# init logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# init s3 client
s3 = boto3.client('s3')

# init substring to search
substring_to_search = os.environ['SUBSTRING_TO_SEARCH']

def lambda_handler(event, context):
    try:
        bucket_name, file_key, file_content = get_fasta_s3_object(event)
        sequence_data = set_sequence_data(file_content)
        match_data = set_match_data(file_key, sequence_data)
        upload_results_s3_object(match_data, file_key, bucket_name)
    except Exception as e:
        error_msg = json_to_string(traceback.format_exception(*sys.exc_info()))
        logger.error(f'***Error: {error_msg}***')
        upload_errors_s3_object(file_key, bucket_name, error_msg)
        return {
            'statusCode': 500,
            'body': error_msg
        }

    logger.info(f'***Completed matching {substring_to_search} in {file_key}***')
    return {
        'statusCode': 200,
        'body': match_data
    }

# ----------------------------------------------------------------------------------------------------------------------
# GETTERS
# ----------------------------------------------------------------------------------------------------------------------

def get_fasta_s3_object(event):
    # retrieve bucket name and file_key from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    # get the object
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    # get lines of file
    file_content = obj['Body'].read().decode('utf-8').splitlines()
    logger.info(f'***Fasta File {file_key} was uploaded***')
    logger.info(f'***Begin substring match of {substring_to_search} on file {file_key}***')
    return bucket_name, file_key, file_content

# ----------------------------------------------------------------------------------------------------------------------
# SETTERS
# ----------------------------------------------------------------------------------------------------------------------

def set_match_data(file_key, sequence_data):
    # format all data to be inserted in s3 file
    return json_to_string({
        "file_name": file_key,
        "substring_to_search": substring_to_search,
        "sequences_data": sequence_data,
        "timestamp": datetime.now(timezone.utc)
    })

def set_sequence_data(fc):
    sequence_data = []
    # for each sequence block create a dictionary and append to sequence data
    for name, seq in extract_name_seq(fc):
        matches = 0
        match_start_positions = []
        # for each match in the sequence increment match and record its character position
        for match in re.finditer(substring_to_search, seq):
            matches += 1
            match_start_positions.append(match.start())
        sequence_data.append({
            'name': name,
            'sequence': seq,
            'matches': matches,
            'match_start_positions': match_start_positions
        })
    return sequence_data

# ----------------------------------------------------------------------------------------------------------------------
# UPLOAD TO S3 HELPERS
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
# HELPERS
# ----------------------------------------------------------------------------------------------------------------------

def json_to_string(value):
    return json.dumps(
        value, 
        indent=4, 
        sort_keys=True, 
        default=str
    ).encode("utf-8")

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
