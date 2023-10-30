import logging
import boto3
from botocore.exceptions import ClientError
from core.config import settings
from fastapi import UploadFile
from datetime import datetime
import re
import json


bucket_name = settings.AWS_BUCKET_NAME
region = settings.AWS_REGOIN
access_key = settings.AWS_ACCESS_KEY
secret_key = settings.AWS_SECRET_KEY

async def create_bucket():
    s3 = boto3.client('s3', region_name=region,
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
    response = s3.list_buckets()

    buckets = [bucket['Name'] for bucket in response['Buckets']]
    if bucket_name not in buckets:
        try:
            s3_client = boto3.client('s3', region_name=region,
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name)
            bucket_policy = {
                "Version": "2008-10-17",
                "Statement": [
                    {
                        "Sid": "AllowPublicRead",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "*"
                        },
                        "Action": "s3:GetObject",
                        'Resource': f'arn:aws:s3:::{bucket_name}/*'
                    }
                ]
            }
            bucket_policy = json.dumps(bucket_policy)

            s3 = boto3.client('s3', region_name=region,
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
            s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
        except ClientError as e:
            logging.error(e)
            return False
        return True
    return True
        
async def upload_file_to_s3(file: UploadFile, username) -> str:
    s3 = boto3.client('s3', region_name=region,
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
    try:
        name = re.sub(r'\s', '', str(file.filename))
        date = datetime.now().strftime("%Y%m%d-%H-%M-%S")
        file_name = f"{username}/{date}/{name}"
        url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

        s3.upload_fileobj(file.file, bucket_name, file_name)
        return url
    except ClientError as e:
        logging.error(e)
        return False
    return True
