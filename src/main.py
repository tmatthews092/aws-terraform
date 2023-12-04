# imports
import logging
import os
import sys
import traceback
from utils.helpers import *
from utils.s3_helpers import *
from services.fasta_file_parser_service import set_match_data, set_sequence_data

# init logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# envir variables
substring_to_search = os.environ['SUBSTRING_TO_SEARCH']

def lambda_handler(event, context):
    try:
        bucket_name, file_key, file_content = get_s3_object(event)
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
