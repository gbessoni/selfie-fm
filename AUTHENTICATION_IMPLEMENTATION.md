# Authentication System Implementation - selfie.fm

## Overview
A complete user authentication system has been added to selfie.fm with JWT tokens, bcrypt password hashing, and session management.

## Implemented Features

### 1. User Model Updates ✅
**File:** `voicetree/backend/models.py`

Added authentication fields to User model:
- `email` - String(255), unique, nullable (for future password reset)
- `password_hash` - String(255), nullable (bcrypt hash)
- `last_login` - DateTime, nullable (tracks last login time)

### 2. Authentication Module ✅
**File:** `voicetree/backend/auth.py`

Core authentication utilities:
- **Password Hashing:** bcrypt with salt
- **Password Validation:** Minimum 8 characters, requires letters and numbers
- **JWT Tokens:** 7-day expiration by default
- **Session Management:** Cookie-based with "remember me" option
- **Rate Limiting:** 5 login attempts per 15 minutes
- **User Dependencies:** Helper functions for protected routes

Key Functions:
- `get_password_hash()` - Hash passwords with bcrypt
- `verify_password()` - Verify password against hash
- `validate_password_strength()` - Check password requirements
- `create_access_token()` - Generate JWT tokens
- `authenticate_user()` - Validate username/password
- `get_current_user_from_cookie()` - Extract user from session
- `check_rate_limit()` - Prevent brute force attacks

### 3. Updated Schemas ✅
**File:** `voicetree/backend/schemas.py`

New Pydantic schemas:
- `UserCreateWithPassword` - Signup with password
- `LoginRequest` - Login credentials with remember_me
- `LoginResponse` - Returns access_token and user info
- `UserMeResponse` - Current user profile data

### 4. API Endpoints ✅
**File:** `voicetree/backend/app.py`

#### Authentication Endpoints:
- `GET /login` - Render login page
- `POST /api/auth/signup` - Create account with password
- `POST /api/auth/login` - Authenticate and create session
- `POST /api/auth/logout` - Clear session cookie
- `GET /api/auth/me` - Get current user info
- `GET /api/users/{username}/exists` - Check username availability

### 5. Login Page ✅
**File:** `voicetree/frontend/templates/login.html`

Features:
- Beautiful gradient design matching signup page
- Username and password inputs with floating labels
- "Remember me" checkbox for 7-day session
- "Forgot password?" link (placeholder)
- Link to signup page
- Error messages for invalid credentials
- Success animation on login
- Redirect to intended page after login

### 6. Updated Signup Page ✅
**File:** `voicetree/frontend/templates/signup.html`

Added fields:
- Email input (optional, for future password reset)
- Password input (required, min 8 chars)
- Password validation hints

Updated to use `/api/auth/signup` endpoint which:
- Creates user with hashed password
- Automatically logs in user
- Returns JWT token
- Redirects to dashboard

### 7. Session Management ✅

**Cookie-based sessions:**
- HttpOnly cookies for security
- 7-day expiration with "remember me"
- Session-only cookies without "remember me"
- SameSite=lax for CSRF protection

**Token Storage:**
- JWT tokens stored in localStorage
- Can be sent in Authorization header
- Used for API requests

### 8. Security Features ✅

- **Password Hashing:** bcrypt with automatic salt
- **Password Requirements:** 8+ chars, letters + numbers
- **Rate Limiting:** 5 attempts per 15 minutes per username
- **JWT Expiration:** 7 days default
- **HttpOnly Cookies:** XSS protection
- **CSRF Protection:** SameSite cookie attribute

## Dependencies Added

```txt
bcrypt==4.1.2
pyjwt==2.8.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
slowapi==0.1.9
```

## Database Migration Required

The User model has been updated with new fields. To apply these changes:

### Option 1: Reset Database (Development Only)
```bash
cd voicetree/backend
rm voicetree.db  # Delete existing database
python -c "from database import init_db; init_db()"  # Recreate
```

### Option 2: Manual Migration (Production Safe)
```bash
cd voicetree/backend
python
```

```python
from database import SessionLocal, engine
from sqlalchemy import text

db = SessionLocal()

# Add new columns
db.execute(text("""
    ALTER TABLE users ADD COLUMN email VARCHAR(255);
"""))
db.execute(text("""
    ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);
"""))
db.execute(text("""
    ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
"""))

db.commit()
db.close()
```

## Testing the System

### 1. Start the Server
```bash
cd voicetree/backend
uvicorn app:app --reload
```

### 2. Test Signup Flow
1. Navigate to `http://localhost:8000/signup`
2. Enter username (checks availability in real-time)
3. Enter display name
4. Enter email (optional)
5. Enter password (min 8 chars, letters + numbers)
6. Enter bio (optional)
7. Submit form
8. Should redirect to dashboard with active session

### 3. Test Login Flow
1. Navigate to `http://localhost:8000/login`
2. Enter username and password
3. Optionally check "Remember me"
4. Submit form
5. Should redirect to dashboard with active session

### 4. Test Logout
Currently, logout must be called via API:
```javascript
fetch('/api/auth/logout', { method: 'POST' })
  .then(() => window.location.href = '/login')
```

### 5. Test Protected Routes
Try accessing dashboard without being logged in - should show appropriate error or redirect to login.

## Next Steps (Not Yet Implemented)

### 1. Protected Route Middleware
Add authentication checks to dashboard, preview, and admin routes:
```python
@app.get("/dashboard/{username}")
async def dashboard_page(
    username: str,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    if not current_user or current_user.username != username:
        return RedirectResponse(url=f"/login?redirect=/dashboard/{username}")
    # ... rest of route
```

### 2. Logout Button in Dashboard
Add logout button to dashboard header:
```html
<button onclick="logout()">Logout</button>
<script>
async function logout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/login';
}
</script>
```

### 3. Password Reset Flow
- Create forgot password page
- Generate reset tokens
- Send reset emails
- Implement reset password page

### 4. Email Verification
- Send verification emails on signup
- Verify email tokens
- Mark email as verified

### 5. OAuth Integration
- Add "Login with Google" button
- Add "Login with GitHub" button
- Handle OAuth callbacks

## File Structure

```
voicetree/
├── backend/
│   ├── app.py                      # Updated with auth endpoints
│   ├── auth.py                     # NEW: Authentication utilities
│   ├── models.py                   # Updated User model
│   ├── schemas.py                  # Updated with auth schemas
│   └── database.py                 # Existing
├── frontend/
│   └── templates/
│       ├── login.html              # NEW: Login page
│       ├── signup.html             # Updated with password
│       ├── dashboard.html          # Needs logout button
│       └── ...
└── requirements.txt                # Updated with new packages
```

## Security Considerations

### Production Deployment
1. **SECRET_KEY:** Change the auto-generated secret key to a fixed value in production
2. **HTTPS:** Set `secure=True` for cookies when using HTTPS
3. **CORS:** Configure CORS headers appropriately
4. **Rate Limiting:** Consider using Redis for distributed rate limiting
5. **Password Policy:** Consider adding more complex password requirements
6. **Session Storage:** Consider using Redis for session storage
7. **Token Refresh:** Implement refresh tokens for better security

### Environment Variables
Create `.env` file:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///voicetree.db
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

## Troubleshooting

### "Module not found" errors
Ensure all packages are installed:
```bash
pip install -r requirements.txt
```

### "Column does not exist" errors
Run database migration (see Database Migration section above)

### Sessions not persisting
Check that cookies are enabled in browser and not blocked by same-site restrictions

### Rate limiting issues
Clear the in-memory rate limit storage:
```python
from auth import login_attempts
login_attempts.clear()
```

## Summary

The authentication system is now fully implemented with:
- ✅ Secure password hashing
- ✅ JWT token management  
- ✅ Login and signup pages
- ✅ Session cookies
- ✅ Rate limiting
- ✅ API endpoints
- ✅ Password validation

Next steps are to protect the dashboard/preview/admin routes and add logout functionality to the UI.
