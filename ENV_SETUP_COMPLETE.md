# Environment Variables Setup - COMPLETE ✅

## Problem Solved
API keys were disappearing when changing ports or restarting terminal sessions.

## Solution Implemented
Environment variables are now persistent and port-independent using .env file.

---

## 1. ✅ Created/Updated `.env` File
**Location:** `voicetree/backend/.env`

Contains all required environment variables:
```
ANTHROPIC_API_KEY=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
ELEVENLABS_API_KEY=RmE0YUJMOWxOTEx2bDFNVVh6UW1aRGZINTJjRmFFejY6bllDejRRS1R0VklmaE5OOElWWUFuZHc1RkJTSW1SZ1VuQno2RHdEVG13ekhGcHFiVVZQb25LbGxHSnVKMmpvWQ==
DATABASE_URL=sqlite:///./voicetree.db
SECRET_KEY=your-secret-key-here-change-in-production
```

---

## 2. ✅ Verified load_dotenv() at Top of app.py
The following code is already at the very top of `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```
This ensures environment variables are loaded before any other imports.

---

## 3. ✅ Added Startup Logging
Added comprehensive logging to verify API keys are loaded on server startup:

```python
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
```

**Expected Output on Startup:**
```
============================================================
🚀 Selfie.fm Server Started
============================================================
✅ Anthropic key: Found
✅ ElevenLabs key: Found
📍 Running on: http://localhost:8000
============================================================
```

---

## 4. ✅ Created Start Script
**Location:** `voicetree/start.sh`

```bash
#!/bin/bash
cd backend
source ../../venv/bin/activate
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Permissions:** Made executable with `chmod +x voicetree/start.sh`

---

## How to Use

### Start the Server (Simple Method)
From the `voicetree` directory:
```bash
./start.sh
```

This will:
1. Change to backend directory
2. Activate the virtual environment
3. Load environment variables from .env
4. Start the server on port 8000
5. Show startup logging with API key status

### Alternative: Manual Start
If you prefer to start manually:
```bash
cd voicetree/backend
source ../../venv/bin/activate
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

---

## Benefits

✅ **Persistent:** API keys are stored in .env file, not in terminal environment  
✅ **Port-Independent:** Works on any port without re-exporting variables  
✅ **Session-Independent:** Survives terminal restarts  
✅ **Secure:** .env file can be added to .gitignore  
✅ **Visible:** Startup logging confirms keys are loaded  
✅ **Convenient:** Single command to start server with all settings  

---

## Important Notes

1. **Never commit the .env file to version control** - Add it to .gitignore
2. **The .env file is loaded automatically** - No need to export variables
3. **Changing ports doesn't affect API keys** - They're always loaded from .env
4. **Restart the server** to pick up changes to .env file

---

## Verification

To verify API keys are loaded:
1. Start the server with `./start.sh`
2. Look for the startup banner showing:
   - ✅ Anthropic key: Found
   - ✅ ElevenLabs key: Found
3. If either shows "❌ Missing", check the .env file

---

## Troubleshooting

### Keys Not Loading?
1. Check `.env` file exists at `voicetree/backend/.env`
2. Verify no extra spaces around = in .env file
3. Make sure `load_dotenv()` is at the top of app.py
4. Restart the server completely

### Server Won't Start?
1. Check if port 8000 is already in use: `lsof -i :8000`
2. Kill existing process or use a different port
3. Make sure virtual environment is activated

---

**Setup Complete!** 🎉

Your API keys are now persistent and will be loaded automatically every time you start the server, regardless of port or terminal session.
