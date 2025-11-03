# Selfie.fm Complete Onboarding Flow Implementation

This document details the complete end-to-end onboarding implementation for Selfie.fm, allowing users to go from importing links to publishing their voice-enabled bio page in 3-5 minutes.

## Overview

The onboarding flow consists of 5 main steps:
1. **Import Links** - From Linktree or manual entry
2. **AI Generate Scripts** - 3 variations per link (brief, standard, conversational)
3. **Voice Cloning** - One-time voice sample recording
4. **Audio Generation** - AI generates audio for each link
5. **Validate & Publish** - Preview and publish live page

## Database Schema Changes

### New Fields Added to `Link` Model

```python
# Script variations
script_brief: TEXT - 10-15 word script
script_standard: TEXT - 25-40 word script  
script_conversational: TEXT - 40-60 word script
selected_script: TEXT - User's chosen script

# Content scraping
scraped_content: TEXT - Page content (already exists)
```

### Migration

Run the migration to add new fields:
```bash
cd voicetree/backend
python3 migrate_add_script_variations.py
```

## Backend Components

### 1. Enhanced Scraper (`scraper_enhanced.py`)

Extracts comprehensive content from destination URLs:
- Page title (<title> tag)
- Meta description
- First 200 words of main content
- Identifies link type (course, coaching, product, etc.)

**Usage:**
```python
from scraper_enhanced import scrape_link_content

content = scrape_link_content("https://example.com/course")
# Returns: {
#   'title': '...',
#   'meta_description': '...',
#   'preview_text': '...',
#   'full_content': '...',
#   'link_type': 'course',
#   'context_summary': '...'
# }
```

### 2. AI Script Generator (`script_generator.py`)

Generates 3 script variations using Claude or OpenAI:
- **Brief**: 10-15 words (quick, punchy)
- **Standard**: 25-40 words (balanced)
- **Conversational**: 40-60 words (natural, friendly)

**Requirements:**
- Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` environment variable

**Usage:**
```python
from script_generator import generate_link_scripts

scripts = generate_link_scripts(
    url="https://example.com/course",
    title="Master Python Programming",
    description="Learn Python from scratch",
    preview_text="Course content...",
    link_type="course",
    user_name="Sarah"
)
# Returns scripts with word counts
```

### 3. Voice Clone Manager (`voice_clone.py`)

Integrates with ElevenLabs API for voice cloning and audio generation:

**Requirements:**
- Set `ELEVENLABS_API_KEY` environment variable

**Key Functions:**
- `create_voice_from_sample()` - Create voice clone from audio sample
- `generate_voice_audio()` - Generate audio from text using voice clone

**Usage:**
```python
from voice_clone import create_voice_from_sample, generate_voice_audio

# Create voice clone (one-time)
voice_id = create_voice_from_sample(
    sample_path="path/to/audio.mp3",
    voice_name="User Name",
    user_id=123
)

# Generate audio
success = generate_voice_audio(
    text="Check out my awesome course!",
    voice_id=voice_id,
    output_path="output/audio.mp3"
)
```

## API Endpoints

### Onboarding Flow Endpoints

#### 1. Scrape Link Content
```
POST /api/links/scrape-content
Body: {
  "url": "https://example.com/product",
  "link_id": 123  // optional
}
Response: {
  "success": true,
  "title": "Product Name",
  "meta_description": "...",
  "preview_text": "...",
  "link_type": "product"
}
```

#### 2. Generate Script Variations
```
POST /api/links/{link_id}/generate-scripts
Response: {
  "success": true,
  "link_id": 123,
  "scripts": {
    "brief": {
      "text": "Check out my course!",
      "word_count": 4
    },
    "standard": {
      "text": "I'm excited to share my new Python course...",
      "word_count": 32
    },
    "conversational": {
      "text": "Hey! So I wanted to share this awesome course...",
      "word_count": 45
    }
  }
}
```

#### 3. Select Script Variation
```
POST /api/links/{link_id}/select-script
Body: {
  "script_type": "standard"  // or "brief", "conversational"
  // OR
  "custom_text": "User's edited version"
}
Response: {
  "success": true,
  "link_id": 123,
  "selected_script": "..."
}
```

#### 4. Create Voice Clone
```
POST /api/voice/clone
Form Data:
  - audio_sample: File (30-60 seconds MP3/WAV)
  - username: string
Response: {
  "success": true,
  "voice_id": "elevenlabs_voice_id_here",
  "message": "Voice clone created successfully!"
}
```

#### 5. Generate Audio for Link
```
POST /api/links/{link_id}/generate-audio
Response: {
  "success": true,
  "link_id": 123,
  "audio_path": "link_voices/link_123_1234567890.mp3"
}
```

#### 6. Publish Profile
```
POST /api/profile/publish
Body: {
  "username": "johndoe"
}
Response: {
  "success": true,
  "message": "Profile published successfully!",
  "profile_url": "/johndoe"
}
```

## Frontend Flow (To Be Implemented)

### Onboarding Wizard Component

Create a multi-step wizard in `dashboard.html`:

```javascript
// Step 1: Import Links (existing)
// User imports from Linktree or adds manually

// Step 2: Generate Scripts
async function generateScriptsForAllLinks() {
  const links = getUserLinks();
  showLoadingState("Generating scripts...");
  
  for (const link of links) {
    const response = await fetch(`/api/links/${link.id}/generate-scripts`, {
      method: 'POST'
    });
    const data = await response.json();
    displayScriptOptions(link.id, data.scripts);
  }
}

// Step 3: Record Voice Sample
async function recordVoiceSample() {
  const recorder = new MediaRecorder(stream);
  // Record 30-60 seconds
  // Upload to /api/voice/clone
}

// Step 4: Generate Audio for All Links
async function generateAllAudio() {
  const links = getUserLinks();
  showLoadingState("Generating audio...");
  
  for (const link of links) {
    await fetch(`/api/links/${link.id}/generate-audio`, {
      method: 'POST'
    });
  }
  
  showSuccess("Audio generated for all links!");
}

// Step 5: Publish
async function publishProfile() {
  await fetch('/api/profile/publish', {
    method: 'POST',
    body: JSON.stringify({ username: currentUser })
  });
  
  window.location.href = `/${currentUser}`;
}
```

### UI Components Needed

1. **Script Selection Cards**
   - Display 3 script options side by side
   - Show word count for each
   - Radio buttons to select
   - Edit button to customize
   - "Regenerate" button for new options

2. **Voice Recording Interface**
   - Timer (30-60 seconds)
   - Start/Stop recording buttons
   - Audio playback preview
   - Re-record button

3. **Progress Indicator**
   - Step 1: ✓ Import Links
   - Step 2: ⏳ Generate Scripts
   - Step 3: ⏳ Record Voice
   - Step 4: ⏳ Generate Audio
   - Step 5: ⏳ Publish

4. **Audio Preview Players**
   - For each link
   - Play/Pause buttons
   - Regenerate option

## Testing

### Test the Complete Flow

1. **Setup Environment Variables**
```bash
export ANTHROPIC_API_KEY="your_key_here"
# OR
export OPENAI_API_KEY="your_key_here"

export ELEVENLABS_API_KEY="your_key_here"
```

2. **Run Migration**
```bash
cd voicetree/backend
python3 migrate_add_script_variations.py
```

3. **Test Individual Components**

**Test Scraper:**
```bash
cd voicetree/backend
python3 scraper_enhanced.py
```

**Test Script Generator:**
```bash
cd voicetree/backend
python3 script_generator.py
```

**Test Voice Clone:**
```bash
cd voicetree/backend
python3 voice_clone.py
```

4. **Test API Endpoints**
```bash
# Start server
cd voicetree/backend
uvicorn app:app --reload

# In another terminal, test endpoints:
curl -X POST http://localhost:8000/api/links/scrape-content \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Deployment Considerations

### Environment Variables Required

```bash
# AI Script Generation (choose one)
ANTHROPIC_API_KEY=sk-ant-...
# OR
OPENAI_API_KEY=sk-...

# Voice Cloning & Audio Generation
ELEVENLABS_API_KEY=...

# Existing variables
DATABASE_URL=...
SECRET_KEY=...
```

### API Rate Limits

- **Anthropic Claude**: 50 requests/min (free tier)
- **OpenAI GPT-4**: 10,000 requests/min (paid tier)
- **ElevenLabs**: 
  - Free tier: 10,000 characters/month
  - Starter: 30,000 characters/month
  - Creator: 100,000 characters/month

### Storage Requirements

- Voice samples: ~1-2 MB per user
- Generated audio: ~50-100 KB per link
- Estimate: 5-10 MB per user on average

## Timeline Estimates

### Development Time
- ✓ Backend implementation: **COMPLETE**
  - Database migration: ✓
  - Enhanced scraper: ✓
  - AI script generator: ✓
  - Voice clone integration: ✓
  - API endpoints: ✓

- Frontend implementation: **3-4 hours**
  - Onboarding wizard UI: 2 hours
  - Voice recording interface: 1 hour
  - Script selection UI: 1 hour

### User Onboarding Time
- Step 1 (Import): 30 seconds
- Step 2 (Scripts): 1-2 minutes (review/select)
- Step 3 (Voice): 1 minute (record)
- Step 4 (Audio): 30 seconds (auto-generate)
- Step 5 (Publish): 10 seconds

**Total: 3-5 minutes** ✓

## Next Steps

1. **Frontend Implementation**
   - Create onboarding wizard component
   - Build script selection UI
   - Implement voice recording interface
   - Add progress indicators

2. **Testing**
   - End-to-end testing with real users
   - Test with various link types
   - Verify audio quality
   - Check mobile responsiveness

3. **Polish**
   - Error handling
   - Loading states
   - Success messages
   - Help tooltips

4. **Launch**
   - Deploy to production
   - Monitor API usage
   - Collect user feedback
   - Iterate based on usage

## Troubleshooting

### Common Issues

**Script Generation Fails**
- Check API key is set correctly
- Verify API quota/limits
- Check network connectivity

**Voice Clone Creation Fails**
- Ensure audio sample is 30-60 seconds
- Check file format (MP3/WAV)
- Verify ElevenLabs API key

**Audio Generation Slow**
- ElevenLabs API can take 2-5 seconds per audio
- Consider implementing queue system for bulk generation
- Show progress indicators to user

## Support

For questions or issues:
1. Check API documentation:
   - Anthropic: https://docs.anthropic.com/
   - OpenAI: https://platform.openai.com/docs
   - ElevenLabs: https://elevenlabs.io/docs

2. Review logs in backend console
3. Test individual components in isolation
4. Contact support if API issues persist
