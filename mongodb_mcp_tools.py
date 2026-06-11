from mongo_store import (
    save_audit_log_to_mongodb,
    load_audit_logs_from_mongodb,
    load_recent_decisions_by_workload,
    test_mongodb_connection,
)

def test_mongodb_memory():
    return test_mongodb_connection()

def load_audit_ledger(limit=20):
    return load_audit_logs_from_mongodb(limit)

def load_recent_decisions(workload_name, limit=5):
    return load_recent_decisions_by_workload(
        workload_name,
        limit
    )

def save_carbon_decision(audit_log):
    return save_audit_log_to_mongodb(audit_log)