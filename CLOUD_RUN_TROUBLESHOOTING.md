# Cloud Run Deployment Troubleshooting Guide

## Current Status
✅ Cloud Run service deployed successfully
✅ Container is running
✅ HTTP requests are being received
❌ Application likely failing to connect to MongoDB

## Diagnostic Steps

### 1. Check Secret Manager Secrets

The deployment is failing because the secrets are not configured. Run these commands:

```bash
# Check if secrets exist
gcloud secrets list

# You should see:
# - kabro-netzero-secret-key
# - kabro-netzero-mongodb-uri
# - kabro-netzero-jwt-secret

# If they don't exist, create them:
echo "your-django-secret-key" | gcloud secrets create kabro-netzero-secret-key --data-file=-
echo "mongodb+srv://user:password@cluster.mongodb.net/kabronetzero?retryWrites=true" | gcloud secrets create kabro-netzero-mongodb-uri --data-file=-
echo "your-jwt-secret" | gcloud secrets create kabro-netzero-jwt-secret --data-file=-
```

### 2. Verify Service Account Permissions

```bash
# Get current service account
gcloud iam service-accounts list

# Grant Secret Manager access
gcloud secrets add-iam-policy-binding kabro-netzero-secret-key \
  --member="serviceAccount:YOUR-SERVICE-ACCOUNT@PROJECT-ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding kabro-netzero-mongodb-uri \
  --member="serviceAccount:YOUR-SERVICE-ACCOUNT@PROJECT-ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding kabro-netzero-jwt-secret \
  --member="serviceAccount:YOUR-SERVICE-ACCOUNT@PROJECT-ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 3. Check Cloud Run Service Configuration

```bash
# View current service configuration
gcloud run services describe kabronetzero --region=europe-west1

# Check if secrets are properly mounted:
# Look for "secretEnvironmentVariables" section
# Should show:
# - SECRET_KEY
# - MONGODB_URI
# - JWT_SECRET
```

### 4. View Application Logs

```bash
# See full logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=kabronetzero" --limit=100 --format=json

# Or use Cloud Run console:
# Cloud Run → kabronetzero service → Logs tab
```

### 5. Common Issues & Solutions

#### Issue: "Secret not found"
```
Solution: Create the secrets using commands in Step 1
```

#### Issue: "Permission denied accessing secret"
```
Solution: Grant service account permissions using commands in Step 2
```

#### Issue: "MongoDB connection refused"
```
Solution: 
- Verify MONGODB_URI is correct
- Add Cloud Run IP to MongoDB Atlas firewall (if using Atlas)
- Check MongoDB credentials are correct
```

#### Issue: "Timeout connecting to database"
```
Solution:
- Cloud Run needs to be in same VPC as MongoDB (use VPC connector)
- Or allow public internet access from Cloud Run IP
```

## Quick Fix Steps

### Step 1: Create Secrets
```bash
# Replace with your actual values
gcloud secrets create kabro-netzero-secret-key --data-file=- <<< "your-django-secret-key-here"
gcloud secrets create kabro-netzero-mongodb-uri --data-file=- <<< "mongodb+srv://user:password@cluster.mongodb.net/kabronetzero"
gcloud secrets create kabro-netzero-jwt-secret --data-file=- <<< "your-jwt-secret-here"
```

### Step 2: Get Project ID and Service Account
```bash
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT="$(gcloud iam service-accounts list --format='value(email)' --filter='displayName:Cloud Run' | head -n1)"

echo "Project: $PROJECT_ID"
echo "Service Account: $SERVICE_ACCOUNT"
```

### Step 3: Grant Permissions
```bash
for secret in kabro-netzero-secret-key kabro-netzero-mongodb-uri kabro-netzero-jwt-secret; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --quiet
done
```

### Step 4: Redeploy Service
```bash
gcloud run deploy kabronetzero \
  --image=europe-west1-docker.pkg.dev/$PROJECT_ID/kabro-netzero/kabro-netzero-api:latest \
  --region=europe-west1 \
  --set-secrets=SECRET_KEY=kabro-netzero-secret-key:latest,MONGODB_URI=kabro-netzero-mongodb-uri:latest,JWT_SECRET=kabro-netzero-jwt-secret:latest
```

### Step 5: Verify Deployment
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe kabronetzero --region=europe-west1 --format='value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health/

# Test API
curl $SERVICE_URL/api/v1/
```

## Monitoring & Debugging

### View Real-time Logs
```bash
gcloud logging read "resource.type=cloud_run_revision" --follow --limit=50
```

### Check Service Metrics
```bash
# Cloud Run console → kabronetzero → Metrics tab
# Look for:
# - Request count
# - Request latency
# - Error count
# - CPU/Memory usage
```

### Test Database Connection Locally
```bash
# In your local environment
python manage.py shell

from django.db import connection
connection.cursor()  # Will fail if DB unreachable
```

## MongoDB Atlas Specific Setup

If using MongoDB Atlas (recommended):

### 1. Get Connection String
```
https://cloud.mongodb.com → Cluster → Connect → Python 3.6+
Copy the connection string
```

### 2. Add Cloud Run IP to Firewall
```
MongoDB Atlas → Network Access → Add IP Address
- Add 0.0.0.0/0 (NOT recommended for production)
- Or: Add specific Cloud Run IP range (better)

For Google Cloud Run:
- Region: europe-west1
- IP: Check Cloud Run documentation for region IPs
```

### 3. Update Secret
```bash
gcloud secrets versions add kabro-netzero-mongodb-uri \
  --data-file=- <<< "mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/kabronetzero?retryWrites=true&w=majority"
```

## Testing After Fix

```bash
# Test health check
curl https://kabronetzero-XXXXX.europe-west1.run.app/health/

# Expected response: 200 OK with JSON

# Test API endpoints
curl https://kabronetzero-XXXXX.europe-west1.run.app/api/v1/

# Check logs for errors
gcloud logging read "resource.type=cloud_run_revision AND severity=ERROR" --limit=10
```

## Still Having Issues?

1. Check Cloud Run logs in the console
2. Verify all environment variables are set: 
   ```bash
   gcloud run services describe kabronetzero --region=europe-west1
   ```
3. Rebuild the container locally to test:
   ```bash
   docker build -f infrastructure/Dockerfile -t test-image .
   docker run -p 8000:8000 --env-file .env test-image
   ```
4. Check MongoDB connection string in .env.example vs actual

## Additional Resources

- Cloud Run Troubleshooting: https://cloud.google.com/run/docs/troubleshooting
- Secret Manager: https://cloud.google.com/secret-manager/docs
- MongoDB Atlas: https://docs.atlas.mongodb.com/
- Django-MongoEngine: https://docs.mongoengine.org/
