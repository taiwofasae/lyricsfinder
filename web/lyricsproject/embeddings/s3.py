import json
import os
import boto3
from common import log
from lyricsproject import settings
from botocore.exceptions import ClientError


S3_BUCKET = settings.S3["BUCKET_NAME"]
S3_FOLDER = settings.S3["FOLDER"]

embeddings_folder = os.path.join(S3_FOLDER, 'embeds/')
song_folder = os.path.join(embeddings_folder, 'song/')
phrase_folder = os.path.join(embeddings_folder, 'phrase/')
search_folder = os.path.join(embeddings_folder, 'search/')

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


def download_file(file_name):
    """Download a file from an S3 bucket

    :param file_name: File to upload
    :return: {Body: }
    """
    data = None
    s3_client = boto3.client('s3')
    try:
        log.info("downloading data from s3 bucket")
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=file_name)
        data = json.loads(response['Body'].read())

    except ClientError as e:
        log.error(e)
        log.info("downloading failed")
        
    return data


def save_song_embedding(song_id, embeddings):
    
    upload_file("{0}{1}.csv".format(song_folder, song_id), json.dumps(embeddings))

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

if __name__ == "__main__":
    log.getLogger().setLevel(log.INFO)

sample = {
    "it": "hello everyone",
    "okay": "thank you"
}

#upload_file(os.path.join(embeddings_folder, 'sample.json'), json.dumps(sample))
#print(download_file(os.path.join(embeddings_folder, 'sample.json')))