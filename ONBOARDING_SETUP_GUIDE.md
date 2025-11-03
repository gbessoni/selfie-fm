# Selfie.fm Onboarding Flow - Setup Guide

## Quick Start

This guide will help you set up and test the complete onboarding flow that was just implemented.

## What's Been Implemented

### ✅ Backend Components (COMPLETE)

1. **Database Migration**
   - New fields for 3 script variations per link
   - Migration script: `migrate_add_script_variations.py`

2. **Enhanced Scraper** (`scraper_enhanced.py`)
   - Extracts page title, meta description, and content
   - Identifies link type (course, coaching, product, etc.)
   - Returns structured data for AI processing

3. **AI Script Generator** (`script_generator.py`)
   - Generates 3 script variations per link:
     - Brief (10-15 words)
     - Standard (25-40 words)
     - Conversational (40-60 words)
   - Supports both Anthropic Claude and OpenAI GPT

4. **Voice Clone Manager** (`voice_clone.py`)
   - ElevenLabs API integration
   - Create voice clone from audio sample
   - Generate audio from text using voice clone

5. **API Endpoints** (added to `app.py`)
   - `/api/links/scrape-content` - Scrape link content
   - `/api/links/{link_id}/generate-scripts` - Generate 3 script variations
   - `/api/links/{link_id}/select-script` - User selects script
   - `/api/voice/clone` - Create voice clone
   - `/api/links/{link_id}/generate-audio` - Generate audio
   - `/api/profile/publish` - Publish profile

### 📝 Frontend (TO BE IMPLEMENTED)

The frontend onboarding wizard needs to be built to use these APIs. See the JavaScript examples in `ONBOARDING_FLOW_IMPLEMENTATION.md`.

## Installation Steps

### 1. Install New Dependencies

```bash
cd voicetree
pip install -r requirements.txt
```

This installs:
- `anthropic` - Claude AI for script generation
- `openai` - OpenAI GPT (alternative to Claude)
- `elevenlabs` - Voice cloning and TTS

### 2. Run Database Migration

```bash
cd voicetree/backend
python3 migrate_add_script_variations.py
```

You should see:
```
✓ Added script_brief column
✓ Added script_standard column
✓ Added script_conversational column
✓ Added selected_script column

✅ Migration completed successfully!
```

### 3. Set Environment Variables

Create a `.env` file or export variables:

```bash
# AI Script Generation (choose ONE)
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
# OR
export OPENAI_API_KEY="sk-your-key-here"

# Voice Cloning (REQUIRED)
export ELEVENLABS_API_KEY="your-elevenlabs-key"

# Existing variables
export SECRET_KEY="your-secret-key"
```

**Get API Keys:**
- Anthropic: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/
- ElevenLabs: https://elevenlabs.io/

### 4. Test Individual Components

**Test Enhanced Scraper:**
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

### 5. Start the Server

```bash
cd voicetree/backend
uvicorn app:app --reload --port 8000
```

Server should start at: http://localhost:8000

## Testing the API Endpoints

### Test 1: Scrape Link Content

```bash
curl -X POST http://localhost:8000/api/links/scrape-content \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.python.org/about/"
  }'
```

Expected response:
```json
{
  "success": true,
  "url": "https://www.python.org/about/",
  "title": "About Python™ | Python.org",
  "meta_description": "The official home of the Python...",
  "preview_text": "Python is powerful... and fast...",
  "link_type": "website"
}
```

### Test 2: Generate Scripts (requires existing link)

First, create a test link in your database, then:

```bash
curl -X POST http://localhost:8000/api/links/1/generate-scripts
```

Expected response:
```json
{
  "success": true,
  "link_id": 1,
  "scripts": {
    "brief": {
      "text": "Check out my Python course!",
      "word_count": 5
    },
    "standard": {
      "text": "I'm excited to share my Python programming course...",
      "word_count": 28
    },
    "conversational": {
      "text": "Hey! So I've been working on this awesome Python course...",
      "word_count": 42
    }
  }
}
```

### Test 3: Select Script

```bash
curl -X POST http://localhost:8000/api/links/1/select-script \
  -H "Content-Type: application/json" \
  -d '{
    "script_type": "standard"
  }'
```

### Test 4: Create Voice Clone

```bash
curl -X POST http://localhost:8000/api/voice/clone \
  -F "audio_sample=@/path/to/voice_sample.mp3" \
  -F "username=testuser"
```

### Test 5: Generate Audio

```bash
curl -X POST http://localhost:8000/api/links/1/generate-audio
```

### Test 6: Publish Profile

```bash
curl -X POST http://localhost:8000/api/profile/publish \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser"
  }'
```

## File Structure

```
voicetree/
├── backend/
│   ├── app.py                           # Main FastAPI app with new endpoints
│   ├── scraper_enhanced.py              # NEW: Enhanced content scraper
│   ├── script_generator.py              # NEW: AI script generator
│   ├── voice_clone.py                   # NEW: ElevenLabs integration
│   ├── migrate_add_script_variations.py # NEW: Database migration
│   ├── models.py                        # Existing (voice_clone_id already added)
│   └── audio/
│       ├── voice_samples/               # User voice samples stored here
│       └── link_voices/                 # Generated audio files stored here
├── requirements.txt                     # Updated with new dependencies
├── ONBOARDING_FLOW_IMPLEMENTATION.md    # Complete implementation docs
└── ONBOARDING_SETUP_GUIDE.md           # This file
```

## Troubleshooting

### "No API key found" Error

Make sure you've set the environment variables:
```bash
export ANTHROPIC_API_KEY="your-key"
export ELEVENLABS_API_KEY="your-key"
```

Or add them to a `.env` file and use `python-dotenv`.

### "Script generation failed"

Check:
1. API key is valid
2. API quota hasn't been exceeded
3. Network connection is working
4. Check logs for specific error message

### "Voice clone creation failed"

Check:
1. Audio file is 30-60 seconds long
2. File format is MP3 or WAV
3. ElevenLabs API key is valid
4. File size is reasonable (< 5MB)

### Database migration already run

If you see "column already exists", that's OK - the migration is idempotent and will skip existing columns.

## Next Steps

### Immediate: Frontend Integration

1. **Create Onboarding Wizard UI**
   - Multi-step wizard component
   - Progress indicator
   - Step navigation

2. **Build Script Selection Interface**
   - Display 3 script options in cards
   - Radio buttons for selection
   - Edit functionality
   - Word count display

3. **Implement Voice Recording**
   - Browser MediaRecorder API
   - Timer (30-60 seconds)
   - Playback preview
   - Re-record option

4. **Add Progress Indicators**
   - Loading states
   - Success messages
   - Error handling

### Testing Checklist

- [ ] User can import links from Linktree
- [ ] User can manually add links
- [ ] Scripts generate for all link types
- [ ] User can select/edit scripts
- [ ] Voice recording works (30-60s)
- [ ] Voice clone creates successfully
- [ ] Audio generates for all links
- [ ] Preview page shows all audio players
- [ ] Audio plays correctly
- [ ] Publish makes page live
- [ ] Complete flow takes 3-5 minutes

### Production Deployment

Before deploying:
1. Set all environment variables on server
2. Configure file storage (local or S3)
3. Set up monitoring for API usage
4. Implement error logging
5. Add user feedback mechanisms
6. Test with real users

## API Rate Limits & Costs

### Anthropic Claude
- Free tier: 50 requests/min
- Paid: Higher limits based on plan
- Cost: ~$0.01 per script generation

### OpenAI GPT-4
- Paid only: 10,000 requests/min
- Cost: ~$0.03 per script generation

### ElevenLabs
- Free: 10,000 characters/month
- Starter: $5/month - 30,000 characters
- Creator: $22/month - 100,000 characters
- Cost: ~$0.30 per minute of audio

### Estimate for 1000 Users
- Script Generation: $10-30
- Voice Cloning: $0 (one-time per user)
- Audio Generation: $300-500
- **Total: ~$310-530/month**

## Support & Resources

- **Documentation**: See `ONBOARDING_FLOW_IMPLEMENTATION.md`
- **API Docs**: 
  - Anthropic: https://docs.anthropic.com/
  - OpenAI: https://platform.openai.com/docs
  - ElevenLabs: https://elevenlabs.io/docs

- **Example Frontend Code**: See `ONBOARDING_FLOW_IMPLEMENTATION.md` for JavaScript examples

## Success Metrics

Track these KPIs:
- Onboarding completion rate
- Time to complete onboarding
- Script regeneration rate
- Voice clone success rate
- Audio generation success rate
- User satisfaction scores

## Congratulations! 🎉

The backend for the complete onboarding flow is now implemented. Once the frontend is built, users will be able to:

1. Import their links
2. Get AI-generated scripts in seconds
3. Record their voice once
4. Get audio for all links automatically
5. Publish their page live

**Total time: 3-5 minutes from start to finish!**
