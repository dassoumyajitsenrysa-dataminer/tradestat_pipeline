# Streamlit Cloud Deployment Guide - Private Access

## Quick Start (5 minutes)

### Step 1: Push Code to GitHub

```bash
cd c:\Users\das.soumyajit\Desktop\tradestat_pipeline

# Initialize git (first time only)
git init
git config user.name "Your Name"
git config user.email "your@email.com"

# Add files
git add .

# Commit
git commit -m "Initial dashboard commit"

# Create repository on GitHub:
# 1. Go to https://github.com/new
# 2. Name it "tradestat_pipeline"
# 3. DO NOT initialize with README (you have one)
# 4. Click Create Repository
# 5. Copy the repository URL

# Push to GitHub (replace with your URL)
git remote add origin https://github.com/YOUR-USERNAME/tradestat_pipeline.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. **Go to**: https://share.streamlit.io
2. **Sign in**: With your GitHub account (create one if needed)
3. **Click**: "New app" button
4. **Select**:
   - GitHub Repo: `YOUR-USERNAME/tradestat_pipeline`
   - Branch: `main`
   - Main file path: `dashboard/app.py`
5. **Click**: "Deploy"

⏳ Wait 2-3 minutes for deployment to complete.

---

## Private Access Options

### Option A: Password Protection (Recommended) ✅

**Most Secure - Only you control access**

1. **Add secrets file locally** (NOT committed to GitHub):
   
   Create `.streamlit/secrets.toml`:
   ```toml
   [credentials]
   password = "MySecurePassword123!"
   ```

2. **Update dashboard code** - Add this at the START of `dashboard/app.py`:

   ```python
   import streamlit as st
   
   def check_password():
       """Returns `True` if user has correct password."""
       if "password_correct" not in st.session_state:
           st.session_state.password_correct = False
   
       if not st.session_state.password_correct:
           with st.form("password_form"):
               st.write("🔐 Enter Password to Access Dashboard")
               password = st.text_input("Password", type="password")
               if st.form_submit_button("Login"):
                   if password == st.secrets["credentials"]["password"]:
                       st.session_state.password_correct = True
                       st.rerun()
                   else:
                       st.error("❌ Incorrect password")
           return False
       return True
   
   # Check password at app startup
   if not check_password():
       st.stop()
   
   # Rest of your dashboard code continues below...
   ```

3. **Deploy to Streamlit Cloud**:
   - In Streamlit Cloud, go to your app → Settings
   - Under "Secrets", paste your password:
     ```
     [credentials]
     password = "MySecurePassword123!"
     ```

4. **Share with Manager**:
   - Share the URL: `https://share.streamlit.io/your-username/tradestat_pipeline/main/dashboard/app.py`
   - Share password via separate secure channel (email, messaging app)

---

### Option B: Streamlit Sharing Permissions

**Use Built-in Privacy Controls**

1. **Deploy normally** (as above)
2. **Go to Streamlit Cloud dashboard**
3. **Click your app** → Three dots menu → **Settings**
4. **Under "Sharing settings"**:
   - Toggle to **Private**
   - Add your manager's email address
   - App will only be accessible to invited users

⚠️ Requires manager to have GitHub account.

---

### Option C: Custom Authentication

**Advanced - For enterprise environments**

Create `auth_manager.py`:
```python
import streamlit as st
from datetime import datetime, timedelta

def authenticate_user(username, password):
    """Check against your credentials"""
    valid_users = {
        "manager": "SecurePassword123!",
        "admin": "AdminPass456!",
    }
    return valid_users.get(username) == password

def login_widget():
    """Display login form"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("## 🔐 Trade Dashboard Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                if authenticate_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        return False
    
    return True
```

Use in dashboard:
```python
from auth_manager import login_widget

if not login_widget():
    st.stop()

# Your dashboard code...
```

---

## Deployment Checklist

- [ ] GitHub account created
- [ ] Code pushed to GitHub repository
- [ ] Streamlit account created (via GitHub)
- [ ] App deployed to Streamlit Cloud
- [ ] Password/authentication configured
- [ ] Test access with manager credentials
- [ ] Share link with manager
- [ ] Document password (store securely)
- [ ] Monitor Streamlit logs for errors

---

## Troubleshooting

### "App isn't loading"
- Check Streamlit Cloud logs
- Verify `dashboard/app.py` exists
- Ensure `requirements.txt` is in root directory

### "MongoDB connection error"
- For cloud: Use MongoDB Atlas (cloud-hosted)
- Update MongoDB URI in Streamlit secrets
- Whitelist Streamlit IP in MongoDB Atlas

### "Password not working"
- Verify `secrets.toml` is in `.streamlit/` folder
- Check password in Streamlit Cloud settings matches locally
- Clear browser cache and try again

### "Manager can't access"
- For password: Ensure password shared via secure channel
- For GitHub auth: Invite manager's GitHub account
- For public: Check app visibility settings

---

## Security Checklist

✅ **DO:**
- Use strong passwords (12+ chars, mixed case, numbers, symbols)
- Store passwords in `secrets.toml` (never in code)
- Use HTTPS only (Streamlit Cloud default)
- Change password periodically
- Monitor access logs
- Keep dependencies updated

❌ **DON'T:**
- Commit `secrets.toml` to GitHub
- Share passwords in email/chat
- Use same password across apps
- Expose API keys in code
- Allow public access to analytics

---

## After Deployment

### Monitor & Maintain

```bash
# Check recent deployments
# In Streamlit Cloud dashboard → Your app → Deployments

# View logs
# In Streamlit Cloud dashboard → Your app → Logs

# Update code
git add .
git commit -m "Update dashboard"
git push origin main
# Streamlit Cloud auto-deploys!

# Update dependencies
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

### Share Link Template

```
Subject: India Trade Analytics Dashboard Access

Hi [Manager Name],

Your exclusive access to the Trade Statistics Dashboard is ready!

🔗 Dashboard URL: https://share.streamlit.io/[your-username]/tradestat_pipeline/main/dashboard/app.py

🔐 Password: [send separately via secure channel]

📊 Features:
- Real-time trade data analysis
- Country-level drill-down analysis
- Growth trends and recommendations
- World map visualization
- Export data as CSV

For questions, contact: [your email]

Best regards,
[Your Name]
```

---

## Advanced: MongoDB Atlas Setup

For cloud deployment, use MongoDB Atlas (free tier):

1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create a free cluster
4. Get connection string
5. Add to `.streamlit/secrets.toml`:
   ```toml
   [database]
   mongo_uri = "mongodb+srv://username:password@cluster.mongodb.net/tradestat"
   ```
6. Update `api/main.py` to use the URI from secrets

---

**Questions?** Check Streamlit docs: https://docs.streamlit.io/streamlitcloud/deploy-your-app
