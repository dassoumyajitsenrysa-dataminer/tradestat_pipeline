# Deploy to Streamlit Cloud - Quick Commands

## Step 1: Initialize Git & Push to GitHub (Copy & Paste)

```powershell
cd C:\Users\das.soumyajit\Desktop\tradestat_pipeline

# Initialize git
git init
git config user.name "Your Name"
git config user.email "your.email@gmail.com"

# Add all files
git add .

# Create initial commit
git commit -m "Trade Statistics Dashboard - Ready for Deployment"

# Create new repository on GitHub: https://github.com/new
# Then paste your repository URL below (replace with your actual URL):

git remote add origin https://github.com/YOUR-USERNAME/tradestat_pipeline.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy on Streamlit Cloud

1. Go to: **https://share.streamlit.io**
2. Sign in with GitHub (create account if needed)
3. Click: **"New app"** button
4. Select:
   - **GitHub Repo**: `YOUR-USERNAME/tradestat_pipeline`
   - **Branch**: `main`
   - **Main file path**: `dashboard/app.py`
5. Click: **"Deploy"**

⏳ **Wait 2-3 minutes** for deployment...

---

## Step 3: Add Password Protection (RECOMMENDED)

### 3a. Locally (YOUR COMPUTER):

Create `.streamlit/secrets.toml` file with:
```toml
[credentials]
password = "MySecurePassword123!"
```

### 3b. Update Code:

Edit `dashboard/app.py` - Add this code at the VERY TOP (before any st.markdown):

```python
import streamlit as st

def check_password():
    """Password protection for dashboard"""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        with st.form("password_form"):
            st.write("🔐 **Enter Password to Access Dashboard**")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if password == st.secrets.get("credentials", {}).get("password", ""):
                    st.session_state.password_correct = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Try again.")
        return False
    return True

# Check password first
if not check_password():
    st.stop()

# ============ REST OF YOUR DASHBOARD CODE BELOW ============
```

### 3c. Push to GitHub:

```powershell
git add .
git commit -m "Add password protection"
git push origin main
```

### 3d. Add Secret to Streamlit Cloud:

1. Go to **https://share.streamlit.io**
2. Click your app
3. Click **"Settings"** (⚙️ icon)
4. Scroll to **"Secrets"** section
5. Paste:
   ```
   [credentials]
   password = "MySecurePassword123!"
   ```
6. Save

---

## Step 4: Share with Your Manager

**Send them:**
```
Dashboard URL: https://share.streamlit.io/YOUR-USERNAME/tradestat_pipeline/main/dashboard/app.py

Password: MySecurePassword123!
(Send password separately via email/message, not in the URL link)
```

---

## Files Ready for Deployment

✅ `dashboard/app.py` - Main dashboard (with all 6 pages)
✅ `requirements.txt` - All dependencies
✅ `.streamlit/config.toml` - Configuration
✅ `.gitignore` - Protects secrets
✅ `README.md` - Documentation

---

## Verify Before Deploying

Run these commands locally:

```powershell
# Install dependencies
pip install -r requirements.txt

# Check dashboard loads without errors
streamlit run dashboard/app.py --server.port=8502

# Visit http://localhost:8502 in browser
# Test each page works
```

---

## Troubleshooting

### Git not installed?
Download from: https://git-scm.com/download/win

### Can't find GitHub repo URL?
1. Go to https://github.com/your-username/tradestat_pipeline
2. Click green "Code" button
3. Copy HTTPS URL

### Dashboard won't load on Streamlit Cloud?
1. Check app logs in Streamlit Cloud dashboard
2. Ensure `requirements.txt` is in root directory
3. Verify `dashboard/app.py` exists

### Password not working?
1. Verify `.streamlit/secrets.toml` has the password locally
2. Check Streamlit Cloud "Secrets" has the same password
3. Clear browser cache (Ctrl+Shift+Delete)

---

## What Your Manager Will See

✅ Professional dashboard with India trade data
✅ 3 analysis modes (Overview, Drill-Down, Growth)
✅ Interactive charts and world map
✅ Search and export capabilities
✅ Strategic recommendations
✅ Password protected (private access)

---

## Done! 🎉

Your dashboard is now live and private!

**Share the URL + Password with your manager.**

---

## Future Updates

After deployment, if you want to update the dashboard:

```powershell
cd C:\Users\das.soumyajit\Desktop\tradestat_pipeline

# Make your changes to files

# Commit and push
git add .
git commit -m "Update description"
git push origin main

# Streamlit Cloud auto-deploys! ✅
# (Takes ~1 minute)
```

---

**Questions?** Check `DEPLOYMENT.md` or `README.md`
