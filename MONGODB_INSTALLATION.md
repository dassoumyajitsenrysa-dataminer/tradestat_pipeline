# MongoDB Installation Guide for Windows

## Method 1: Using Windows Package Manager (Easiest) ✅

Run this command in PowerShell (Admin):
```powershell
winget install MongoDB.Server -e
```

Wait for the installation to complete (~5-10 minutes).

## Method 2: Using Chocolatey

If you have Chocolatey installed:
```powershell
choco install mongodb-community -y
```

## Method 3: Manual Download from Official Site

1. Go to: https://www.mongodb.com/try/download/community
2. Select:
   - Version: Latest (currently 7.0)
   - OS: Windows
   - Package: .msi Installer
3. Download and run the installer
4. Follow installation wizard with default settings

## Method 4: Pre-Configured Download Link

**Direct download (click to download):**
- https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.6-signed.msi

Then run: `msiexec /i mongodb-windows-x86_64-7.0.6-signed.msi /quiet /norestart`

---

## Verify MongoDB Installation

After installation, verify MongoDB is installed:

```powershell
mongod --version
```

You should see output like: `db version v7.0.6`

---

## Start MongoDB

### Option A: Run as Windows Service (Auto-start)
```powershell
net start MongoDB
```

### Option B: Run in Terminal
```powershell
mongod --dbpath="C:\data\db"
```

---

## Troubleshooting

**"mongod not found" after installation?**
- Restart your terminal
- Or add to PATH manually if needed

**Installation failed?**
- Try the direct download link (Method 4)
- Or run installer as Administrator
- Check disk space (needs ~1-2 GB)

**Can't start service?**
- Try running PowerShell as Administrator
- Check if port 27017 is available

---

## Next Steps After MongoDB is Running

Once you see "mongod --version" works:

1. **Verify setup:**
   ```bash
   python verify_setup.py
   ```

2. **Load data to MongoDB:**
   ```bash
   python -m data_loader.loader
   ```

3. **Start FastAPI (Terminal 1):**
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

4. **Start Streamlit (Terminal 2):**
   ```bash
   streamlit run dashboard/app.py
   ```

5. **Open Dashboard:**
   - http://localhost:8501

---

**Estimated Installation Time:** 5-10 minutes
**Disk Space Required:** ~1-2 GB
