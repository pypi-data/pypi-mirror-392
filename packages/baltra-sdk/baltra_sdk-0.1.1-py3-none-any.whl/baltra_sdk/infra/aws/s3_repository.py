# Python
from __future__ import annotations
import logging
from typing import Optional, Dict
import boto3
from flask import current_app
from baltra_sdk.domain.storage.storage_repository import StorageRepository

class S3Repository(StorageRepository):
    """
    Adapter: S3 implementation of StorageRepository using boto3.
    Uses IAM roles or environment credentials by default.
    """

    def __init__(self, region_name: Optional[str] = None):
        kwargs = {}
        try:
            region = region_name or (current_app.config.get("AWS_REGION") if current_app else None)
        except Exception:
            region = region_name
        if region:
            kwargs["region_name"] = region
        self._s3 = boto3.client("s3", **kwargs)

    def upload_bytes(
        self,
        bucket: str,
        key: str,
        content: bytes,
        content_type: str,
        metadata: Optional[Dict[str, str]] = None,
        server_side_encryption: Optional[str] = "AES256",
    ) -> Optional[str]:
        try:
            put_kwargs = {
                "Bucket": bucket,
                "Key": key,
                "Body": content,
                "ContentType": content_type,
            }
            if server_side_encryption:
                put_kwargs["ServerSideEncryption"] = server_side_encryption
            if metadata:
                put_kwargs["Metadata"] = metadata

            self._s3.put_object(**put_kwargs)
            url = self.generate_public_url(bucket, key)
            logging.info(f"[S3Repository] Uploaded s3://{bucket}/{key}")
            return url
        except Exception as e:
            logging.error(f"[S3Repository] Upload failed s3://{bucket}/{key}: {e}")
            return None

    def delete_object(self, bucket: str, key: str) -> bool:
        try:
            self._s3.delete_object(Bucket=bucket, Key=key)
            logging.info(f"[S3Repository] Deleted s3://{bucket}/{key}")
            return True
        except Exception as e:
            logging.error(f"[S3Repository] Delete failed s3://{bucket}/{key}: {e}")
            return False

    def generate_public_url(self, bucket: str, key: str) -> str:
        # Standard S3 public URL (adjust if you use regional or accelerated endpoints)
        return f"https://{bucket}.s3.amazonaws.com/{key}"

    def generate_presigned_url(self, bucket: str, key: str, expires_in: int = 3600) -> Optional[str]:
        try:
            return self._s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except Exception as e:
            logging.error(f"[S3Repository] Presign failed s3://{bucket}/{key}: {e}")
            return None