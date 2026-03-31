# Installation Guide - Soups, Snacks & More

## Prerequisites

Before installing, you need:

| Requirement | Mac Install | Windows Install |
|-------------|-------------|-----------------|
| **Python 3.10+** | `brew install python` or [python.org](https://www.python.org/downloads/) | [python.org](https://www.python.org/downloads/) (check "Add to PATH") |
| **Node.js 18+** | `brew install node` or [nodejs.org](https://nodejs.org/) | [nodejs.org](https://nodejs.org/) |
| **Git** | `brew install git` or [git-scm.com](https://git-scm.com/) | [git-scm.com](https://git-scm.com/) |

### Verify prerequisites:
```bash
python3 --version   # Mac/Linux
python --version    # Windows
node --version
npm --version
git --version
```

---

## Mac Installation (Step-by-Step)

### Step 1: Open Terminal
Press `Cmd + Space`, type "Terminal", press Enter.

### Step 2: Choose a location
```bash
cd ~   # Or: cd ~/Documents or cd ~/Projects
```

### Step 3: Clone the repository
```bash
git clone https://github.com/ssubrahm/SoupsSnacks.git
```

### Step 4: Enter the directory
```bash
cd SoupsSnacks
```

### Step 5: Run the installer
```bash
./install.sh
```

If you get "permission denied":
```bash
chmod +x install.sh setup.sh
./install.sh
```

### Step 6: Seed demo data (optional but recommended)
```bash
source SSCo/bin/activate
python seed_demo_data.py
```

### Step 7: Start the application
```bash
./setup.sh
```

### Step 8: Open in browser
Go to: **http://localhost:3000**

Login with: `admin` / `admin123`

---

## Windows Installation (Step-by-Step)

### Step 1: Open Command Prompt
Press `Win + R`, type `cmd`, press Enter.

### Step 2: Choose a location
```cmd
cd %USERPROFILE%\Documents
```
Or any folder you prefer.

### Step 3: Clone the repository
```cmd
git clone https://github.com/ssubrahm/SoupsSnacks.git
```

### Step 4: Enter the directory
```cmd
cd SoupsSnacks
```

### Step 5: Run the installer
```cmd
install.bat
```

### Step 6: Seed demo data (optional but recommended)
```cmd
SSCo\Scripts\activate
python seed_demo_data.py
```

### Step 7: Start the application
```cmd
setup.bat
```

This opens two windows (backend and frontend). Keep both open.

### Step 8: Open in browser
Go to: **http://localhost:3000**

Login with: `admin` / `admin123`

---

## Installing from ZIP file

If you have `SoupsSnacks-dist.zip`:

### Mac:
```bash
unzip SoupsSnacks-dist.zip
cd SoupsSnacks
./install.sh
source SSCo/bin/activate
python seed_demo_data.py
./setup.sh
```

### Windows:
1. Right-click the zip → "Extract All"
2. Open Command Prompt in the extracted folder
3. Run:
```cmd
install.bat
SSCo\Scripts\activate
python seed_demo_data.py
setup.bat
```

---

## Creating a ZIP for distribution

From your existing Mac installation:
```bash
cd /Users/Srinath.Subrahmanyan
zip -r SoupsSnacks-dist.zip SoupsSnacks \
  -x "SoupsSnacks/.git/*" \
  -x "SoupsSnacks/SSCo/*" \
  -x "SoupsSnacks/frontend/node_modules/*" \
  -x "SoupsSnacks/db.sqlite3" \
  -x "SoupsSnacks/*.pyc" \
  -x "SoupsSnacks/*/__pycache__/*" \
  -x "SoupsSnacks/*/*/__pycache__/*"
```

This creates a ~500KB zip file you can share.

---

## Demo Credentials

After running `python seed_demo_data.py`:

| Role | Username | Password | Access |
|------|----------|----------|--------|
| Admin | admin | admin123 | Full access |
| Operator | operator | operator123 | Customers, Orders, Payments, Reports |
| Cook | cook | cook123 | Menu/Products only |

---

## Starting & Stopping

### Start the app:
- **Mac:** `./setup.sh`
- **Windows:** `setup.bat`

### Stop the app:
- Press `Ctrl + C` in each terminal window
- Or close the terminal windows

### Restart after computer reboot:
```bash
# Mac
cd ~/SoupsSnacks   # or wherever you installed it
./setup.sh

# Windows
cd %USERPROFILE%\Documents\SoupsSnacks
setup.bat
```

---

## Troubleshooting

### "command not found: python3" (Mac)
```bash
brew install python
```
Or download from python.org

### "python is not recognized" (Windows)
Reinstall Python from python.org and check **"Add Python to PATH"** during installation.

### "command not found: node"
Install Node.js from nodejs.org

### Port 3000 or 8000 already in use

**Mac:**
```bash
lsof -i :3000
kill -9 <PID>
```

**Windows:**
```cmd
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### "CSRF verification failed"
Clear browser cookies and try again, or use incognito mode.

### Database issues
Reset the database:
```bash
rm db.sqlite3
python manage.py migrate
python seed_demo_data.py
```

---

## What's Included

- **Customer Management** - Track customers with apartment/block filters
- **Product Catalog** - Products with cost breakdown and profit margins
- **Daily Offerings** - Manage daily menus
- **Order Management** - Full order lifecycle
- **Payment Tracking** - Multiple payment methods
- **Reports & Analytics** - Sales, profitability, customer analytics
- **Google Forms Integration** - Import orders from Google Forms
- **CSV/Excel Import** - Bulk import data

---

## Support

For issues: https://github.com/ssubrahm/SoupsSnacks/issues
