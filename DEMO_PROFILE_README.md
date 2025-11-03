# Demo Profile: Beauty Influencer "beautybyluna"

## Overview
A professionally crafted demo profile showcasing VoiceTree's features for a beauty influencer persona. This profile demonstrates how content creators can use VoiceTree to create an engaging, voice-enhanced link-in-bio experience.

## Profile Details

### User Information
- **Username**: `beautybyluna`
- **Password**: `demo123`
- **Display Name**: Luna Martinez
- **Email**: luna@beautybyluna.com
- **Bio**: "Beauty creator | Skincare obsessed | Sharing my journey to glowing skin ✨"
- **Avatar**: Initials "LM" (auto-generated from display name)
- **Status**: Published (publicly accessible)
- **Voice Clone ID**: `demo_voice_id_placeholder`

### Demo Statistics
- **Profile Views**: 247
- **Total Link Clicks**: 89
- **Voice Message Plays**: 156
- **Auto-approve Voice**: Enabled

### Welcome Message
"Hey! Welcome to my beauty world. I'm so excited to share my favorite products and tips with you!"

## Links (6 Total)

### 1. 📸 Instagram (@beautybyluna)
- **URL**: https://instagram.com/beautybyluna
- **Platform**: Instagram
- **Voice Message**: "Follow me on Instagram for daily skincare tips and real, unfiltered reviews of products I actually use"
- **Click Count**: 34

### 2. 🎥 YouTube Channel
- **URL**: https://youtube.com/@beautybyluna
- **Platform**: YouTube
- **Voice Message**: "Subscribe to my YouTube for in-depth tutorials and my honest thoughts on trending beauty products"
- **Click Count**: 28

### 3. 💄 Amazon Storefront
- **URL**: https://amazon.com/shop/beautybyluna
- **Platform**: Amazon
- **Voice Message**: "Check out my curated Amazon favorites - these are products I genuinely love and recommend"
- **Click Count**: 15

### 4. ✉️ Newsletter
- **URL**: https://beautybyluna.substack.com
- **Platform**: Substack
- **Voice Message**: "Join my weekly newsletter where I share my current routines and insider beauty secrets"
- **Click Count**: 8

### 5. 🎙️ Podcast - "Glow Up Stories"
- **URL**: https://podcasts.apple.com/glowupstories
- **Platform**: Podcast
- **Voice Message**: "Listen to my podcast where I interview beauty experts and share real stories about self-confidence"
- **Click Count**: 3

### 6. 🛍️ Shop My Favorites
- **URL**: https://shopmy.us/beautybyluna
- **Platform**: ShopMy
- **Voice Message**: "Browse my shop for all the products that have transformed my skin and makeup routine"
- **Click Count**: 1

## How to Seed This Profile

### Option 1: Python Script (Recommended)
```bash
cd voicetree/backend
python seed_demo_profile.py
```

### Option 2: SQL Script
```bash
cd voicetree/backend
sqlite3 voicetree.db < seed_demo_profile.sql
```

## Accessing the Demo Profile

### Public Profile Page
```
http://localhost:8000/beautybyluna
```
or
```
https://yourdomain.com/beautybyluna
```

### Login to Dashboard
```
http://localhost:8000/login
Username: beautybyluna
Password: demo123
```

## Features Demonstrated

### 1. Voice-Enhanced Links
Each link has a personalized voice message that plays when visitors hover over or tap the link, creating an engaging and personal experience.

### 2. Professional Bio
A concise, engaging bio that clearly communicates the creator's niche and value proposition.

### 3. Strategic Link Order
Links are ordered by priority:
1. Primary social media (Instagram) - highest engagement
2. Content platform (YouTube) - long-form content
3. Monetization (Amazon) - product recommendations
4. Direct connection (Newsletter) - owned audience
5. Additional content (Podcast) - bonus engagement
6. Shopping platform (ShopMy) - additional monetization

### 4. Platform Detection
Each link is tagged with its platform type for proper icon display and tracking.

### 5. Analytics Ready
Pre-populated with realistic click counts to demonstrate analytics features.

### 6. Voice Clone Integration
Voice clone ID is set up for AI-generated voice messages (placeholder for demo).

## Use Cases

### For Demos
- Show potential customers how VoiceTree works
- Demonstrate voice-enhanced features
- Showcase professional profile design
- Highlight analytics capabilities

### For Testing
- Test new features on a populated profile
- Verify voice message playback
- Test link tracking and analytics
- Validate UI/UX improvements

### For Development
- Use as reference for profile structure
- Test database queries and relationships
- Validate API endpoints
- Debug frontend components

## Customization

To customize this profile for different niches, modify the following in `seed_demo_profile.py`:

1. **User Details**: Change username, display name, bio, and email
2. **Links**: Update titles, URLs, platforms, and voice messages
3. **Statistics**: Adjust view counts, clicks, and engagement metrics
4. **Voice Clone**: Update voice_clone_id for different voice personalities

## Resetting the Demo Profile

The seed script automatically deletes and recreates the profile if it already exists, so you can run it multiple times safely:

```bash
python seed_demo_profile.py
```

## Notes

- All URLs in the demo are examples and may not be real pages
- Voice audio files are not pre-generated (will be created on-demand when voice AI is active)
- Profile photo uses initials "LM" as a placeholder
- Password hash is for "demo123" - change for production use
- Demo statistics are static - they won't increment during testing

## Security Considerations

⚠️ **Important**: This demo profile should NOT be used in production without:
1. Changing the password to something secure
2. Using a real email address
3. Removing or updating placeholder voice IDs
4. Validating all URLs are correct and accessible

## Integration with VoiceTree Features

This profile is designed to work seamlessly with:
- ✅ Voice AI message generation (ElevenLabs integration)
- ✅ Click tracking and analytics
- ✅ Profile view counting
- ✅ Link ordering and management
- ✅ Platform icon detection
- ✅ User authentication
- ✅ Dashboard editing
- ✅ Public profile display

## Future Enhancements

Potential additions to make the demo even better:
- Pre-generated voice audio files
- Sample profile banner image
- Additional demo profiles (different niches)
- Sample analytics data over time
- Example voice messages from visitors
