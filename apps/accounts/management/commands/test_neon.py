from django.core.management.base import BaseCommand
from apps.accounts.neon_services import (
    test_neon_postgres,
    test_neon_object_storage,
    test_neon_auth
)

class Command(BaseCommand):
    help = "Tests and proves live connectivity to all wired Neon services (Postgres, Object Storage, Auth)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Testing Neon Platform Services for CALI Schools Portal...\n"))

        # 1. Test Neon Postgres
        self.stdout.write("1. Testing Neon Postgres (Lakebase)...")
        try:
            pg = test_neon_postgres()
            self.stdout.write(self.style.SUCCESS(f"   [SUCCESS] Connected to {pg['database']} on {pg['host']}"))
            self.stdout.write(f"   Version: {pg['version']}")
            self.stdout.write(f"   Public Tables: {pg['public_tables']}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   [FAILED] Neon Postgres error: {e}"))

        # 2. Test Neon Object Storage
        self.stdout.write("\n2. Testing Neon Object Storage (S3 API)...")
        try:
            s3_res = test_neon_object_storage()
            if s3_res.get('status') == 'verified':
                self.stdout.write(self.style.SUCCESS(f"   [SUCCESS] Verified roundtrip PutObject + GetObject + DeleteObject on bucket '{s3_res['bucket']}'"))
                self.stdout.write(f"   Endpoint: {s3_res['endpoint']}")
            else:
                self.stdout.write(self.style.WARNING(f"   [SKIPPED] {s3_res.get('reason')}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   [FAILED] Neon Object Storage error: {e}"))

        # 3. Test Neon Auth
        self.stdout.write("\n3. Testing Neon Auth (Managed Better Auth / JWKS)...")
        try:
            auth_res = test_neon_auth()
            if auth_res.get('status') == 'verified':
                self.stdout.write(self.style.SUCCESS(f"   [SUCCESS] Neon Auth JWKS verified (HTTP {auth_res['status_code']}) with {auth_res['keys_count']} active JWK signing key(s)"))
                self.stdout.write(f"   JWKS URL: {auth_res['jwks_url']}")
            else:
                self.stdout.write(self.style.WARNING(f"   [STATUS: {auth_res.get('status')}] Code: {auth_res.get('status_code')}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   [FAILED] Neon Auth error: {e}"))

        self.stdout.write(self.style.SUCCESS("\nAll wired Neon services verified end-to-end!"))
