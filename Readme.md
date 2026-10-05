# SWIFTLINK LOGISTICS
### INTRODUCTION
An object-oriented courier management system for SwiftLink Logistics in Kigali. The application demonstrates inheritance and polymorphism across different courier services, implements service-specific charge calculations, handles invalid data through exception handling, generates daily manifests, and provides JSON-based persistence for shipment records.

### How to run the code
- Put shipments.py and demo.py in the same directory
- Run Python demo.py

### Generated Files
- output.txt: console output from the run
- daily_manifest.txt: daily shipment report from write_manifest()
- consignment.json: all shipments serialized by save_consignment()()

### Class Diagram
![alt text](<shipment_class_diagram_fixed (1).png>)

### Domain Model
The system is organized into a hierarchy of shipment classes, where common attributes and behaviours are inherited by more specialized shipment types.

- Shipment(Base class)
This is the parent class for the shipment types. It stores the basic information required for every shipment, such as the tracking ID, sender and recipient details, destination, weight, and base rate.

- TrackedShipment (Inherits from Shipment)
This class builds on Shipment by adding shipment status and insurance information. It includes the current status, declared value, and insurance rate.

- ExpressParcel(Inherits from TrackedShipment)
This class is designed for express deliveries. It adds a guaranteed delivery time and applies an additional priority when calculating the shipping cost.

- FragileParcel (Inherits from TrackedShipment)
This class is used for items that require careful handling. It adds a handling classification and a packaging fee to account for specialized packaging requirements.

- BulkFreight (Inherits from Shipment)
This class is intended for large or heavy cargo.It records the shipment volume and number of pallets and uses a different pricing method from the standard per-kilogram calculation.

### Design Decisions
# Encapsulation
The tracking_id attribute is kept private because it is assigned when a shipment is created and should remain unchanged throughout the shipment's lifecycle. This helps prevent accidental changes that could lead to incorrect tracking or duplicate IDs.

 -Python internally name-mangles the attribute as `_Shipment__tracking_id`. Therefore, assigning `parcel.tracking_id = "SL-9999"` from outside the class does not modify the original private attribute; instead, it creates a separate instance attribute. Python uses name mangling rather than true access control for double-underscore attributes. Although the original attribute can technically be accessed using its mangled name, `parcel._Shipment__tracking_id` where parcel is the object reference, doing so is generally discouraged because it bypasses the class's intended interface.



# Mutability
Different shipment attributes have different levels of mutability:
- Recipient_name and destination_city have setters because delivery information may need to be corrected or updated while a shipment is in transit.

- base_rate_per_kg can be updated through update_base_rate_per_kg(), allowing administrative changes such as adjustments to fuel or operating costs.

- __tracking_id does not have a setter because it should remain unchanged after the shipment is created.

# Pricing: Extending vs. Replacing
The shipment classes use two approaches when calculating costs:

- Extending the base calculation: Trackedshipment, ExpressParcel and FragileParcel first call super().calculate_cost() and then add their specific charges, such as insurance, priority fee delivery, packaging, or handling fees.

- Replacing or overridding the base calculation: BulkFreight uses a different pricing model because large cargo requires volume and pallet considerations. Instead of using only the standard weight-based formula, it calculates both the weight-based and volumetric cost and uses the higher value. A pallet handling charge is then added:

max(weight_kg × base_rate_per_kg, volume_m3 × VOLUMETRIC_RATE_PER_M3) + (pallet_count × PALLET_HANDLING_FEE)

### Class-Level Features
company_name, shipment_count, PRIORITY_FEES, VOLUMETRIC_RATE_PER_M3 and PALLET_HANDLING_FEE are class variables because they are shared constants, lookup tables or system wide counters rather than per instance data

### Validation and Exception Handling
Constructors and property setters validate input. A violation raises ValueError with a descriptive message and leaves the object unchanged.

### Shipment Validation

The `Shipment` class validates the following attributes:

- **Tracking ID:** Must follow the `SL-1234` format.
- **Weight:** Must be greater than 0 and no more than 1000 kg.
- **Base rate:** Must be greater than zero.

### TrackedShipment Validation

- **Declared value:** Must be zero or greater.
- **Insurance rate:** Must be between 0% and 5%.
- **Current status:** Must be one of the supported shipment statuses.

### ExpressParcel Validation

- **Guaranteed hours:** Must be 6, 12, 24, or 48 hours.

### FragileParcel Validation

- **Handling class:** Must be `glass`, `electronics`, or `artwork`.
- **Packaging fee:** Must not be negative.

### BulkFreight Validation

- **Pallet count:** Must be between 1 and 20.
- **Volume:** Must be greater than zero.

### File I/O and JSON Persistence
Manifest `write_manifest()`

- Uses with open(...) so the file always closes, even on error
- Each line shows tracking ID, destination city, service class, and formatted price.
- Catches OSError and PermissionError and returns False rather than raising.

### Serialization and Round-Trip
- Derived values excluded: Computed fees such as priority_fee are not saved, since they are recalculated from guarenteed_hours via PRIORITY_FEES. Storing them would duplicate data and risk inconsistency on reload.

- Type tagging: every to_dict() includes a "type" key with the class name(e.g. "ExpressParcel").

- Loading: load_consignment() reads the JSON array, uses each "type" to rebuild the right class, and returns a list of shipments.

- Load errors: If the file is missing (FileNotFoundError) or malformed (json.JSONDecodeError), it prints a warning and returns [] so the caller can carry on.