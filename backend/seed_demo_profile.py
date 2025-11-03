"""
Seed script to create demo beauty influencer profile
Run with: python seed_demo_profile.py
"""
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Link
import bcrypt

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def create_demo_profile():
    """Create beautybyluna demo profile"""
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == "beautybyluna").first()
        if existing_user:
            print("❌ User 'beautybyluna' already exists. Deleting and recreating...")
            db.delete(existing_user)
            db.commit()
        
        # Create demo user
        print("Creating demo user: beautybyluna")
        
        # Hash a demo password
        password = "demo123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        demo_user = User(
            username="beautybyluna",
            email="luna@beautybyluna.com",
            password_hash=password_hash,
            display_name="Luna Martinez",
            bio="Beauty creator | Skincare obsessed | Sharing my journey to glowing skin ✨",
            avatar_url=None,  # Will use initials "LM"
            banner_url=None,
            is_published=True,
            imported_from_linktree=False,
            voice_clone_id="demo_voice_id_placeholder",  # Placeholder voice ID
            voice_sample_path=None,
            welcome_message_text="Hey! Welcome to my beauty world. I'm so excited to share my favorite products and tips with you!",
            welcome_message_audio=None,
            welcome_message_type="static",
            profile_views=247,  # Start with some demo stats
            total_link_clicks=89,
            voice_message_plays=156,
            auto_approve_voice=True,
            last_login=datetime.now()
        )
        
        db.add(demo_user)
        db.flush()  # Get the user ID
        
        print(f"✓ Created user: {demo_user.username} (ID: {demo_user.id})")
        
        # Create links with voice messages
        links_data = [
            {
                "title": "📸 Instagram (@beautybyluna)",
                "url": "https://instagram.com/beautybyluna",
                "description": "Follow for daily skincare tips",
                "platform": "instagram",
                "voice_message_text": "Follow me on Instagram for daily skincare tips and real, unfiltered reviews of products I actually use",
                "order": 1,
                "click_count": 34
            },
            {
                "title": "🎥 YouTube Channel",
                "url": "https://youtube.com/@beautybyluna",
                "description": "In-depth tutorials and reviews",
                "platform": "youtube",
                "voice_message_text": "Subscribe to my YouTube for in-depth tutorials and my honest thoughts on trending beauty products",
                "order": 2,
                "click_count": 28
            },
            {
                "title": "💄 Amazon Storefront",
                "url": "https://amazon.com/shop/beautybyluna",
                "description": "My curated favorites",
                "platform": "amazon",
                "voice_message_text": "Check out my curated Amazon favorites - these are products I genuinely love and recommend",
                "order": 3,
                "click_count": 15
            },
            {
                "title": "✉️ Newsletter",
                "url": "https://beautybyluna.substack.com",
                "description": "Weekly beauty secrets",
                "platform": "substack",
                "voice_message_text": "Join my weekly newsletter where I share my current routines and insider beauty secrets",
                "order": 4,
                "click_count": 8
            },
            {
                "title": "🎙️ Podcast - \"Glow Up Stories\"",
                "url": "https://podcasts.apple.com/glowupstories",
                "description": "Beauty expert interviews",
                "platform": "podcast",
                "voice_message_text": "Listen to my podcast where I interview beauty experts and share real stories about self-confidence",
                "order": 5,
                "click_count": 3
            },
            {
                "title": "🛍️ Shop My Favorites",
                "url": "https://shopmy.us/beautybyluna",
                "description": "All my favorite products",
                "platform": "shopmy",
                "voice_message_text": "Browse my shop for all the products that have transformed my skin and makeup routine",
                "order": 6,
                "click_count": 1
            }
        ]
        
        print("\nCreating links:")
        for link_data in links_data:
            link = Link(
                user_id=demo_user.id,
                title=link_data["title"],
                url=link_data["url"],
                description=link_data.get("description"),
                platform=link_data.get("platform"),
                voice_message_text=link_data["voice_message_text"],
                voice_message_audio=None,  # Will be generated when needed
                is_active=True,
                order=link_data["order"],
                click_count=link_data.get("click_count", 0)
            )
            db.add(link)
            print(f"  ✓ {link.title}")
        
        # Commit all changes
        db.commit()
        
        print("\n" + "="*80)
        print("✅ DEMO PROFILE CREATED SUCCESSFULLY!")
        print("="*80)
        print(f"\nProfile Details:")
        print(f"  Username: beautybyluna")
        print(f"  Password: {password}")
        print(f"  Display Name: {demo_user.display_name}")
        print(f"  Bio: {demo_user.bio}")
        print(f"  Published: {demo_user.is_published}")
        print(f"  Voice Clone ID: {demo_user.voice_clone_id}")
        print(f"  Links Created: {len(links_data)}")
        print(f"\nProfile URL: http://localhost:8000/beautybyluna")
        print(f"Login URL: http://localhost:8000/login")
        print("\n" + "="*80)
        
        return demo_user
        
    except Exception as e:
        print(f"\n❌ Error creating demo profile: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("VOICETREE DEMO PROFILE SEEDER")
    print("="*80 + "\n")
    
    user = create_demo_profile()
    
    if user:
        print("\n🎉 Demo profile is ready to showcase!")
        sys.exit(0)
    else:
        print("\n❌ Failed to create demo profile")
        sys.exit(1)
