import boto3
import pytest
from moto import mock_s3
from utils.s3 import upload_file_to_s3, create_bucket
from fastapi import UploadFile 
from core.config import settings


@pytest.fixture
def s3():
    with mock_s3():
        yield boto3.client('s3')

bucket_name = settings.AWS_BUCKET_NAME

async def test_create_bucket(s3):
    result = await create_bucket()

    assert result is True

    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]

    assert bucket_name in buckets

    bucket_policy = s3.get_bucket_policy(Bucket=bucket_name)

    assert 'AllowPublicRead' in bucket_policy['Policy']
    assert 's3:GetObject' in bucket_policy['Policy']

async def test_upload_file_to_s3(s3):
    s3.create_bucket(Bucket=bucket_name)    
    sample_image_content = b'Simulated image content'
    sample_image = UploadFile(filename="sample.jpg")
    result = await upload_file_to_s3(sample_image, 'your-username')

    assert result is not None
    
    response = s3.list_objects(Bucket=bucket_name)
    assert 'your-username' in response['Contents'][0]['Key']


