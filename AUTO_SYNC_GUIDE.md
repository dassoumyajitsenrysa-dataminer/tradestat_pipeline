# 🔄 Database Auto-Sync Setup

Your database is now synced with MongoDB Atlas! Here's how to keep it updated automatically.

## Option 1: Sync Every Hour (Recommended)

Run in a terminal:
```bash
python sync_database.py --interval 3600
```

This will:
- Connect to local MongoDB
- Check for new scraped data
- Sync to MongoDB Atlas
- Run every hour automatically

## Option 2: Sync Daily

```bash
python sync_database.py --interval 86400
```

## Option 3: Sync Once (Manual)

```bash
python sync_database.py --once
```

Useful after manual scraping or testing.

## How It Works

```
Scraper
   ↓
Local MongoDB (port 27017)
   ↓ (sync_database.py)
   ↓
MongoDB Atlas (Cloud)
   ↓
Streamlit Cloud Dashboard
```

## What Gets Synced?

- ✅ hs_codes (12 documents)
- ✅ partner_countries (0 currently)

Latest sync status:
- Local MongoDB: Connected ✓
- MongoDB Atlas: Connected ✓
- Last sync: 2026-01-21 23:40:50

## Setup for Production

To run continuously in the background:

**Windows (PowerShell):**
```powershell
Start-Process python "sync_database.py --interval 3600"
```

**Linux/Mac:**
```bash
nohup python sync_database.py --interval 3600 &
```

**Docker (if needed):**
```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "sync_database.py", "--interval", "3600"]
```

## Troubleshooting

**Connection refused on localhost:27017?**
- Make sure MongoDB is running locally

**Can't connect to MongoDB Atlas?**
- Check MONGO_URI in .env file
- Verify IP is whitelisted in Atlas (0.0.0.0/0 for testing)

**What if sync fails?**
- Check logs for error messages
- Logs are saved to: logs/DB_SYNC_*.log

## Stop Auto-Sync

Press `Ctrl+C` in the terminal where sync is running.

---

**Your dashboard will now always have the latest data!** 🚀
