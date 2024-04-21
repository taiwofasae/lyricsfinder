import os
import boto3
import mimetypes

from dotenv import load_dotenv
load_dotenv()

S3_BUCKET = os.getenv("AWS_STORAGE_BUCKET_NAME")
S3_FOLDER = os.getenv("AWS_LOCATION")

s3_client = boto3.client('s3')

def uploadDirectory(path,bucketname):
        for root,dirs,files in os.walk(path):
            for file in files:
                  
                local_path = os.path.join(root, file)

                relative_path = os.path.relpath(local_path, path)
                s3_path = os.path.join(S3_FOLDER, relative_path).replace("\\","/")

                content_type = mimetypes.guess_type(file)[0] or 'binary/octet-stream'

                print("{0} uploading to {1}; {2}".format(relative_path, s3_path, content_type))
                s3_client.upload_file(local_path, bucketname, s3_path,
                                      ExtraArgs={'ContentType': content_type}) #'ACL': 'public-read', 


uploadDirectory('.', S3_BUCKET)
