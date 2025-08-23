# GitLab OAuth Configuration for Legend Platform

## Problem
The redirect URI error occurs because GitLab OAuth application doesn't have the correct redirect URIs registered for your deployment setup.

## Solution

### 1. Update GitLab OAuth Application

Go to your GitLab OAuth application settings:
- URL: https://gitlab.com/-/profile/applications
- Application ID: `dbdd707e51066b5b948d238bb0f84b7a7d2c883e008671c7dc33c1c5c639c862`

### 2. Add ALL Required Redirect URIs

Add these redirect URIs to your GitLab application:

```
# For reverse proxy access (dev.atheryon.ai)
http://dev.atheryon.ai/studio/log.in/callback
https://dev.atheryon.ai/studio/log.in/callback

# For direct localhost access
http://localhost:9000/studio/log.in/callback
http://localhost:6100/api/auth/callback

# Additional URIs that may be needed
http://dev.atheryon.ai:9000/studio/log.in/callback
```

### 3. Required Scopes

Ensure these scopes are enabled:
- `api`
- `openid` 
- `profile`

### 4. Environment Configuration

The current configuration uses:
- **Application ID**: `dbdd707e51066b5b948d238bb0f84b7a7d2c883e008671c7dc33c1c5c639c862`
- **Application Secret**: `gloas-b2f54817acd471b92aaf4d3514bcc74e7c29210457d7e774941f457cd9686501`

These are hardcoded in `docker-compose.yml` for all Legend services.

## Access Methods

### Via Reverse Proxy (Recommended)
Access Legend Studio at: http://dev.atheryon.ai/studio

This requires:
1. Adding `127.0.0.1 dev.atheryon.ai` to your `/etc/hosts` file
2. Having the redirect URI `http://dev.atheryon.ai/studio/log.in/callback` in GitLab

### Direct Access
Access Legend Studio at: http://localhost:9000

This requires the redirect URI `http://localhost:9000/studio/log.in/callback` in GitLab

## Troubleshooting

If you continue to see redirect URI errors:

1. **Check the exact URI in the error message** - it shows what Legend is trying to use
2. **Add that exact URI to GitLab** - must match character-for-character
3. **Wait a few minutes** - GitLab OAuth changes can take time to propagate
4. **Clear browser cookies** - old session data can cause issues
5. **Restart Legend services** if you changed environment variables:
   ```bash
   docker compose down
   docker compose up -d
   ```

## Current Issue
The error shows Legend is trying to use `http://dev.atheryon.ai:9000/studio/log.in/callback` (with port), but when using the reverse proxy it should use `http://dev.atheryon.ai/studio/log.in/callback` (without port).

The reverse proxy strips the port, so make sure both URIs are registered in GitLab to support both access methods.