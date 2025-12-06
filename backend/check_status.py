import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    client = AsyncIOMotorClient(os.getenv('MONGO_URI'))
    db = client.charmstracker
    charms = await db.charms.find({}).limit(10).to_list(length=10)
    
    print("Current charm statuses:")
    print("="*60)
    for c in charms:
        print(f'{c["name"]}: status="{c.get("status", "MISSING")}" is_retired={c.get("is_retired", "MISSING")}')
    print("="*60)
    
    client.close()

asyncio.run(check())
