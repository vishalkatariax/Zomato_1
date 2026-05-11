#!/bin/bash

# Streamlit Deployment Script
# Deploys restaurant recommendation system to Streamlit Cloud

set -e

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

echo "🚀 Streamlit Deployment for Restaurant Recommendation System"
echo "========================================================"

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    if ! command -v streamlit &> /dev/null; then
        print_error "Streamlit is not installed. Installing..."
        pip install streamlit
    fi
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    print_status "Prerequisites check complete!"
}

# Create Streamlit configuration
create_streamlit_config() {
    print_info "Creating Streamlit configuration..."
    
    # Create .streamlit directory
    mkdir -p .streamlit
    
    # Create secrets.toml template
    cat > .streamlit/secrets.toml << 'EOF'
# Streamlit Secrets Configuration
# Copy this file to .streamlit/secrets.toml and fill in your actual values

[database]
url = "your_database_url_here"

[api_keys]
groq = "your_groq_api_key_here"

[deployment]
frontend_url = "your_frontend_url_here"
backend_url = "your_backend_url_here"

[monitoring]
sentry_dsn = "your_sentry_dsn_here"
EOF

    # Create config.toml
    cat > .streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
headless = true
port = 8501
enableCORS = false

[logger]
level = "info"

[browser]
gatherUsageStats = false
EOF

    print_status "Streamlit configuration created!"
}

# Create deployment files
create_deployment_files() {
    print_info "Creating deployment files..."
    
    # Create Procfile for Streamlit Cloud
    cat > Procfile << 'EOF'
web: streamlit run streamlit_app.py --server.port=$PORT --server.headless=true --server.enableCORS=false
EOF

    # Update requirements.txt for Streamlit
    cat > requirements.txt << 'EOF'
streamlit==1.29.0
pandas==2.0.3
numpy==1.24.3
plotly==5.17.0
python-dotenv==1.0.0
requests==2.31.0
gunicorn==21.2.0
flask==2.3.3
flask-cors==4.0.0
EOF

    # Create .gitignore updates
    cat >> .gitignore << 'EOF'

# Streamlit
.streamlit/secrets.toml
.streamlit/config.toml

# Streamlit Cloud
.streamlit/
EOF

    print_status "Deployment files created!"
}

# Create local development script
create_dev_script() {
    print_info "Creating development script..."
    
    cat > run_streamlit.sh << 'EOF'
#!/bin/bash

# Local Streamlit Development Script

echo "🚀 Starting Streamlit development server..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  .env file not found. Using default values."
fi

# Install dependencies
pip install -r requirements.txt

# Start Streamlit
streamlit run streamlit_app.py --server.port=8501 --server.headless=false
EOF

    chmod +x run_streamlit.sh
    
    print_status "Development script created!"
}

# Create deployment instructions
create_deployment_guide() {
    print_info "Creating deployment guide..."
    
    cat > STREAMLIT_DEPLOYMENT.md << 'EOF'
# Streamlit Deployment Guide

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Locally
```bash
streamlit run streamlit_app.py
```

Or use the convenience script:
```bash
./run_streamlit.sh
```

## Streamlit Cloud Deployment

### 1. Prepare Your App
1. Make sure all files are committed to Git
2. Configure secrets in Streamlit Cloud
3. Test locally first

### 2. Deploy to Streamlit Community Cloud
```bash
# Install Streamlit CLI
pip install streamlit

# Login to Streamlit
streamlit login

# Deploy
streamlit deploy
```

### 3. Deploy to Streamlit Cloud (Automated)
```bash
# Deploy with custom configuration
streamlit deploy --theme.base light --theme.primaryColor "#FF6B6B"
```

## Environment Variables

### Required Secrets
Set these in Streamlit Cloud (Settings → Secrets):

```toml
# .streamlit/secrets.toml
[database]
url = "postgresql://user:password@host:port/db"

[api_keys]
groq = "your_groq_api_key"

[deployment]
frontend_url = "https://your-app.streamlit.app"
backend_url = "https://your-backend.onrender.com"
```

### Accessing Secrets in Code
```python
import streamlit as st

# Access secrets
database_url = st.secrets["database"]["url"]
groq_api_key = st.secrets["api_keys"]["groq"]
```

## Custom Domain (Optional)

### 1. Add Custom Domain
1. Go to Streamlit Cloud dashboard
2. Select your app
3. Click "Settings" → "Custom domain"
4. Add your domain (e.g., app.yourdomain.com)
5. Configure DNS records

### 2. SSL Certificate
- Streamlit provides free SSL certificates
- Automatic HTTPS redirection
- Custom domain support

## Performance Optimization

### 1. Caching
```python
@st.cache_data
def expensive_function(param):
    # Cache expensive computations
    return result

@st.cache_resource
def load_model():
    # Cache ML models
    return model
```

### 2. Lazy Loading
```python
# Load data only when needed
if st.sidebar.button("Load Data"):
    data = load_expensive_data()
    st.write(data)
```

### 3. Session State
```python
# Maintain state across reruns
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
```

## Monitoring and Analytics

### 1. Streamlit Analytics
- Built-in usage statistics
- User engagement metrics
- Performance monitoring

### 2. Custom Analytics
```python
import time

# Track page views
start_time = time.time()
# ... your code ...
load_time = time.time() - start_time

# Log to external service
log_analytics("page_view", {"load_time": load_time})
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**
   ```bash
   pip install -r requirements.txt
   ```

2. **Secrets not accessible**
   - Check secrets.toml format
   - Restart Streamlit app
   - Verify secret names

3. **Performance issues**
   - Use @st.cache_data decorators
   - Optimize data loading
   - Reduce unnecessary reruns

4. **Deployment failures**
   - Check requirements.txt
   - Verify all files are committed
   - Check Streamlit logs

### Debug Commands
```bash
# Check Streamlit version
streamlit version

# Clear cache
streamlit cache clear

# Check config
streamlit config show

# Run with debug logging
streamlit run streamlit_app.py --logger.level debug
```

## Security Considerations

### 1. Secrets Management
- Never commit secrets to Git
- Use Streamlit secrets for sensitive data
- Rotate API keys regularly

### 2. Input Validation
```python
# Validate user inputs
location = st.text_input("Location")
if not location or len(location) < 2:
    st.error("Please enter a valid location")
    st.stop()
```

### 3. Rate Limiting
```python
# Implement rate limiting
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0

st.session_state.request_count += 1
if st.session_state.request_count > 100:
    st.error("Too many requests. Please try again later.")
    st.stop()
```

## Scaling and Performance

### 1. Resource Limits
- Free tier: 1GB RAM, 1 CPU core
- Pro tier: More resources available
- Consider upgrading for high traffic

### 2. Optimization Tips
- Use caching extensively
- Minimize data loading
- Optimize images and assets
- Use lazy loading for large datasets

## Advanced Features

### 1. Multi-page Apps
```python
# streamlit_app.py
import streamlit as st

PAGES = {
    "Recommendations": "pages/recommendations.py",
    "Analytics": "pages/analytics.py",
    "Profile": "pages/profile.py"
}

selection = st.sidebar.selectbox("Choose a page", list(PAGES.keys()))
exec(open(PAGES[selection]).read())
```

### 2. Custom Components
```python
# Create reusable components
def recommendation_card(restaurant):
    with st.container():
        st.markdown(f"**{restaurant['name']}**")
        st.write(f"Rating: {restaurant['rating']}/5")
        st.write(f"Cost: ₹{restaurant['cost']}")
```

### 3. File Uploads
```python
# Handle file uploads
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(df)
```

## Support and Resources

### Documentation
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Cloud](https://streamlit.io/cloud)
- [Streamlit Community](https://discuss.streamlit.io/)

### Getting Help
- Check Streamlit logs
- Review deployment logs
- Ask questions on community forum
- Check GitHub issues

## Next Steps

1. Deploy to Streamlit Cloud
2. Set up custom domain
3. Configure monitoring
4. Optimize performance
5. Add advanced features
EOF

    print_status "Deployment guide created!"
}

# Main deployment function
deploy_to_streamlit() {
    print_info "Deploying to Streamlit Cloud..."
    
    # Check if we're in a Git repository
    if [ ! -d ".git" ]; then
        print_error "Not in a Git repository. Please initialize Git first."
        exit 1
    fi
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "You have uncommitted changes. Committing them now..."
        git add .
        git commit -m "Add Streamlit deployment files"
    fi
    
    # Deploy to Streamlit Cloud
    print_info "Deploying to Streamlit Cloud..."
    
    if command -v streamlit &> /dev/null; then
        streamlit deploy --theme.base light --theme.primaryColor "#FF6B6B"
        print_status "✅ Deployment initiated!"
        print_info "Check your Streamlit Cloud dashboard for deployment status."
    else
        print_error "Streamlit CLI not found. Please install it first:"
        print_info "pip install streamlit"
        exit 1
    fi
}

# Main execution
main() {
    echo "🚀 Streamlit Deployment Setup"
    echo "==========================="
    echo ""
    
    # Run all setup functions
    check_prerequisites
    create_streamlit_config
    create_deployment_files
    create_dev_script
    create_deployment_guide
    
    # Ask user if they want to deploy
    echo ""
    read -p "🚀 Do you want to deploy to Streamlit Cloud now? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        deploy_to_streamlit
    else
        print_status "Setup complete! You can deploy later by running:"
        print_info "  streamlit deploy"
        print_info "  ./run_streamlit.sh (for local development)"
    fi
    
    echo ""
    print_status "🎉 Streamlit deployment setup complete!"
    echo ""
    print_info "Next steps:"
    print_info "1. Configure secrets in Streamlit Cloud dashboard"
    print_info "2. Test locally with ./run_streamlit.sh"
    print_info "3. Deploy with streamlit deploy"
    print_info "4. Set up custom domain (optional)"
    print_info "5. Configure monitoring and analytics"
    echo ""
    print_info "📚 For detailed instructions, see STREAMLIT_DEPLOYMENT.md"
}

# Run main function
main "$@"
