#!/bin/bash
# Kabro NetZero - Google Cloud Run Deployment Setup Script
# This script automates the deployment setup to Google Cloud Run

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found. Install it from: https://cloud.google.com/sdk/docs/install"
    fi
    
    # Check docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Install it from: https://docs.docker.com/get-docker/"
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        log_error "Git not found. Install it from: https://git-scm.com/"
    fi
    
    log_success "All prerequisites installed"
}

# Get user configuration
get_configuration() {
    log_info "Enter your Google Cloud configuration:"
    
    read -p "Project ID (e.g., kabro-netzero-prod): " PROJECT_ID
    read -p "Region (default: us-central1): " REGION
    REGION=${REGION:-us-central1}
    
    read -p "Django SECRET_KEY: " SECRET_KEY
    read -p "MongoDB URI (e.g., mongodb+srv://...): " MONGODB_URI
    read -p "JWT SECRET: " JWT_SECRET
    
    read -p "GitHub Repository Owner: " GITHUB_OWNER
    read -p "GitHub Repository Name: " GITHUB_REPO
    
    # Confirm configuration
    echo ""
    echo -e "${BLUE}Configuration Summary:${NC}"
    echo "Project ID: $PROJECT_ID"
    echo "Region: $REGION"
    echo "GitHub: $GITHUB_OWNER/$GITHUB_REPO"
    echo ""
    read -p "Continue? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Setup cancelled"
    fi
}

# Set up Google Cloud project
setup_gcp_project() {
    log_info "Setting up Google Cloud project..."
    
    # Set project
    gcloud config set project $PROJECT_ID
    
    # Create project if it doesn't exist
    if ! gcloud projects describe $PROJECT_ID &>/dev/null; then
        log_info "Creating Google Cloud project..."
        gcloud projects create $PROJECT_ID --name="Kabro NetZero API" || log_warning "Project creation failed or already exists"
    fi
    
    # Enable APIs
    log_info "Enabling required APIs..."
    gcloud services enable \
        artifactregistry.googleapis.com \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        secretmanager.googleapis.com \
        cloudlogging.googleapis.com \
        monitoring.googleapis.com \
        --project=$PROJECT_ID
    
    log_success "Google Cloud project configured"
}

# Create Artifact Registry repository
create_artifact_registry() {
    log_info "Creating Artifact Registry repository..."
    
    gcloud artifacts repositories create kabro-netzero \
        --repository-format=docker \
        --location=$REGION \
        --description="Kabro NetZero API Docker images" \
        --project=$PROJECT_ID || log_warning "Repository already exists"
    
    log_success "Artifact Registry repository created"
}

# Configure Docker authentication
configure_docker_auth() {
    log_info "Configuring Docker authentication..."
    
    gcloud auth configure-docker $REGION-docker.pkg.dev --quiet
    
    log_success "Docker authentication configured"
}

# Create secrets in Secret Manager
create_secrets() {
    log_info "Creating secrets in Google Secret Manager..."
    
    # Create Django SECRET_KEY
    echo -n "$SECRET_KEY" | gcloud secrets create kabro-netzero-secret-key \
        --data-file=- \
        --replication-policy="automatic" \
        --project=$PROJECT_ID \
        2>/dev/null || gcloud secrets versions add kabro-netzero-secret-key \
        --data-file=<(echo -n "$SECRET_KEY") \
        --project=$PROJECT_ID
    
    # Create MongoDB URI
    echo -n "$MONGODB_URI" | gcloud secrets create kabro-netzero-mongodb-uri \
        --data-file=- \
        --replication-policy="automatic" \
        --project=$PROJECT_ID \
        2>/dev/null || gcloud secrets versions add kabro-netzero-mongodb-uri \
        --data-file=<(echo -n "$MONGODB_URI") \
        --project=$PROJECT_ID
    
    # Create JWT SECRET
    echo -n "$JWT_SECRET" | gcloud secrets create kabro-netzero-jwt-secret \
        --data-file=- \
        --replication-policy="automatic" \
        --project=$PROJECT_ID \
        2>/dev/null || gcloud secrets versions add kabro-netzero-jwt-secret \
        --data-file=<(echo -n "$JWT_SECRET") \
        --project=$PROJECT_ID
    
    log_success "Secrets created in Secret Manager"
}

# Create service account
create_service_account() {
    log_info "Creating service account..."
    
    gcloud iam service-accounts create kabro-netzero-app \
        --display-name="Kabro NetZero API Service Account" \
        --project=$PROJECT_ID \
        2>/dev/null || log_warning "Service account already exists"
    
    # Grant roles
    for role in \
        "roles/secretmanager.secretAccessor" \
        "roles/logging.logWriter" \
        "roles/monitoring.metricWriter" \
        "roles/artifactregistry.reader"
    do
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:kabro-netzero-app@$PROJECT_ID.iam.gserviceaccount.com" \
            --role="$role" \
            --quiet || log_warning "Failed to add $role"
    done
    
    log_success "Service account configured"
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building Docker image..."
    
    docker build \
        -f infrastructure/Dockerfile \
        -t $REGION-docker.pkg.dev/$PROJECT_ID/kabro-netzero/kabro-netzero-api:latest \
        -t $REGION-docker.pkg.dev/$PROJECT_ID/kabro-netzero/kabro-netzero-api:v1.0.0 \
        .
    
    log_success "Docker image built"
    
    log_info "Pushing image to Artifact Registry..."
    docker push $REGION-docker.pkg.dev/$PROJECT_ID/kabro-netzero/kabro-netzero-api:latest
    docker push $REGION-docker.pkg.dev/$PROJECT_ID/kabro-netzero/kabro-netzero-api:v1.0.0
    
    log_success "Docker image pushed to Artifact Registry"
}

# Deploy to Cloud Run
deploy_to_cloud_run() {
    log_info "Deploying to Google Cloud Run..."
    
    gcloud run deploy kabro-netzero-api \
        --image $REGION-docker.pkg.dev/$PROJECT_ID/kabro-netzero/kabro-netzero-api:latest \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 1Gi \
        --cpu 1 \
        --timeout 120 \
        --max-instances 10 \
        --set-env-vars \
            DJANGO_SETTINGS_MODULE=config.settings,\
            DEBUG=False,\
            GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
        --set-secrets \
            SECRET_KEY=kabro-netzero-secret-key:latest,\
            MONGODB_URI=kabro-netzero-mongodb-uri:latest,\
            JWT_SECRET=kabro-netzero-jwt-secret:latest \
        --service-account=kabro-netzero-app@$PROJECT_ID.iam.gserviceaccount.com \
        --project=$PROJECT_ID
    
    log_success "Deployment to Cloud Run completed"
}

# Get service URL
get_service_url() {
    log_info "Retrieving service URL..."
    SERVICE_URL=$(gcloud run services describe kabro-netzero-api \
        --region $REGION \
        --format='value(status.url)' \
        --project=$PROJECT_ID)
    
    echo ""
    echo -e "${GREEN}Service deployed successfully!${NC}"
    echo -e "Service URL: ${BLUE}$SERVICE_URL${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Test the health endpoint: curl $SERVICE_URL/health/"
    echo "2. Update your DNS records to point to: $SERVICE_URL"
    echo "3. View logs: gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=kabro-netzero-api\" --limit 50"
    echo "4. Check metrics: gcloud monitoring dashboards create --config-from-file=/dev/stdin"
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║       Kabro NetZero - Google Cloud Run Deployment        ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_prerequisites
    get_configuration
    setup_gcp_project
    create_artifact_registry
    configure_docker_auth
    create_secrets
    create_service_account
    build_and_push_image
    deploy_to_cloud_run
    get_service_url
    
    log_success "Setup complete!"
}

# Run main
main
