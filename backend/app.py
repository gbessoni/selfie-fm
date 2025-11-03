from dotenv import load_dotenv
load_dotenv()

# Log ElevenLabs API key status
import os
elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
if elevenlabs_key:
    print(f"✅ ElevenLabs API key loaded: {elevenlabs_key[:10]}...")
else:
    print("⚠️ WARNING: ELEVENLABS_API_KEY not found in environment")

"""
selfie.fm - FastAPI Backend
AI-Powered Link Sharing Platform with Voice Messages
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi import Request
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import logging

from database import get_db, init_db
from models import User, Link, ProfileView, LinkClick, VoiceMessage
from schemas import (
    UserCreate, UserResponse, LinkCreate, LinkResponse,
    ScrapeRequest, ScrapeResponse, UserCreateFromLinktree,
    VoiceCloneResponse, GenerateVoiceRequest, GenerateWelcomeRequest,
    VoiceMessageResponse, UserCreateWithPassword, LoginRequest, 
    LoginResponse, UserMeResponse, SignupRequest
)
from scraper import scraper
from voice_ai import VoiceAIService
from platform_utils import detect_platform
from script_writer import script_writer
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from auth import (
    get_password_hash, authenticate_user, create_access_token,
    verify_user_access, get_current_user_from_cookie, 
    get_current_user_required, set_auth_cookie, clear_auth_cookie,
    check_rate_limit, reset_rate_limit, validate_password_strength
)

app = FastAPI(title="selfie.fm", description="AI-powered link sharing with voice messages")

# Initialize logger
logger = logging.getLogger(__name__)

# Mount static files and templates
import os
from pathlib import Path

# Get the directory of the current file
BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("="*60)
    print("🚀 Selfie.fm Server Started")
    print("="*60)
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    print(f"✅ Anthropic key: {'Found' if anthropic_key else '❌ Missing'}")
    print(f"✅ ElevenLabs key: {'Found' if elevenlabs_key else '❌ Missing'}")
    print(f"📍 Running on: http://localhost:{os.getenv('PORT', '8000')}")
    print("="*60)

# Homepage route
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """Render the homepage"""
    return templates.TemplateResponse("index.html", {"request": request})

# Signup page route
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Render the signup page"""
    return templates.TemplateResponse("signup.html", {"request": request})

# Login page route
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render the login page"""
    return templates.TemplateResponse("login.html", {"request": request})

# Preview page route
@app.get("/preview/{username}", response_class=HTMLResponse)
async def preview_page(request: Request, username: str, response: Response, db: Session = Depends(get_db)):
    """Render the preview page for a user before publishing - always shows fresh data"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get fresh link data from database
    links = db.query(Link).filter(Link.user_id == user.id, Link.is_active == True).order_by(Link.order).all()
    
    # Set cache-control headers to prevent caching and ensure fresh data on each load
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return templates.TemplateResponse(
        "preview.html",
        {"request": request, "user": user, "links": links}
    )

# Dashboard page route
@app.get("/dashboard/{username}", response_class=HTMLResponse)
async def dashboard_page(request: Request, username: str, db: Session = Depends(get_db)):
    """Render the dashboard page for editing"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    links = db.query(Link).filter(Link.user_id == user.id, Link.is_active == True).all()
    
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "links": links}
    )

# User profile route
@app.get("/{username}", response_class=HTMLResponse)
async def user_profile(request: Request, username: str, db: Session = Depends(get_db)):
    """Render user profile page with their links"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Only show published profiles
    if not user.is_published:
        raise HTTPException(status_code=404, detail="Profile not published yet")
    
    # Track profile view
    referrer = request.headers.get("referer", "direct")
    profile_view = ProfileView(user_id=user.id, referrer=referrer)
    db.add(profile_view)
    user.profile_views += 1
    db.commit()
    
    links = db.query(Link).filter(Link.user_id == user.id, Link.is_active == True).all()
    
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user, "links": links}
    )

# API Routes

@app.post("/api/scrape", response_model=ScrapeResponse)
def scrape_linktree(scrape_request: ScrapeRequest):
    """Scrape a Linktree URL and return the data"""
    try:
        data = scraper.scrape_linktree(scrape_request.linktree_url)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    db_user = User(
        username=user.username,
        display_name=user.display_name,
        bio=user.bio,
        avatar_url=user.avatar_url
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/users/from-linktree", response_model=UserResponse)
def create_user_from_linktree(user_data: UserCreateFromLinktree, db: Session = Depends(get_db)):
    """Create a new user with imported Linktree data"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    db_user = User(
        username=user_data.username,
        display_name=user_data.display_name,
        bio=user_data.bio,
        imported_from_linktree=True,
        is_published=False
    )
    db.add(db_user)
    db.flush()
    
    # Add links
    for idx, link_data in enumerate(user_data.links):
        db_link = Link(
            user_id=db_user.id,
            title=link_data['title'],
            url=link_data['url'],
            order=idx
        )
        db.add(db_link)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/users/{username}", response_model=UserResponse)
def get_user(username: str, db: Session = Depends(get_db)):
    """Get user by username"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/preview/{username}", response_model=UserResponse)
def get_preview(username: str, db: Session = Depends(get_db)):
    """Get preview data for a user"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/users/{username}/publish")
def publish_profile(username: str, db: Session = Depends(get_db)):
    """Publish a user's profile"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_published = True
    db.commit()
    return {"message": "Profile published successfully"}

@app.put("/api/users/{username}")
def update_user(username: str, user_data: UserCreate, db: Session = Depends(get_db)):
    """Update user profile"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.display_name = user_data.display_name
    user.bio = user_data.bio
    if user_data.avatar_url:
        user.avatar_url = user_data.avatar_url
    
    db.commit()
    db.refresh(user)
    return user

@app.post("/api/users/{username}/links", response_model=LinkResponse)
def create_link(username: str, link: LinkCreate, db: Session = Depends(get_db)):
    """Create a new link for a user"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Auto-detect platform from URL
    platform = detect_platform(link.url)
    
    db_link = Link(
        user_id=user.id,
        title=link.title,
        url=link.url,
        description=link.description,
        platform=platform
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

@app.put("/api/users/{username}/links/{link_id}", response_model=LinkResponse)
def update_link(username: str, link_id: int, link: LinkCreate, db: Session = Depends(get_db)):
    """Update a link"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_link = db.query(Link).filter(
        Link.id == link_id,
        Link.user_id == user.id
    ).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    db_link.title = link.title
    db_link.url = link.url
    if link.description:
        db_link.description = link.description
    
    # Re-detect platform when URL changes
    db_link.platform = detect_platform(link.url)
    
    db.commit()
    db.refresh(db_link)
    return db_link

@app.delete("/api/users/{username}/links/{link_id}")
def delete_link(username: str, link_id: int, db: Session = Depends(get_db)):
    """Delete a link"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_link = db.query(Link).filter(
        Link.id == link_id,
        Link.user_id == user.id
    ).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    db.delete(db_link)
    db.commit()
    return {"message": "Link deleted successfully"}

@app.get("/api/users/{username}/links", response_model=List[LinkResponse])
def get_user_links(username: str, db: Session = Depends(get_db)):
    """Get all links for a user - returns ALL links for dashboard management"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # For dashboard management, show ALL links (active and inactive)
    # The frontend can toggle is_active status as needed
    links = db.query(Link).filter(Link.user_id == user.id).order_by(Link.order).all()
    return links

# Authentication API Routes

@app.get("/api/users/{username}/exists")
def check_username_exists(username: str, db: Session = Depends(get_db)):
    """Check if a username already exists"""
    user = db.query(User).filter(User.username == username).first()
    return {"exists": user is not None}

@app.post("/api/auth/signup")
async def signup(
    signup_request: SignupRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Create a new user account with email and password only"""
    try:
        # Extract email and password from request
        email = signup_request.email
        password = signup_request.password
        
        # Validate email
        if not email or '@' not in email:
            raise HTTPException(status_code=400, detail="Valid email is required")
        
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Validate password strength
        is_valid, error_message = validate_password_strength(password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Auto-generate username from email
        base_username = email.split('@')[0].lower()
        # Remove special characters, keep only alphanumeric and underscore
        base_username = ''.join(c if c.isalnum() or c == '_' else '' for c in base_username)
        
        # Find available username
        username = base_username
        counter = 2
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Hash password
        password_hash = get_password_hash(password)
        
        # Create user with generated username and email as display name initially
        display_name = email.split('@')[0]
        
        db_user = User(
            username=username,
            display_name=display_name,
            email=email,
            password_hash=password_hash,
            bio="",
            is_published=False
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create access token
        access_token = create_access_token(data={"sub": db_user.username})
        
        # Set cookie
        set_auth_cookie(response, access_token, remember_me=False)
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "username": db_user.username,
            "display_name": db_user.display_name,
            "redirect": f"/dashboard/{db_user.username}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login", response_model=LoginResponse)
def login(login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate user and create session"""
    # Check rate limit
    if not check_rate_limit(login_data.email):
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again in 15 minutes."
        )
    
    # Authenticate user
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Reset rate limit on successful login
    reset_rate_limit(login_data.email)
    
    # Update last login
    user.last_login = datetime.now()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    # Set cookie
    set_auth_cookie(response, access_token, remember_me=login_data.remember_me)
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        username=user.username,
        display_name=user.display_name
    )

@app.post("/api/auth/logout")
def logout(response: Response):
    """Clear authentication session"""
    clear_auth_cookie(response)
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me", response_model=UserMeResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user_required)
):
    """Get current authenticated user information"""
    return current_user

# Analytics API Routes

@app.get("/api/admin/{username}/stats")
def get_dashboard_stats(username: str, db: Session = Depends(get_db)):
    """Get overview statistics for admin dashboard"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get views from last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_views = db.query(func.count(ProfileView.id)).filter(
        ProfileView.user_id == user.id,
        ProfileView.view_date >= thirty_days_ago
    ).scalar()
    
    # Calculate conversion rate
    conversion_rate = 0
    if user.profile_views > 0:
        conversion_rate = (user.total_link_clicks / user.profile_views) * 100
    
    return {
        "profile_views_30d": recent_views or 0,
        "total_link_clicks": user.total_link_clicks,
        "voice_message_plays": user.voice_message_plays,
        "conversion_rate": round(conversion_rate, 2)
    }

@app.get("/api/admin/{username}/views-chart")
def get_views_chart_data(username: str, db: Session = Depends(get_db)):
    """Get profile views over time for chart (last 30 days)"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # Group views by date
    views_by_date = db.query(
        func.date(ProfileView.view_date).label('date'),
        func.count(ProfileView.id).label('count')
    ).filter(
        ProfileView.user_id == user.id,
        ProfileView.view_date >= thirty_days_ago
    ).group_by(func.date(ProfileView.view_date)).all()
    
    # Create complete date range with zeros for missing dates
    date_counts = {str(v.date): v.count for v in views_by_date}
    labels = []
    data = []
    
    for i in range(30):
        date = (datetime.now() - timedelta(days=29-i)).date()
        labels.append(date.strftime("%m/%d"))
        data.append(date_counts.get(str(date), 0))
    
    return {
        "labels": labels,
        "data": data
    }

@app.get("/api/admin/{username}/clicks-chart")
def get_clicks_chart_data(username: str, db: Session = Depends(get_db)):
    """Get link clicks by link for bar chart (top 10)"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get top 10 links by click count
    top_links = db.query(Link).filter(
        Link.user_id == user.id
    ).order_by(desc(Link.click_count)).limit(10).all()
    
    labels = [link.title for link in top_links]
    data = [link.click_count for link in top_links]
    
    return {
        "labels": labels,
        "data": data
    }

@app.get("/api/admin/{username}/traffic-sources")
def get_traffic_sources(username: str, db: Session = Depends(get_db)):
    """Get traffic sources for pie chart"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # Group by referrer
    traffic = db.query(
        ProfileView.referrer,
        func.count(ProfileView.id).label('count')
    ).filter(
        ProfileView.user_id == user.id,
        ProfileView.view_date >= thirty_days_ago
    ).group_by(ProfileView.referrer).all()
    
    # Categorize traffic sources
    direct = 0
    social = 0
    other = 0
    
    social_domains = ['facebook', 'twitter', 'instagram', 'linkedin', 'tiktok', 'youtube']
    
    for t in traffic:
        if not t.referrer or t.referrer == 'direct':
            direct += t.count
        elif any(domain in t.referrer.lower() for domain in social_domains):
            social += t.count
        else:
            other += t.count
    
    return {
        "labels": ["Direct", "Social Media", "Other"],
        "data": [direct, social, other]
    }

@app.get("/api/admin/{username}/recent-clicks")
def get_recent_clicks(username: str, limit: int = 20, db: Session = Depends(get_db)):
    """Get recent link clicks for analytics table"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get recent clicks with link information
    recent_clicks = db.query(LinkClick).filter(
        LinkClick.user_id == user.id
    ).order_by(desc(LinkClick.click_date)).limit(limit).all()
    
    # Format the data
    clicks_data = []
    for click in recent_clicks:
        clicks_data.append({
            "id": click.id,
            "link_title": click.link.title if click.link else "Unknown",
            "link_url": click.link.url if click.link else "",
            "click_date": click.click_date.isoformat(),
            "referrer": click.referrer or "direct",
            "user_agent": click.user_agent or "Unknown"
        })
    
    return clicks_data

# Link Management API Routes

@app.put("/api/admin/{username}/links/{link_id}/toggle")
def toggle_link_active(username: str, link_id: int, db: Session = Depends(get_db)):
    """Toggle link active/inactive status"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    link = db.query(Link).filter(Link.id == link_id, Link.user_id == user.id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    link.is_active = not link.is_active
    db.commit()
    
    return {"is_active": link.is_active}

@app.put("/api/users/{username}/links/reorder")
def reorder_links(username: str, request: dict, db: Session = Depends(get_db)):
    """Reorder links - expects {"link_ids": [id1, id2, id3]} array in order"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    link_ids = request.get('link_ids', [])
    for idx, link_id in enumerate(link_ids):
        link = db.query(Link).filter(Link.id == int(link_id), Link.user_id == user.id).first()
        if link:
            link.order = idx
    
    db.commit()
    return {"message": "Links reordered successfully"}

@app.post("/api/users/{username}/import-linktree")
def import_linktree_links(username: str, request: dict, db: Session = Depends(get_db)):
    """Import links from Linktree URL for existing user"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    linktree_url = request.get('linktree_url', '')
    if not linktree_url:
        raise HTTPException(status_code=400, detail="Linktree URL is required")
    
    try:
        # Scrape Linktree
        data = scraper.scrape_linktree(linktree_url)
        
        # Get current max order
        max_order = db.query(func.max(Link.order)).filter(Link.user_id == user.id).scalar() or -1
        
        # Add links
        imported_count = 0
        for idx, link_data in enumerate(data.get('links', [])):
            platform = detect_platform(link_data['url'])
            db_link = Link(
                user_id=user.id,
                title=link_data['title'],
                url=link_data['url'],
                platform=platform,
                order=max_order + idx + 1
            )
            db.add(db_link)
            imported_count += 1
        
        db.commit()
        
        return {
            "message": f"Successfully imported {imported_count} links from Linktree",
            "count": imported_count
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/clicks/{username}/{link_id}")
def track_link_click(
    username: str,
    link_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Track a link click with full analytics data"""
    # Get user
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get link
    link = db.query(Link).filter(Link.id == link_id, Link.user_id == user.id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Extract analytics data
    referrer = request.headers.get("referer", "direct")
    user_agent = request.headers.get("user-agent", "")
    
    # Increment counters
    link.click_count += 1
    user.total_link_clicks += 1
    
    # Record click event with full data
    click = LinkClick(
        link_id=link_id,
        user_id=user.id,
        referrer=referrer,
        user_agent=user_agent
    )
    db.add(click)
    db.commit()
    
    return {"message": "Click tracked", "link_id": link_id}

@app.post("/api/track/voice-play/{username}")
def track_voice_play(username: str, db: Session = Depends(get_db)):
    """Track a voice message play"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.voice_message_plays += 1
    db.commit()
    
    return {"message": "Voice play tracked"}

# Voice Message Approval API Routes

@app.get("/api/admin/{username}/pending-voices")
def get_pending_voice_messages(username: str, db: Session = Depends(get_db)):
    """Get pending voice messages for approval"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    pending = db.query(VoiceMessage).filter(
        VoiceMessage.user_id == user.id,
        VoiceMessage.is_approved == False,
        VoiceMessage.is_active == True
    ).order_by(desc(VoiceMessage.created_at)).all()
    
    return [{
        "id": vm.id,
        "text_content": vm.text_content,
        "audio_file_path": vm.audio_file_path,
        "created_at": vm.created_at.isoformat()
    } for vm in pending]

@app.put("/api/admin/{username}/voices/{voice_id}/approve")
def approve_voice_message(username: str, voice_id: int, db: Session = Depends(get_db)):
    """Approve a voice message"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    voice = db.query(VoiceMessage).filter(
        VoiceMessage.id == voice_id,
        VoiceMessage.user_id == user.id
    ).first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice message not found")
    
    voice.is_approved = True
    voice.approved_at = datetime.now()
    db.commit()
    
    return {"message": "Voice message approved"}

@app.put("/api/admin/{username}/voices/{voice_id}/reject")
def reject_voice_message(username: str, voice_id: int, db: Session = Depends(get_db)):
    """Reject a voice message"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    voice = db.query(VoiceMessage).filter(
        VoiceMessage.id == voice_id,
        VoiceMessage.user_id == user.id
    ).first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice message not found")
    
    voice.is_active = False
    db.commit()
    
    return {"message": "Voice message rejected"}

@app.put("/api/admin/{username}/auto-approve")
def toggle_auto_approve(username: str, db: Session = Depends(get_db)):
    """Toggle auto-approve setting for voice messages"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.auto_approve_voice = not user.auto_approve_voice
    db.commit()
    
    return {"auto_approve": user.auto_approve_voice}

# Profile Settings API Routes

@app.put("/api/admin/{username}/profile")
def update_profile_settings(
    username: str,
    display_name: str = Form(...),
    bio: str = Form(None),
    db: Session = Depends(get_db)
):
    """Update profile settings"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.display_name = display_name
    if bio is not None:
        user.bio = bio
    db.commit()
    
    return {"message": "Profile updated"}

@app.post("/api/admin/{username}/upload-avatar")
async def upload_avatar(
    username: str,
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload profile picture"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if avatar.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed.")
    
    # Validate file size (max 5MB)
    avatar_data = await avatar.read()
    if len(avatar_data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")
    
    # Save file
    import os
    from pathlib import Path
    
    upload_dir = Path(__file__).parent / "uploads" / "avatars"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_extension = avatar.filename.split('.')[-1]
    filename = f"{username}_avatar_{datetime.now().timestamp()}.{file_extension}"
    file_path = upload_dir / filename
    
    with open(file_path, 'wb') as f:
        f.write(avatar_data)
    
    # Update user avatar URL
    user.avatar_url = f"/uploads/avatars/{filename}"
    db.commit()
    
    return {"message": "Avatar uploaded successfully", "avatar_url": user.avatar_url}

@app.post("/api/admin/{username}/upload-banner")
async def upload_banner(
    username: str,
    banner: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload banner/background image"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if banner.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed.")
    
    # Validate file size (max 5MB)
    banner_data = await banner.read()
    if len(banner_data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")
    
    # Save file
    import os
    from pathlib import Path
    
    upload_dir = Path(__file__).parent / "uploads" / "banners"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_extension = banner.filename.split('.')[-1]
    filename = f"{username}_banner_{datetime.now().timestamp()}.{file_extension}"
    file_path = upload_dir / filename
    
    with open(file_path, 'wb') as f:
        f.write(banner_data)
    
    # Update user banner URL
    user.banner_url = f"/uploads/banners/{filename}"
    db.commit()
    
    return {"message": "Banner uploaded successfully", "banner_url": user.banner_url}

@app.get("/uploads/{folder}/{filename}")
async def serve_upload(folder: str, filename: str):
    """Serve uploaded files"""
    from pathlib import Path
    file_path = Path(__file__).parent / "uploads" / folder / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.put("/api/admin/{username}/toggle-publish")
def toggle_publish(username: str, db: Session = Depends(get_db)):
    """Toggle profile publish status"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_published = not user.is_published
    db.commit()
    
    return {"is_published": user.is_published}

# Onboarding Flow API Routes

@app.post("/api/links/scrape-content")
async def scrape_link_content_endpoint(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Scrape content from a link URL for onboarding
    Extracts title, description, and first 200 words
    """
    from scraper_enhanced import scrape_link_content
    
    url = request.get('url')
    link_id = request.get('link_id')
    
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    try:
        # Scrape the content
        content = scrape_link_content(url)
        
        # If link_id provided, save to database
        if link_id:
            link = db.query(Link).filter(Link.id == link_id).first()
            if link:
                link.scraped_content = content.get('context_summary', '')
                db.commit()
        
        return {
            "success": True,
            "url": url,
            "title": content.get('title'),
            "meta_description": content.get('meta_description'),
            "preview_text": content.get('preview_text'),
            "link_type": content.get('link_type'),
            "full_content": content.get('full_content')
        }
    except Exception as e:
        logger.error(f"Error scraping content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to scrape content: {str(e)}")

@app.post("/api/links/{link_id}/generate-scripts")
async def generate_scripts_for_link_variations(
    link_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate 3 script variations (brief, standard, conversational) for a link
    Returns array of 3 scripts for frontend wizard
    """
    try:
        print(f"🔵 Generating scripts for link {link_id}")
        
        from scraper_enhanced import scrape_link_content
        
        link = db.query(Link).filter(Link.id == link_id).first()
        if not link:
            print(f"❌ Link not found: {link_id}")
            logger.error(f"Link not found: {link_id}")
            raise HTTPException(status_code=404, detail="Link not found")
        
        print(f"✅ Found link: {link.title} - {link.url}")
        
        user = db.query(User).filter(User.id == link.user_id).first()
        if not user:
            print(f"❌ User not found for link {link_id}")
            logger.error(f"User not found for link {link_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"✅ Found user: {user.display_name}")
        
        # Step 1: Scrape content if not already cached
        logger.info(f"Starting script generation for link {link_id}: {link.url}")
        
        if not link.scraped_content:
            print(f"🔍 Scraping content from {link.url}")
            logger.info(f"Scraping content from {link.url}")
            content = scrape_link_content(link.url)
            link.scraped_content = content.get('context_summary', '')
            db.commit()
            print(f"✅ Scraped content saved")
        else:
            print(f"📋 Using cached content for link {link_id}")
            logger.info(f"Using cached content for link {link_id}")
            content = {'title': link.title, 'meta_description': '', 'preview_text': link.scraped_content, 'link_type': 'website'}
        
        # Step 2: Generate 3 script variations using script_writer (supports OpenAI)
        print(f"✍️ Generating 3 script variations for link {link_id}")
        logger.info(f"Generating 3 script variations for link {link_id}")
        
        # Use script_writer which automatically uses OpenAI if available
        scripts_list = script_writer.generate_pitch_scripts(
            link_url=link.url,
            link_title=content.get('title', link.title),
            scraped_content=link.scraped_content,
            user_business_context=user.bio if user.bio else None,
            num_options=3
        )
        
        # Convert to dict format expected by rest of code
        scripts_dict = {
            'brief': scripts_list[0]['script'] if len(scripts_list) > 0 else '',
            'brief_word_count': scripts_list[0]['word_count'] if len(scripts_list) > 0 else 0,
            'standard': scripts_list[1]['script'] if len(scripts_list) > 1 else '',
            'standard_word_count': scripts_list[1]['word_count'] if len(scripts_list) > 1 else 0,
            'conversational': scripts_list[2]['script'] if len(scripts_list) > 2 else '',
            'conversational_word_count': scripts_list[2]['word_count'] if len(scripts_list) > 2 else 0,
        }
        
        print(f"✅ Scripts generated successfully")
        
        # Save scripts to link
        link.script_brief = scripts_dict['brief']
        link.script_standard = scripts_dict['standard']
        link.script_conversational = scripts_dict['conversational']
        db.commit()
        
        print(f"✅ Scripts saved to database")
        
        # Return as array (frontend expects array)
        scripts_array = [
            {
                "script": scripts_dict['brief'],
                "word_count": scripts_dict['brief_word_count']
            },
            {
                "script": scripts_dict['standard'],
                "word_count": scripts_dict['standard_word_count']
            },
            {
                "script": scripts_dict['conversational'],
                "word_count": scripts_dict['conversational_word_count']
            }
        ]
        
        logger.info(f"Successfully generated scripts for link {link_id}")
        print(f"✅ Returning {len(scripts_array)} scripts")
        
        return {
            "success": True,
            "link_id": link_id,
            "scripts": scripts_array
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR generating scripts: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error generating scripts for link {link_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/links/{link_id}/select-script")
async def select_script_for_link(
    link_id: int,
    request: dict,
    db: Session = Depends(get_db)
):
    """
    User selects which script variation they want to use
    Accepts either script_type OR direct script text
    """
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Accept either script_type (old way) or direct script text (new way from wizard)
    script_type = request.get('script_type')  # 'brief', 'standard', or 'conversational'
    custom_text = request.get('custom_text')  # User can also provide custom edited text
    script = request.get('script')  # Direct script text from wizard
    script_index = request.get('script_index')  # Which variation was selected (-1 for custom)
    
    if not script_type and not custom_text and not script:
        raise HTTPException(status_code=400, detail="Either script_type, custom_text, or script is required")
    
    # Save selected script
    if script:
        # New wizard flow - direct script text
        link.selected_script = script
        link.voice_message_text = script
    elif custom_text:
        link.selected_script = custom_text
        link.voice_message_text = custom_text
    elif script_type == 'brief':
        link.selected_script = link.script_brief
        link.voice_message_text = link.script_brief
    elif script_type == 'standard':
        link.selected_script = link.script_standard
        link.voice_message_text = link.script_standard
    elif script_type == 'conversational':
        link.selected_script = link.script_conversational
        link.voice_message_text = link.script_conversational
    else:
        raise HTTPException(status_code=400, detail="Invalid script_type")
    
    db.commit()
    
    logger.info(f"Script selected for link {link_id}: {len(link.selected_script)} characters")
    
    return {
        "success": True,
        "link_id": link_id,
        "selected_script": link.selected_script
    }

@app.post("/api/voice/clone")
async def create_voice_clone_onboarding(
    audio_sample: UploadFile = File(...),
    username: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Create voice clone for onboarding (one-time setup)
    Uses ElevenLabs API to create voice clone from audio sample
    """
    from voice_clone import create_voice_from_sample
    import os
    from pathlib import Path
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if ELEVENLABS_API_KEY is set
    if not os.getenv('ELEVENLABS_API_KEY'):
        raise HTTPException(
            status_code=500, 
            detail="Voice cloning is not configured. Please set ELEVENLABS_API_KEY environment variable."
        )
    
    try:
        # Validate audio file
        if not audio_sample.content_type or not audio_sample.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid audio file type. Please upload an audio file.")
        
        # Save audio sample temporarily
        audio_dir = Path(__file__).parent / "audio" / "voice_samples"
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        sample_filename = f"{username}_sample_{datetime.now().timestamp()}.mp3"
        sample_path = audio_dir / sample_filename
        
        audio_data = await audio_sample.read()
        
        # Validate file size (should be reasonable for 30-60 seconds)
        if len(audio_data) < 100000:  # Less than 100KB
            raise HTTPException(status_code=400, detail="Audio file too short. Please record at least 30 seconds.")
        
        if len(audio_data) > 10000000:  # More than 10MB
            raise HTTPException(status_code=400, detail="Audio file too large. Please keep recording under 2 minutes.")
        
        with open(sample_path, 'wb') as f:
            f.write(audio_data)
        
        logger.info(f"Saved audio sample for user {username}: {sample_path}")
        
        # Create voice clone with ElevenLabs
        voice_id = create_voice_from_sample(
            sample_path=str(sample_path),
            voice_name=user.display_name,
            user_id=user.id
        )
        
        if not voice_id:
            raise HTTPException(
                status_code=500, 
                detail="Failed to create voice clone. Please check your audio quality and try again."
            )
        
        # Save voice_id to user
        user.voice_clone_id = voice_id
        user.voice_sample_path = f"voice_samples/{sample_filename}"
        db.commit()
        
        logger.info(f"Voice clone created successfully for user {username}: {voice_id}")
        
        return {
            "success": True,
            "voice_id": voice_id,
            "message": "Voice clone created successfully!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating voice clone: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create voice clone: {str(e)}")

@app.post("/api/links/{link_id}/generate-audio")
async def generate_audio_for_link(
    link_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate audio for a link using user's voice clone
    """
    from voice_clone import generate_voice_audio
    from pathlib import Path
    
    # Check if ELEVENLABS_API_KEY is set
    if not os.getenv('ELEVENLABS_API_KEY'):
        raise HTTPException(
            status_code=500, 
            detail="Audio generation is not configured. Please set ELEVENLABS_API_KEY environment variable."
        )
    
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    user = db.query(User).filter(User.id == link.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.voice_clone_id:
        raise HTTPException(
            status_code=400, 
            detail="Voice clone not set up. Please create a voice clone first by recording your voice."
        )
    
    if not link.voice_message_text:
        raise HTTPException(
            status_code=400, 
            detail="No script selected for this link. Please select a script first."
        )
    
    try:
        # Use voice_message_text
        text = link.voice_message_text
        
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Script text is empty")
        
        logger.info(f"Generating audio for link {link_id} with voice {user.voice_clone_id}")
        
        # Generate audio file
        audio_dir = Path(__file__).parent / "audio" / "link_voices"
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        audio_filename = f"link_{link_id}_{datetime.now().timestamp()}.mp3"
        audio_path = audio_dir / audio_filename
        
        success = generate_voice_audio(
            text=text,
            voice_id=user.voice_clone_id,
            output_path=str(audio_path)
        )
        
        if not success:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate audio. Please check your voice clone and try again."
            )
        
        # Verify file was created
        if not audio_path.exists():
            raise HTTPException(status_code=500, detail="Audio file was not created")
        
        # Delete old audio if exists
        if link.voice_message_audio:
            old_audio_path = Path(__file__).parent / "audio" / link.voice_message_audio
            if old_audio_path.exists():
                try:
                    old_audio_path.unlink()
                except Exception as e:
                    logger.warning(f"Could not delete old audio file: {e}")
        
        # Save audio path to link
        link.voice_message_audio = f"link_voices/{audio_filename}"
        link.voice_message_text = text
        db.commit()
        
        logger.info(f"Audio generated successfully for link {link_id}: {audio_filename}")
        
        return {
            "success": True,
            "link_id": link_id,
            "audio_path": f"link_voices/{audio_filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating audio for link {link_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")

@app.post("/api/profile/publish")
async def publish_user_profile(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Publish user's profile (final step of onboarding)
    """
    username = request.get('username')
    
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Publish the profile
    user.is_published = True
    db.commit()
    
    return {
        "success": True,
        "message": "Profile published successfully!",
        "profile_url": f"/{username}"
    }


@app.post("/api/links/{link_id}/generate-script")
async def generate_script_for_link(
    link_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered sales script for a link (single script - legacy)
    Analyzes the destination and creates a pitch script
    """
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    try:
        # Scrape the link destination
        scraped_data = script_writer.scrape_link_content(link.url)
        scraped_content = scraped_data.get('scraped_content', '')
        
        # Get user's bio as business context
        user = db.query(User).filter(User.id == link.user_id).first()
        business_context = user.bio if user and user.bio else None
        
        # Generate the script
        script = script_writer.generate_pitch_script(
            link_url=link.url,
            link_title=link.title,
            scraped_content=scraped_content,
            user_business_context=business_context
        )
        
        # Save script and scraped content to link
        link.ai_generated_script = script
        link.scraped_content = scraped_content
        db.commit()
        
        return {
            "success": True,
            "script": script,
            "link_id": link_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating script: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}")

@app.post("/api/links/{link_id}/regenerate-script")
async def regenerate_script_for_link(
    link_id: int,
    db: Session = Depends(get_db)
):
    """
    Regenerate AI script for a link (uses cached scraped content if available)
    """
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    try:
        # Use cached scraped content if available, otherwise scrape again
        if link.scraped_content:
            scraped_content = link.scraped_content
        else:
            scraped_data = script_writer.scrape_link_content(link.url)
            scraped_content = scraped_data.get('scraped_content', '')
            link.scraped_content = scraped_content
        
        # Get user's bio as business context
        user = db.query(User).filter(User.id == link.user_id).first()
        business_context = user.bio if user and user.bio else None
        
        # Generate new script
        script = script_writer.generate_pitch_script(
            link_url=link.url,
            link_title=link.title,
            scraped_content=scraped_content,
            user_business_context=business_context
        )
        
        # Update script
        link.ai_generated_script = script
        db.commit()
        
        return {
            "success": True,
            "script": script,
            "link_id": link_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error regenerating script: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to regenerate script: {str(e)}")

@app.post("/api/links/{link_id}/record-voice")
async def record_voice_for_link(
    link_id: int,
    audio: UploadFile = File(...),
    text: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload recorded audio for a link's pitch
    User records their own voice reading the script
    """
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    try:
        # Validate audio file
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid audio file type")
        
        # Read audio data
        audio_data = await audio.read()
        
        # Validate size (max 5MB)
        if len(audio_data) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file too large (max 5MB)")
        
        # Save audio file
        from pathlib import Path
        audio_dir = Path(__file__).parent / "audio" / "link_voices"
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        filename = f"link_{link_id}_{datetime.now().timestamp()}.webm"
        audio_path = audio_dir / filename
        
        with open(audio_path, 'wb') as f:
            f.write(audio_data)
        
        # Delete old audio if exists
        if link.voice_message_audio:
            old_audio_path = Path(__file__).parent / "audio" / link.voice_message_audio
            if old_audio_path.exists():
                old_audio_path.unlink()
        
        # Update link
        link.voice_message_text = text
        link.voice_message_audio = f"link_voices/{filename}"
        db.commit()
        
        return {
            "success": True,
            "audio_path": f"link_voices/{filename}",
            "text": text,
            "message": "Voice recording saved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving voice recording: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save recording: {str(e)}")

@app.post("/api/links/{link_id}/generate-ai-voice")
async def generate_ai_voice_for_link(
    link_id: int,
    text: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Generate AI voice for a link using the user's voice clone
    """
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    user = db.query(User).filter(User.id == link.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.voice_clone_id:
        raise HTTPException(status_code=400, detail="Voice clone not set up. Please create a voice clone first.")
    
    try:
        # Delete old audio if exists
        if link.voice_message_audio:
            VoiceAIService.delete_audio_file(link.voice_message_audio)
        
        # Generate AI voice
        audio_path = VoiceAIService.generate_with_voice_clone(
            text=text,
            voice_id=user.voice_clone_id,
            user_id=user.id,
            purpose=f"link_{link_id}"
        )
        
        if not audio_path:
            raise HTTPException(status_code=500, detail="Failed to generate AI voice")
        
        # Update link
        link.voice_message_text = text
        link.voice_message_audio = audio_path
        db.commit()
        
        return {
            "success": True,
            "audio_path": audio_path,
            "text": text,
            "message": "AI voice generated successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating AI voice: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate AI voice: {str(e)}")

# Voice AI Routes

@app.post("/api/voice/clone/{username}", response_model=VoiceCloneResponse)
async def create_voice_clone(
    username: str,
    voice_samples: List[UploadFile] = File(...),
    voice_name: str = Form(...),
    language: str = Form(default="en-US"),
    tags: str = Form(default=""),
    description: str = Form(default=""),
    remove_noise: bool = Form(default=True),
    db: Session = Depends(get_db)
):
    """
    Create voice clone from recorded samples using Inworld AI
    
    This endpoint handles the complete voice cloning process:
    1. Receives 1-3 voice samples from browser recording
    2. Sends samples to Inworld AI to create voice clone
    3. Saves voice_id to user profile
    4. Returns success with voice_id
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate number of samples
    if not voice_samples or len(voice_samples) == 0:
        raise HTTPException(status_code=400, detail="At least one voice sample is required")
    
    if len(voice_samples) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 voice samples allowed")
    
    # Read all uploaded files
    samples_data = []
    for sample in voice_samples:
        voice_data = await sample.read()
        
        # Validate file size per sample (5-15 seconds of audio, roughly 100KB-2MB)
        if len(voice_data) < 50000:  # Less than ~50KB
            raise HTTPException(status_code=400, detail=f"Voice sample '{sample.filename}' too short. Please record 5-15 seconds.")
        
        if len(voice_data) > 3000000:  # More than ~3MB
            raise HTTPException(status_code=400, detail=f"Voice sample '{sample.filename}' too large. Please keep under 20 seconds.")
        
        samples_data.append(voice_data)
    
    try:
        # Create voice clone with Inworld AI
        result = VoiceAIService.create_voice_clone(
            voice_samples=samples_data,
            voice_name=voice_name,
            language=language,
            tags=tags,
            description=description,
            remove_noise=remove_noise,
            username=username
        )
        
        if not result or not result.get("voice_id"):
            raise HTTPException(status_code=500, detail="Failed to create voice clone")
        
        # Update user with voice clone ID
        user.voice_clone_id = result["voice_id"]
        if result.get("sample_paths"):
            user.voice_sample_path = result["sample_paths"][0]  # Save first sample path
        db.commit()
        
        return VoiceCloneResponse(
            voice_id=result["voice_id"],
            sample_path=result.get("sample_paths", [None])[0],
            message=result.get("message", "Voice clone created successfully!")
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating voice clone: {str(e)}")


@app.post("/api/voice/test/{username}")
async def test_voice(
    username: str,
    text: str = Form(...),
    db: Session = Depends(get_db)
):
    """Test the user's cloned voice with custom text"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.voice_clone_id:
        raise HTTPException(status_code=400, detail="Voice clone not set. Please provide your voice ID first.")
    
    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if len(text) > 500:
        raise HTTPException(status_code=400, detail="Text too long. Maximum 500 characters for testing.")
    
    try:
        # Generate test audio
        audio_bytes = VoiceAIService.test_voice_clone(
            text=text,
            voice_id=user.voice_clone_id
        )
        
        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate test audio")
        
        # Return audio as response
        from fastapi.responses import Response
        return Response(content=audio_bytes, media_type="audio/mpeg")
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing voice: {str(e)}")

@app.post("/api/voice/generate-link/{username}/{link_id}", response_model=VoiceMessageResponse)
async def generate_link_voice(
    username: str,
    link_id: int,
    request: GenerateVoiceRequest,
    db: Session = Depends(get_db)
):
    """Generate voice message for a specific link"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    link = db.query(Link).filter(Link.id == link_id, Link.user_id == user.id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    if not user.voice_clone_id:
        raise HTTPException(status_code=400, detail="Voice clone not set up. Please upload a voice sample first.")
    
    try:
        # Delete old audio if exists
        if link.voice_message_audio:
            VoiceAIService.delete_audio_file(link.voice_message_audio)
        
        # Generate new voice message
        audio_path = VoiceAIService.generate_with_voice_clone(
            text=request.text,
            voice_id=user.voice_clone_id,
            user_id=user.id,
            purpose=f"link_{link_id}"
        )
        
        if not audio_path:
            raise HTTPException(status_code=500, detail="Failed to generate voice message")
        
        # Update link with voice message
        link.voice_message_text = request.text
        link.voice_message_audio = audio_path
        db.commit()
        
        return VoiceMessageResponse(
            audio_path=audio_path,
            text=request.text,
            message="Voice message generated successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating voice: {str(e)}")

@app.delete("/api/voice/link/{username}/{link_id}")
async def delete_link_voice(
    username: str,
    link_id: int,
    db: Session = Depends(get_db)
):
    """Delete voice message from a link"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    link = db.query(Link).filter(Link.id == link_id, Link.user_id == user.id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    if link.voice_message_audio:
        VoiceAIService.delete_audio_file(link.voice_message_audio)
        link.voice_message_text = None
        link.voice_message_audio = None
        db.commit()
    
    return {"message": "Voice message deleted successfully"}

@app.post("/api/voice/generate-welcome/{username}", response_model=VoiceMessageResponse)
async def generate_welcome_message(
    username: str,
    request: GenerateWelcomeRequest,
    db: Session = Depends(get_db)
):
    """Generate welcome message for user profile"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.voice_clone_id:
        raise HTTPException(status_code=400, detail="Voice clone not set up. Please upload a voice sample first.")
    
    try:
        # Delete old audio if exists
        if user.welcome_message_audio:
            VoiceAIService.delete_audio_file(user.welcome_message_audio)
        
        # Generate new welcome message
        audio_path = VoiceAIService.generate_with_voice_clone(
            text=request.text,
            voice_id=user.voice_clone_id,
            user_id=user.id,
            purpose="welcome"
        )
        
        if not audio_path:
            raise HTTPException(status_code=500, detail="Failed to generate welcome message")
        
        # Update user with welcome message
        user.welcome_message_text = request.text
        user.welcome_message_audio = audio_path
        user.welcome_message_type = request.message_type
        db.commit()
        
        return VoiceMessageResponse(
            audio_path=audio_path,
            text=request.text,
            message="Welcome message generated successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating welcome message: {str(e)}")

@app.get("/audio/{folder}/{filename}")
async def get_audio_with_folder(folder: str, filename: str):
    """Serve audio files from subfolders"""
    from pathlib import Path
    audio_path = Path(__file__).parent / "audio" / folder / filename
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(audio_path, media_type="audio/mpeg")

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve audio files"""
    from pathlib import Path
    audio_path = Path(__file__).parent / "audio" / filename
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(audio_path, media_type="audio/mpeg")

@app.get("/api/voice/check-clone/{username}")
async def check_voice_clone(username: str, db: Session = Depends(get_db)):
    """Check if user has a voice clone set up"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    has_clone = bool(user.voice_clone_id)
    
    return {
        "has_clone": has_clone,
        "voice_clone_id": user.voice_clone_id if has_clone else None,
        "voice_sample_path": user.voice_sample_path if has_clone else None
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
