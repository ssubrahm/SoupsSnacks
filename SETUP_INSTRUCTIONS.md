# Local Setup Instructions for Mac

## Prerequisites Checklist
- [ ] Python 3.10+ installed (`python3 --version`)
- [ ] Node.js 16+ installed (`node --version`)
- [ ] Git installed (`git --version`)
- [ ] GitHub Personal Access Token created

## Step 1: Get GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Configure:
   - Note: `SoupsSnacks Development`
   - Expiration: Your choice (90 days or No expiration)
   - Scopes: Check **repo** (full control)
4. Click "Generate token"
5. **COPY THE TOKEN** - you'll need it in Step 4

## Step 2: Set Up Local Directory

```bash
# Navigate to your home directory
cd /Users/Srinath.Subrahmanyan

# Remove incomplete directory
rm -rf SoupsSnacks

# Initialize fresh git repository
mkdir SoupsSnacks
cd SoupsSnacks
git init
git branch -M main
```

## Step 3: Copy Project Files

Option A - If you have the workspace files locally:
```bash
# Copy all files from workspace
cp -r /project/workspace/SoupsSnacks/* .
cp /project/workspace/SoupsSnacks/.env .
cp /project/workspace/SoupsSnacks/.env.example .
cp /project/workspace/SoupsSnacks/.gitignore .
```

Option B - Or download from the workspace and extract:
```bash
# If you have SoupsSnacks.tar.gz
tar -xzf ~/Downloads/SoupsSnacks.tar.gz
```

Option C - Clone from GitHub after pushing (use this after Step 4 completes):
```bash
cd /Users/Srinath.Subrahmanyan
rm -rf SoupsSnacks
git clone https://github.com/ssubrahm/SoupsSnacks.git
cd SoupsSnacks
```

## Step 4: Connect to GitHub and Push

```bash
cd /Users/Srinath.Subrahmanyan/SoupsSnacks

# Configure git
git config user.name "Srinath Subrahmanyan"
git config user.email "ssubrahm@users.noreply.github.com"

# Add all files
git add .
git status  # Verify what will be committed

# Commit
git commit -m "Initial project setup - Step 1 Foundation"

# Add remote (if not already added)
git remote add origin https://github.com/ssubrahm/SoupsSnacks.git

# Push to GitHub - You'll be prompted for credentials
git push -u origin main
```

**When prompted:**
- Username: `ssubrahm`
- Password: **Paste your Personal Access Token** (not your GitHub password!)

## Step 5: Set Up Python Virtual Environment

```bash
cd /Users/Srinath.Subrahmanyan/SoupsSnacks

# Create virtual environment
python3 -m venv SSCo

# Activate it
source SSCo/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Test the backend
python manage.py runserver
```

Open browser to http://localhost:8000/api/health/ - should see:
```json
{"status":"healthy","message":"Soups, Snacks, and More API is running"}
```

## Step 6: Set Up Frontend

```bash
# Open a NEW terminal window
cd /Users/Srinath.Subrahmanyan/SoupsSnacks/frontend

# Install dependencies
npm install

# Start React dev server
npm start
```

Browser should auto-open to http://localhost:3000

## Step 7: Verify Everything Works

### Backend (Terminal 1):
- [ ] `python manage.py runserver` - running on port 8000
- [ ] http://localhost:8000/api/health/ - returns healthy status
- [ ] http://localhost:8000/admin/ - admin panel loads

### Frontend (Terminal 2):
- [ ] `npm start` - running on port 3000
- [ ] http://localhost:3000 - dashboard loads
- [ ] Sidebar navigation works
- [ ] "API Status" shows green checkmark

## Alternative: Use Personal Access Token in Git Config (Store Token)

To avoid entering token every time:

```bash
# macOS Keychain will remember the token
git config --global credential.helper osxkeychain

# Or use this format for remote (includes token in URL - LESS SECURE)
git remote set-url origin https://YOUR_TOKEN@github.com/ssubrahm/SoupsSnacks.git
```

## Troubleshooting

### "Authentication failed" when pushing
- Make sure you're using the **Personal Access Token** as password, not GitHub password
- Verify token has **repo** scope enabled
- Token might have expired - create a new one

### "Permission denied" errors
- Check file permissions: `ls -la`
- Make sure you own the directory: `sudo chown -R $(whoami) SoupsSnacks`

### Port 8000 or 3000 already in use
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Python/Node version issues
```bash
# Check versions
python3 --version  # Should be 3.10+
node --version     # Should be 16+
npm --version
```

## Next Steps

Once validation passes, you're ready for **Step 2 - Auth and Roles**!

## Quick Reference Commands

```bash
# Backend (from project root)
source venv/bin/activate        # Activate virtual env
python manage.py runserver      # Start backend
python manage.py migrate        # Run migrations
python manage.py createsuperuser # Create admin user

# Frontend (from frontend/)
npm start                       # Start dev server
npm run build                   # Build for production
npm test                        # Run tests

# Git
git status                      # Check status
git add .                       # Stage all changes
git commit -m "message"         # Commit
git push                        # Push to GitHub
```
