#!/usr/bin/env python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
dbs = client.list_database_names()
print('Available databases:', dbs)

# Check both potential database names
for db_name in ['tradestat', 'tradestat_db']:
    if db_name in dbs:
        count = client[db_name].hs_codes.count_documents({})
        print(f'\n✓ Database "{db_name}" found:')
        print(f'  - HS Codes count: {count}')
        
        # Check for HS Code 61091000
        doc = client[db_name].hs_codes.find_one({'hs_code': '61091000'})
        if doc:
            print(f'  - HS Code 61091000 found')
            print(f'    Trade Mode: {doc.get("trade_mode")}')
            print(f'    Completeness: {doc.get("metadata", {}).get("data_completeness_percent")}%')
        else:
            print(f'  - HS Code 61091000 NOT found')

# Show API database name used
from api.database import MONGO_DB_NAME
print(f'\n⚙️ API is configured to use database: "{MONGO_DB_NAME}"')
