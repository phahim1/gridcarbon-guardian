import os
from datetime import datetime
from typing import Any, Dict, List

from pymongo import MongoClient, DESCENDING
from pymongo.errors import PyMongoError


def get_mongo_collection():
    mongodb_uri = os.getenv("MONGODB_URI")
    database_name = os.getenv("MONGODB_DB", "gridcarbon_guardian")
    collection_name = os.getenv("MONGODB_COLLECTION", "audit_logs")

    if not mongodb_uri:
        return None

    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    db = client[database_name]
    return db[collection_name]


def save_audit_log_to_mongodb(log_entry: Dict[str, Any]) -> bool:
    collection = get_mongo_collection()

    if collection is None:
        return False

    try:
        log_entry = dict(log_entry)
        log_entry["stored_at"] = datetime.utcnow().isoformat()
        collection.insert_one(log_entry)
        return True
    except PyMongoError:
        return False


def load_audit_logs_from_mongodb(limit: int = 20) -> List[Dict[str, Any]]:
    collection = get_mongo_collection()

    if collection is None:
        return []

    try:
        cursor = collection.find({}, {"_id": 0}).sort("stored_at", DESCENDING).limit(limit)
        return list(cursor)
    except PyMongoError:
        return []