from shipments2 import Shipment, TrackedShipment, ExpressParcel, FragileParcel, BulkFreight


s3 = ExpressParcel("SL-3120", "Uwera Trading", "J. Mugisha", "Huye", 2.5, 1800, 250000, 0.02, "received", 12)
print(s3.get_tracking_id(), s3.calculate_cost())

s4 = FragileParcel("SL-4077", "Peter K.", "Grace M.", "Rubavu", 8, 1600, 900000, 0.05, "received", "glass", 5000)
print(s4.get_tracking_id(), s4.calculate_cost())

s5 = BulkFreight("SL-5003", "John T.", "Eric R.", "Nyagatare", 320, 900, 0, 0, "received", 6, 14)
print(s5.get_tracking_id(), s5.calculate_cost())

s6 = BulkFreight("SL-5004", "Mary A.", "Claudine B.", "Kigali", 500, 900, 0, 0, "received", 4, 12)
print(s6.get_tracking_id(), s6.calculate_cost())

#Tracking Test code
from tracking import ScanEvent

e = ScanEvent("SL-3120", "2026-09-14 08:30", "Kigali Depot", "received")
print(e.get_timestamp(), e.get_location(), e.get_status())

try:
    ScanEvent("SL-3120", "14/09/2026", "Kigali Depot", "received")
except ValueError as err:
    print("Rejected:", err)

try:
    ScanEvent("SL-3120", "2026-09-14 08:30", "Kigali Depot", "lost")
except ValueError as err:
    print("Rejected:", err)

print(e)
print(e.to_dict())

first = e.get_datetime()
later = ScanEvent("SL-3120", "2026-09-14 18:15", "Huye", "delivered").get_datetime()
hours = (later - first).total_seconds() / 3600
print(f"Transit took {hours:.2f} hours")

from lmis import DuplicateTrackingIDError, ShipmentNotFoundError

try:
    raise DuplicateTrackingIDError("SL-3120 is already registered")
except DuplicateTrackingIDError as err:
    print("Rejected:", err)

try:
    raise ShipmentNotFoundError("no shipment with tracking id SL-9999")
except ShipmentNotFoundError as err:
    print("Rejected:", err)

#catching one must not catch the other.
try:
    try:
        raise ShipmentNotFoundError("missing")
    except DuplicateTrackingIDError:
        print("WRONG: caught by the wrong handler")
except ShipmentNotFoundError:
    print("Correct: each exception is caught only by its own handler")