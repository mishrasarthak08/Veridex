import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge.storage.minio_store import MinioStorage

async def main():
    print("1. Initializing MinIO Storage Client (aioboto3)...")
    storage = MinioStorage()
    
    print(f"2. Ensuring bucket '{storage.bucket}' exists at endpoint {storage.endpoint}...")
    await storage.ensure_bucket_exists()
    
    test_object_name = "test/verification_doc.txt"
    test_content = b"This is a test document to verify the MinIO async upload and download pipeline."
    
    print(f"3. Uploading test document '{test_object_name}'...")
    try:
        s3_uri = await storage.upload(test_object_name, test_content, content_type="text/plain")
        print(f"   -> Successfully uploaded! URI: {s3_uri}")
    except Exception as e:
        print(f"   -> FAILED to upload: {e}")
        sys.exit(1)
        
    print(f"4. Downloading test document from MinIO...")
    try:
        downloaded_content = await storage.download(test_object_name)
        if downloaded_content == test_content:
            print(f"   -> Successfully downloaded and verified content match!")
            print("\nSUCCESS: The MinIO integration is fully operational and asynchronous.")
        else:
            print(f"   -> FAILED: Downloaded content does not match uploaded content.")
    except Exception as e:
        print(f"   -> FAILED to download: {e}")

if __name__ == "__main__":
    asyncio.run(main())
