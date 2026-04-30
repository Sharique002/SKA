# Render Deployment Fix

The backend was running Flask dev server on port 5000, but Render expects port 8000.

## Changes Made

✅ Updated `Dockerfile` to:
- Only copy backend files
- Use gunicorn WSGI server
- Bind to port 8000 via $PORT environment variable

✅ Updated `render.yaml` to:
- Use Docker runtime
- Set PORT=8000 explicitly
- Reference Dockerfile

✅ Created `.dockerignore`:
- Excludes frontend code
- Excludes unnecessary files

## To Deploy

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Fix Render backend deployment"
   git push
   ```

2. **In Render Dashboard**:
   - Go to your service
   - Click "Manual Deploy" → "Deploy latest commit"
   - Wait for build to complete

3. **Check Status**:
   - Render should now detect port 8000
   - Backend URL: `https://ska-backend.onrender.com`
   - Health check: `https://ska-backend.onrender.com/api/health`

## What Changed

| Before | After |
|--------|-------|
| Flask dev server on 5000 | Gunicorn on 8000 |
| Manual build command | Docker automated |
| Dev mode | Production mode |

## If Still Issues

Check logs in Render dashboard for:
- "Bind 0.0.0.0:8000" message
- No "port scan timeout" warnings

Both should appear after fix is deployed.
