from collections import Counter
from datetime import datetime
from typing import Iterable, Dict, Any


def bookings_summary(bookings: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute simple KPIs for Supply Chain Portal bookings.

    `bookings` is a list of dicts (e.g. items from DynamoDB).
    """
    bookings = list(bookings)
    total = len(bookings)

    # Count by status
    statuses = [b.get("status", "UNKNOWN") for b in bookings]
    by_status = Counter(statuses)

    # Earliest / latest date (if date field exists, YYYY-MM-DD)
    def parse_date(b):
        d = b.get("date")
        if not d:
            return None
        try:
            return datetime.strptime(d, "%Y-%m-%d").date()
        except Exception:
            return None

    dates = [d for d in (parse_date(b) for b in bookings) if d]
    earliest = min(dates) if dates else None
    latest = max(dates) if dates else None

    return {
        "total_bookings": total,
        "by_status": dict(by_status),
        "earliest_date": earliest.isoformat() if earliest else None,
        "latest_date": latest.isoformat() if latest else None,
    }
