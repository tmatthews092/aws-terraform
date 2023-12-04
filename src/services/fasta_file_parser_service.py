from datetime import datetime, timezone
import os
import re
from utils.helpers import *

# envir variables
substring_to_search = os.environ['SUBSTRING_TO_SEARCH']

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
        matches, match_start_positions = do_match_logic(seq)
        sequence_data.append({
            'name': name,
            'sequence': seq,
            'matches': matches,
            'match_start_positions': match_start_positions
        })
    return sequence_data

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

def do_match_logic(seq):
    matches = 0
    match_start_positions = []
    # for each match in the sequence increment match and record its character position
    for match in re.finditer(substring_to_search, seq):
        matches += 1
        match_start_positions.append(match.start())
    return matches, match_start_positions
