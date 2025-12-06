from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone
import sys

# Import routes
from routes.charms import router as charms_router
from routes.market import router as market_router
from routes.scraper import router as scraper_router

# Import scheduler
from services.scheduler import start_scheduler, stop_scheduler


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Setup logging to file
class TeeLogger:
    """Logger that writes to both console and file"""
    def __init__(self, filepath):
        self.file = open(filepath, 'a', encoding='utf-8')
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        
    def write(self, message):
        self.stdout.write(message)
        self.file.write(message)
        self.file.flush()
        
    def flush(self):
        self.stdout.flush()
        self.file.flush()

# Redirect stdout and stderr to note.txt
log_file = ROOT_DIR / 'note.txt'
tee_logger = TeeLogger(log_file)
sys.stdout = tee_logger
sys.stderr = tee_logger

print(f"\n{'='*60}")
print(f"SERVER STARTED AT: {datetime.now()}")
print(f"Logging to: {log_file}")
print(f"{'='*60}\n")

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="CharmTracker API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "CharmTracker API is running"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include routers
app.include_router(charms_router)
app.include_router(market_router)
app.include_router(scraper_router)
app.include_router(api_router)

# CORS Configuration - MUST be after routers but before any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://charmstracker.com",
        "https://www.charmstracker.com",
        "https://charms.freelixe.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Start background scheduler on app startup"""
    try:
        logger.info("🚀 Starting CharmTracker API...")
        
        # Start background scheduler
        logger.info("Starting background scheduler...")
        await start_scheduler(db)
        logger.info("✅ Background scheduler started successfully")
        
        # NOTE: Removed automatic scraping on startup
        # Use add_fallback_listings.py script to populate data manually
        # Or trigger updates via API: POST /api/scraper/update-all
        
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        logger.info("Stopping background scheduler...")
        await stop_scheduler()
        logger.info("Background scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
    
    client.close()
    logger.info("MongoDB connection closed")