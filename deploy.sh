#!/bin/bash

# Restaurant Recommendation System Deployment Script
# This script automates the complete deployment process

set -e

echo "🚀 Starting Restaurant Recommendation System Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check if required tools are installed
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    print_status "All prerequisites are installed!"
}

# Create project structure
create_project_structure() {
    print_info "Creating project structure..."
    
    # Create necessary directories
    mkdir -p .github/workflows
    mkdir -p templates
    mkdir -p static/css
    mkdir -p static/js
    mkdir -p tests
    
    print_status "Project structure created!"
}

# Create deployment configurations
create_deployment_configs() {
    print_info "Creating deployment configurations..."
    
    # Create package.json for Vercel
    cat > package.json << 'EOF'
{
  "name": "restaurant-recommendation-system",
  "version": "1.0.0",
  "description": "AI-powered restaurant recommendation system",
  "main": "app.py",
  "scripts": {
    "start": "python app.py",
    "dev": "python app.py",
    "build": "echo 'Build complete'",
    "test": "python -m pytest tests/ -v"
  },
  "dependencies": {
    "@vercel/python": "^3.0.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
EOF

    # Create .gitignore
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# Environment variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Node modules
node_modules/

# Vercel
.vercel

# Docker
Dockerfile
docker-compose.yml
EOF

    print_status "Deployment configurations created!"
}

# Create simple test file
create_tests() {
    print_info "Creating test files..."
    
    cat > tests/test_app.py << 'EOF'
import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test health endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_recommendations_endpoint(client):
    """Test recommendations endpoint"""
    response = client.post('/api/recommendations',
                          json={
                              'location': 'Bellandur',
                              'budget': 2000,
                              'min_rating': 4.0,
                              'cuisine_preference': 'Italian',
                              'top_n': 5
                          })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'recommendations' in data
EOF

    print_status "Test files created!"
}

# Initialize Git repository
init_git() {
    print_info "Initializing Git repository..."
    
    # Initialize git if not already initialized
    if [ ! -d ".git" ]; then
        git init
        git add .
        git commit -m "Initial commit: Restaurant Recommendation System
        
        - Complete Phase 1-7 implementation
        - Production-ready Flask application
        - Advanced personalization features
        - Free deployment configurations
        - CI/CD pipeline setup
        
        Features:
        - AI-powered restaurant recommendations
        - User profile management
        - Collaborative filtering
        - Machine learning personalization
        - Predictive analytics
        - Real-time monitoring"
        
        print_status "Git repository initialized!"
    else
        print_warning "Git repository already exists."
    fi
}

# Setup environment variables
setup_environment() {
    print_info "Setting up environment variables..."
    
    # Create .env.example
    cat > .env.example << 'EOF'
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
PORT=5000

# API Keys
GROQ_API_KEY=your-groq-api-key-here

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database

# Deployment URLs
FRONTEND_URL=https://your-app.vercel.app
BACKEND_URL=https://your-app.onrender.com

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
EOF

    print_status "Environment variables template created!"
    print_warning "Please copy .env.example to .env and fill in your actual values"
}

# Create deployment scripts
create_deployment_scripts() {
    print_info "Creating deployment scripts..."
    
    # Create local development script
    cat > run_local.sh << 'EOF'
#!/bin/bash
# Local development script

echo "🔧 Starting local development server..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  .env file not found. Using default values."
fi

# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py
EOF

    # Make scripts executable
    chmod +x run_local.sh
    
    print_status "Deployment scripts created!"
}

# Create documentation
create_documentation() {
    print_info "Creating documentation..."
    
    cat > README_DEPLOYMENT.md << 'EOF'
# Restaurant Recommendation System - Deployment Guide

## Quick Start

### 1. Local Development
```bash
# Clone the repository
git clone <your-repo-url>
cd restaurant-recommendation-system

# Copy environment variables
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Run locally
./run_local.sh
```

### 2. Deploy to Vercel (Frontend)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### 3. Deploy to Render (Backend)
```bash
# Connect GitHub repository to Render
# 1. Go to render.com
# 2. Click "New +"
# 3. Connect your GitHub repository
# 4. Select "Python" as environment
# 5. Configure environment variables
# 6. Deploy
```

## Environment Variables

Required environment variables:
- `FLASK_ENV`: Set to "production"
- `SECRET_KEY`: Your Flask secret key
- `GROQ_API_KEY`: Your Groq API key
- `DATABASE_URL`: Your database connection string

## Monitoring

### Health Check
- URL: `https://your-app.onrender.com/health`
- Method: GET
- Response: JSON with status

### Metrics
- URL: `https://your-app.onrender.com/api/dashboard`
- Method: GET
- Response: System performance metrics

## API Endpoints

### Recommendations
- URL: `https://your-app.onrender.com/api/recommendations`
- Method: POST
- Body: JSON with location, budget, etc.

### Personalized Recommendations
- URL: `https://your-app.onrender.com/api/personalized-recommendations`
- Method: POST
- Body: JSON with user_id, preferences

### User Profile
- URL: `https://your-app.onrender.com/api/user-profile`
- Method: POST
- Body: JSON with user_id, preferences

## Troubleshooting

### Common Issues
1. **Port binding**: Use PORT environment variable
2. **Database connection**: Check DATABASE_URL
3. **CORS errors**: Configure CORS properly
4. **Timeout errors**: Optimize queries

### Debug Commands
```bash
# Check logs
render logs
vercel logs

# Test locally
docker build -t restaurant-app .
docker run -p 5000:5000 restaurant-app
```

## Support

For issues:
1. Check Render dashboard for backend logs
2. Check Vercel dashboard for frontend logs
3. Review GitHub Actions for deployment issues
4. Check environment variables configuration
EOF

    print_status "Documentation created!"
}

# Main deployment function
deploy() {
    print_info "Starting deployment process..."
    
    # Check if we're in a Git repository
    if [ ! -d ".git" ]; then
        print_error "Not in a Git repository. Please run init_git() first."
        exit 1
    fi
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "You have uncommitted changes. Please commit them first."
        git status
        exit 1
    fi
    
    # Push to GitHub
    print_info "Pushing to GitHub..."
    git push origin main
    
    print_status "Code pushed to GitHub!"
    
    print_info "Deployment will be triggered automatically via GitHub Actions."
    print_info "Monitor deployment at:"
    print_info "  - Vercel: https://vercel.com/dashboard"
    print_info "  - Render: https://dashboard.render.com"
    print_info "  - GitHub Actions: https://github.com/$(git config --get remote.origin.url | sed 's/.*\/\([^/]*\)\.git/\1/')/actions"
}

# Main execution
main() {
    echo "🍽️  Restaurant Recommendation System Deployment"
    echo "=============================================="
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "app.py" ]; then
        print_error "app.py not found. Please run this script from the project root."
        exit 1
    fi
    
    # Run all setup functions
    check_prerequisites
    create_project_structure
    create_deployment_configs
    create_tests
    setup_environment
    create_deployment_scripts
    create_documentation
    
    # Ask user if they want to deploy
    echo ""
    read -p "🚀 Do you want to deploy now? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        init_git
        deploy
    else
        print_info "Setup complete! You can deploy later by running:"
        print_info "  ./deploy.sh"
    fi
    
    echo ""
    print_status "🎉 Deployment setup complete!"
    echo ""
    print_info "Next steps:"
    print_info "1. Fill in your .env file with actual values"
    print_info "2. Set up your Vercel account and connect your repository"
    print_info "3. Set up your Render account and connect your repository"
    print_info "4. Configure environment variables in both platforms"
    print_info "5. Deploy using ./deploy.sh"
    echo ""
    print_info "📚 For detailed instructions, see README_DEPLOYMENT.md"
    print_info "🔧 For troubleshooting, see deployment_guide.md"
}

# Run main function
main "$@"
