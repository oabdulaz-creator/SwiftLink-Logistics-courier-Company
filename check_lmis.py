from shipments2 import Shipment, TrackedShipment, ExpressParcel, FragileParcel, BulkFreight
from lmis import LogisticsMIS, DuplicateTrackingIDError, ShipmentNotFoundError

s1 = Shipment("SL-1001", "Amara K.", "J. Niyonzima", "Kigali", 4, 1500)
s2 = TrackedShipment("SL-2014", "David M.", "Aline U.", "Musanze", 6, 1500, 400000, 0.03, "received")
s3 = ExpressParcel("SL-3120", "Uwera Trading", "J. Mugisha", "Huye", 2.5, 1800, 250000, 0.02, "received", 12)
s4 = FragileParcel("SL-4077", "Peter K.", "Grace M.", "Rubavu", 8, 1600, 900000, 0.05, "received", "glass", 5000)
s5 = BulkFreight("SL-5003", "John T.", "Eric R.", "Nyagatare", 320, 900, 0, 0, "received", 6, 14)
s6 = BulkFreight("SL-5004", "Mary A.", "Claudine B.", "Kigali", 500, 900, 0, 0, "received", 4, 12)

mis = LogisticsMIS(corporate_accounts=["David M.", "Uwera Trading", "Peter K.", "John T.", "Mary A."])

for shipment in [s1, s2, s3, s4, s5, s6]:
    mis.add_shipment(shipment)
print("Shipments registered:", mis.count_shipments())

try:
    mis.add_shipment(s3)
except DuplicateTrackingIDError as err:
    print("Rejected:", err)

try:
    mis.get_shipment("SL-9999")
except ShipmentNotFoundError as err:
    print("Rejected:", err)

print(mis.get_shipment("SL-3120").get_destination_city())
mis.update_shipment("SL-3120", "destination_city", "Rubavu")
print(mis.get_shipment("SL-3120").get_destination_city())

for args in [("SL-3120", "guaranteed_hours", 36),
             ("SL-1001", "guaranteed_hours", 12),
             ("SL-1001", "colour", "red"),
             ("SL-1001", "weight_kg", "abc")]:
    try:
        mis.update_shipment(*args)
    except ValueError as err:
        print("Rejected:", err)

mis.remove_shipment("SL-5004")
print("Shipments registered:", mis.count_shipments())

try:
    mis.remove_shipment("SL-5004")
except ShipmentNotFoundError as err:
    print("Rejected:", err)

print([s.get_tracking_id() for s in mis.get_all_shipments()])