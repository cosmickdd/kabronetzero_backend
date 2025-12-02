#!/usr/bin/env python
"""
Cloud Run Deployment Troubleshooting & Recovery Script
Diagnoses and fixes common deployment issues
"""

import subprocess
import json
import sys

def run_cmd(cmd):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def check_gcp_project():
    """Check GCP project configuration"""
    print_section("GCP Project Configuration")
    stdout, stderr, code = run_cmd("gcloud config get-value project")
    if code == 0:
        project = stdout
        print(f"✅ Project: {project}")
        return project
    else:
        print("❌ No GCP project configured")
        print("   Run: gcloud config set project YOUR_PROJECT_ID")
        return None

def check_cloud_run_service():
    """Check Cloud Run service status"""
    print_section("Cloud Run Service Status")
    
    cmd = 'gcloud run services describe kabro-netzero-api --region=europe-west1 --format=json'
    stdout, stderr, code = run_cmd(cmd)
    
    if code == 0:
        service = json.loads(stdout)
        url = service.get('status', {}).get('url', 'N/A')
        status = service.get('status', {}).get('conditions', [{}])[0].get('type', 'Unknown')
        print(f"✅ Service found")
        print(f"   URL: {url}")
        print(f"   Status: {status}")
        return url
    else:
        print("❌ Cloud Run service not found")
        return None

def check_secrets():
    """Check if secrets are created"""
    print_section("Secret Manager Secrets")
    
    secrets = [
        "kabro-netzero-secret-key",
        "kabro-netzero-mongodb-uri",
        "kabro-netzero-jwt-secret"
    ]
    
    missing = []
    for secret in secrets:
        cmd = f'gcloud secrets describe {secret} --format="value(name)"'
        stdout, stderr, code = run_cmd(cmd)
        
        if code == 0:
            print(f"✅ {secret}")
        else:
            print(f"❌ {secret} (MISSING)")
            missing.append(secret)
    
    return missing

def check_service_account():
    """Check service account and permissions"""
    print_section("Service Account & Permissions")
    
    stdout, stderr, code = run_cmd("gcloud config get-value project")
    if code != 0:
        print("❌ Cannot determine project")
        return
    
    project = stdout
    sa_email = f"kabro-netzero-app@{project}.iam.gserviceaccount.com"
    
    cmd = f'gcloud iam service-accounts describe {sa_email} --format="value(email)"'
    stdout, stderr, code = run_cmd(cmd)
    
    if code == 0:
        print(f"✅ Service account: {sa_email}")
    else:
        print(f"❌ Service account not found: {sa_email}")
        return
    
    # Check permissions
    roles = [
        "roles/secretmanager.secretAccessor",
        "roles/logging.logWriter",
        "roles/monitoring.metricWriter"
    ]
    
    for role in roles:
        cmd = (
            f'gcloud projects get-iam-policy {project} '
            f'--flatten="bindings[].members" '
            f'--filter="bindings.role:{role} AND bindings.members:{sa_email}" '
            f'--format="value(bindings.role)"'
        )
        stdout, stderr, code = run_cmd(cmd)
        
        if code == 0 and stdout:
            print(f"✅ {role}")
        else:
            print(f"❌ {role} (MISSING)")

def check_logs():
    """Check recent Cloud Run logs"""
    print_section("Recent Logs (Last 20 lines)")
    
    cmd = (
        'gcloud logging read '
        '"resource.type=cloud_run_revision AND resource.labels.service_name=kabro-netzero-api" '
        '--limit=20 '
        '--format=json'
    )
    stdout, stderr, code = run_cmd(cmd)
    
    if code == 0 and stdout:
        try:
            logs = json.loads(stdout)
            for log in logs[-5:]:  # Show last 5
                msg = log.get('textPayload', log.get('jsonPayload', {}).get('message', 'N/A'))
                timestamp = log.get('timestamp', 'N/A')
                print(f"[{timestamp}] {msg}")
        except:
            print(stdout[:500])
    else:
        print("❌ No logs found")

def test_service():
    """Test service health endpoint"""
    print_section("Service Health Test")
    
    cmd = 'gcloud run services describe kabro-netzero-api --region=europe-west1 --format="value(status.url)"'
    stdout, stderr, code = run_cmd(cmd)
    
    if code == 0:
        url = stdout
        print(f"Testing: {url}/health/")
        
        import subprocess
        try:
            result = subprocess.run(
                f"curl -s {url}/health/ -w '\\nStatus: %{{http_code}}'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            print(result.stdout)
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ Cannot determine service URL")

def suggest_fixes(missing_secrets):
    """Suggest fixes based on issues found"""
    print_section("Suggested Fixes")
    
    if missing_secrets:
        print("Missing secrets detected. Run:")
        print(f"  python setup-secrets.py")
        print("\nOr manually create them:")
        print("  MongoDB URI:")
        print("    echo 'your-mongodb-uri' | gcloud secrets create kabro-netzero-mongodb-uri --data-file=-")
        print("  Django Secret Key:")
        print("    python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())' | gcloud secrets create kabro-netzero-secret-key --data-file=-")
    
    print("\nAfter fixing issues:")
    print("  1. Re-deploy: gcloud run deploy kabro-netzero-api --image=...")
    print("  2. Or wait for next push to main (triggers Cloud Build)")
    print("  3. Monitor logs: gcloud logging read 'resource.type=cloud_run_revision'")

def main():
    """Run full diagnostics"""
    print("\n" + "="*60)
    print("🚀 Kabro NetZero - Cloud Run Diagnostics & Recovery")
    print("="*60)
    
    project = check_gcp_project()
    if not project:
        sys.exit(1)
    
    url = check_cloud_run_service()
    missing = check_secrets()
    check_service_account()
    check_logs()
    test_service()
    suggest_fixes(missing)
    
    print("\n" + "="*60)
    if missing:
        print("⚠️  ACTION REQUIRED: Missing secrets detected")
    else:
        print("✅ All checks passed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
