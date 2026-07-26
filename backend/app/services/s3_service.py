import os
import shutil

from app.core.config import settings


class S3Service:
    def __init__(self):
        self.use_local = settings.USE_LOCAL_STORAGE
        self.local_dir = settings.LOCAL_STORAGE_DIR
        self.provider = os.environ.get(
            "STORAGE_PROVIDER", "aws_s3" if not self.use_local else "local"
        ).lower()

        self.s3_client = None
        if not self.use_local:
            try:
                import boto3

                client_kwargs = {
                    "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
                    "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
                    "region_name": settings.AWS_S3_REGION,
                }
                custom_endpoint = os.environ.get("S3_ENDPOINT_URL")
                if custom_endpoint:
                    client_kwargs["endpoint_url"] = custom_endpoint

                self.s3_client = boto3.client("s3", **client_kwargs)
            except Exception as e:
                print(
                    f"Could not initialize S3/MinIO client ({e}). Defaulting to local storage."
                )
                self.use_local = True

    def is_connected(self):
        if self.use_local:
            return True
        if self.s3_client:
            try:
                self.s3_client.list_buckets()
                return True
            except Exception:
                return False
        return False

    def upload_file(self, file_stream, s3_key):
        """Uploads a file stream to S3/MinIO or local storage."""
        if self.use_local:
            local_path = os.path.join(self.local_dir, s3_key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            with open(local_path, "wb") as f:
                if hasattr(file_stream, "read"):
                    file_stream.seek(0)
                    shutil.copyfileobj(file_stream, f)
                else:
                    f.write(file_stream)
            return s3_key
        else:
            try:
                if hasattr(file_stream, "seek"):
                    file_stream.seek(0)
                self.s3_client.upload_fileobj(
                    file_stream, settings.AWS_S3_BUCKET_NAME, s3_key
                )
                return s3_key
            except Exception as e:
                print(f"Error uploading to object storage: {e}")
                raise e

    def get_file_path(self, s3_key):
        """Returns local filesystem path. Downloads from object storage if necessary."""
        local_path = os.path.join(self.local_dir, s3_key)

        if self.use_local:
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file {s3_key} does not exist.")
            return local_path
        else:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            try:
                self.s3_client.download_file(
                    settings.AWS_S3_BUCKET_NAME, s3_key, local_path
                )
                return local_path
            except Exception as e:
                print(f"Error downloading from object storage: {e}")
                raise e

    def get_download_url(self, s3_key, expires_in=3600):
        """Generates pre-signed download URL or local download path."""
        if self.use_local or not self.s3_client:
            return f"/api/contracts/download/{s3_key}"
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_S3_BUCKET_NAME, "Key": s3_key},
                ExpiresIn=expires_in,
            )
            return url
        except Exception:
            return f"/api/contracts/download/{s3_key}"

    def delete_file(self, s3_key):
        """Deletes file from storage."""
        if self.use_local:
            local_path = os.path.join(self.local_dir, s3_key)
            if os.path.exists(local_path):
                os.remove(local_path)
                return True
        else:
            try:
                self.s3_client.delete_object(
                    Bucket=settings.AWS_S3_BUCKET_NAME, Key=s3_key
                )
                return True
            except Exception as e:
                print(f"Error deleting from object storage: {e}")
                return False
        return False


s3_service = S3Service()

# Export instantiated service
storage_service = S3Service()
