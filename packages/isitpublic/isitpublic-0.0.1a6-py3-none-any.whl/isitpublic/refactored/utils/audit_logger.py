"""
Audit logging functionality for public domain validations.
This module handles logging, tracking, and audit trail functionality.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..models import ContentItem


class AuditLogger:
    """
    Handles audit logging, PD determinations tracking, and change tracking functionality.
    """

    def __init__(self):
        """Initialize the AuditLogger."""
        self.audit_log: List[Dict[str, Any]] = []
        self.historical_copyright_data: Dict[str, List[Dict[str, Any]]] = {}
        self.pd_determinations: List[Dict[str, Any]] = []

    def log_pd_determination(
        self, content_item: ContentItem, result: Dict[str, Any], method: str = "unknown"
    ) -> str:
        """
        Log a PD determination for audit trail and change tracking.

        Args:
            content_item: The item that was analyzed
            result: The result of the PD analysis
            method: The method used for analysis

        Returns:
            Unique ID for the log entry
        """
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": method,
            "input": {
                "title": content_item.title,
                "has_content": bool(content_item.content),
                "has_snippet": bool(content_item.snippet),
                "has_url": bool(content_item.url),
            },
            "result": result,
            "version": getattr(self, "__version__", "unknown"),
        }

        self.pd_determinations.append(log_entry)
        self.audit_log.append(log_entry)  # Also add to general audit log

        return log_entry["id"]

    def get_audit_log(
        self, limit: int | None = None, method: str | None = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit log entries.

        Args:
            limit: Maximum number of entries to return (None for all)
            method: Filter by specific analysis method

        Returns:
            List of audit log entries
        """
        entries = self.audit_log[:]

        if method:
            entries = [entry for entry in entries if entry.get("method") == method]

        if limit:
            entries = entries[-limit:]  # Get last N entries

        return entries

    def get_pd_determinations(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """
        Retrieve PD determination history.

        Args:
            limit: Maximum number of determinations to return (None for all)

        Returns:
            List of PD determination entries
        """
        if limit:
            return self.pd_determinations[-limit:]
        return self.pd_determinations

    def track_copyright_status_change(
        self,
        work_identifier: str,
        from_status: Dict[str, Any],
        to_status: Dict[str, Any],
        reason: str = "unknown",
    ) -> str:
        """
        Track a change in copyright status for a specific work.

        Args:
            work_identifier: Unique identifier for the work
            from_status: Previous copyright status
            to_status: New copyright status
            reason: Reason for the status change

        Returns:
            Unique ID for the change tracking entry
        """
        change_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "work_identifier": work_identifier,
            "from_status": from_status,
            "to_status": to_status,
            "reason": reason,
            "version": getattr(self, "__version__", "unknown"),
        }

        if work_identifier not in self.historical_copyright_data:
            self.historical_copyright_data[work_identifier] = []

        self.historical_copyright_data[work_identifier].append(change_entry)

        # Add to audit log as well
        audit_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": "copyright_status_change",
            "input": {"work_identifier": work_identifier, "reason": reason},
            "result": {"status_changed": True, "new_status": to_status},
            "version": getattr(self, "__version__", "unknown"),
        }
        self.audit_log.append(audit_entry)

        return change_entry["id"]

    def get_historical_copyright_status(
        self, work_identifier: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve historical copyright status changes for a work.

        Args:
            work_identifier: Unique identifier for the work

        Returns:
            List of status change entries for the work
        """
        return self.historical_copyright_data.get(work_identifier, [])

    def get_work_copyright_timeline(self, work_identifier: str) -> Dict[str, Any]:
        """
        Get a complete timeline of copyright status for a work.

        Args:
            work_identifier: Unique identifier for the work

        Returns:
            Dictionary with timeline information
        """
        history = self.get_historical_copyright_status(work_identifier)

        if not history:
            return {
                "work_identifier": work_identifier,
                "has_history": False,
                "timeline": [],
                "current_status": None,
            }

        # Sort by timestamp
        sorted_history = sorted(history, key=lambda x: x["timestamp"])

        return {
            "work_identifier": work_identifier,
            "has_history": True,
            "timeline": sorted_history,
            "current_status": sorted_history[-1]["to_status"]
            if sorted_history
            else None,
            "first_status": sorted_history[0]["from_status"]
            if sorted_history
            else None,
        }

    def get_tracked_works_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all tracked works.

        Returns:
            Dictionary with summary statistics
        """
        works_with_history = {}
        for work_id, history in self.historical_copyright_data.items():
            # Filter to only work status changes (not law updates)
            work_changes = [
                h for h in history if h.get("type") != "copyright_law_update"
            ]
            if work_changes:
                works_with_history[work_id] = {
                    "change_count": len(work_changes),
                    "first_change": work_changes[0]["timestamp"]
                    if work_changes
                    else None,
                    "last_change": work_changes[-1]["timestamp"]
                    if work_changes
                    else None,
                }

        return {
            "total_tracked_works": len(works_with_history),
            "works_with_history": works_with_history,
            "total_audit_entries": len(self.audit_log),
            "total_pd_determinations": len(self.pd_determinations),
        }
