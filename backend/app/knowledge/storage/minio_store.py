import io
from minio import Minio
from .base import BaseStorage

class MinioStorage(BaseStorage):
    def __init__(self, endpoint="localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False):
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
        self.bucket = "veridex-knowledge"
        
        # In a real app we'd make bucket creation async or do it in startup, but doing it here for simplicity
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except Exception:
            pass # Ignore if Minio is not running during tests

    async def upload(self, object_name: str, data: bytes, content_type: str = "text/plain") -> str:
        self.client.put_object(
            self.bucket, 
            object_name, 
            io.BytesIO(data), 
            length=len(data),
            content_type=content_type
        )
        return f"s3://{self.bucket}/{object_name}"
        
    async def download(self, object_name: str) -> bytes:
        response = self.client.get_object(self.bucket, object_name)
        return response.read()
