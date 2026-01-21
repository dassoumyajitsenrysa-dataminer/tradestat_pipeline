#!/usr/bin/env python
"""
Upload local MongoDB data to MongoDB Atlas
Usage: python upload_to_atlas.py <MONGO_ATLAS_URI>

Example:
python upload_to_atlas.py "mongodb+srv://admin:password@cluster0.mongodb.net/tradestat?retryWrites=true&w=majority"
"""

import json
import sys
from pymongo import MongoClient

def upload_data(atlas_uri):
    """Upload HS codes and partner countries to MongoDB Atlas"""
    
    try:
        # Connect to Atlas
        print(f"🔗 Connecting to MongoDB Atlas...")
        client = MongoClient(atlas_uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # Test connection
        print("✅ Connected to MongoDB Atlas!")
        
        db = client['tradestat']
        
        # Upload HS codes
        print("\n📤 Uploading HS codes...")
        with open('hs_codes.json', 'r') as f:
            hs_codes = json.load(f)
        
        # Clear existing data
        db['hs_codes'].delete_many({})
        
        # Insert new data
        result = db['hs_codes'].insert_many(hs_codes)
        print(f"✅ Uploaded {len(hs_codes)} HS codes")
        
        # Upload partner countries (if exists)
        try:
            print("\n📤 Uploading partner countries...")
            with open('partner_countries.json', 'r') as f:
                partner_countries = json.load(f)
            
            if partner_countries:  # Only insert if not empty
                db['partner_countries'].delete_many({})
                result = db['partner_countries'].insert_many(partner_countries)
                print(f"✅ Uploaded {len(partner_countries)} partner countries")
            else:
                print("ℹ️ partner_countries.json is empty, skipping")
        except FileNotFoundError:
            print("ℹ️ partner_countries.json not found, skipping")
        
        # Verify
        print("\n🔍 Verification:")
        hs_count = db['hs_codes'].count_documents({})
        partner_count = db['partner_countries'].count_documents({})
        print(f"  • HS Codes in Atlas: {hs_count}")
        print(f"  • Partner Countries in Atlas: {partner_count}")
        
        print("\n✨ SUCCESS! Your data is now on MongoDB Atlas!")
        print("   Your Streamlit dashboard will use this data automatically.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nMake sure your connection string is correct:")
        print("  mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/database")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Missing connection string!")
        print("\nUsage: python upload_to_atlas.py '<MONGO_ATLAS_URI>'")
        print("\nExample:")
        print('  python upload_to_atlas.py "mongodb+srv://admin:password@cluster0.mongodb.net/tradestat"')
        sys.exit(1)
    
    atlas_uri = sys.argv[1]
    upload_data(atlas_uri)
