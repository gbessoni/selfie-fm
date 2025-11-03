# AI Pitch-Writing Feature Documentation

## Overview

The AI Pitch-Writing feature is the core value proposition of selfie.fm. It automatically generates persuasive 10-second sales scripts for each link using AI, analyzes the destination content, and allows users to either record the script themselves or use AI voice generation.

## Architecture

### Backend Components

#### 1. Database Models (`backend/models.py`)
- **Link Model** additions:
  - `ai_generated_script` (Text): Stores the AI-generated pitch script
  - `scraped_content` (Text): Caches scraped page content for regeneration

#### 2. Script Writer Module (`backend/script_writer.py`)
Core AI script generation functionality:

**Key Functions:**
- `scrape_link_content(url)`: Analyzes destination URL and extracts:
  - Page title
  - Meta description
  - Key headings (h1, h2)
  - Relevant paragraph content
  
- `generate_pitch_script(link_url, link_title, scraped_content, user_business_context)`:
  - Generates 50-word max scripts using OpenAI GPT-4 or Anthropic Claude
  - Uses Seth Godin-style copywriting principles
  - Incorporates user's business context from bio

**AI Provider Support:**
- OpenAI (GPT-4) - via `OPENAI_API_KEY`
- Anthropic (Claude 3.5 Sonnet) - via `ANTHROPIC_API_KEY`
- Automatically uses whichever API key is configured

#### 3. API Endpoints (`backend/app.py`)

**POST `/api/links/{link_id}/generate-script`**
- Generates initial AI script for a link
- Scrapes destination URL
- Uses user's bio as business context
- Stores script and scraped content in database

**POST `/api/links/{link_id}/regenerate-script`**
- Regenerates script using cached scraped content
- Allows users to get alternative versions

**POST `/api/links/{link_id}/record-voice`**
- Uploads user-recorded audio reading the script
- Accepts audio files up to 5MB
- Stores in `audio/link_voices/` directory

**POST `/api/links/{link_id}/generate-ai-voice`**
- Generates AI voice using user's voice clone
- Requires user to have created voice clone first
- Uses Inworld AI voice generation

## Workflow

### 1. Link Analysis
When a user adds or edits a link:
```python
# Backend automatically:
1. Fetches destination URL
2. Scrapes: title, meta description, headings, content
3. Stores scraped data for future use
```

### 2. Script Generation
```python
# AI generates script using:
- Link URL and title
- Scraped page content
- User's bio (business context)
- Seth Godin-style copywriting principles

# Script requirements:
- 50 words maximum (10 seconds spoken)
- Address specific pain point or desire
- Show urgency/social proof/scarcity when relevant
- End with clear call-to-action
- Sound natural when spoken aloud
```

### 3. Recording Options

**Option A: Record Your Voice**
- User records themselves reading the script
- Browser-based recording (WebRTC)
- Preview and re-record if needed
- Upload to server

**Option B: Generate AI Voice**
- Uses user's voice clone (if created)
- Generates audio via Inworld AI
- Preview before publishing
- Instant generation

## AI Prompt Engineering

The system uses this carefully crafted prompt:

```
You are a master copywriter who writes direct, human, authentic copy - no hype, just clear value.

Write a 10-second voice script (50 words max) for this link.

Link: {link_title}
Destination: {link_url}
Page content: {scraped_content}
Business context: {user_business_context}

The script must:
- Address a specific pain point or desire
- Show urgency, social proof, or scarcity (if relevant)
- End with clear call-to-action
- Sound natural when spoken aloud
- Be conversational and authentic
- Be exactly 50 words or less

Write ONLY the script, no explanations or meta-commentary.
```

## Environment Setup

### Required Environment Variables

Add to `.env` or environment:

```bash
# Choose ONE of these AI providers:

# Option 1: OpenAI (recommended)
OPENAI_API_KEY=sk-...

# Option 2: Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...

# Voice AI (for voice generation)
INWORLD_API_KEY=your_inworld_key_here
```

### Installation

No additional packages needed - all dependencies already in `requirements.txt`:
- `requests` - for web scraping and API calls
- `beautifulsoup4` - for HTML parsing

## Usage Examples

### Example 1: Generate Script for Product Link

```python
# Input:
Link: "Buy My Course"
URL: https://example.com/course
Scraped Content: "Learn web development in 30 days..."
User Bio: "I teach coding to beginners"

# AI Output:
"Stuck in tutorial hell? My 30-day course gives you real projects, 
not endless videos. Over 1,000 students landed jobs. Limited spots 
this month. Start building today."
```

### Example 2: Social Media Link

```python
# Input:
Link: "Follow on Instagram"
URL: https://instagram.com/myprofile
User Bio: "Fitness coach for busy professionals"

# AI Output:
"No time for the gym? Follow me for 15-minute workouts you can do 
anywhere. Real results from real people. New workout every Monday. 
Join 50K followers getting fit on their schedule."
```

## Frontend Integration (TODO)

The dashboard UI will include:

1. **Link Edit Modal**:
   - "Generate AI Script" button
   - Loading state: "Analyzing page and writing your pitch..."
   - Editable textarea with generated script
   - Character counter (50 words / 10 seconds)

2. **Recording Options**:
   - Option A: "Record Your Voice" button
     - Timer display
     - Waveform visualization
     - Preview player
   - Option B: "Generate with AI Voice" button
     - Requires voice clone
     - Instant preview

3. **Script Management**:
   - "Regenerate Script" button for alternatives
   - "Save & Publish" button

## API Response Examples

### Generate Script Success
```json
{
  "success": true,
  "script": "Your AI-generated pitch script here...",
  "link_id": 123
}
```

### Generate Script Error
```json
{
  "detail": "No AI API key configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY."
}
```

### Record Voice Success
```json
{
  "success": true,
  "audio_path": "link_voices/link_123_1730563200.webm",
  "text": "The script text",
  "message": "Voice recording saved successfully"
}
```

## Error Handling

The system handles various error scenarios:

1. **No AI API Key**: Clear error message asking to configure API key
2. **Scraping Fails**: Uses fallback text, still generates script
3. **Invalid URL**: Catches and reports connection errors
4. **API Rate Limits**: Returns appropriate HTTP error codes
5. **Audio Upload Issues**: Validates file type and size

## Performance Considerations

- **Caching**: Scraped content is cached to avoid re-scraping on regeneration
- **Async Operations**: Script generation runs asynchronously
- **Timeout Handling**: Web scraping has 10-second timeout
- **File Size Limits**: Audio uploads capped at 5MB

## Security

- Input validation on all user-provided data
- URL validation before scraping
- File type validation for audio uploads
- SQL injection prevention via ORM
- API key management via environment variables

## Testing

### Test Script Generation
```bash
# With OpenAI
export OPENAI_API_KEY=sk-...
curl -X POST http://localhost:8000/api/links/1/generate-script

# With Anthropic
export ANTHROPIC_API_KEY=sk-ant-...
curl -X POST http://localhost:8000/api/links/1/generate-script
```

### Test Voice Recording
```bash
curl -X POST http://localhost:8000/api/links/1/record-voice \
  -F "audio=@recording.webm" \
  -F "text=Your script text here"
```

## Future Enhancements

1. **A/B Testing**: Generate multiple script variations
2. **Analytics**: Track which scripts convert best
3. **Voice Style Options**: Different tones (professional, casual, excited)
4. **Language Support**: Multi-language script generation
5. **Script Templates**: Pre-built templates for common use cases
6. **Performance Metrics**: Track conversion rates per script

## Troubleshooting

### Script Generation Fails
- Verify API key is set correctly
- Check API provider has available credits
- Ensure network connectivity to AI provider

### Scraping Issues
- Some sites block scraping - this is expected
- System gracefully handles scraping failures
- Falls back to generating script with available info

### Voice Recording Issues
- Check audio format is supported (webm, mp3, wav)
- Ensure file size is under 5MB
- Verify browser has microphone permissions

## Support

For issues or questions:
- Check logs: `tail -f voicetree/backend/logs/app.log`
- Review error responses from API
- Ensure all environment variables are set
- Verify database migrations ran successfully

---

**Version**: 1.0.0  
**Last Updated**: November 1, 2025  
**Author**: selfie.fm Development Team
