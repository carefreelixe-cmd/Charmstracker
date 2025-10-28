"""
Schema and indexes for MongoDB collections
"""

from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING, TEXT


def setup_mongodb_indexes(db):
    """Setup all required indexes for the application"""
    
    # Charms collection indexes
    db.charms.create_indexes([
        IndexModel([("id", ASCENDING)], unique=True),
        IndexModel([("name", TEXT)]),
        IndexModel([("material", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("avg_price", ASCENDING)]),
        IndexModel([("popularity", DESCENDING)]),
        IndexModel([("last_updated", ASCENDING)]),
    ])
    
    # Price history collection indexes
    db.price_history.create_indexes([
        IndexModel([("charm_id", ASCENDING)]),
        IndexModel([("date", ASCENDING)]),
        IndexModel([
            ("charm_id", ASCENDING),
            ("date", ASCENDING)
        ]),
    ])
    
    # Listings collection indexes
    db.listings.create_indexes([
        IndexModel([("charm_id", ASCENDING)]),
        IndexModel([("platform", ASCENDING)]),
        IndexModel([("scraped_at", ASCENDING)]),
        IndexModel([
            ("charm_id", ASCENDING),
            ("platform", ASCENDING)
        ]),
    ])