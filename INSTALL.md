# Installation Guide

## Quick Install (Mac/Linux)

1. **Extract the zip file:**
   ```bash
   unzip SoupsSnacks.zip
   cd SoupsSnacks
   ```

2. **Run the installer:**
   ```bash
   ./install.sh
   ```

3. **Seed demo data (optional):**
   ```bash
   python seed_demo_data.py
   ```

4. **Start the app:**
   ```bash
   ./setup.sh
   ```

5. **Open in browser:** http://localhost:3000

---

## Prerequisites

Before installing, ensure you have:

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)

### Check versions:
```bash
python3 --version   # Should be 3.10 or higher
node --version      # Should be 18 or higher
npm --version       # Should be 8 or higher
```

---

## Manual Installation

If the install script doesn't work:

```bash
# 1. Create virtual environment
python3 -m venv SSCo
source SSCo/bin/activate

# 2. Install Python packages
pip install -r requirements.txt

# 3. Install frontend packages
cd frontend
npm install
cd ..

# 4. Set up database
python manage.py migrate

# 5. Create admin user
python manage.py createsuperuser

# 6. Start the app
./setup.sh
```

---

## Demo Credentials

If you ran `python seed_demo_data.py`:

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Operator | operator | operator123 |
| Cook | cook | cook123 |

---

## Troubleshooting

### "command not found: python3"
Install Python from https://www.python.org/downloads/

### "command not found: node"
Install Node.js from https://nodejs.org/

### Port 3000 already in use
```bash
# Find and kill the process
lsof -i :3000
kill -9 <PID>
```

### Port 8000 already in use
```bash
lsof -i :8000
kill -9 <PID>
```

### Permission denied on install.sh
```bash
chmod +x install.sh
./install.sh
```

---

## Google Sheets Integration (Optional)

To enable Google Forms order import:

1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create a Service Account
4. Download JSON credentials
5. Save as `google_credentials.json` in project root
6. Share your Google Sheet with the service account email

See `GOOGLE_FORMS_SETUP.md` for detailed instructions.
