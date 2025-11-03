# 🎙️ selfie.fm - Voice-Powered Link Sharing

**AI-Powered Link Sharing Platform with Voice Messages**

selfie.fm is a next-generation link-in-bio platform that adds your voice to every link you share. Create a personalized page with AI-powered voice messages that introduce each of your links.

## Features (Phase 1 - MVP)

✅ FastAPI backend with SQLite database  
✅ User profile model and link management  
✅ Basic routes: homepage and `/{username}` profile pages  
✅ Simple frontend HTML/CSS  

## Project Structure

```
voicetree/
├── backend/
│   ├── __init__.py
│   ├── app.py              # Main FastAPI application
│   ├── models.py           # SQLAlchemy models (User, Link)
│   ├── database.py         # Database configuration
│   └── schemas.py          # Pydantic schemas
├── frontend/
│   ├── templates/
│   │   ├── index.html      # Homepage
│   │   └── profile.html    # User profile page
│   └── static/
│       └── css/
│           └── style.css   # Styles
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation (Local Development)

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/voicetree-app.git
cd voicetree-app
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r voicetree/requirements.txt
```

4. **Set up environment variables:**
Create a `.env` file in `voicetree/backend/` with:
```env
# AI API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# JWT Secret (generate a random string)
SECRET_KEY=your_secret_key_here

# Optional: Database URL (defaults to SQLite if not set)
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

5. **Run the application:**
```bash
cd voicetree/backend
python app.py
```

Or using uvicorn directly:
```bash
uvicorn voicetree.backend.app:app --reload
```

6. **Open your browser:**
```
http://localhost:8000
```

## Deployment (Railway/Render)

### Prerequisites
- A Railway or Render account
- PostgreSQL database provisioned
- API keys for Anthropic and ElevenLabs

### Environment Variables

Set these environment variables in your hosting platform:

**Required:**
- `DATABASE_URL` - PostgreSQL connection string (auto-provided by Railway/Render)
- `ANTHROPIC_API_KEY` - Your Anthropic API key for AI script generation
- `ELEVENLABS_API_KEY` - Your ElevenLabs API key for voice cloning
- `SECRET_KEY` - Random string for JWT token signing (generate a secure one)
- `PORT` - Port number (auto-provided by Railway/Render)

**Optional:**
- `OPENAI_API_KEY` - OpenAI API key (if using GPT instead of Claude)

### Deployment Steps

#### Railway

1. **Connect your repository:**
   - Go to [Railway](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your voicetree repository

2. **Add PostgreSQL database:**
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically provide `DATABASE_URL`

3. **Configure environment variables:**
   - Go to your service → "Variables" tab
   - Add all required environment variables listed above

4. **Deploy:**
   - Railway will automatically detect the `Procfile` and deploy
   - Your app will be available at the provided Railway URL

#### Render

1. **Create a new Web Service:**
   - Go to [Render](https://render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure the service:**
   - **Name:** voicetree-app (or your preferred name)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r voicetree/requirements.txt`
   - **Start Command:** `cd voicetree/backend && uvicorn app:app --host 0.0.0.0 --port $PORT`

3. **Add PostgreSQL database:**
   - Click "New" → "PostgreSQL"
   - Once created, copy the "Internal Database URL"
   - Add it as `DATABASE_URL` in your web service environment variables

4. **Configure environment variables:**
   - Go to your web service → "Environment" tab
   - Add all required environment variables listed above

5. **Deploy:**
   - Click "Create Web Service"
   - Render will build and deploy your application

### Post-Deployment

After deployment, your database tables will be automatically created on first run. To verify:

1. Check the logs in Railway/Render dashboard
2. Visit your deployed URL
3. Try creating a user and adding links via the API

### Database Migrations

The app automatically creates tables on startup. If you need to run migrations:

```bash
# Set DATABASE_URL locally
export DATABASE_URL="your_production_database_url"

# Run migration scripts
python voicetree/backend/migrate_add_link_columns.py
python voicetree/backend/migrate_add_script_variations.py
```

## Usage

### Create a User (API)

```bash
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "display_name": "John Doe",
    "bio": "Tech enthusiast and creator",
    "avatar_url": "https://example.com/avatar.jpg"
  }'
```

### Add Links (API)

```bash
curl -X POST "http://localhost:8000/api/users/johndoe/links" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Website",
    "url": "https://johndoe.com",
    "description": "Check out my personal website"
  }'
```

### View Profile

Visit: `http://localhost:8000/johndoe`

## API Endpoints

- `GET /` - Homepage
- `GET /{username}` - User profile page
- `POST /api/users` - Create a new user
- `GET /api/users/{username}` - Get user details
- `POST /api/users/{username}/links` - Add a link
- `GET /api/users/{username}/links` - Get all links

## Database

Uses SQLite database (`voicetree.db`) with two tables:
- **users**: User profiles
- **links**: User links

The database is automatically created on first run.

## Current Features

✅ User profiles with customizable bio and avatar
✅ Link management with voice messages
✅ AI voice cloning with ElevenLabs
✅ Click tracking and analytics
✅ Voice message plays tracking
✅ Dashboard with charts and stats
✅ Auto-approve voice messages
✅ Profile publishing controls
✅ Linktree import functionality

## Technology Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - SQL toolkit and ORM
- SQLite - Embedded database
- ElevenLabs API - AI voice cloning and generation

**Frontend:**
- HTML5/CSS3 - Modern responsive design
- Vanilla JavaScript - No framework dependencies
- Jinja2 - Template engine
- Chart.js - Analytics visualization

**Server:**
- Uvicorn - ASGI server

## Voice AI Features

selfie.fm uses ElevenLabs AI to provide:
- **Voice Cloning**: Clone your voice with 3 audio samples
- **Voice Messages**: Generate personalized voice intros for each link
- **Auto-Generation**: AI-powered voice message creation
- **Voice Testing**: Test your cloned voice before publishing

## Contributing

selfie.fm is built to help creators add personality to their link sharing. Feel free to contribute improvements and new features.

---

**Built with ❤️ using AI voice technology**
