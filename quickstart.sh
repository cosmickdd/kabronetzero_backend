#!/bin/bash
# Quick Start Script - Kabro NetZero Auth API
# Run this to get started locally

set -e

echo "======================================"
echo "Kabro NetZero - Auth API Quick Start"
echo "======================================"
echo

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check Python
echo -e "${BLUE}[1/5]${NC} Checking Python installation..."
python --version
echo

# Step 2: Create virtual environment
echo -e "${BLUE}[2/5]${NC} Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate venv
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

echo

# Step 3: Install dependencies
echo -e "${BLUE}[3/5]${NC} Installing dependencies..."
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo

# Step 4: Setup environment
echo -e "${BLUE}[4/5]${NC} Setting up environment..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
MONGODB_URI=mongodb://localhost:27017/kabro_netzero_db
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
    echo "  Edit .env to configure MongoDB connection"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi
echo

# Step 5: Run server
echo -e "${BLUE}[5/5]${NC} Starting development server..."
echo -e "${GREEN}✓ Setup complete!${NC}"
echo
echo "=================================================="
echo "API Server: http://localhost:8000"
echo "API Docs:   http://localhost:8000/v1/"
echo "Health:     http://localhost:8000/health/"
echo "=================================================="
echo
echo "To start the server, run:"
echo -e "${BLUE}  python manage.py runserver${NC}"
echo
echo "In another terminal, you can test:"
echo -e "${BLUE}  curl http://localhost:8000/health/${NC}"
echo
echo "For more info, see:"
echo "  - AUTH_ENDPOINTS_SUMMARY.md (quick reference)"
echo "  - AUTH_API_DOCUMENTATION.md (full reference)"
echo "  - DEPLOYMENT_GUIDE.md (setup & deployment)"
echo

# Optional: Run migrations
read -p "Run migrations now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
    echo -e "${GREEN}✓ Migrations complete${NC}"
    
    # Seed roles
    read -p "Seed roles and permissions? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python manage.py seed_roles_permissions
        echo -e "${GREEN}✓ Roles and permissions seeded${NC}"
    fi
fi

echo
echo "Ready to go! 🚀"
