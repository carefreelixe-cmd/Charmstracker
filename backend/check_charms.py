"""Check database for sample charm"""
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URI'))
db = client['charmstracker']

charms = list(db.charms.find().limit(5))

print("\n" + "="*60)
print("📋 Sample Charms in Database")
print("="*60 + "\n")

for i, charm in enumerate(charms, 1):
    print(f"{i}. {charm['name']}")
    print(f"   ID: {charm['_id']}")
    print(f"   Listings: {charm.get('listing_count', 0)}")
    print(f"   Last Updated: {charm.get('last_updated', 'Never')}")
    print()
