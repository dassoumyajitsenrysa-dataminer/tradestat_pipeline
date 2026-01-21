# Streamlit Secrets Setup for Production

The dashboard now connects directly to MongoDB, removing the API dependency. For Streamlit Cloud production deployment, follow these steps:

## Option 1: Using Local MongoDB (Development)

When running locally on port 8502:
```bash
streamlit run dashboard/app.py
```

The app will automatically connect to `mongodb://localhost:27017` (default).

## Option 2: Using MongoDB Atlas (Production on Streamlit Cloud)

### Step 1: Get Your MongoDB Atlas Connection String

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create/select your cluster
3. Click "Connect" → "Drivers" → Select "Python 3.12 or later"
4. Copy the connection string (it looks like):
   ```
   mongodb+srv://username:password@cluster.mongodb.net/tradestat?retryWrites=true&w=majority
   ```

### Step 2: Add Secrets to Streamlit Cloud

1. Go to your app on [Streamlit Cloud](https://share.streamlit.io)
2. Click the three dots (⋯) → "Settings"
3. Go to "Secrets" tab
4. Add this secret (replace with your actual connection string):
   ```
   MONGO_URI = "mongodb+srv://username:password@cluster.mongodb.net/tradestat?retryWrites=true&w=majority"
   ```
5. Click "Save"

### Step 3: Rerun Your App

Your app will automatically redeploy and connect to MongoDB Atlas.

## Connection Behavior

The dashboard has graceful fallback:

- **If MONGO_URI secret exists**: Uses it (MongoDB Atlas in production)
- **If local MongoDB available**: Uses `mongodb://localhost:27017` (development)
- **If both fail**: Shows warnings but dashboard still loads with fallback data

## Testing Connectivity

To verify MongoDB connection is working:

1. Open your Streamlit app
2. Check the app logs - no connection warnings means it's working
3. Try loading the HS Code Details page
4. Charts should populate with data

## Troubleshooting

### Connection Timeout Error

**Problem**: `ServerSelectionTimeoutException`

**Solution**:
- Check your MongoDB URI is correct
- Verify database credentials are right
- If using Atlas, ensure IP whitelist includes Streamlit Cloud's IP range (use `0.0.0.0/0` for testing only, not recommended for production)

### No Data Displays

**Problem**: Dashboard loads but no data shows

**Solution**:
- Verify data is in your MongoDB database
- Check collection names match: `hs_codes`, `partner_countries`
- Query the database directly to confirm data exists

### "Could not fetch statistics" Warning

**Problem**: Warning message in dashboard

**Solution**:
- This is normal if MongoDB isn't available - fallback data is displayed
- Check `MONGO_AVAILABLE` flag in logs
- Verify your MONGO_URI secret in Streamlit Cloud settings

## Database Schema

The dashboard expects these collections:

### `hs_codes` Collection

```javascript
{
  "hs_code": "0101",
  "product_label": "Live horses",
  "trade_type": "EXPORT",
  // other fields...
}
```

### `partner_countries` Collection

```javascript
{
  "country_code": "IN",
  "country_name": "India",
  // other fields...
}
```

## Changing Secrets Later

1. Go to app settings on Streamlit Cloud
2. Update the `MONGO_URI` value
3. Click "Save"
4. App will redeploy automatically

## Security Best Practices

✅ **DO:**
- Use MongoDB Atlas (cloud-hosted)
- Keep connection string in Streamlit Secrets (not in code)
- Use database user with read-only permissions if possible
- Set IP whitelist to specific IPs (not 0.0.0.0/0)

❌ **DON'T:**
- Commit connection strings to GitHub
- Share your MongoDB URI in public forums
- Use production URI during development
- Set overly permissive IP whitelists

## Next Steps

1. **If you have MongoDB Atlas**: Add the MONGO_URI secret to Streamlit Cloud
2. **If you only have local MongoDB**: Dataset will show fallback data in production but work fully in development
3. **Optional**: Set up MongoDB Atlas for production-grade cloud hosting
