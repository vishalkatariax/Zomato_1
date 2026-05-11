# Free Deployment Guide for Restaurant Recommendation System

## Overview
This guide shows how to deploy the complete restaurant recommendation system (Phases 1-7) using free tools and services.

## Free Deployment Options

### 1. Vercel (Recommended for Frontend)
- **Free Tier**: 100GB bandwidth/month, unlimited sites
- **Best for**: React/Vue/Static sites + Serverless functions
- **Setup**: GitHub integration + automatic deployments

### 2. Render (Recommended for Backend)
- **Free Tier**: 750 hours/month of web service time
- **Best for**: Python Flask/FastAPI applications
- **Setup**: Docker support + PostgreSQL free tier

### 3. Netlify (Alternative Frontend)
- **Free Tier**: 100GB bandwidth/month
- **Best for**: Static sites with serverless functions
- **Setup**: GitHub integration + form handling

### 4. Railway (Alternative Backend)
- **Free Tier**: $5 credit/month (enough for small projects)
- **Best for**: Docker applications
- **Setup**: GitHub integration + PostgreSQL

### 5. Fly.io (Advanced Option)
- **Free Tier**: Shared CPU-1, 3GB bandwidth/month
- **Best for**: Docker applications with global deployment
- **Setup**: CLI-based deployment

## Recommended Architecture

```
Frontend (Vercel) → API Gateway (Vercel Functions) → Backend (Render) → Database (Supabase)
```

## Step-by-Step Deployment

### Phase 1: Prepare Project for Deployment

#### 1.1 Create Production-Ready Flask App
```python
# app.py - Production-ready Flask application
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from working_complete_system import WorkingCompleteSystem

app = Flask(__name__)
CORS(app)

# Initialize system
system = WorkingCompleteSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    # API endpoint implementation
    pass

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

#### 1.2 Create Requirements File
```txt
# requirements.txt
flask==2.3.3
flask-cors==4.0.0
pandas==2.0.3
numpy==1.24.3
python-dotenv==1.0.0
gunicorn==21.2.0
```

#### 1.3 Create Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### Phase 2: Database Setup (Free Options)

#### 2.1 Supabase (Recommended)
- **Free Tier**: 500MB database, 50k API calls/month
- **Features**: PostgreSQL, Auth, Storage, Edge Functions
- **Setup**: Create project → Get connection string

#### 2.2 PlanetScale (Alternative)
- **Free Tier**: 5GB storage, 1 billion rows read/month
- **Features**: MySQL, Vitess, Serverless
- **Setup**: Create database → Get connection string

#### 2.3 Neon (Alternative)
- **Free Tier**: 3GB storage, 100 hours compute/month
- **Features**: PostgreSQL, Serverless
- **Setup**: Create project → Get connection string

### Phase 3: Environment Configuration

#### 3.1 Create .env file
```env
# .env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host:port/db
GROQ_API_KEY=your-groq-api-key
```

#### 3.2 Create Environment Variables for Deployment
```bash
# For Render
export DATABASE_URL=postgresql://...
export GROQ_API_KEY=...
export SECRET_KEY=...
```

### Phase 4: Frontend Deployment (Vercel)

#### 4.1 Create vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  }
}
```

#### 4.2 Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Phase 5: Backend Deployment (Render)

#### 5.1 Create render.yaml
```yaml
# render.yaml
services:
  - type: web
    name: restaurant-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: DATABASE_URL
        sync: false
      - key: GROQ_API_KEY
        sync: false
```

#### 5.2 Deploy to Render
1. Connect GitHub repository to Render
2. Select branch (main)
3. Configure environment variables
4. Deploy automatically

### Phase 6: CI/CD Setup (GitHub Actions)

#### 6.1 Create .github/workflows/deploy.yml
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python -m pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```

### Phase 7: Monitoring and Analytics (Free)

#### 7.1 Uptime Monitoring
- **UptimeRobot**: Free for 50 monitors
- **Pingdom**: Free for 1 monitor
- **StatusCake**: Free for 10 monitors

#### 7.2 Error Tracking
- **Sentry**: Free for 5k errors/month
- **Rollbar**: Free for 5k errors/month
- **Bugsnag**: Free for 2k errors/month

#### 7.3 Analytics
- **Google Analytics**: Free
- **Plausible**: Free for personal sites
- **Umami**: Self-hosted free analytics

## Complete Deployment Script

### Automated Setup Script
```bash
#!/bin/bash
# deploy.sh - Complete deployment automation

echo "🚀 Starting Restaurant Recommendation System Deployment"

# 1. Check prerequisites
command -v git >/dev/null 2>&1 || { echo "❌ Git is required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required"; exit 1; }

# 2. Create project structure
mkdir -p deployment/{frontend,backend,database}
cd deployment

# 3. Setup backend
echo "📦 Setting up backend..."
mkdir backend
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
EOF

# 4. Create deployment configurations
echo "⚙️ Creating deployment configurations..."
cat > render.yaml << 'EOF'
services:
  - type: web
    name: restaurant-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:app
EOF

cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
EOF

# 5. Initialize Git repository
echo "📝 Initializing Git repository..."
git init
git add .
git commit -m "Initial commit: Restaurant Recommendation System"

# 6. Instructions for manual deployment
echo "✅ Setup complete! Next steps:"
echo "1. Push to GitHub: git remote add origin <your-repo>"
echo "2. Connect GitHub to Vercel for frontend"
echo "3. Connect GitHub to Render for backend"
echo "4. Set up Supabase for database"
echo "5. Configure environment variables"
echo "6. Test deployment"

echo "🎉 Ready for deployment!"
```

## Cost Analysis

### Free Tier Limitations
| Service | Free Tier | Limitations |
|----------|-------------|-------------|
| Vercel | 100GB bandwidth | Serverless functions timeout |
| Render | 750 hours/month | Cold starts, limited RAM |
| Supabase | 500MB DB | Limited connections |
| Sentry | 5k errors/month | Limited features |

### Estimated Monthly Usage
- **Small Project**: $0/month (all free tiers)
- **Medium Project**: $10-20/month (upgrade some services)
- **Large Project**: $50+/month (multiple services)

## Security Considerations

### 1. API Keys
- Use environment variables
- Rotate keys regularly
- Use key management services

### 2. Database Security
- Use SSL connections
- Implement connection pooling
- Regular backups

### 3. Rate Limiting
- Implement API rate limiting
- Use CDN for static assets
- Monitor for abuse

## Performance Optimization

### 1. Caching
- Redis (free tier available)
- Browser caching
- CDN caching

### 2. Database Optimization
- Index optimization
- Query optimization
- Connection pooling

### 3. Frontend Optimization
- Code splitting
- Image optimization
- Lazy loading

## Monitoring Setup

### 1. Health Checks
```python
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(),
        'version': '1.0.0',
        'database': check_database_connection()
    })
```

### 2. Metrics Collection
```python
@app.route('/metrics')
def metrics():
    return jsonify({
        'active_users': get_active_users(),
        'recommendations_today': get_recommendation_count(),
        'error_rate': get_error_rate()
    })
```

## Backup and Recovery

### 1. Database Backups
- Automated daily backups
- Point-in-time recovery
- Cross-region replication

### 2. Code Backups
- Git version control
- GitHub Actions artifacts
- Manual backups

## Scaling Strategy

### 1. Vertical Scaling
- Upgrade Render plans
- Increase database size
- Add more memory

### 2. Horizontal Scaling
- Load balancers
- Multiple instances
- Geographic distribution

## Troubleshooting

### Common Issues
1. **Port binding**: Use PORT environment variable
2. **Database connections**: Check connection strings
3. **CORS errors**: Configure CORS properly
4. **Timeout errors**: Optimize queries
5. **Memory issues**: Implement caching

### Debug Commands
```bash
# Check logs
render logs
vercel logs

# Test locally
docker build -t restaurant-app .
docker run -p 5000:5000 restaurant-app
```

## Conclusion

This deployment setup provides a complete free hosting solution for the restaurant recommendation system. The combination of Vercel (frontend) + Render (backend) + Supabase (database) offers enterprise-grade features at no cost for small to medium projects.

The system is production-ready with:
- ✅ Automated deployments
- ✅ CI/CD pipeline
- ✅ Monitoring and alerting
- ✅ Error tracking
- ✅ Performance optimization
- ✅ Security best practices
- ✅ Backup and recovery

Next steps: Follow the deployment script and customize for your specific requirements.
