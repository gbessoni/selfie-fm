# 🚀 VoiceTree Deployment Guide

This guide provides complete instructions for deploying the VoiceTree application to production platforms like Railway or Render.

## 📋 Pre-Deployment Checklist

### Files Created for Deployment

All necessary deployment files have been created:

- ✅ `requirements.txt` - Updated with all dependencies including PostgreSQL support
- ✅ `Procfile` - Configuration for Railway/Render deployment
- ✅ `backend/database.py` - Updated to support both SQLite (dev) and PostgreSQL (prod)
- ✅ `.gitignore` - Comprehensive ignore rules for Python projects
- ✅ `README.md` - Complete setup and deployment instructions

### Required API Keys

Before deploying, ensure you have:

1. **Anthropic API Key** - For AI script generation with Claude
   - Get from: https://console.anthropic.com/

2. **ElevenLabs API Key** - For voice cloning and text-to-speech
   - Get from: https://elevenlabs.io/

3. **Secret Key** - For JWT token signing
   - Generate a secure random string (e.g., use `openssl rand -hex 32`)

## 🏗️ Deployment Architecture

### Local Development
- **Database**: SQLite (`voicetree.db`)
- **Server**: Uvicorn development server
- **Port**: 8000 (default)

### Production
- **Database**: PostgreSQL (provided by hosting platform)
- **Server**: Uvicorn with production settings
- **Port**: Dynamic (provided by `$PORT` environment variable)

## 🚂 Railway Deployment

### Step 1: Create New Project

1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `voicetree-app` repository

### Step 2: Add PostgreSQL Database

1. In your project, click "New"
2. Select "Database"
3. Choose "Add PostgreSQL"
4. Railway automatically provides `DATABASE_URL` environment variable

### Step 3: Configure Environment Variables

Go to your service → "Variables" tab and add:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
ELEVENLABS_API_KEY=xxxxxxxxxxxxx
SECRET_KEY=your_secure_random_string_here
```

### Step 4: Deploy

Railway will automatically:
1. Detect the `Procfile`
2. Install dependencies from `requirements.txt`
3. Start the application with the command in `Procfile`

Your app will be live at: `https://your-app.up.railway.app`

## 🎨 Render Deployment

### Step 1: Create Web Service

1. Go to [Render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub account
4. Select your `voicetree-app` repository

### Step 2: Configure Service Settings

**Basic Settings:**
- **Name**: `voicetree-app` (or your choice)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users

**Build & Deploy:**
- **Build Command**: `pip install -r voicetree/requirements.txt`
- **Start Command**: `cd voicetree/backend && uvicorn app:app --host 0.0.0.0 --port $PORT`

### Step 3: Add PostgreSQL Database

1. Click "New" → "PostgreSQL"
2. Choose a name (e.g., `voicetree-db`)
3. Select plan (Free tier available)
4. Wait for database to be provisioned
5. Copy the "Internal Database URL"

### Step 4: Configure Environment Variables

In your web service, go to "Environment" tab and add:

```env
DATABASE_URL=postgresql://user:password@host:port/database
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
ELEVENLABS_API_KEY=xxxxxxxxxxxxx
SECRET_KEY=your_secure_random_string_here
```

### Step 5: Deploy

Click "Create Web Service". Render will:
1. Clone your repository
2. Install dependencies
3. Start your application

Your app will be live at: `https://voicetree-app.onrender.com`

## 🗄️ Database Setup

### Automatic Table Creation

The application automatically creates all necessary database tables on first startup using SQLAlchemy's `create_all()` method.

Tables created:
- `users` - User accounts and profiles
- `links` - User links with voice messages
- `clicks` - Click tracking analytics

### Manual Migrations (if needed)

If you need to run database migrations:

```bash
# Set the DATABASE_URL environment variable
export DATABASE_URL="your_production_database_url"

# Run migration scripts
python voicetree/backend/migrate_add_link_columns.py
python voicetree/backend/migrate_add_script_variations.py
```

## 🔍 Post-Deployment Verification

### 1. Check Application Logs

**Railway:**
- Go to your service → "Deployments" tab
- Click on the latest deployment
- View logs for any errors

**Render:**
- Go to your service → "Logs" tab
- Check for successful startup messages

### 2. Verify Database Connection

Look for log messages like:
```
INFO: Database connected successfully
INFO: Tables created/verified
```

### 3. Test the Application

1. Visit your deployed URL
2. Try to sign up for a new account
3. Create a test link
4. Verify all features work

### 4. Test API Endpoints

```bash
# Replace with your actual deployed URL
export APP_URL="https://your-app.up.railway.app"

# Test health check
curl $APP_URL/

# Test user creation
curl -X POST "$APP_URL/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

## 🔧 Troubleshooting

### Database Connection Issues

**Problem**: `OperationalError: could not connect to server`

**Solution**:
1. Verify `DATABASE_URL` is set correctly
2. Check if database service is running
3. Ensure database allows connections from your app

### Missing Dependencies

**Problem**: `ModuleNotFoundError: No module named 'psycopg2'`

**Solution**:
1. Verify `psycopg2-binary` is in `requirements.txt`
2. Re-deploy to trigger fresh installation

### Port Binding Issues

**Problem**: App crashes with port-related errors

**Solution**:
1. Ensure Procfile uses `--port $PORT`
2. Don't hardcode port numbers in app.py
3. Verify hosting platform provides `PORT` variable

### API Key Errors

**Problem**: `AuthenticationError` from AI services

**Solution**:
1. Double-check API keys are correctly set
2. Verify no extra spaces in environment variables
3. Check API key validity on provider dashboards

## 📊 Monitoring & Maintenance

### View Application Logs

**Railway:**
```bash
railway logs
```

**Render:**
- Use the web dashboard → Logs tab

### Database Backups

**Railway:**
- Automatic daily backups included
- Manual backup: Use Railway CLI or dashboard

**Render:**
- Paid plans include automatic backups
- Export data using PostgreSQL tools

### Scaling Considerations

**When to Scale:**
- Response times increase
- High CPU/memory usage
- Database connection pool exhaustion

**How to Scale:**
- **Railway**: Upgrade plan, adjust resources
- **Render**: Change instance type, add more workers

## 🔒 Security Checklist

Before going live:

- [ ] Change default `SECRET_KEY` to a strong random value
- [ ] Set up HTTPS (automatic on Railway/Render)
- [ ] Review and update CORS settings if needed
- [ ] Enable rate limiting on sensitive endpoints
- [ ] Regular security updates for dependencies
- [ ] Set up monitoring and alerts
- [ ] Configure proper database access controls
- [ ] Review `.gitignore` to ensure no secrets committed

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [SQLAlchemy with PostgreSQL](https://docs.sqlalchemy.org/en/14/dialects/postgresql.html)

## 🆘 Getting Help

If you encounter issues:

1. Check application logs first
2. Review this guide's troubleshooting section
3. Consult platform-specific documentation
4. Check API provider status pages
5. Review GitHub issues for known problems

---

**Happy Deploying! 🚀**
