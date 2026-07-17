import os
import shutil
from flask import current_app
from app.config import Config

class S3Service:
    def __init__(self):
        self.use_local = Config.USE_LOCAL_STORAGE
        self.local_dir = Config.LOCAL_STORAGE_DIR
        
        # Instantiate boto3 only if we are using S3
        self.s3_client = None
        if not self.use_local:
            try:
                import boto3
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                    region_name=Config.AWS_S3_REGION
                )
            except ImportError:
                print("boto3 is not installed. Defaulting to local storage.")
                self.use_local = True

    def upload_file(self, file_stream, s3_key):
        """
        Uploads a file stream to S3 or saves it to the local uploads directory.
        """
        if self.use_local:
            local_path = os.path.join(self.local_dir, s3_key)
            # Ensure subdirectories exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, 'wb') as f:
                # Handle Werkzeug FileStorage or standard file streams
                if hasattr(file_stream, 'read'):
                    file_stream.seek(0)
                    shutil.copyfileobj(file_stream, f)
                else:
                    f.write(file_stream)
            return s3_key
        else:
            try:
                if hasattr(file_stream, 'seek'):
                    file_stream.seek(0)
                self.s3_client.upload_fileobj(
                    file_stream,
                    Config.AWS_S3_BUCKET_NAME,
                    s3_key
                )
                return s3_key
            except Exception as e:
                print(f"Error uploading to S3: {e}")
                raise e

    def get_file_path(self, s3_key):
        """
        Returns a local path to the file. Downloads it from S3 if necessary.
        """
        local_path = os.path.join(self.local_dir, s3_key)
        
        if self.use_local:
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file {s3_key} does not exist.")
            return local_path
        else:
            # S3 fallback: download it to a temp local file
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            try:
                self.s3_client.download_file(
                    Config.AWS_S3_BUCKET_NAME,
                    s3_key,
                    local_path
                )
                return local_path
            except Exception as e:
                print(f"Error downloading from S3: {e}")
                raise e

    def delete_file(self, s3_key):
        """
        Deletes a file from local storage or S3.
        """
        if self.use_local:
            local_path = os.path.join(self.local_dir, s3_key)
            if os.path.exists(local_path):
                os.remove(local_path)
                return True
        else:
            try:
                self.s3_client.delete_object(
                    Bucket=Config.AWS_S3_BUCKET_NAME,
                    Key=s3_key
                )
                return True
            except Exception as e:
                print(f"Error deleting from S3: {e}")
                return False
        return False

# Export instantiated service
storage_service = S3Service()
