# ⚠️ CLOUD RUN DEPLOYMENT - NEXT STEPS REQUIRED

## Current Status
✅ Service deployed to Google Cloud Run  
✅ Container running successfully  
✅ HTTP requests being received  
⚠️ **Secrets NOT YET CONFIGURED** ← This is the blocker

## What's Happening
The Cloud Run service is deployed but failing because:
1. MongoDB URI secret is not created/set
2. Django SECRET_KEY not in Secret Manager
3. JWT secret not configured
4. Service account may not have permissions to access secrets

## ⚡ Quick Fix (5 minutes)

### Step 1: Set Your Environment Variables
```bash
export PROJECT_ID="utopian-surface-475500"  # Your GCP Project ID
export REGION="europe-west1"
export MONGODB_URI="mongodb+srv://USER:PASSWORD@cluster.mongodb.net/kabronetzero?retryWrites=true"
```

### Step 2: Create Secrets in Google Secret Manager
```bash
# Create Django SECRET_KEY
gcloud secrets create kabro-netzero-secret-key \
  --data-file=- <<< "django-insecure-your-secret-key-here-change-this"

# Create MongoDB URI
gcloud secrets create kabro-netzero-mongodb-uri \
  --data-file=- <<< "$MONGODB_URI"

# Create JWT Secret
gcloud secrets create kabro-netzero-jwt-secret \
  --data-file=- <<< "your-jwt-secret-key-here"
```

### Step 3: Grant Service Account Access
```bash
# Get default Compute Engine service account
SERVICE_ACCOUNT="$(gcloud iam service-accounts list --format='value(email)' | grep "compute@")"

# Grant permissions to access secrets
for secret in kabro-netzero-secret-key kabro-netzero-mongodb-uri kabro-netzero-jwt-secret; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
done
```

### Step 4: Redeploy Service with Secrets
```bash
gcloud run deploy kabronetzero \
  --image=${REGION}-docker.pkg.dev/$PROJECT_ID/kabro-netzero/kabro-netzero-api:latest \
  --region=$REGION \
  --set-secrets=SECRET_KEY=kabro-netzero-secret-key:latest,MONGODB_URI=kabro-netzero-mongodb-uri:latest,JWT_SECRET=kabro-netzero-jwt-secret:latest \
  --memory=1Gi \
  --cpu=1 \
  --timeout=120 \
  --max-instances=10
```

### Step 5: Verify Deployment
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe kabronetzero --region=$REGION --format='value(status.url)')
echo "Service URL: $SERVICE_URL"

# Test health endpoint
curl $SERVICE_URL/health/

# Expected response: {"status": "healthy", "service": "kabro-netzero-api"}
```

## 📋 Detailed Troubleshooting

See `CLOUD_RUN_TROUBLESHOOTING.md` for:
- MongoDB connection issues
- Secret Manager configuration
- Permission denied errors
- Database unreachable errors
- Network/firewall issues

## 🔑 Key Points

**Secrets Required**:
- `SECRET_KEY`: Django secret key (minimum 50 chars, random)
- `MONGODB_URI`: Full MongoDB connection string
- `JWT_SECRET`: JWT signing secret

**MongoDB Connection String Format**:
```
mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/DATABASE?retryWrites=true&w=majority
```

**If using MongoDB Atlas**:
1. Get connection string from Atlas dashboard
2. Add Cloud Run IP to firewall (or allow 0.0.0.0/0 for testing)
3. Test connection locally first before deploying

## 🚀 After Secrets are Set

1. Service should start responding to requests
2. Health check: `GET /health/` → 200 OK
3. API endpoints: `GET /api/v1/` → Should be accessible
4. Check logs if still failing:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=kabronetzero" --limit=50
   ```

## 📞 Still Having Issues?

1. Check Secret Manager secrets are created:
   ```bash
   gcloud secrets list
   ```

2. Verify service account has permissions:
   ```bash
   gcloud secrets get-iam-policy kabro-netzero-secret-key
   ```

3. View full deployment logs:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision" --limit=100 --format=json
   ```

4. Test container locally:
   ```bash
   docker run -p 8000:8000 --env-file .env europe-west1-docker.pkg.dev/$PROJECT_ID/kabro-netzero/kabro-netzero-api:latest
   ```

---

**Status**: ✅ All code deployed, ⚠️ Secrets need to be configured
**Next Action**: Run the Quick Fix steps above
