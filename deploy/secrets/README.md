# Legend Platform Secrets Management

This directory contains templates and documentation for managing secrets across different deployment environments.

## 🔐 Security First

**NEVER commit real credentials to git!** All files containing actual secrets should be:
- Named with `.env.local`, `.env.docker`, or `.env.azure` 
- Listed in `.gitignore`
- Kept only on your local machine or in secure secret management systems

## 📁 File Structure

```
legend-guardian-workspace/
├── .env.example              # Main template with ALL variables (safe to commit)
├── .env.local                # Your local development secrets (gitignored)
├── .env.docker               # Docker deployment secrets (gitignored)
├── .env.azure                # Azure deployment secrets (gitignored)
└── deploy/secrets/
    ├── README.md             # This file
    ├── setup.sh              # Interactive setup script
    ├── .env.local.example    # Local development template
    └── .env.azure.example    # Azure production template
```

## 🚀 Quick Start

### 1. Local Development Setup

```bash
# Copy the local template
cp deploy/secrets/.env.local.example .env.local

# Edit with your GitLab OAuth credentials
nano .env.local

# Run the setup script for validation
./deploy/secrets/setup.sh
```

### 2. Azure Production Setup

```bash
# Copy the Azure template
cp deploy/secrets/.env.azure.example .env.azure

# Edit with your Azure and GitLab credentials
nano .env.azure

# Validate configuration
./deploy/secrets/setup.sh --env azure
```

## 🔑 GitLab OAuth Setup

### Creating a GitLab OAuth Application

1. Navigate to https://gitlab.com/-/profile/applications
2. Click "New Application"
3. Configure the application:
   - **Name**: Legend Platform (or any name)
   - **Confidential**: ✅ **MUST be checked**
   - **Scopes**: Select `api`, `openid`, and `profile`

4. Add ALL redirect URIs for your environment:

#### Local Development URIs:
```
http://localhost:6300/callback
http://localhost:6100/api/auth/callback
http://localhost:6100/api/pac4j/login/callback
http://localhost:6201/depot-store/callback
http://localhost:6200/depot/callback
http://localhost:9000/studio/log.in/callback
http://localhost:9001/query/log.in/callback
```

#### Production URIs (replace YOUR-DOMAIN):
```
https://legend-engine.YOUR-DOMAIN/callback
https://legend-sdlc.YOUR-DOMAIN/api/auth/callback
https://legend-sdlc.YOUR-DOMAIN/api/pac4j/login/callback
https://legend-depot.YOUR-DOMAIN/depot/callback
https://legend-studio.YOUR-DOMAIN/studio/log.in/callback
https://legend-query.YOUR-DOMAIN/query/log.in/callback
```

5. After creating the application, you'll see:
   - **Application ID**: A long hex string like `dbdd707e51066b5b948d238bb0f84b7a7d2c883e008671c7dc33c1c5c639c862`
   - **Secret**: Starts with `gloas-` 

### ⚠️ Common OAuth Mistakes

❌ **DON'T use the numeric ID from the URL** (e.g., `29713286`)
✅ **DO use the Application ID** (hex string)

❌ **DON'T forget to check "Confidential"**
✅ **DO ensure Confidential is checked**

❌ **DON'T use mismatched redirect URIs**
✅ **DO add all redirect URIs exactly as shown**

## 🔧 Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GITLAB_APP_ID` | GitLab OAuth Application ID (hex) | `dbdd707e51066b5b948d238bb0f84b7a7d2c883e008671c7dc33c1c5c639c862` |
| `GITLAB_APP_SECRET` | GitLab OAuth Secret | `gloas-xxxxxxxxxxxxx` |
| `GITLAB_HOST` | GitLab instance | `gitlab.com` |

### Service URLs

| Variable | Local | Production |
|----------|-------|------------|
| `LEGEND_ENGINE_URL` | `http://localhost:6300` | `https://legend-engine.YOUR-DOMAIN` |
| `LEGEND_SDLC_URL` | `http://localhost:6100` | `https://legend-sdlc.YOUR-DOMAIN` |
| `LEGEND_STUDIO_URL` | `http://localhost:9000` | `https://legend-studio.YOUR-DOMAIN` |

### Azure-Specific (Production Only)

| Variable | Description |
|----------|-------------|
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |
| `AZURE_RESOURCE_GROUP` | Resource group name |
| `AZURE_ACR_NAME` | Container registry name |
| `AZURE_ACR_PASSWORD` | Container registry password |
| `AZURE_AKS_CLUSTER` | AKS cluster name |

## 🐛 Troubleshooting

### "Client authentication failed due to unknown client"

**Causes:**
- Using numeric ID instead of Application ID
- "Confidential" checkbox not enabled
- Wrong GitLab instance

**Solution:**
1. Check you're using the hex Application ID
2. Recreate the OAuth app with Confidential checked
3. Verify GITLAB_HOST matches your GitLab instance

### "State parameter is different from the one sent"

**Causes:**
- Cookie/session issues
- Multiple tabs with different sessions

**Solution:**
1. Clear all cookies for localhost
2. Use incognito/private browsing
3. Close all other localhost tabs
4. Try again with a single tab

### "Redirect URI mismatch"

**Causes:**
- Redirect URI not added to GitLab app
- HTTP vs HTTPS mismatch
- Port number mismatch

**Solution:**
1. Add exact URI to GitLab application
2. Ensure protocol matches (http/https)
3. Verify port numbers are correct

## 🛡️ Security Best Practices

1. **Never commit secrets** - Use `.env.local` or similar gitignored files
2. **Rotate credentials regularly** - Change OAuth secrets periodically
3. **Use environment-specific credentials** - Don't reuse production secrets in dev
4. **Implement secret scanning** - Use tools to detect accidental commits
5. **Consider secret management tools**:
   - Azure Key Vault (for Azure deployments)
   - HashiCorp Vault
   - Kubernetes Secrets
   - Docker Secrets

## 📝 File Validation

Run the setup script to validate your configuration:

```bash
# Validate local environment
./deploy/secrets/setup.sh --env local

# Validate Azure environment
./deploy/secrets/setup.sh --env azure

# Interactive setup for new installation
./deploy/secrets/setup.sh --interactive
```

## 🆘 Getting Help

If you encounter issues:

1. Check this documentation first
2. Run validation: `./deploy/secrets/setup.sh --validate`
3. Review logs: `docker-compose logs` or `kubectl logs`
4. Check GitLab OAuth application settings
5. Ensure all environment variables are set correctly

## 📚 Related Documentation

- [Deployment Guide](../DEPLOYMENT_GUIDE.md)
- [Docker Setup](../docker-finos-official/README_DOCKER.md)
- [Kubernetes Setup](../k8s/README.md)
- [Azure Deployment](../k8s-azure/)