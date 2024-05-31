import json
import boto3
from common import log
from lyricsproject import settings
from botocore.exceptions import ClientError


S3_BUCKET = settings.S3["BUCKET_NAME"]
S3_FOLDER = settings.S3["FOLDER"]

def _full_key(file_name):
    return "{0}/{1}".format(S3_FOLDER, file_name).replace('//','/')


def upload_file(file_name, json_dump):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param json_dump: json data to be uploaded
    :return: True if file was uploaded, else False
    """
    file_name = _full_key(file_name)
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
    file_name = _full_key(file_name)
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

def download_file_to(src_file_name, dest_file_name):
    data = None
    file_name = _full_key(src_file_name)
    s3_client = boto3.client('s3')
    try:
        log.info("downloading data from s3 bucket")
        s3_client.download_file(Bucket=S3_BUCKET, Key=file_name, Filename=dest_file_name)

    except ClientError as e:
        log.error(e)
        log.info("downloading failed. key:{0}".format(file_name))
        
def file_exists(file_name):
    s3_client = boto3.client('s3')
    file_name = _full_key(file_name)
    try:
        log.info("checking key in s3 bucket")
        s3_client.head_object(Bucket=S3_BUCKET, Key=file_name)

        return True
    except ClientError as e:
        log.error(e)
        log.info("key check failed. key:{0}".format(file_name))
        
    return False