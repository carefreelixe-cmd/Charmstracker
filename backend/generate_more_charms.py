"""
Generate more sample charms for CharmTracker
Creates 80 charms with realistic data
"""

import asyncio
import sys
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Extended charm templates
ADJECTIVES = ["Vintage", "Modern", "Classic", "Delicate", "Elegant", "Rustic", "Shiny", "Antique", "Handcrafted", "Minimalist"]
MATERIALS = ["Silver", "Gold"]
DESIGNS = [
    "Heart", "Cross", "Star", "Moon", "Sun", "Butterfly", "Dragonfly", "Angel Wings", 
    "Flower", "Tree", "Bird", "Feather", "Key", "Lock", "Crown", "Shell", 
    "Anchor", "Compass", "Infinity", "Music Note"
]
STATUS = ["Active", "Retired"]

def generate_price():
    return round(random.uniform(25.0, 299.99), 2)

def generate_popularity():
    return random.randint(1, 100)

def generate_description(name):
    descriptions = [
        f"Beautiful {name.lower()} design crafted with attention to detail",
        f"Elegant {name.lower()} charm perfect for any collection",
        f"Timeless {name.lower()} piece with intricate detailing",
        f"Stunning {name.lower()} charm that captures the essence of beauty",
        f"Exquisite {name.lower()} charm with remarkable craftsmanship"
    ]
    return random.choice(descriptions)

async def generate_charms():
    try:
        # Connect to MongoDB
        mongo_uri = os.getenv('MONGO_URL')
        db_name = os.getenv('DB_NAME', 'charmtracker')
        
        client = AsyncIOMotorClient(mongo_uri)
        db = client[db_name]
        
        # Clear existing charms
        await db.charms.delete_many({})
        
        # Generate 80 unique charms
        charms_to_insert = []
        used_names = set()
        
        while len(charms_to_insert) < 80:
            adj = random.choice(ADJECTIVES)
            design = random.choice(DESIGNS)
            name = f"{adj} {design} Charm"
            
            if name in used_names:
                continue
                
            used_names.add(name)
            
            from bson import ObjectId
            
            charm = {
                "_id": ObjectId(),
                "name": name,
                "description": generate_description(name),
                "material": random.choice(MATERIALS),
                "status": random.choice(STATUS),
                "price": generate_price(),
                "popularity": generate_popularity(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Add some market data
            current_price = charm["price"]
            price_history = []
            listings = []
            
            # Generate price history for last 30 days
            for i in range(30):
                date = datetime.utcnow() - timedelta(days=i)
                variation = random.uniform(-10, 10)
                historic_price = max(25.0, current_price + variation)
                price_history.append({
                    "date": date,
                    "price": round(historic_price, 2)
                })
            
            # Generate some sample listings
            num_listings = random.randint(3, 8)
            for _ in range(num_listings):
                listing_price = round(current_price * random.uniform(0.8, 1.2), 2)
                listings.append({
                    "source": random.choice(["James Avery", "eBay", "Etsy", "Poshmark"]),
                    "price": listing_price,
                    "url": "https://example.com/listing",
                    "created_at": datetime.utcnow()
                })
            
            charm["price_history"] = price_history
            charm["listings"] = listings
            
            charms_to_insert.append(charm)
        
        # Insert all charms
        await db.charms.insert_many(charms_to_insert)
        print(f"Successfully generated and inserted {len(charms_to_insert)} charms")
        
    except Exception as e:
        print(f"Error: {e}")
        raise e
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(generate_charms())