#!/usr/bin/env python
"""
Setup Google Cloud Secrets for Kabro NetZero deployment
Run: python setup-secrets.py
"""

import subprocess
import sys
import os
from getpass import getpass

def run_command(cmd, check=True):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return "", str(e), 1

def get_project_id():
    """Get current GCP project ID"""
    stdout, stderr, code = run_command("gcloud config get-value project")
    if code != 0:
        print("❌ Error: Cannot determine GCP project")
        print("   Run: gcloud config set project YOUR_PROJECT_ID")
        sys.exit(1)
    return stdout

def create_django_secret():
    """Create Django SECRET_KEY"""
    print("🔑 Creating Django SECRET_KEY...")
    from django.core.management.utils import get_random_secret_key
    secret = get_random_secret_key()
    
    # Try to create, if exists add version
    cmd = f"echo {secret} | gcloud secrets create kabro-netzero-secret-key --data-file=-"
    stdout, stderr, code = run_command(cmd)
    
    if "already exists" in stderr:
        print("   Secret already exists, adding new version...")
        cmd = f"echo {secret} | gcloud secrets versions add kabro-netzero-secret-key --data-file=-"
        run_command(cmd)
    
    print("✅ Django SECRET_KEY created")
    return secret

def create_mongodb_secret():
    """Create MongoDB URI secret"""
    print("\n🔑 Creating MongoDB URI secret...")
    mongodb_uri = input("Enter MongoDB URI (mongodb+srv://...): ").strip()
    
    if not mongodb_uri:
        print("❌ Error: MongoDB URI cannot be empty")
        sys.exit(1)
    
    # Try to create, if exists add version
    cmd = f'echo "{mongodb_uri}" | gcloud secrets create kabro-netzero-mongodb-uri --data-file=-'
    stdout, stderr, code = run_command(cmd)
    
    if "already exists" in stderr:
        print("   Secret already exists, adding new version...")
        cmd = f'echo "{mongodb_uri}" | gcloud secrets versions add kabro-netzero-mongodb-uri --data-file=-'
        run_command(cmd)
    
    print("✅ MongoDB URI created")
    return mongodb_uri

def create_jwt_secret():
    """Create JWT SECRET"""
    print("\n🔑 Creating JWT SECRET...")
    from django.core.management.utils import get_random_secret_key
    secret = get_random_secret_key()
    
    # Try to create, if exists add version
    cmd = f"echo {secret} | gcloud secrets create kabro-netzero-jwt-secret --data-file=-"
    stdout, stderr, code = run_command(cmd)
    
    if "already exists" in stderr:
        print("   Secret already exists, adding new version...")
        cmd = f"echo {secret} | gcloud secrets versions add kabro-netzero-jwt-secret --data-file=-"
        run_command(cmd)
    
    print("✅ JWT SECRET created")
    return secret

def grant_service_account_access(project_id):
    """Grant service account access to secrets"""
    print("\n🔐 Granting service account access...")
    
    service_account = f"kabro-netzero-app@{project_id}.iam.gserviceaccount.com"
    secrets = [
        "kabro-netzero-secret-key",
        "kabro-netzero-mongodb-uri",
        "kabro-netzero-jwt-secret"
    ]
    
    for secret in secrets:
        cmd = (
            f"gcloud secrets add-iam-policy-binding {secret} "
            f'--member="serviceAccount:{service_account}" '
            f'--role="roles/secretmanager.secretAccessor" '
            f"--quiet"
        )
        run_command(cmd, check=False)
    
    print("✅ Service account permissions granted")

def list_secrets():
    """List created secrets"""
    print("\n📋 Created secrets:")
    cmd = 'gcloud secrets list --filter="name:kabro" --format="table(name,created)"'
    stdout, stderr, code = run_command(cmd)
    print(stdout)

def main():
    """Main setup flow"""
    print("=" * 60)
    print("🚀 Kabro NetZero - Google Cloud Secrets Setup")
    print("=" * 60)
    
    # Get project ID
    project_id = get_project_id()
    print(f"\n✅ Project ID: {project_id}\n")
    
    # Create secrets
    create_django_secret()
    mongodb_uri = create_mongodb_secret()
    create_jwt_secret()
    
    # Grant permissions
    grant_service_account_access(project_id)
    
    # List secrets
    list_secrets()
    
    print("\n" + "=" * 60)
    print("✅ Secrets setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update Cloud Run service with new secrets")
    print("2. Or re-deploy: gcloud run deploy kabro-netzero-api")
    print("3. Monitor logs: gcloud logging read 'resource.type=cloud_run_revision'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
