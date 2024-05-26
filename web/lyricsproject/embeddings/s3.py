import json
import os
import boto3
import ast
from common import log
from lyricsproject import settings
from botocore.exceptions import ClientError


S3_BUCKET = settings.S3["BUCKET_NAME"]
S3_FOLDER = settings.S3["FOLDER"]

embeddings_folder = os.path.join(S3_FOLDER, 'embeds/')
song_folder = os.path.join(embeddings_folder, 'song/')
phrase_folder = os.path.join(embeddings_folder, 'phrase/')
search_folder = os.path.join(embeddings_folder, 'search/')

status_file = os.path.join(embeddings_folder, 'song/status.txt')


def upload_file(file_name, json_dump):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param json_dump: json data to be uploaded
    :return: True if file was uploaded, else False
    """

    # Upload the file
    s3_client = boto3.client('s3')

    log.info("uploading data to s3 bucket")
    response = s3_client.put_object(Bucket=S3_BUCKET, Key=file_name, Body=json_dump, ContentType='application/json' )


def download_file(file_name, json_deserialize=True):
    """Download a file from an S3 bucket

    :param file_name: File to upload
    :return: {Body: }
    """
    data = None
    s3_client = boto3.client('s3')
    try:
        log.info("downloading data from s3 bucket")
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=file_name)
        data = response['Body'].read()
        if json_deserialize:
            data = json.loads(data)

    except ClientError as e:
        log.error(e)
        log.info("downloading failed. key:{0}".format(file_name))
        
    return data

def file_exists(file_name):
    s3_client = boto3.client('s3')
    try:
        log.info("checking key in s3 bucket")
        s3_client.head_object(Bucket=S3_BUCKET, Key=file_name)

        return True
    except ClientError as e:
        log.error(e)
        log.info("key check failed. key:{0}".format(file_name))
        
    return False


def save_song_embedding(song_id, embeddings):
    
    upload_file("{0}{1}.csv".format(song_folder, song_id), json.dumps(embeddings))
    _update_status(song_id)

def load_song_embedding(song_id):
    
    return download_file("{0}{1}.csv".format(song_folder, song_id)) or []

def save_phrase_embedding(phrase_id, embeddings):
    
    upload_file("{0}{1}.csv".format(phrase_folder, phrase_id), json.dumps(embeddings))


def load_phrase_embedding(phrase_id):
    
    return download_file("{0}{1}.csv".format(phrase_folder, phrase_id)) or []

def save_search_phrase_embedding(search_id, embeddings):
    
    upload_file("{0}{1}.csv".format(search_folder, search_id), json.dumps(embeddings))

def load_search_phrase_embedding(search_id):
    
    return download_file("{0}{1}.csv".format(search_folder, search_id)) or []

## status management

def _load_status():
    log.info("loading status set from s3")
    return ast.literal_eval(download_file(status_file, json_deserialize=False).decode('utf-8') or '') or set()

def _save_status(status_set):
    log.info("saving status set to s3")
    upload_file(status_file, str(status_set))


def _update_status(song_id):
    status_set = _load_status()
    if song_id not in status_set:
        status_set.add(song_id)
        _save_status(status_set)

def song_embedding_exists(song_id):
    try:
        status_set = _load_status()
    except:
        _save_status(set())
        status_set = _load_status()

    if isinstance(song_id, list):
        return [id in status_set for id in song_id]
    
    return song_id in status_set

def all_song_statuses():
    return _load_status()