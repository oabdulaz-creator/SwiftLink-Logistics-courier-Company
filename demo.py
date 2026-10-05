# Import the shipment classes from shipments.py
from shipments import Shipment, TrackedShipment, BulkFreight, FragileParcel, ExpressParcel, write_manifest, save_consignment, load_consignment


# ---------------------------------------------------------
# 1. CREATE SHIPMENT OBJECTS
# ---------------------------------------------------------
shipment1 = Shipment(
    "SL-1001",
    "Amara K.",
    "J. Niyonzima",
    "Kigali",
    4,
    1500
)

shipment2 = TrackedShipment(
    "SL-1002",
    "David M.",
    "Aline U.",
    "Huye",
    6,
    1500,
    400000,
    0.03,
    "received"
)

shipment3 = ExpressParcel(
    "SL-1003",
    "Sarah N.",
    "Jean P.",
    "Musanze",
    2.5,
    1800,
    250000,
    0.02,
    "received",
    12
)

shipment4 = FragileParcel(
    "SL-1004",
    "Peter K.",
    "Grace M.",
    "Kigali",
    8,
    1600,
    900000,
    0.05,
    "received",
    "glass",
    5000
)

shipment5 = BulkFreight(
    "SL-1005",
    "John T.",
    "Eric R.",
    "Kigali",
    320,
    900,
    100000,
    5,
    "received",
    6,
    14
)

shipment6 = BulkFreight(
    "SL-1006",
    "Mary A.",
    "Claudine B.",
    "Kigali",
    500,
    900,
    100000,
    5,
    "received",
    4,
    12
)

# ---------------------------------------------------------
# 2. DISPLAY SHIPMENT DETAILS
# ---------------------------------------------------------
print(shipment1)
print()
print(shipment2)
print()
print(shipment3)
print()
print(shipment4)
print()
print(shipment5)
print()
print(shipment6)

# ---------------------------------------------------------
# 3. CREATE THE MANIFEST LIST
# ---------------------------------------------------------

manifest = [
    shipment1,
    shipment2,
    shipment3,
    shipment4,
    shipment5,
    shipment6
]

# ---------------------------------------------------------
# 4. DEMONSTRATE POLYMORPHIC PRICING
# ---------------------------------------------------------

# Each shipment uses its own calculate_cost() method.
# The same method call works for all shipment types.

total = 0

for shipment in manifest:
    cost = shipment.calculate_cost()
    print(f"{shipment.get_tracking_id()}: {cost} RWF")
    total += cost

print(f"\nTotal manifest value: {total} RWF")

# ---------------------------------------------------------
# 5. TEST INVALID INSURANCE RATE
# ---------------------------------------------------------
print("Original insurance rate:", shipment2.get_insurance_rate())

try:
    shipment2.set_insurance_rate(0.20)
except ValueError as e:
    print("Caught ValueError:", e)

print("Insurance rate after invalid update:", shipment2.get_insurance_rate())

#  ---------------------------------------------------------
# 6. TEST INVALID GUARANTEED HOURS 
# ---------------------------------------------------------

print("Original guaranteed hours:", shipment3.get_guaranteed_hours())

try:
    shipment3.set_guaranteed_hours(36)
except ValueError as e:
    print("Caught ValueError:", e)

print("Guaranteed hours after invalid update:", shipment3.get_guaranteed_hours())

# ---------------------------------------------------------
# 7. TEST INVALID PALLET COUNT
# ---------------------------------------------------------
print("Original pallet count:", shipment6.get_pallet_count())

try:
    shipment6.set_pallet_count(-1)
except ValueError as e:
    print("Caught ValueError:", e)

# Confirm that the invalid update did not change the value.

print("Pallet count after invalid update:", shipment6.get_pallet_count())

#  ---------------------------------------------------------
# 8. DEMONSTRATE STATIC METHOD
# ---------------------------------------------------------
# Test the tracking ID validation method.
print("Valid tracking ID (SL-3120):", Shipment.is_valid_tracking_id("SL-3120"))
print("Invalid tracking ID (3120):", Shipment.is_valid_tracking_id("3120"))
print("Invalid tracking ID (SL-12):", Shipment.is_valid_tracking_id("SL-12"))

#---------------------------------------------------------
# 9. DEMONSTRATE CLASS METHOD
# ---------------------------------------------------------

# Display the number of shipment objects created.

print(
    "Total shipments created:",
    Shipment.get_shipment_count()
)

# =========================================================
# 10. WRITE DAILY MANIFEST
# =========================================================

consignment = manifest

result = write_manifest(consignment)

if result:
    print("Manifest written to daily_manifest.txt")
# =========================================================
# 11. SAVE CONSIGNMENT TO JSON
# =========================================================

# Convert each shipment object to a dictionaryset
# and save the dictionaries to consignment.json.

result = save_consignment(consignment, "consignment.json")

if result:
    print(f"Consignment saved to consignment.json ({len(consignment)} shipments)")

# =========================================================
# 12. LOAD CONSIGNMENT FROM JSON
# =========================================================
loaded_consignment = load_consignment("consignment.json")
print(
    f"Consignment reloaded from consignment.json "
    f"({len(loaded_consignment)} shipments)"
)

# =========================================================
# 14. VERIFY RECONSTRUCTED SHIPMENT TYPES
# =========================================================# %%
for shipment in  loaded_consignment:
    print(type(shipment).__name__, "->", shipment.to_dict()["type"])

# =========================================================
# 15. VERIFY JSON ROUND-TRIP
# =========================================================

original_total = sum(
    shipment.calculate_cost()
    for shipment in consignment
)

loaded_total = sum(
    shipment.calculate_cost()
    for shipment in loaded_consignment
)

print(f"Original manifest total: {original_total:,.2f} RWF")
print(f"Reloaded manifest total: {loaded_total:,.2f} RWF")
print(f"Difference: {original_total - loaded_total:,.2f} RWF")


# Compare each original shipment with its reloaded version

print("\n--- Shipment cost comparison ---")

for original, loaded in zip(consignment, loaded_consignment):

    original_cost = original.calculate_cost()
    loaded_cost = loaded.calculate_cost()

    print(
        f"{original.get_tracking_id()} | "
        f"Original: {original_cost:,.2f} RWF | "
        f"Reloaded: {loaded_cost:,.2f} RWF"
    )

if original_cost != loaded_cost:
     print("MISMATCH: Original and reloaded costs are different.")

else:
     print("MATCH: Original and reloaded costs are identical.")
# %%


# %%



