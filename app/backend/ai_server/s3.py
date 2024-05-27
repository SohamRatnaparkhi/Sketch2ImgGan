import boto3
from env import (S3_ACCESS_KEY, S3_BUCKET_NAME, S3_BUCKET_REGION,
                 S3_SECRET_ACCESS_KEY)

s3_client = boto3.client('s3', aws_access_key_id=S3_ACCESS_KEY, aws_secret_access_key=S3_SECRET_ACCESS_KEY, region_name=S3_BUCKET_REGION)

def upload_file_to_s3(file_path):
    file_name = file_path.split('/')[-1]
    s3_client.upload_file(file_path, S3_BUCKET_NAME, file_name)
    return f'https://{S3_BUCKET_NAME}.s3.{S3_BUCKET_REGION}.amazonaws.com/{file_name}'