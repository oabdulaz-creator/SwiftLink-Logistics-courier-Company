from shipments2 import Shipment, ExpressParcel, BulkFreight
from lmis import (LogisticsMIS, ShipmentNotFoundError, NotDeliveredError)

s1 = Shipment("SL-1001", "Amara K.", "J. Niyonzima", "Kigali", 4, 1500)
s3 = ExpressParcel("SL-3120", "Uwera Trading", "J. Mugisha", "Huye", 2.5, 1800, 250000, 0.02, "received", 12)
s5 = BulkFreight("SL-5003", "John T.", "Eric R.", "Nyagatare", 320, 900, 0, 0, "received", 6, 14)

mis = LogisticsMIS()
for shipment in (s1, s3, s5):
    mis.add_shipment(shipment)

# Recorded OUT of order on purpose.
mis.record_scan("SL-3120", "2026-09-14 16:40", "Huye Depot", "out for delivery")
mis.record_scan("SL-3120", "2026-09-14 08:30", "Kigali Depot", "received")
mis.record_scan("SL-3120", "2026-09-14 18:15", "Huye", "delivered")
mis.record_scan("SL-3120", "2026-09-14 12:05", "Muhanga Hub", "in transit")
mis.record_scan("SL-1001", "2026-09-14 09:00", "Kigali Depot", "received")
mis.record_scan("SL-5003", "2026-09-15 07:00", "Kigali Depot", "in transit")

print("History SL-3120")
for scan in mis.get_scan_history("SL-3120"):
    print(" ", scan)

print("Scans on 2026-09-14:", len(mis.get_scans_for_day("2026-09-14")))
print("Scans on 2026-09-15:", len(mis.get_scans_for_day("2026-09-15")))
print(f"Transit time: {mis.get_transit_time('SL-3120'):.2f} hours")

try:
    mis.get_transit_time("SL-5003")
except NotDeliveredError as err:
    print("Rejected:", err)

try:
    mis.record_scan("SL-9999", "2026-09-14 09:00", "Kigali Depot", "received")
except ShipmentNotFoundError as err:
    print("Rejected:", err)

try:
    mis.record_scan("SL-1001", "14/09/2026", "Kigali Depot", "received")
except ValueError as err:
    print("Rejected:", err)

print(mis.get_current_status("SL-5003"), "|", mis.get_current_location("SL-5003"))
print(mis.check_guarantee_compliance())