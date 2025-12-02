#!/bin/bash
# Cloud Run deployment script
# This is used by cloudbuild.yaml for deployment

set -e

PROJECT_ID=$1
IMAGE=$2
REGION=${3:-us-central1}
SERVICE_NAME="kabro-netzero-api"

echo "Deploying to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Image: $IMAGE"
echo "Region: $REGION"

gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE \
  --platform managed \
  --region=$REGION \
  --memory=1Gi \
  --cpu=1 \
  --timeout=120 \
  --max-instances=10 \
  --min-instances=1 \
  --allow-unauthenticated \
  --set-env-vars=DJANGO_SETTINGS_MODULE=config.settings,DEBUG=False,GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
  --set-secrets=SECRET_KEY=kabro-netzero-secret-key:latest,MONGODB_URI=kabro-netzero-mongodb-uri:latest,JWT_SECRET=kabro-netzero-jwt-secret:latest \
  --project=$PROJECT_ID

echo "Deployment complete!"
