import aioboto3
from botocore.exceptions import ClientError
from botocore.client import Config
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .base import BaseStorage
from app.core.config import settings

class MinioStorage(BaseStorage):
    def __init__(self):
        self.endpoint = settings.MINIO_ENDPOINT
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.bucket = settings.MINIO_BUCKET
        
        self.session = aioboto3.Session()
        
    def _get_client(self):
        return self.session.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4')
        )

    async def ensure_bucket_exists(self):
        """Creates the bucket if it doesn't already exist."""
        async with self._get_client() as s3:
            try:
                await s3.head_bucket(Bucket=self.bucket)
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code')
                if error_code == '404':
                    try:
                        print(f"Creating MinIO bucket: {self.bucket}")
                        await s3.create_bucket(Bucket=self.bucket)
                    except Exception as ex:
                        print(f"Failed to create bucket: {ex}")
                else:
                    print(f"Error checking bucket: {e}")
            except Exception as e:
                print(f"Failed to connect to MinIO during startup: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def upload(self, object_name: str, data: bytes, content_type: str = "text/plain") -> str:
        """Asynchronously upload bytes to MinIO/S3."""
        async with self._get_client() as s3:
            try:
                await s3.put_object(
                    Bucket=self.bucket,
                    Key=object_name,
                    Body=data,
                    ContentType=content_type
                )
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code')
                if error_code == 'NoSuchBucket':
                    await self.ensure_bucket_exists()
                    # Retry
                    await s3.put_object(
                        Bucket=self.bucket,
                        Key=object_name,
                        Body=data,
                        ContentType=content_type
                    )
                else:
                    raise
            # The returned path mimics standard S3 URIs
            return f"s3://{self.bucket}/{object_name}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(Exception)
    )
    async def download(self, object_name: str) -> bytes:
        """Asynchronously download bytes from MinIO/S3."""
        async with self._get_client() as s3:
            response = await s3.get_object(
                Bucket=self.bucket,
                Key=object_name
            )
            async with response['Body'] as stream:
                return await stream.read()
