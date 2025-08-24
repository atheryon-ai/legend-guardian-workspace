# GitLab OAuth Redirect URI Fix

## Problem
Legend Studio is trying to use: `http://dev.atheryon.ai:9000/studio/log.in/callback`
But this exact URI is missing from your GitLab OAuth application.

## Solution
Add this missing redirect URI to your GitLab OAuth application:

```
http://dev.atheryon.ai:9000/studio/log.in/callback
```

Note: You have the HTTPS version but you need the HTTP version.

## Current Redirect URIs in GitLab
You already have these configured:
- ✅ http://localhost:6300/callback
- ✅ http://localhost:6100/api/auth/callback
- ✅ http://localhost:6100/api/pac4j/login/callback
- ✅ http://localhost:6201/depot-store/callback
- ✅ http://localhost:6200/depot/callback
- ✅ http://localhost:9000/studio/log.in/callback
- ✅ http://localhost:9001/query/log.in/callback
- ✅ https://dev.atheryon.ai:9000/studio/log.in/callback (HTTPS version)
- ✅ https://dev.atheryon.ai/sdlc/api/auth/callback
- ✅ http://dev.atheryon.ai/sdlc/api/auth/callback
- ✅ http://dev.atheryon.ai/studio/log.in/callback

Missing:
- ❌ **http://dev.atheryon.ai:9000/studio/log.in/callback** (HTTP with port)

## Steps to Fix
1. Go to https://gitlab.com/-/profile/applications
2. Find your OAuth application
3. Click Edit
4. Add the missing redirect URI: `http://dev.atheryon.ai:9000/studio/log.in/callback`
5. Save the application
6. Clear browser cookies/cache
7. Try the OAuth flow again

## Why This Happens
When you access Legend Studio at `http://dev.atheryon.ai:9000`, it constructs the callback URL using the exact same protocol and port. Since you're using HTTP (not HTTPS) with port 9000, it needs that exact combination registered in GitLab.