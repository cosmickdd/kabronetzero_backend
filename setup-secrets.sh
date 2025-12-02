#!/bin/bash
# Create Google Cloud secrets for Kabro NetZero deployment
# Run this script to set up all required secrets in Secret Manager

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Setting up Google Cloud Secrets...${NC}\n"

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID${NC}"
    exit 1
fi

echo "Project ID: $PROJECT_ID"
echo ""

# 1. Create Django SECRET_KEY secret
echo "Creating Django SECRET_KEY secret..."
DJANGO_SECRET=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

echo -n "$DJANGO_SECRET" | gcloud secrets create kabro-netzero-secret-key \
    --data-file=- \
    --replication-policy="automatic" 2>/dev/null || \
echo -n "$DJANGO_SECRET" | gcloud secrets versions add kabro-netzero-secret-key --data-file=-

echo -e "${GREEN}✓ Django SECRET_KEY created${NC}"

# 2. Create MongoDB URI secret
echo "Creating MongoDB URI secret..."
read -p "Enter MongoDB URI (mongodb+srv://...): " MONGODB_URI

if [ -z "$MONGODB_URI" ]; then
    echo -e "${RED}Error: MongoDB URI cannot be empty${NC}"
    exit 1
fi

echo -n "$MONGODB_URI" | gcloud secrets create kabro-netzero-mongodb-uri \
    --data-file=- \
    --replication-policy="automatic" 2>/dev/null || \
echo -n "$MONGODB_URI" | gcloud secrets versions add kabro-netzero-mongodb-uri --data-file=-

echo -e "${GREEN}✓ MongoDB URI created${NC}"

# 3. Create JWT SECRET
echo "Creating JWT SECRET..."
JWT_SECRET=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

echo -n "$JWT_SECRET" | gcloud secrets create kabro-netzero-jwt-secret \
    --data-file=- \
    --replication-policy="automatic" 2>/dev/null || \
echo -n "$JWT_SECRET" | gcloud secrets versions add kabro-netzero-jwt-secret --data-file=-

echo -e "${GREEN}✓ JWT SECRET created${NC}"

# 4. Grant service account access to secrets
echo ""
echo "Granting Cloud Run service account access to secrets..."

SERVICE_ACCOUNT="kabro-netzero-app@${PROJECT_ID}.iam.gserviceaccount.com"

for secret in kabro-netzero-secret-key kabro-netzero-mongodb-uri kabro-netzero-jwt-secret; do
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:${SERVICE_ACCOUNT}" \
        --role="roles/secretmanager.secretAccessor" \
        --quiet 2>/dev/null || true
done

echo -e "${GREEN}✓ Service account permissions granted${NC}"

echo ""
echo -e "${GREEN}All secrets created successfully!${NC}"
echo ""
echo "Secrets:"
gcloud secrets list --filter="name:kabro" --format="table(name,created)"
