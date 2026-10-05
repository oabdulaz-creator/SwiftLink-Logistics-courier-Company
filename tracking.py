"""
tracking.py - Scan tracking for the SwiftLink Logistics MIS.

This module contains the ScanEvent class. A ScanEvent records one moment in
a shipment's journey: which shipment was scanned, when, where, and what stage
of delivery it had reached. The class validates its inputs, so an invalid
timestamp or status can never be stored inside the system.
"""

from datetime import datetime
from shipments2 import VALID_STATUSES
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"


class ScanEvent:
    """Record of one scan of a shipment at one point in the depot network.

    Data members:
        tracking_id, 
        timestamp,
        location,
        status
    """

    def __init__(self, tracking_id, timestamp, location, status):
       #check the timestamp can be parsed with our format.
        try:
            datetime.strptime(timestamp, TIMESTAMP_FORMAT)
        except ValueError:
            raise ValueError(
                f"'{timestamp}' is not a valid timestamp, "
                f"expected YYYY-MM-DD HH:MM")

        # check the status is one of the allowed values.
        clean_status = status.strip().lower()
        if clean_status not in VALID_STATUSES:
            raise ValueError(
                f"'{status}' is not a valid status, "
                f"expected one of: {', '.join(VALID_STATUSES)}")

        #store the validated values.
        self._tracking_id = tracking_id
        self._timestamp = timestamp
        self._location = location
        self._status = clean_status
    def get_tracking_id(self):
        """Return the id of the shipment that was scanned."""
        return self._tracking_id

    def get_timestamp(self):
        """Return the scan time as text in the form "YYYY-MM-DD HH:MM"."""
        return self._timestamp()

    def get_location(self):
        """Return the place where the shipment was scanned."""
        return self._location()

    def get_status(self):
        """Return the delivery stage recorded by this scan."""
        return self._status()
    def __str__(self):
        return f"{self._timestamp} {self._location} {self._status}"

    def to_dict(self):
        return {
            "type": "ScanEvent",
            "tracking_id": self._tracking_id,
            "timestamp": self._timestamp,
            "location": self._location,
            "status": self._status,
        }

    def get_datetime(self):
        return datetime.strptime(self._timestamp, TIMESTAMP_FORMAT)
    @classmethod
    def from_dict(cls, data):
        """Rebuild a scan event from a to_dict() dictionary.

        Raises:
            KeyError: a required field is missing from the dictionary.
            ValueError: the timestamp or status in the dictionary is invalid.
        """
        return cls(data["tracking_id"], data["timestamp"],
                   data["location"], data["status"])