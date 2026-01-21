# MongoDB Installation & Startup Guide

## ✅ What Just Happened

MongoDB is being installed via Windows Package Manager. This may take **5-15 minutes** depending on your internet speed and system.

---

## 🚀 Installation Status

Run this command to check if MongoDB is ready:

```powershell
mongod --version
```

**Expected output:** `db version v7.0.6` (or similar)

---

## ⏳ If Installation is Still Running

**Please wait** - Do NOT close the terminal. MongoDB is downloading (~750 MB).

You'll see it's done when:
1. The terminal returns to the prompt
2. `mongod --version` returns a version number

---

## 🔄 Next Steps (Once MongoDB Shows a Version)

### Step 1: Create Data Directory
```powershell
mkdir C:\data\db
```

### Step 2: Start MongoDB (Choose ONE)

**Option A: Run in Background (Easier)**
```powershell
# Start MongoDB in a new PowerShell window
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'mongod --dbpath="C:\data\db"'
```

**Option B: Run in Current Terminal**
```powershell
mongod --dbpath="C:\data\db"
```

You should see:
```
{"msg":"waiting for connections","port":27017}
```

### Step 3: Verify Everything Works

In a **new** PowerShell terminal, run:
```bash
python verify_setup.py
```

All checks should show ✓

---

## 🚀 Start the Platform

Once MongoDB is running and verified:

**Terminal 1: Start API**
```bash
uvicorn api.main:app --reload --port 8000
```

**Terminal 2: Start Dashboard**
```bash
streamlit run dashboard/app.py
```

**Terminal 3: Load Data**
```bash
python -m data_loader.loader
```

Then open: **http://localhost:8501**

---

## ⚠️ Troubleshooting

### "mongod: command not found"
- Wait for winget installation to complete
- Try: `refreshenv` in PowerShell
- Or restart PowerShell

### "Address already in use"
- Another process is using port 27017
- Run: `netstat -ano | findstr :27017`
- Kill the process: `taskkill /PID <PID> /F`

### Installation hung?
- Kill the process: `Ctrl+C`
- Check disk space: `dir C:\ -h` (need ~2GB free)
- Try manual installation: https://www.mongodb.com/try/download/community

---

## 📍 MongoDB Files Location

After installation, MongoDB files are in:
```
C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe
```

Data will be stored at:
```
C:\data\db\
```

---

## 🎯 Quick Reference

| Step | Command |
|------|---------|
| Check install | `mongod --version` |
| Create data dir | `mkdir C:\data\db` |
| Start MongoDB | `mongod --dbpath="C:\data\db"` |
| Verify setup | `python verify_setup.py` |
| Load data | `python -m data_loader.loader` |
| Start API | `uvicorn api.main:app --reload` |
| Start Dashboard | `streamlit run dashboard/app.py` |

---

## ⏱️ Expected Times

- MongoDB Installation: 5-15 minutes
- Data Loading: 2-5 minutes
- Platform Startup: 3-5 minutes
- **Total Setup Time: 15-30 minutes**

---

**Keep this terminal open while MongoDB installs!**

When you see the prompt return, run:
```powershell
mongod --version
```

Then let me know if it shows a version number! 🎉
