import os
import uuid
import pathlib
from typing import Optional
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def create_sheet_dump_directory():
    """
    Create sheet_dump directory if it doesn't exist
    """
    sheet_dump_dir = pathlib.Path(__file__).parent.parent / "sheet_dump"
    sheet_dump_dir.mkdir(exist_ok=True)
    return sheet_dump_dir

async def upload_csv_to_local(file_buffer: bytes, original_name: str) -> str:
    """
    Upload CSV file to local directory
    """
    try:
        # Create sheet_dump directory
        sheet_dump_dir = create_sheet_dump_directory()
        
        # Generate unique filename
        file_ext = pathlib.Path(original_name).suffix
        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = sheet_dump_dir / file_name
        
        # Write file to local directory
        with open(file_path, 'wb') as f:
            f.write(file_buffer)
        
        print(f"File saved locally: {file_path}")
        return str(file_path)
        
    except Exception as e:
        print(f"Local file save error: {e}")
        raise Exception("Failed to save file locally")

async def upload_csv_to_s3(file_buffer: bytes, original_name: str) -> Optional[str]:
    """
    Upload CSV file to S3 (if AWS credentials are configured)
    """
    try:
        # Check if AWS credentials are available
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        aws_bucket = os.getenv("AWS_BUCKET_NAME")
        
        if not all([aws_access_key, aws_secret_key, aws_bucket]):
            print("AWS credentials not configured, skipping S3 upload")
            return None
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # Generate unique filename
        file_ext = pathlib.Path(original_name).suffix
        file_name = f"uploads/csv/{uuid.uuid4()}{file_ext}"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=aws_bucket,
            Key=file_name,
            Body=file_buffer,
            ContentType="text/csv"
        )
        
        # Return S3 URL
        s3_url = f"https://{aws_bucket}.s3.{aws_region}.amazonaws.com/{file_name}"
        print(f"File uploaded to S3: {s3_url}")
        return s3_url
        
    except NoCredentialsError:
        print("AWS credentials not found")
        return None
    except ClientError as e:
        print(f"S3 upload error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during S3 upload: {e}")
        return None 