# Deployment Guide - Zomato AI Restaurant Recommendation System

## Architecture Overview

```
Frontend (Vercel) → API Requests → Backend (Railway)
```

- **Frontend**: Static HTML/JS deployed on Vercel
- **Backend**: Flask API deployed on Railway with Groq LLaMA 3.3
- **Connection**: Vercel proxies API requests to Railway via vercel.json rewrites

## Environment Variables

### Vercel (Frontend)
**No environment variables required.**

The frontend is a static site that uses vercel.json rewrites to proxy API requests to the Railway backend. All API calls go through the Vercel domain and are automatically forwarded to Railway.

### Railway (Backend)
Required environment variables:

| Variable | Description | How to Set |
|----------|-------------|------------|
| `GROQ_API_KEY` | Your Groq API key for LLaMA 3.3 access | Add in Railway dashboard → Variables tab |
| `PORT` | Port for the application (optional) | Railway sets this automatically |

**Getting a Groq API Key:**
1. Visit https://console.groq.com
2. Sign up/login
3. Create a new API key
4. Copy the key and add it to Railway variables

## Deployment Steps

### 1. Railway (Backend) Deployment

The backend is automatically deployed from GitHub when you push changes.

**Configuration Files:**
- `Procfile`: `web: gunicorn --chdir src restaurant_app:app`
- `railway.toml`: Uses NIXPACKS builder
- `requirements.txt`: Python dependencies

**Setup Steps:**
1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Python configuration
3. Add `GROQ_API_KEY` in Railway Variables tab
4. Railway will build and deploy automatically

**Verify Deployment:**
- Check health endpoint: `https://zomato1-production.up.railway.app/health`
- Should return: `{"records":12119,"status":"healthy"}`

### 2. Vercel (Frontend) Deployment

The frontend is automatically deployed from GitHub when you push changes.

**Configuration Files:**
- `vercel.json`: Proxies API requests to Railway
- `.vercelignore`: Excludes backend files from Vercel build
- `index.html`: Main frontend file

**Setup Steps:**
1. Connect your GitHub repository to Vercel
2. Vercel will detect the static site configuration
3. No environment variables needed
4. Vercel will build and deploy automatically

**How API Proxying Works:**
The `vercel.json` file contains rewrites that:
- Forward `/api/*` requests to `https://zomato1-production.up.railway.app/api/*`
- Forward `/health` requests to `https://zomato1-production.up.railway.app/health`
- Serve all other routes from `index.html` (SPA routing)

**Frontend API Configuration:**
In `index.html`, the API_BASE is set to:
```javascript
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:5050'  // Local development
  : window.location.origin;  // Production (Vercel domain)
```

This means:
- Local development: Calls `http://localhost:5050` directly
- Production: Calls the Vercel domain, which proxies to Railway

## Local Development

### Backend (Flask)
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env and add GROQ_API_KEY

# Run backend
python src/restaurant_app.py
```
Backend runs on: http://localhost:5050

### Frontend (Static)
```bash
# Option 1: Use Flask backend (serves both API and frontend)
python src/restaurant_app.py
# Access at: http://localhost:5050

# Option 2: Run static file server separately
python3 -m http.server 8080
# Access at: http://localhost:8080
# Note: This won't have API connectivity unless backend is also running
```

## Troubleshooting

### Railway Issues
**Problem**: Backend crashes on startup with FileNotFoundError
- **Solution**: Ensure the dataset path in `src/restaurant_app.py` is correct. The BASE_DIR logic should resolve the path correctly.

**Problem**: API calls failing from Vercel
- **Solution**: 
  - Verify Railway URL in `vercel.json` is correct
  - Check Railway health endpoint is accessible
  - Ensure GROQ_API_KEY is set in Railway variables

### Vercel Issues
**Problem**: Frontend not loading
- **Solution**: 
  - Check Vercel deployment logs
  - Ensure `index.html` is in the repository root
  - Verify `.vercelignore` isn't excluding necessary files

**Problem**: API calls failing from frontend
- **Solution**:
  - Check browser console for CORS errors
  - Verify vercel.json rewrites are correct
  - Test Railway API directly first

### Common Issues
1. **CORS Errors**: Ensure `CORS(app)` is configured in `src/restaurant_app.py`
2. **API Limitations**: Monitor Groq API usage to avoid throttling
3. **Dataset Loading**: Ensure the CSV file exists in `data/processed/restaurants_cleaned.csv`

## URLs

- **Railway Backend**: https://zomato1-production.up.railway.app
- **Vercel Frontend**: (Add your Vercel URL here after deployment)
- **GitHub Repository**: https://github.com/vishalkatariax/Zomato_1

## Monitoring

### Railway
- Check deployment logs in Railway dashboard
- Monitor resource usage in Metrics tab
- View environment variables in Variables tab

### Vercel
- Check deployment logs in Vercel dashboard
- Monitor analytics in Analytics tab
- View deployment history in Deployments tab

## Security Considerations

1. **Never commit `.env` file** - It contains sensitive API keys
2. **Use environment variables** - All secrets should be in platform variables
3. **HTTPS only** - Both Railway and Vercel provide HTTPS by default
4. **API Key protection** - GROQ_API_KEY is only stored in Railway, never exposed to frontend

## Cost

- **Railway**: Free tier ($5 credit/month) - sufficient for this project
- **Vercel**: Free tier (100GB bandwidth/month) - sufficient for static frontend
- **Groq API**: Free tier available - check current limits at console.groq.com

## Support

For issues or questions:
- Check Railway logs for backend issues
- Check Vercel logs for frontend issues
- Review this deployment guide
- Check the main README.md for project details
