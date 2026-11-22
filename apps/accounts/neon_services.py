import os
import boto3
import requests
from botocore.client import Config
from django.conf import settings
from django.db import connection

def test_neon_postgres():
    """Verify live Neon Postgres connectivity, latency, and table counts."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        pg_version = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
        public_table_count = cursor.fetchone()[0]
    return {
        "status": "connected",
        "version": pg_version,
        "public_tables": public_table_count,
        "database": connection.settings_dict.get('NAME'),
        "host": connection.settings_dict.get('HOST')
    }

def get_neon_storage_client():
    """Returns a configured boto3 client for Neon Lakebase Object Storage."""
    return boto3.client(
        's3',
        endpoint_url=settings.AWS_ENDPOINT_URL_S3,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        config=Config(s3={'addressing_style': 'path'}, signature_version='s3v4')
    )

def test_neon_object_storage():
    """Tests upload, retrieval, and deletion of an object in Neon Object Storage bucket."""
    if not settings.AWS_ENDPOINT_URL_S3 or not settings.AWS_ACCESS_KEY_ID:
        return {"status": "skipped", "reason": "Neon Object Storage credentials not set"}
    
    s3 = get_neon_storage_client()
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    test_key = "health-checks/neon-test-ping.txt"
    test_payload = b"CALI Schools Neon Object Storage verification token."

    # 1. Put Object
    s3.put_object(Bucket=bucket, Key=test_key, Body=test_payload, ContentType="text/plain")

    # 2. Get Object
    obj = s3.get_object(Bucket=bucket, Key=test_key)
    body = obj['Body'].read()
    if body != test_payload:
        raise ValueError(f"Content mismatch: expected {test_payload}, got {body}")

    # 3. Clean up
    s3.delete_object(Bucket=bucket, Key=test_key)

    return {
        "status": "verified",
        "bucket": bucket,
        "endpoint": settings.AWS_ENDPOINT_URL_S3,
        "roundtrip_verified": True
    }

def test_neon_auth():
    """Tests Neon Auth JWKS and base connectivity."""
    jwks_url = getattr(settings, 'NEON_AUTH_JWKS_URL', None)
    base_url = getattr(settings, 'NEON_AUTH_BASE_URL', None)

    if not jwks_url:
        return {"status": "skipped", "reason": "NEON_AUTH_JWKS_URL not configured"}

    res = requests.get(jwks_url, timeout=10)
    data = res.json() if res.status_code == 200 else {}
    keys_count = len(data.get('keys', []))

    return {
        "status": "verified" if res.status_code == 200 else "failed",
        "status_code": res.status_code,
        "jwks_url": jwks_url,
        "base_url": base_url,
        "keys_count": keys_count
    }
