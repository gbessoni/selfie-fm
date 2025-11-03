# Quick Setup Guide: AI Pitch-Writing Feature

## Prerequisites

- Python 3.8+
- Existing voicetree application installed
- OpenAI API key OR Anthropic API key

## Setup Steps

### 1. Set Environment Variables

Add to your `.env` file or export:

```bash
# Choose ONE of these:
export OPENAI_API_KEY=sk-your-openai-key-here
# OR
export ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

### 2. Database Migration

The database has already been migrated with the new fields:
- `ai_generated_script` - stores the AI-generated script
- `scraped_content` - caches scraped page content

To verify, run:
```bash
cd voicetree
python3 -c "from backend.database import init_db; init_db(); print('✓ Database ready')"
```

### 3. Start the Server

```bash
cd voicetree
python3 backend/app.py
# OR
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

## Testing the Feature

### Test Script Generation

```bash
# First, create a test link (or use existing link ID)
curl -X POST http://localhost:8000/api/links/1/generate-script

# Expected response:
{
  "success": true,
  "script": "Your AI-generated pitch...",
  "link_id": 1
}
```

### Test Regeneration

```bash
curl -X POST http://localhost:8000/api/links/1/regenerate-script
```

### Test Voice Recording

```bash
# Record audio in browser, then upload:
curl -X POST http://localhost:8000/api/links/1/record-voice \
  -F "audio=@test_recording.webm" \
  -F "text=Your script text here"
```

### Test AI Voice Generation

```bash
# Requires user to have voice clone set up
curl -X POST http://localhost:8000/api/links/1/generate-ai-voice \
  -F "text=Your script text here"
```

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/links/{link_id}/generate-script` | POST | Generate initial AI script |
| `/api/links/{link_id}/regenerate-script` | POST | Regenerate script |
| `/api/links/{link_id}/record-voice` | POST | Upload recorded audio |
| `/api/links/{link_id}/generate-ai-voice` | POST | Generate AI voice |

## Troubleshooting

### "No AI API key configured"
- Verify environment variable is set correctly
- Restart server after setting env var
- Check variable name spelling

### Script generation fails
- Verify AI provider has credits
- Check network connectivity
- Review server logs for details

### Scraping issues
- Some sites block scraping (this is normal)
- System will still generate script with available info
- No action needed - gracefully handled

## What's Implemented

✅ Database models with new fields  
✅ Script writer module with AI integration  
✅ Link content scraping  
✅ API endpoints for script generation  
✅ Voice recording upload  
✅ AI voice generation integration  
✅ Error handling and validation  
✅ Caching for performance  
✅ Comprehensive documentation  

## What's Next (Frontend TODO)

The frontend UI integration is not yet complete. The backend is fully functional and ready to be integrated with:

- Dashboard link edit modal with "Generate Script" button
- Editable textarea for script
- Recording interface with timer
- Preview and playback functionality
- Save/publish workflow

See `AI_PITCH_WRITING_FEATURE.md` for full frontend specifications.

## Key Features

1. **Automatic Script Generation**: AI analyzes link destination and writes persuasive pitch
2. **Dual AI Support**: Works with OpenAI or Anthropic
3. **Content Analysis**: Scrapes and analyzes destination pages
4. **Flexible Recording**: Record yourself OR use AI voice
5. **Caching**: Scraped content cached for instant regeneration
6. **Seth Godin Style**: Direct, authentic, no-hype copywriting

## Next Steps

1. **Add API Key**: Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
2. **Test Endpoints**: Use curl commands above
3. **Build Frontend**: Integrate with dashboard UI
4. **Test with Real Links**: Try various link types
5. **Monitor Performance**: Check script quality and conversion

## Support

For detailed documentation, see `AI_PITCH_WRITING_FEATURE.md`

---

Ready to generate amazing sales scripts! 🚀
