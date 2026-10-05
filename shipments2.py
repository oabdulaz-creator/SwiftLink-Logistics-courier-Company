"""
SwiftLink Logistics shipment hierarchy 
"""
import json
import re

VALID_STATUSES = ("received", "in transit", "out for delivery", "delivered")


class Shipment:
    """
    data members: tracking_id, sender_name, recipient_name, destination_city, weight_kg, base_rate_per_kg
    methods: get_tracking_id(), get_sender_name(), get_recipient_name(), get_destination_city(), get_weight_kg(), get_base_rate_per_kg()
    return: String
    """

    company_name = "SwiftLink Logistics"
    shipment_count = 0

    def __init__(self, tracking_id, sender_name, recipient_name,
                 destination_city, weight_kg, base_rate_per_kg):
        """Create a shipment; raise ValueError if any value is invalid."""
        if not self.is_valid_tracking_id(tracking_id):
            raise ValueError("Invalid tracking ID. Format must be SL-1234")
        self.__tracking_id = tracking_id
        self._sender_name = self._clean_text(sender_name, "Sender name")
        self._recipient_name = self._clean_text(recipient_name,
                                                "Recipient name")
        self._destination_city = self._clean_text(destination_city,
                                                  "Destination city")
        self.set_weight_kg(weight_kg)
        self.update_base_rate_per_kg(base_rate_per_kg)
        Shipment.shipment_count += 1

    # validation helpers 
    @staticmethod
    def _clean_text(value, label):
        """Return stripped text, or raise ValueError if empty or not text."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} must be non-empty text")
        return value.strip()

    @staticmethod
    def _require_number(value, label):
        """Return value if it is a real number, else raise ValueError."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{label} must be a number")
        return value

    # getters 
    def get_tracking_id(self):
        """Return the tracking identifier (read-only, never changes)."""
        return self.__tracking_id

    def get_sender_name(self):
        """Return the sender's name."""
        return self._sender_name

    def get_recipient_name(self):
        """Return the recipient's name."""
        return self._recipient_name

    def get_destination_city(self):
        """Return the destination city."""
        return self._destination_city

    def get_weight_kg(self):
        """Return the weight in kilograms."""
        return self._weight_kg

    def get_base_rate_per_kg(self):
        """Return the base rate per kilogram in RWF."""
        return self._base_rate_per_kg

    #setters 
    def set_weight_kg(self, new_weight):
        """Set the weight; must be > 0 and <= 1000."""
        self._require_number(new_weight, "Weight")
        if new_weight <= 0 or new_weight > 1000:
            raise ValueError(
                "Weight must be greater than 0 and not more than 1000")
        self._weight_kg = new_weight

    def set_recipient_name(self, new_name):
        """Change the recipient's name."""
        self._recipient_name = self._clean_text(new_name, "Recipient name")

    def set_destination_city(self, city):
        """Change the destination city."""
        self._destination_city = self._clean_text(city, "Destination city")

    def update_base_rate_per_kg(self, new_rate):
        """Set the base rate; must be greater than zero."""
        self._require_number(new_rate, "Base rate per kg")
        if new_rate <= 0:
            raise ValueError("Base rate per kg must be greater than zero")
        self._base_rate_per_kg = new_rate

    #methods
    def display_details(self):
        """Print the basic shipment details."""
        print(f"Tracking ID: {self.__tracking_id}")
        print(f"Sender Name: {self._sender_name}")
        print(f"Recipient Name: {self._recipient_name}")
        print(f"Destination City: {self._destination_city}")
        print(f"Weight (kg): {self._weight_kg}")

    def calculate_cost(self):
        """Return the transport cost in RWF: weight x base rate."""
        return self._weight_kg * self._base_rate_per_kg

    @classmethod
    def get_shipment_count(cls):
        """Return how many shipment objects have been created."""
        return cls.shipment_count

    @staticmethod
    def is_valid_tracking_id(tracking_id):
        """Return True if tracking_id looks like SL-1234."""
        return isinstance(tracking_id, str) and bool(
            re.fullmatch(r"SL-\d{4}", tracking_id))

    def to_dict(self):
        """Return a JSON-friendly dictionary including the type key."""
        return {
            "type": "Shipment",
            "tracking_id": self.__tracking_id,
            "sender_name": self._sender_name,
            "recipient_name": self._recipient_name,
            "destination_city": self._destination_city,
            "weight_kg": self._weight_kg,
            "base_rate_per_kg": self._base_rate_per_kg,
        }

    def __str__(self):
        """Return a readable multi-line description."""
        return (f"Tracking ID: {self.__tracking_id}\n"
                f"Sender Name: {self._sender_name}\n"
                f"Recipient Name: {self._recipient_name}\n"
                f"Destination City: {self._destination_city}\n"
                f"Weight (kg): {self._weight_kg}\n"
                f"Base Rate per kg: {self._base_rate_per_kg}\n"
                f"Cost: {self.calculate_cost()} RWF")


class TrackedShipment(Shipment):
    """
    data members: declare_value, insurance_rate
    methods: get_declare_value(), get_insurance_rate()
    return: float
    """

    def __init__(self, tracking_id, sender_name, recipient_name,
                 destination_city, weight_kg, base_rate_per_kg,
                 declare_value, insurance_rate, current_status):
        """Create a tracked shipment; raise ValueError on invalid values."""
        super().__init__(tracking_id, sender_name, recipient_name,
                         destination_city, weight_kg, base_rate_per_kg)
        self.set_declare_value(declare_value)
        self.set_insurance_rate(insurance_rate)
        self.set_current_status(current_status)

    def get_declare_value(self):
        """Return the declared value in RWF."""
        return self._declare_value

    def get_insurance_rate(self):
        """Return the insurance rate (a fraction such as 0.02)."""
        return self._insurance_rate

    def get_current_status(self):
        """Return the current status text."""
        return self._current_status

    def set_declare_value(self, new_value):
        """Set the declared value; must not be negative."""
        self._require_number(new_value, "Declare value")
        if new_value < 0:
            raise ValueError("Declare value cannot be negative")
        self._declare_value = new_value

    def set_insurance_rate(self, new_rate):
        """Set the insurance rate; must be between 0 and 0.05."""
        self._require_number(new_rate, "Insurance rate")
        if new_rate < 0 or new_rate > 0.05:
            raise ValueError("Insurance rate must be between 0% and 5%")
        self._insurance_rate = new_rate

    def set_current_status(self, new_status):
        """Set the status; stored in lower case, must be a valid status."""
        if (not isinstance(new_status, str)
                or new_status.strip().lower() not in VALID_STATUSES):
            raise ValueError("Invalid status. One of received, in transit, "
                             "out for delivery, delivered")
        self._current_status = new_status.strip().lower()

    def calculate_cost(self):
        """Return weight cost plus insurance (declared value x rate)."""
        return super().calculate_cost() + (self._declare_value
                                           * self._insurance_rate)

    def to_dict(self):
        """Extend the parent dictionary with tracked-shipment fields."""
        data = super().to_dict()
        data["type"] = "TrackedShipment"
        data["declared_value"] = self._declare_value
        data["insurance_rate"] = self._insurance_rate
        data["current_status"] = self._current_status
        return data

    def __str__(self):
        """Return the parent description plus tracked-shipment fields."""
        return (f"{super().__str__()}\n"
                f"Declare Value: {self._declare_value}\n"
                f"Insurance Rate: {self._insurance_rate}\n"
                f"Current Status: {self._current_status}")


class ExpressParcel(TrackedShipment):
    """
    data members: guaranteed_hours
    methods: get_guaranteed_hours()
    return: int
    """

    PRIORITY_FEES = {6: 20000, 12: 12000, 24: 6000, 48: 3000}

    def __init__(self, tracking_id, sender_name, recipient_name,
                 destination_city, weight_kg, base_rate_per_kg,
                 declare_value, insurance_rate, current_status,
                 guaranteed_hours):
        """Create an express parcel; guaranteed_hours is 6, 12, 24 or 48."""
        super().__init__(tracking_id, sender_name, recipient_name,
                         destination_city, weight_kg, base_rate_per_kg,
                         declare_value, insurance_rate, current_status)
        self.set_guaranteed_hours(guaranteed_hours)

    def get_guaranteed_hours(self):
        """Return the guaranteed delivery time in hours."""
        return self._guaranteed_hours

    def set_guaranteed_hours(self, new_hours):
        """Set the guarantee; must be exactly 6, 12, 24 or 48."""
        if new_hours not in self.PRIORITY_FEES:
            raise ValueError("Invalid guaranteed hours. Exactly 6, 12, 24 "
                             "or 48")
        self._guaranteed_hours = new_hours

    def calculate_cost(self):
        """Return tracked-shipment cost plus the priority fee."""
        return super().calculate_cost() + self.PRIORITY_FEES[
            self._guaranteed_hours]

    def to_dict(self):
        """Extend the parent dictionary with the guarantee."""
        data = super().to_dict()
        data["type"] = "ExpressParcel"
        data["guaranteed_hours"] = self._guaranteed_hours
        return data

    def __str__(self):
        """Return the parent description plus the guarantee."""
        return f"{super().__str__()}\nGuaranteed Hours: {self._guaranteed_hours}"


class FragileParcel(TrackedShipment):
    """
    data members: handling_class, packaging_fee
    methods: get_handling_class(), get_packaging_fee(), set_handling_class(), set_packaging_fee()
    return: float
    """

    HANDLING_CLASSES = ("glass", "electronics", "artwork")
    FRAGILE_SURCHARGE = 0.15

    def __init__(self, tracking_id, sender_name, recipient_name,
                 destination_city, weight_kg, base_rate_per_kg,
                 declare_value, insurance_rate, current_status,
                 handling_class, packaging_fee):
        """Create a fragile parcel; raise ValueError on invalid values."""
        super().__init__(tracking_id, sender_name, recipient_name,
                         destination_city, weight_kg, base_rate_per_kg,
                         declare_value, insurance_rate, current_status)
        self.set_handling_class(handling_class)
        self.set_packaging_fee(packaging_fee)

    def get_handling_class(self):
        """Return the handling class."""
        return self._handling_class

    def get_packaging_fee(self):
        """Return the packaging fee in RWF."""
        return self._packaging_fee

    def set_handling_class(self, new_class):
        """Set the handling class: glass, electronics or artwork."""
        if new_class not in self.HANDLING_CLASSES:
            raise ValueError("Invalid handling class. One of glass, "
                             "electronics or artwork")
        self._handling_class = new_class

    def set_packaging_fee(self, new_fee):
        """Set the packaging fee; must not be negative."""
        self._require_number(new_fee, "Packaging fee")
        if new_fee < 0:
            raise ValueError("Packaging fee must not be negative")
        self._packaging_fee = new_fee

    def calculate_cost(self):
        """Return tracked cost + packaging fee + 15% fragile surcharge."""
        surcharge = (self._weight_kg
                     * self._base_rate_per_kg * self.FRAGILE_SURCHARGE)
        return round(super().calculate_cost() + self._packaging_fee
                     + surcharge, 2)

    def to_dict(self):
        """Extend the parent dictionary with fragile-parcel fields."""
        data = super().to_dict()
        data["type"] = "FragileParcel"
        data["handling_class"] = self._handling_class
        data["packaging_fee"] = self._packaging_fee
        return data

    def __str__(self):
        """Return the parent description plus fragile-parcel fields."""
        return (f"{super().__str__()}\n"
                f"Handling Class: {self._handling_class}\n"
                f"Packaging Fee: {self._packaging_fee}")


class BulkFreight(Shipment):
    """
    data members: pallet_count, volume_m3
    methods: get_pallet_count(), get_volume_m3(), set_pallet_count(), set_volume_m3()
    return: float
    """
    VOLUMETRIC_RATE_PER_M3 = 25000
    PALLET_HANDLING_FEE = 2000

    def __init__(self, tracking_id, sender_name, recipient_name,
                 destination_city, weight_kg, base_rate_per_kg,
                 declare_value, insurance_rate, current_status,
                 pallet_count, volume_m3):
        """Create bulk freight; raise ValueError on invalid values."""
        super().__init__(tracking_id, sender_name, recipient_name,
                         destination_city, weight_kg, base_rate_per_kg)
        self.set_pallet_count(pallet_count)
        self.set_volume_m3(volume_m3)

    def get_pallet_count(self):
        """Return the number of pallets."""
        return self._pallet_count

    def get_volume_m3(self):
        """Return the volume in cubic metres."""
        return self._volume_m3

    def set_pallet_count(self, new_count):
        """Set the pallet count; must be between 1 and 20 inclusive."""
        self._require_number(new_count, "Pallet count")
        if new_count < 1 or new_count > 20:
            raise ValueError("Pallet count must be between 1 and 20 "
                             "inclusive")
        self._pallet_count = new_count

    def set_volume_m3(self, new_volume):
        """Set the volume; must be greater than zero."""
        self._require_number(new_volume, "Volume")
        if new_volume <= 0:
            raise ValueError("Volume must be greater than zero")
        self._volume_m3 = new_volume

    def calculate_cost(self):
        """Return max(weight cost, volume cost) plus pallet handling."""
        weight_cost = super().calculate_cost()
        volume_cost = self._volume_m3 * self.VOLUMETRIC_RATE_PER_M3
        pallet_cost = self._pallet_count * self.PALLET_HANDLING_FEE
        return max(weight_cost, volume_cost) + pallet_cost

    def to_dict(self):
        """Extend the parent dictionary with bulk-freight fields."""
        data = super().to_dict()
        data["type"] = "BulkFreight"
        data["pallet_count"] = self._pallet_count
        data["volume_m3"] = self._volume_m3
        return data

    def __str__(self):
        """Return the parent description plus bulk-freight fields."""
        return (f"{super().__str__()}\n"
                f"Pallet Count: {self._pallet_count}\n"
                f"Volume (m3): {self._volume_m3} m\u00b3")


def shipment_from_dict(data):
    kind = data.get("type")
    base = [data["tracking_id"], data["sender_name"],
            data["recipient_name"], data["destination_city"],
            data["weight_kg"], data["base_rate_per_kg"]]
    if kind == "Shipment":
        return Shipment(*base)
    if kind == "BulkFreight":
        return BulkFreight(*base, 0, 0, "received",
                           data["pallet_count"], data["volume_m3"])
    if kind in ("TrackedShipment", "ExpressParcel", "FragileParcel"):
        tracked = base + [data["declared_value"], data["insurance_rate"],
                          data["current_status"]]
        if kind == "TrackedShipment":
            return TrackedShipment(*tracked)
        if kind == "ExpressParcel":
            return ExpressParcel(*tracked, data["guaranteed_hours"])
        return FragileParcel(*tracked, data["handling_class"],
                             data["packaging_fee"])
    raise ValueError(f"Unknown shipment type: {kind!r}")
def write_manifest(shipments, filename="daily_manifest.txt"):
    """
    Writes the daily manifest for a list of shipments to a text file.

    Parameters:
        shipments: list of Shipment objects
        filename: name of the manifest file

    Returns:
        True if the manifest was written successfully,
        False otherwise.
    """
    try:
        with open(filename, "w") as file:
            file.write("=== SwiftLink Logistics: daily manifest ===\n")

            for shipment in shipments:
                file.write(
                    f"{shipment.get_tracking_id()} "
                    f"{shipment.get_destination_city()} "
                    f"{type(shipment).__name__} "
                    f"{shipment.calculate_cost():,.2f}\n"
                )

            total = sum(shipment.calculate_cost() for shipment in shipments)

            file.write("-" * 53 + "\n")
            file.write(f"Manifest total {total:,.2f}\n")

        return True

    except (OSError, PermissionError) as error:
        print(f"Could not write manifest: {error}")
        return False
def save_consignment(shipments, filename):
    """
    Saves a list of shipment objects to a JSON file.

    Parameters:
        shipments: list of Shipment objects
        filename: name of the JSON file

    Returns:
        True if the consignment was saved successfully,
        False otherwise.
    """
    try:
        data = [shipment.to_dict() for shipment in shipments]

        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

        return True

    except (OSError, TypeError) as error:
        print(f"Could not save consignment: {error}")
        return False
def load_consignment(filename):
    """
    Loads shipment objects from a JSON file.

    Parameters:
        filename: name of the JSON file

    Returns:
        A list of reconstructed shipment objects if successful,
        or an empty list if the file cannot be loaded.
    """
    try:
        with open(filename, "r") as file:
            data_list = json.load(file)

        loaded_consignment = []

        for data in data_list:
            shipment_type = data["type"]

            if shipment_type == "Shipment":
                shipment = Shipment(
                    data["tracking_id"],
                    data["sender_name"],
                    data["recipient_name"],
                    data["destination_city"],
                    data["weight_kg"],
                    data["base_rate_per_kg"]
                )

            elif shipment_type == "TrackedShipment":
                shipment = TrackedShipment(
                    data["tracking_id"],
                    data["sender_name"],
                    data["recipient_name"],
                    data["destination_city"],
                    data["weight_kg"],
                    data["base_rate_per_kg"],
                    data["declared_value"],
                    data["insurance_rate"],
                    data["current_status"]
                )

            elif shipment_type == "ExpressParcel":
                shipment = ExpressParcel(
                    data["tracking_id"],
                    data["sender_name"],
                    data["recipient_name"],
                    data["destination_city"],
                    data["weight_kg"],
                    data["base_rate_per_kg"],
                    data["declared_value"],
                    data["insurance_rate"],
                    data["current_status"],
                    data["guaranteed_hours"]
                )

            elif shipment_type == "FragileParcel":
                shipment = FragileParcel(
                    data["tracking_id"],
                    data["sender_name"],
                    data["recipient_name"],
                    data["destination_city"],
                    data["weight_kg"],
                    data["base_rate_per_kg"],
                    data["declared_value"],
                    data["insurance_rate"],
                    data["current_status"],
                    data["handling_class"],
                    data["packaging_fee"]
                )

            elif shipment_type == "BulkFreight":
                shipment = BulkFreight(
                    data["tracking_id"],
                    data["sender_name"],
                    data["recipient_name"],
                    data["destination_city"],
                    data["weight_kg"],
                    data["base_rate_per_kg"],
                    0,
                    0,
                    "received",
                    data["pallet_count"],
                    data["volume_m3"]
                )

            else:
                raise ValueError(f"Unknown shipment type: {shipment_type}")

            loaded_consignment.append(shipment)

        return loaded_consignment

    except FileNotFoundError:
        print(f"File not found: {filename}")
        return []

    except (json.JSONDecodeError, OSError, KeyError, ValueError, TypeError) as error:
        print(f"Could not load consignment: {error}")
        return []

    
    