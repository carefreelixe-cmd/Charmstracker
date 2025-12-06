import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def check():
    client = AsyncIOMotorClient(os.getenv('MONGO_URI'))
    db = client.charmstracker
    charm = await db.charms.find_one({})
    
    print("Full charm document:")
    print("="*60)
    print(json.dumps({k: v for k, v in charm.items() if k != '_id'}, indent=2, default=str))
    print("="*60)
    
    client.close()

asyncio.run(check())
