import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from pymongo import MongoClient, DESCENDING
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError, ConfigurationError


def get_mongo_collection():
    mongodb_uri = os.getenv("MONGODB_URI")
    database_name = os.getenv("MONGODB_DB", "gridcarbon_guardian")
    collection_name = os.getenv("MONGODB_COLLECTION", "audit_logs")

    if not mongodb_uri:
        return None

    client = MongoClient(
        mongodb_uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )

    db = client[database_name]
    return db[collection_name]


def test_mongodb_connection() -> bool:
    try:
        collection = get_mongo_collection()

        if collection is None:
            return False

        collection.database.client.admin.command("ping")
        return True

    except Exception:
        return False


def decision_exists(decision_id: str) -> bool:
    try:
        collection = get_mongo_collection()

        if collection is None:
            return False

        existing = collection.find_one(
            {"decision_id": decision_id},
            {"_id": 1},
        )

        return existing is not None

    except Exception:
        return False


def save_audit_log_to_mongodb(log_entry: Dict[str, Any]) -> Dict[str, Any]:
    try:
        collection = get_mongo_collection()

        if collection is None:
            return {
                "success": False,
                "message": "MongoDB URI not configured.",
            }

        log_entry = dict(log_entry)
        decision_id = log_entry.get("decision_id")

        if not decision_id:
            return {
                "success": False,
                "message": "Missing decision_id in audit log.",
            }

        if decision_exists(decision_id):
            return {
                "success": False,
                "message": f"Decision {decision_id} already exists in MongoDB.",
            }

        log_entry["stored_at"] = datetime.utcnow().isoformat()
        collection.insert_one(log_entry)

        return {
            "success": True,
            "message": "Audit log saved to MongoDB decision memory.",
        }

    except ConfigurationError as error:
        return {
            "success": False,
            "message": f"MongoDB DNS/configuration error: {error}",
        }

    except (PyMongoError, ServerSelectionTimeoutError) as error:
        return {
            "success": False,
            "message": f"MongoDB save failed: {error}",
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"Unexpected MongoDB error: {error}",
        }


def load_audit_logs_from_mongodb(limit: int = 20) -> List[Dict[str, Any]]:
    try:
        collection = get_mongo_collection()

        if collection is None:
            return []

        cursor = (
            collection
            .find({}, {"_id": 0})
            .sort("stored_at", DESCENDING)
            .limit(limit)
        )

        return list(cursor)

    except Exception:
        return []


def load_recent_decisions_by_workload(
    workload_name: str,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    try:
        collection = get_mongo_collection()

        if collection is None:
            return []

        cursor = (
            collection
            .find(
                {"workload": workload_name},
                {"_id": 0},
            )
            .sort("stored_at", DESCENDING)
            .limit(limit)
        )

        return list(cursor)

    except Exception:
        return []


def load_recent_high_risk_decisions(limit: int = 5) -> List[Dict[str, Any]]:
    try:
        collection = get_mongo_collection()

        if collection is None:
            return []

        cursor = (
            collection
            .find(
                {
                    "$or": [
                        {"approval_required": True},
                        {"grid_load": {"$gte": 85}},
                        {"deadline_violation": True},
                    ]
                },
                {"_id": 0},
            )
            .sort("stored_at", DESCENDING)
            .limit(limit)
        )

        return list(cursor)

    except Exception:
        return []


