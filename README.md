README.md
# Kabro NetZero Backend

A production-grade Django REST Framework backend for a unified carbon credits infrastructure platform serving India and global markets.

## Project Overview

**Kabro NetZero** is a comprehensive platform for managing carbon credits throughout their complete lifecycle:
- **Project Registration**: Carbon project creation and methodology validation
- **Data Intake**: IoT/satellite/manual data collection and aggregation  
- **MRV (Measurement, Reporting & Verification)**: Validator assessments and quality checks
- **Carbon Registry**: Credit batch issuance and transaction tracking
- **Tokenization**: Blockchain integration for digital carbon credits
- **Marketplace**: Buy/sell platform for carbon credits
- **Retirement**: Credit retirement with public certificates
- **ESG Reporting**: Environmental/Social/Governance sustainability reporting

## Technology Stack

- **Framework**: Django 5.0+ with Django REST Framework 3.14
- **Database**: MongoDB with MongoEngine 0.29 ODM
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API**: RESTful with versioning (`/api/v1/`), pagination, filtering, ordering
- **Authorization**: Role-Based Access Control (RBAC) with 7 user roles
- **Python**: 3.11+

## User Roles

1. **ADMIN** - Full system access
2. **ORG_OWNER** - Organization owner with full permissions
3. **ORG_MEMBER** - Basic organization member
4. **VALIDATOR** - MRV review and approval authority
5. **REGULATOR** - Registry oversight and locking authority
6. **BUYER** - Marketplace buyer access
7. **DEVELOPER** - API key and webhook management

## Project Structure

```
kabronetzero_backend/
│
├── 📂 apps/                       # All Django applications
│   ├── accounts/                  # User authentication & profiles
│   │   ├── models.py             # UserProfile, APIKey, AuditLog
│   │   ├── views.py              # Authentication ViewSets
│   │   ├── serializers.py        # User serializers
│   │   ├── urls.py               # Authentication routes
│   │   └── apps.py
│   │
│   ├── organizations/             # Multi-tenant organization support
│   │   ├── models.py             # Organization, Membership, Location
│   │   ├── views.py              # Organization ViewSets
│   │   ├── serializers.py        # Organization serializers
│   │   └── urls.py               # Organization routes
│   │
│   ├── projects/                  # Carbon project management
│   │   ├── models.py             # Project, CarbonCategory, Methodology
│   │   ├── views.py              # Project ViewSets
│   │   ├── serializers.py        # Project serializers
│   │   ├── urls.py               # Project routes
│   │   ├── management/           # Django management commands
│   │   │   └── commands/
│   │   │       └── seed_carbon_categories.py
│   │   └── apps.py
│   │
│   ├── data_intake/              # Data collection & aggregation
│   │   ├── models.py             # DataSource, DataPoint, DataAggregation
│   │   ├── views.py              # Data ViewSets
│   │   ├── serializers.py        # Data serializers
│   │   ├── urls.py               # Data routes
│   │   └── apps.py
│   │
│   ├── mrv/                      # Measurement, Reporting & Verification
│   │   ├── models.py             # MRVRequest, MRVAssessment
│   │   ├── views.py              # MRV ViewSets
│   │   ├── serializers.py        # MRV serializers
│   │   ├── urls.py               # MRV routes
│   │   └── apps.py
│   │
│   ├── registry/                 # Carbon credit registry
│   │   ├── models.py             # CreditBatch, TransactionLog
│   │   ├── views.py              # Registry ViewSets
│   │   ├── serializers.py        # Registry serializers
│   │   ├── urls.py               # Registry routes
│   │   └── apps.py
│   │
│   ├── tokenization/             # Blockchain tokenization
│   │   ├── models.py             # TokenizationJob, TokenizationEvent
│   │   ├── views.py              # Tokenization ViewSets
│   │   ├── serializers.py        # Tokenization serializers
│   │   ├── urls.py               # Tokenization routes
│   │   └── apps.py
│   │
│   ├── marketplace/              # Carbon credit marketplace
│   │   ├── models.py             # Listing, Order, TradeHistory
│   │   ├── views.py              # Marketplace ViewSets
│   │   ├── serializers.py        # Marketplace serializers
│   │   ├── urls.py               # Marketplace routes
│   │   └── apps.py
│   │
│   ├── retirement/               # Credit retirement & certificates
│   │   ├── models.py             # RetirementRecord, RetirementCertificate
│   │   ├── views.py              # Retirement ViewSets
│   │   ├── serializers.py        # Retirement serializers
│   │   ├── urls.py               # Retirement routes
│   │   └── apps.py
│   │
│   ├── esg/                      # ESG reporting
│   │   ├── models.py             # EmissionInventory, ESGReport, ESGGoal
│   │   ├── views.py              # ESG ViewSets
│   │   ├── serializers.py        # ESG serializers
│   │   ├── urls.py               # ESG routes
│   │   └── apps.py
│   │
│   └── api/                      # API utilities & permissions
│       ├── permissions.py        # 7 custom DRF permission classes
│       ├── exceptions.py         # Custom exception handler
│       └── apps.py
│
├── 📂 config/                     # Django configuration
│   ├── settings.py               # Main settings with MongoDB config
│   ├── urls.py                   # Main URL router
│   ├── wsgi.py                   # WSGI configuration for deployment
│   ├── asgi.py                   # ASGI configuration
│   └── __init__.py
│
├── 📂 docs/                       # Documentation & references
│   ├── QUICKSTART.md             # Quick start guide
│   ├── API_DOCUMENTATION.md      # API reference
│   ├── DEPLOYMENT.md             # Deployment guide
│   ├── DEVELOPER_CHECKLIST.md    # Developer workflow
│   ├── ARCHITECTURE.md           # System architecture
│   ├── INDEX.md                  # Documentation index
│   ├── PROJECT_SUMMARY.md        # Project overview
│   ├── REORGANIZATION_SUMMARY.md # This reorganization
│   ├── audit/                    # Audit & analysis reports
│   │   ├── ARCHITECTURE_ALIGNMENT_ANALYSIS.md
│   │   ├── COMPLETE_CHECKLIST.md
│   │   ├── STRUCTURE_AUDIT_REPORT.md
│   │   ├── STRUCTURE_FIX_SUMMARY.md
│   │   └── STRUCTURE_VERIFICATION_REPORT.md
│   └── references/               # Reference implementations
│       ├── models_complete.py
│       ├── serializers_complete.py
│       └── viewsets_complete.py
│
├── 📂 infrastructure/             # Docker & deployment
│   ├── Dockerfile                # Container build instructions
│   ├── docker-compose.yml        # Multi-container orchestration
│   └── .dockerignore             # Docker build ignore rules
│
├── 📂 tests/                      # Test suite
│   ├── test_complete.py          # Comprehensive test suite (45+ tests)
│   └── __init__.py
│
├── manage.py                      # Django CLI
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── README.md                      # Main project documentation
└── FOLDER_STRUCTURE_ANALYSIS.md  # Structure analysis reference
```

## 11 Django Apps

| App | Purpose | Models |
|-----|---------|--------|
| **accounts** | User auth, profiles, API keys | UserProfile, APIKey, PasswordReset, AuditLog |
| **organizations** | Multi-tenant orgs, memberships | Organization, OrganizationMembership, Location |
| **projects** | Carbon projects, categories | Project, CarbonCategory, ProjectMethodology |
| **data_intake** | Data collection, aggregation | DataSource, DataPoint, DataAggregation |
| **mrv** | MRV workflows, assessments | MRVRequest, MRVAssessment, MRVAuditLog |
| **registry** | Carbon credit registry | CreditBatch, CreditTransactionLog |
| **tokenization** | Blockchain integration | TokenizationJob, TokenizationEvent |
| **marketplace** | Buy/sell platform | Listing, Order, TradeHistory |
| **retirement** | Credit retirement | RetirementRecord, RetirementCertificate |
| **esg** | Sustainability reporting | EmissionInventory, ESGReport, ESGGoal |
| **api** | API utilities | Permissions, Exception handlers |

## Installation & Setup

### 1. Prerequisites
- Python 3.11+
- MongoDB 5.0+ (local or Atlas)
- pip or conda

### 2. Clone & Install

```bash
cd kabronetzero_backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Configuration

Create `.env` file from template:

```bash
cp .env.example .env
```

Configure your environment variables:

```
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# MongoDB
DATABASE_URI=mongodb+srv://user:password@cluster.mongodb.net/kabronetzero?retryWrites=true&w=majority

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Blockchain Service (optional)
BLOCKCHAIN_SERVICE_URL=https://api.blockchain-service.com

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4. Initialize Database

Seed carbon categories:

```bash
python manage.py seed_carbon_categories
```

### 5. Run Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

Server runs at: `http://localhost:8000`

API available at: `http://localhost:8000/api/v1/`

## API Endpoints

### Authentication
```
POST   /auth/token/           - Get JWT access token
POST   /auth/token/refresh/   - Refresh access token
POST   /api/v1/accounts/register/  - Register new user
POST   /api/v1/accounts/login/     - User login
```

### Accounts
```
GET    /api/v1/accounts/me/          - Current user profile
PUT    /api/v1/accounts/me/          - Update profile
GET    /api/v1/accounts/audit-logs/  - Audit trail
```

### Organizations
```
GET    /api/v1/organizations/                    - List organizations
POST   /api/v1/organizations/                    - Create organization
GET    /api/v1/organizations/{id}/               - Organization details
POST   /api/v1/organizations/{id}/add_member/    - Add member
GET    /api/v1/organizations/{id}/members/      - List members
POST   /api/v1/organizations/invitations/        - Send invitation
POST   /api/v1/organizations/invitations/{id}/accept/  - Accept invitation
```

### Projects
```
GET    /api/v1/projects/categories/              - List carbon categories
GET    /api/v1/projects/projects/                - List projects
POST   /api/v1/projects/projects/                - Create project
GET    /api/v1/projects/projects/{id}/           - Project details
POST   /api/v1/projects/projects/{id}/submit_mrv/  - Submit for MRV
GET    /api/v1/projects/projects/{id}/mrv_status/  - MRV status
```

### Data Intake
```
GET    /api/v1/data-intake/sources/     - List data sources
POST   /api/v1/data-intake/sources/     - Create data source
POST   /api/v1/data-intake/points/      - Log data point
GET    /api/v1/data-intake/aggregations/ - Get data aggregations
```

### MRV
```
GET    /api/v1/mrv/requests/                  - List MRV requests
POST   /api/v1/mrv/requests/                  - Create MRV request
GET    /api/v1/mrv/assessments/               - List assessments
POST   /api/v1/mrv/assessments/               - Create assessment
POST   /api/v1/mrv/assessments/{id}/approve/  - Approve MRV
POST   /api/v1/mrv/assessments/{id}/reject/   - Reject MRV
```

### Registry
```
GET    /api/v1/registry/batches/           - List credit batches
POST   /api/v1/registry/batches/           - Create batch
GET    /api/v1/registry/batches/{id}/credits/  - Get batch credits
POST   /api/v1/registry/batches/{id}/lock/     - Lock batch (regulator only)
GET    /api/v1/registry/transactions/      - Transaction history
```

### Tokenization
```
GET    /api/v1/tokenization/jobs/         - List jobs
POST   /api/v1/tokenization/jobs/         - Create tokenization job
GET    /api/v1/tokenization/jobs/{id}/status/  - Job status
POST   /api/v1/tokenization/jobs/{id}/retry/   - Retry failed job
```

### Marketplace
```
GET    /api/v1/marketplace/listings/           - List credit listings
POST   /api/v1/marketplace/listings/           - Create listing
GET    /api/v1/marketplace/orders/             - List orders
POST   /api/v1/marketplace/orders/             - Create order
POST   /api/v1/marketplace/orders/{id}/confirm_payment/  - Confirm payment
```

### Retirement
```
GET    /api/v1/retirement/records/                          - List retirements
POST   /api/v1/retirement/records/                          - Create retirement
GET    /api/v1/retirement/records/public_certificate/      - Get certificate (public)
```

### ESG
```
GET    /api/v1/esg/inventory/           - List emission inventories
POST   /api/v1/esg/inventory/           - Create inventory
GET    /api/v1/esg/reports/             - List ESG reports
POST   /api/v1/esg/reports/generate_report/  - Generate report
```

## Authentication

All endpoints (except public certificate) require JWT Bearer token:

```bash
# 1. Get token
curl -X POST http://localhost:8000/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Response: {"access": "eyJ0...", "refresh": "eyJ0..."}

# 2. Use token in requests
curl -H "Authorization: Bearer eyJ0..." \
  http://localhost:8000/api/v1/projects/projects/
```

## Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test tests.test_complete

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Development

### Add a New Endpoint

1. Define the MongoEngine Document in `app/models.py`
2. Create DRF serializer in `app/serializers.py`
3. Implement ViewSet in `app/views.py`
4. Register in `app/urls.py` with router
5. Add tests in `tests/test_complete.py`

### Use Management Command

```bash
# List available commands
python manage.py help

# Create your own command
touch projects/management/commands/your_command.py
```

### Database Queries

```python
from projects.models import Project

# Get all projects
projects = Project.objects()

# Filter by organization
projects = Project.objects(organization=org_id)

# Complex query
projects = Project.objects(
    status='ACTIVE',
    carbon_category__code='GREEN'
).order_by('-created_at')[:10]

# Update
project.status = 'APPROVED'
project.save()

# Delete
project.delete()
```

## Deployment

### Docker
```bash
docker build -t kabronetzero-backend -f infrastructure/Dockerfile .
docker run -p 8000:8000 --env-file .env kabronetzero-backend
```

### Docker Compose
```bash
cd infrastructure
docker-compose up -d
```

### Gunicorn
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Google Cloud Run

**Quick Start** (Automated):
```bash
# Run the deployment script
bash deploy-gcp.sh
# Follow interactive prompts to configure and deploy
```

**Manual Deployment**:

1. **Set up Google Cloud Project**
   ```bash
   export PROJECT_ID="your-project-id"
   export REGION="us-central1"
   
   gcloud config set project $PROJECT_ID
   gcloud services enable artifactregistry.googleapis.com cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com
   ```

2. **Create Artifact Registry Repository**
   ```bash
   gcloud artifacts repositories create kabro-netzero \
     --repository-format=docker \
     --location=$REGION
   ```

3. **Build & Push Docker Image**
   ```bash
   docker build -f infrastructure/Dockerfile -t $REGION-docker.pkg.dev/$PROJECT_ID/kabro-netzero/kabro-netzero-api:latest .
   docker push $REGION-docker.pkg.dev/$PROJECT_ID/kabro-netzero/kabro-netzero-api:latest
   ```

4. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy kabro-netzero-api \
     --image $REGION-docker.pkg.dev/$PROJECT_ID/kabro-netzero/kabro-netzero-api:latest \
     --platform managed \
     --region $REGION \
     --memory 1Gi \
     --cpu 1
   ```

For detailed setup, see [GOOGLE_CLOUD_DEPLOYMENT.md](GOOGLE_CLOUD_DEPLOYMENT.md)

### CI/CD Pipeline (GitHub Actions + Cloud Build)

The project includes GitHub Actions workflows for:
- Automated testing on push/PR
- Docker image building and pushing
- Automated deployment to Cloud Run
- Security scanning with Trivy

Configure GitHub Actions secrets:
```
GCP_PROJECT_ID          - Google Cloud Project ID
WIF_PROVIDER            - Workload Identity Provider
WIF_SERVICE_ACCOUNT     - Service Account Email
```

### Production Checklist
- [ ] Set `DEBUG=False` in `.env`
- [ ] Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure production database (MongoDB Atlas)
- [ ] Set `CORS_ALLOWED_ORIGINS` to frontend domains
- [ ] Configure email backend for production SMTP
- [ ] Set up SSL/HTTPS
- [ ] Enable logging and monitoring
- [ ] Set up automated backups for MongoDB
- [ ] Configure blockchain service endpoints
- [ ] Store secrets in Secret Manager (not in .env)
- [ ] Enable Cloud Run auto-scaling
- [ ] Configure monitoring and alerting
- [ ] Set up CI/CD pipeline in GitHub Actions

## Architecture Highlights

### Multi-Tenant Design
- Organizations as first-class entities
- All resources filtered by organization context
- OrganizationMembership controls access

### RBAC (Role-Based Access Control)
- 7 user roles with granular permissions
- Custom DRF permission classes per endpoint
- Role checked in UserProfile via Django User link

### MongoDB Integration
- Document-oriented data model (normalized for performance)
- EmbeddedDocument for nested structures (Location, Coordinates)
- ReferenceField for cross-document relationships
- Compound indexes for common queries

### RESTful API Design
- Versioned API (`/api/v1/`)
- Pagination: 20 items per page (configurable)
- Filtering, search, ordering on list endpoints
- Consistent error response format

### Security Features
- JWT Bearer token authentication (1-hour access, 7-day refresh)
- CSRF protection via CSRF middleware
- CORS configured for specific origins
- API key authentication for DEVELOPER role (HMAC-SHA256)
- Audit logging for all sensitive actions

## Key Workflows

### 1. Project Lifecycle
```
Project (DRAFT) 
  → submit_mrv() 
  → Project (SUBMITTED_FOR_MRV)
  → MRVRequest created
  → Validator assesses
  → MRVAssessment decision
  → Project (APPROVED)
  → CreditBatch issued
  → Project (ACTIVE)
```

### 2. MRV Workflow
```
MRVRequest (PENDING)
  → MRVAssessment created
  → Validator reviews data quality
  → Decision (APPROVE/REJECT/NEEDS_CLARIFICATION)
  → CreditBatch created if approved
  → Transaction logged
```

### 3. Carbon Credit Lifecycle
```
CreditBatch (ISSUED)
  → Listed on marketplace
  → Order created
  → Payment confirmed
  → Credits transferred
  → Retired or held
  → RetirementCertificate generated
  → ESGReport includes retired credits
```

### 4. Marketplace Flow
```
CreditBatch ISSUED
  → Listing created (OPEN)
  → Order placed (PENDING_PAYMENT)
  → Payment confirmed
  → Order (COMPLETED)
  → Listing (PARTIALLY_FILLED or FILLED)
  → TradeHistory recorded
```

## Troubleshooting

### MongoDB Connection Error
```
Check MONGO_URI in .env
Verify MongoDB service is running
Ensure network access if using MongoDB Atlas
```

### JWT Token Expired
```
Token expires after 1 hour
Use refresh endpoint: POST /auth/token/refresh/
Request body: {"refresh": "your-refresh-token"}
```

### Permission Denied on Endpoint
```
Check user role in UserProfile
Verify permission_classes on ViewSet
Check organization membership
```

### Data Not Appearing After Create
```
Verify organization context matches
Check filtering logic in ViewSet list()
Ensure document was saved to MongoDB
```

## Support & Documentation

- **API Documentation**: Available at `/api/v1/` (to be configured with drf-spectacular)
- **MongoDB Docs**: https://www.mongodb.com/docs/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **MongoEngine**: https://docs.mongoengine.org/
- **Google Cloud Run**: https://cloud.google.com/run/docs
- **GitHub Repository**: https://github.com/[YOUR-GITHUB-USERNAME]/kabronetzero

## GitHub Setup

### Initial Repository Setup

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: Production-ready Kabro NetZero Django backend"

# Add GitHub remote (replace with your repository)
git remote add origin https://github.com/[USERNAME]/kabronetzero.git
git branch -M main
git push -u origin main
```

### What Gets Pushed to GitHub

✅ **Included in Git**:
- All source code (apps/, config/)
- Infrastructure files (Dockerfile, docker-compose.yml)
- requirements.txt (Python dependencies)
- .env.example (configuration template)
- .gitignore (Git rules)
- README.md and supporting documentation
- GitHub Actions workflows (.github/workflows/)

❌ **Excluded from Git** (not pushed):
- docs/ folder (internal documentation)
- FOLDER_STRUCTURE_ANALYSIS.md
- REORGANIZATION_CHECKLIST.md
- DEPLOYMENT_MONGODB_COMPLETE.md
- .env (actual environment variables)
- __pycache__ and compiled Python files
- venv/ (virtual environment)
- .vscode/ (IDE settings)
- *.pyc, *.pyo files

### Repository Best Practices

1. **Clone the repository**:
   ```bash
   git clone https://github.com/[USERNAME]/kabronetzero.git
   cd kabronetzero_backend
   ```

2. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Create feature branches**:
   ```bash
   git checkout -b feature/your-feature-name
   git add .
   git commit -m "feat: descriptive message"
   git push origin feature/your-feature-name
   ```

4. **Submit pull requests**:
   - Ensure all tests pass: `pytest tests/`
   - Follow commit conventions
   - Add description of changes
   - Request review from team members

5. **Merge to main**:
   ```bash
   # After review approval
   git checkout main
   git pull origin main
   git merge feature/your-feature-name
   git push origin main
   # This triggers GitHub Actions → Cloud Run deployment
   ```

## License

Proprietary - Kabro NetZero 2024

## Contributors

Kabro NetZero Development Team

---

**Last Updated**: 2024
**Version**: 1.0.0
**GitHub**: https://github.com/[YOUR-GITHUB-USERNAME]/kabronetzero
**Status**: ✅ Ready for GitHub and Google Cloud Deployment
