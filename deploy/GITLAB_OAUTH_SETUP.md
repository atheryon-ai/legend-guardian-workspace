# GitLab OAuth Setup for Legend Platform

## Important: Application ID vs Numeric ID

When configuring GitLab OAuth for Legend, you must use the **Application ID** (long hex string), NOT the numeric ID shown in URLs.

### Correct Configuration

```bash
# CORRECT - Use the Application ID (hex string)
GITLAB_APP_ID=dbdd707e51066b5b948d238bb0f84b7a7d2c883e008671c7dc33c1c5c639c862

# WRONG - Don't use the numeric ID from URLs
# GITLAB_APP_ID=29713286  # This will cause "unknown client" errors
```

## Setup Steps

1. Go to https://gitlab.com/-/profile/applications
2. Create a new application with:
   - **Name**: Legend Local (or any name)
   - **Confidential**: ✅ MUST be checked
   - **Scopes**: Select `api`, `openid`, and `profile`
   - **Redirect URIs** (add ALL of these):
     ```
     http://localhost:6300/callback
     http://localhost:6100/api/auth/callback
     http://localhost:6100/api/pac4j/login/callback
     http://localhost:6201/depot-store/callback
     http://localhost:6200/depot/callback
     http://localhost:9000/studio/log.in/callback
     http://localhost:9001/query/log.in/callback
     ```

3. After creating, you'll see:
   - **Application ID**: Long hex string (USE THIS!)
   - **Secret**: Copy this for GITLAB_APP_SECRET

4. Update your `.env` files with these values

## Common Issues

### "Client authentication failed due to unknown client"
- You're using the numeric ID instead of the Application ID
- The "Confidential" checkbox wasn't enabled
- The redirect URI doesn't match exactly

### "State parameter is different from the one sent in authentication request"
This is typically a cookie/session issue. Solutions:
1. **Clear all cookies** for localhost in your browser
2. **Use an incognito/private window** for clean session
3. **Close all other tabs** accessing localhost services
4. **Avoid using multiple tabs** during authentication flow

### "Sign in with GitHub" on GitLab
If you use GitHub SSO for GitLab:
1. Set a password at https://gitlab.com/-/profile/password/edit
2. This allows OAuth flows to work properly

## Testing

After configuration:
1. Clear browser cookies for localhost
2. Navigate to http://localhost:9000
3. Click "Sign in with GitLab"
4. Authorize the application when prompted