import os
from uuid import uuid4
from dotenv import load_dotenv
import boto3

load_dotenv()

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION'),
)

BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')

def upload_file_to_s3(file_bytes: bytes, file_name: str, folder: str = "uploads"):
    extension = file_name.split('.')[-1]
    unique_file_name = f"{uuid4()}.{extension}"
    s3_key = f"{folder}/{unique_file_name}"

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=file_bytes,
        ContentType=f"image/{extension}"
    )

    image_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    return image_url


def delete_file_from_s3(file_url: str):
    try:
        prefix = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/"
        s3_key = file_url.replace(prefix, "")
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
    except Exception as e:
        raise RuntimeError(f"파일 삭제 실패: {str(e)}")

