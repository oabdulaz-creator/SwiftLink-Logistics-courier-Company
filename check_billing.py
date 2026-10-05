from shipments2 import Shipment, TrackedShipment, ExpressParcel, FragileParcel, BulkFreight
from billing import Invoice

s1 = Shipment("SL-1001", "Amara K.", "J. Niyonzima", "Kigali", 4, 1500)
s2 = TrackedShipment("SL-2014", "David M.", "Aline U.", "Musanze", 6, 1500, 400000, 0.03, "received")
s3 = ExpressParcel("SL-3120", "Uwera Trading", "J. Mugisha", "Huye", 2.5, 1800, 250000, 0.02, "received", 12)
s4 = FragileParcel("SL-4077", "Peter K.", "Grace M.", "Rubavu", 8, 1600, 900000, 0.05, "received", "glass", 5000)
s5 = BulkFreight("SL-5003", "John T.", "Eric R.", "Nyagatare", 320, 900, 0, 0, "received", 6, 14)
s6 = BulkFreight("SL-5004", "Mary A.", "Claudine B.", "Kigali", 500, 900, 0, 0, "received", 4, 12)

# Policy lists (the LogisticsMIS will own these later).
remote_districts = ["Nyagatare", "Rusizi", "Kirehe", "Nyamasheke"]
corporate_accounts = ["David M.", "Uwera Trading", "Peter K.", "John T.", "Mary A."]

revenue = 0
for shipment in [s1, s2, s3, s4, s5, s6]:
    invoice = Invoice.for_shipment(shipment, remote_districts, corporate_accounts, "2026-09-14")
    print(invoice.get_tracking_id(), f"{invoice.get_total():,.2f}")
    revenue += invoice.get_total()

print(f"Revenue for the period: {revenue:,.2f}")
print()
print(Invoice.for_shipment(s3, remote_districts, corporate_accounts, "2026-09-14"))

try:
    Invoice("SL-1001", 6000, False, False, "14/09/2026")
except ValueError as err:
    print("Rejected:", err)