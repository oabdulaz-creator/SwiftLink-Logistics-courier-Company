from shipments2 import Shipment, TrackedShipment, ExpressParcel, FragileParcel, BulkFreight
from lmis import LogisticsMIS

s1 = Shipment("SL-1001", "Amara K.", "J. Niyonzima", "Kigali", 4, 1500)
s2 = TrackedShipment("SL-2014", "David M.", "Aline U.", "Musanze", 6, 1500, 400000, 0.03, "received")
s3 = ExpressParcel("SL-3120", "Uwera Trading", "J. Mugisha", "Huye", 2.5, 1800, 250000, 0.02, "received", 12)
s4 = FragileParcel("SL-4077", "Peter K.", "Grace M.", "Rubavu", 8, 1600, 900000, 0.05, "received", "glass", 5000)
s5 = BulkFreight("SL-5003", "John T.", "Eric R.", "Nyagatare", 320, 900, 0, 0, "received", 6, 14)
s6 = BulkFreight("SL-5004", "Mary A.", "Claudine B.", "Kigali", 500, 900, 0, 0, "received", 4, 12)
# Two extra express parcels: one will be late, one still in transit.
s7 = ExpressParcel("SL-3121", "Kigali Foods", "A. Habimana", "Rubavu", 1, 1800, 100000, 0.02, "received", 24)
s8 = ExpressParcel("SL-3122", "Kigali Foods", "B. Uwase", "Musanze", 1, 1800, 100000, 0.02, "received", 6)

mis = LogisticsMIS(corporate_accounts=["David M.", "Uwera Trading", "Peter K.", "John T.", "Mary A.", "Kigali Foods"])
for shipment in (s1, s2, s3, s4, s5, s6, s7, s8):
    mis.add_shipment(shipment)

mis.record_scan("SL-1001", "2026-09-14 09:00", "Kigali Depot", "received")
mis.record_scan("SL-3120", "2026-09-14 08:30", "Kigali Depot", "received")
mis.record_scan("SL-3120", "2026-09-14 12:05", "Muhanga Hub", "in transit")
mis.record_scan("SL-3120", "2026-09-14 16:40", "Huye Depot", "out for delivery")
mis.record_scan("SL-3120", "2026-09-14 18:15", "Huye", "delivered")
mis.record_scan("SL-5003", "2026-09-15 07:00", "Muhanga Hub", "in transit")
mis.record_scan("SL-3121", "2026-09-14 08:00", "Kigali Depot", "received")
mis.record_scan("SL-3121", "2026-09-15 14:00", "Rubavu", "delivered")
mis.record_scan("SL-3122", "2026-09-14 10:00", "Kigali Depot", "in transit")

mis.raise_all_invoices("2026-09-14")

print(mis.consignment_register())
print()
print(mis.scan_summary())
print()
print(mis.revenue_summary("2026-09"))
print()
print(mis.guarantee_compliance_report())
print()

# One invoice moves to October, so the monthly totals must split.
mis.raise_invoice("SL-1001", "2026-10-05")
print(f"{mis.get_revenue_totals('2026-09')['total']:,.2f}  "
      f"{mis.get_revenue_totals('2026-10')['total']:,.2f}  "
      f"{mis.get_revenue_totals()['total']:,.2f}")

print(mis.revenue_summary("2026-11"))

try:
    mis.revenue_summary("09/2026")
except ValueError as err:
    print("Rejected:", err)