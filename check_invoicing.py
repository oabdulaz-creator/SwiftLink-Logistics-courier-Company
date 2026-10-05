from shipments2 import Shipment, TrackedShipment, ExpressParcel, FragileParcel, BulkFreight
from lmis import (LogisticsMIS, ShipmentNotFoundError, InvoiceNotFoundError)

s1 = Shipment("SL-1001", "Amara K.", "J. Niyonzima", "Kigali", 4, 1500)
s2 = TrackedShipment("SL-2014", "David M.", "Aline U.", "Musanze", 6, 1500, 400000, 0.03, "received")
s3 = ExpressParcel("SL-3120", "Uwera Trading", "J. Mugisha", "Huye", 2.5, 1800, 250000, 0.02, "received", 12)
s4 = FragileParcel("SL-4077", "Peter K.", "Grace M.", "Rubavu", 8, 1600, 900000, 0.05, "received", "glass", 5000)
s5 = BulkFreight("SL-5003", "John T.", "Eric R.", "Nyagatare", 320, 900, 0, 0, "received", 6, 14)
s6 = BulkFreight("SL-5004", "Mary A.", "Claudine B.", "Kigali", 500, 900, 0, 0, "received", 4, 12)

mis = LogisticsMIS(corporate_accounts=["David M.", "Uwera Trading", "Peter K.", "John T.", "Mary A."])
for shipment in (s1, s2, s3, s4, s5, s6):
    mis.add_shipment(shipment)

# Asking for an invoice before one is raised must be refused.
try:
    mis.get_invoice("SL-3120")
except InvoiceNotFoundError as err:
    print("Rejected:", err)

invoices = mis.raise_all_invoices("2026-09-14")
print("Invoices raised:", len(invoices))
for invoice in mis.get_all_invoices():
    print(invoice.get_tracking_id(), f"{invoice.get_total():,.2f}")

revenue = sum(invoice.get_total() for invoice in mis.get_all_invoices())
print(f"Revenue: {revenue:,.2f}")

print(mis.get_invoice("SL-5003"))

try:
    mis.raise_invoice("SL-9999", "2026-09-14")
except ShipmentNotFoundError as err:
    print("Rejected:", err)

try:
    mis.raise_invoice("SL-1001", "14/09/2026")
except ValueError as err:
    print("Rejected:", err)

# Re-billing after an update replaces the old invoice.
mis.update_shipment("SL-1001", "weight_kg", 10)
print(f"{mis.get_invoice('SL-1001').get_total():,.2f} (old invoice)")
print(f"{mis.raise_invoice('SL-1001', '2026-09-14').get_total():,.2f} (re-billed)")

mis.add_remote_district("Rwamagana")
mis.add_remote_district("rusizi")   # already there, so ignored
print(mis.get_remote_districts())