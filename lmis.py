"""
lmis.py - The Logistics Management Information System for SwiftLink Logistics.

This module will contain the LogisticsMIS class, which owns all the shipment,
scan and invoice records. It also defines the custom exceptions the system
raises, so that code using the system can react to each kind of failure
separately instead of catching every error at once.
"""
import json
import os
from datetime import datetime

from shipments2 import Shipment, ExpressParcel
from tracking import ScanEvent
from billing import Invoice

class DuplicateTrackingIDError(Exception):
    """Raised when a tracking id being added already exists in the system.
    """


class ShipmentNotFoundError(Exception):
    """Raised when a tracking id is requested that is not in the system.

    This is raised instead of quietly returning None, so a missing shipment
    can never be mistaken for a real result.
    """
class NotDeliveredError(Exception):
    """Raised when a transit time is requested for a shipment that has not
    been delivered yet (or has no scans at all).

    This is raised instead of returning a number, so a misleading figure can
    never be mistaken for a real transit time.
    """

class InvoiceNotFoundError(Exception):
    """Raised when an invoice is requested for a shipment that exists but
    has not been invoiced yet.

    This is different from ShipmentNotFoundError: the shipment is real, it
    just has not been billed, so the clerk needs to raise an invoice first.
    """
class DataFileError(Exception):
    """Raised when a data file cannot be read, written or understood.

    The message says what went wrong AND what the user can do about it. The
    system that was already in memory is never changed by a failed load.
    """

class LogisticsMIS:
    """The system that owns every shipment, scan event and invoice.

    Shipments and invoices are kept in dictionaries keyed by tracking id, so
    finding one is instant. Scan events are kept in a list, because one
    shipment has many scans.
    """

    # Default remote districts (policy). Pass your own list to the
    # constructor to change it, without editing any class.
    DEFAULT_REMOTE_DISTRICTS = ["Nyagatare", "Rusizi", "Kirehe",
                                "Nyamasheke"]

    # Maps the field name a clerk types to the setter method that edits it.
    # Going through the setters means every Assignment 1 validation rule
    # still applies when a shipment is updated.
    EDITABLE_FIELDS = {
        "recipient_name": "set_recipient_name",
        "destination_city": "set_destination_city",
        "weight_kg": "set_weight_kg",
        "base_rate_per_kg": "update_base_rate_per_kg",
        "declare_value": "set_declare_value",
        "insurance_rate": "set_insurance_rate",
        "current_status": "set_current_status",
        "guaranteed_hours": "set_guaranteed_hours",
        "handling_class": "set_handling_class",
        "packaging_fee": "set_packaging_fee",
        "pallet_count": "set_pallet_count",
        "volume_m3": "set_volume_m3",
    }

    def __init__(self, remote_districts=None, corporate_accounts=None):
        """Create an empty system.

        Args:
            remote_districts: list of remote district names. If None, the
                default list (Nyagatare, Rusizi, Kirehe, Nyamasheke) is used.
            corporate_accounts: list of sender names that are registered
                corporate accounts. If None, there are none.
        """
        self._shipments = {}   # tracking id -> shipment object
        self._scans = []       # list of ScanEvent objects
        self._invoices = {}    # tracking id -> Invoice object

        if remote_districts is None:
            remote_districts = self.DEFAULT_REMOTE_DISTRICTS
        if corporate_accounts is None:
            corporate_accounts = []
        # list(...) makes our own copy, so changing the list the caller
        # passed in later cannot silently change the system's policy.
        self._remote_districts = list(remote_districts)
        self._corporate_accounts = list(corporate_accounts)

    # ------------------------------------------------------------------
    # 4.1 Consignment management
    # ------------------------------------------------------------------
    def add_shipment(self, shipment):
        """Add a shipment to the system.

        Raises:
            ValueError: if the object given is not a shipment.
            DuplicateTrackingIDError: if its tracking id is already used.
        """
        if not isinstance(shipment, Shipment):
            raise ValueError("Only Shipment objects can be added")
        tracking_id = shipment.get_tracking_id()
        if tracking_id in self._shipments:
            raise DuplicateTrackingIDError(
                f"{tracking_id} is already registered")
        self._shipments[tracking_id] = shipment

    def get_shipment(self, tracking_id):
        """Return the shipment with this tracking id.

        Raises:
            ShipmentNotFoundError: if no shipment has this id.
        """
        if tracking_id not in self._shipments:
            raise ShipmentNotFoundError(
                f"no shipment with tracking id {tracking_id}")
        return self._shipments[tracking_id]

    def get_all_shipments(self):
        """Return a list of every shipment, sorted by tracking id."""
        return [self._shipments[key] for key in sorted(self._shipments)]

    def count_shipments(self):
        """Return how many shipments are in the system."""
        return len(self._shipments)

    def update_shipment(self, tracking_id, field, new_value):
        """Change one editable detail of a shipment.

        The change goes through the shipment's own setter, so the validation
        rules from Assignment 1 still apply.

        Args:
            tracking_id: id of the shipment to change.
            field: one of the names in EDITABLE_FIELDS, e.g. "weight_kg".
            new_value: the new value.

        Raises:
            ShipmentNotFoundError: if no shipment has this id.
            ValueError: if the field cannot be edited, does not apply to
                this kind of shipment, or the new value is invalid.
        """
        shipment = self.get_shipment(tracking_id)

        if field not in self.EDITABLE_FIELDS:
            allowed = ", ".join(sorted(self.EDITABLE_FIELDS))
            raise ValueError(
                f"'{field}' cannot be edited, choose one of: {allowed}")

        # getattr(object, name, default) looks up a method by its name. It
        # gives None if this class of shipment does not have that setter.
        setter = getattr(shipment, self.EDITABLE_FIELDS[field], None)
        if setter is None:
            raise ValueError(
                f"{tracking_id} is a {type(shipment).__name__}, "
                f"which has no '{field}' to change")
        setter(new_value)

    def remove_shipment(self, tracking_id):
        """Remove a shipment together with its scan events and its invoice.

        Design decision: removal is for consignments entered by mistake, and
        scans and invoices refer to a shipment only by its id. Leaving them
        behind would create records pointing at a shipment that no longer
        exists, which would break the reports and waybills. So they are
        removed with it.

        Raises:
            ShipmentNotFoundError: if no shipment has this id.
        """
        self.get_shipment(tracking_id)   # raises if the id is unknown
        del self._shipments[tracking_id]
        self._scans = [scan for scan in self._scans
                       if scan.get_tracking_id() != tracking_id]
        self._invoices.pop(tracking_id, None)

    def record_scan(self, tracking_id, timestamp, location, status):
        """Record one scan of a shipment and return the new ScanEvent.

        Raises:
            ShipmentNotFoundError: if the tracking id is not in the system.
            ValueError: if the timestamp or the status is invalid.
        """
        shipment = self.get_shipment(tracking_id)   # refuses unknown ids
        scan = ScanEvent(tracking_id, timestamp, location, status)
        self._scans.append(scan)

        # Keep a tracked shipment's own status in step with its latest scan.
        # Plain Shipment and BulkFreight have no status of their own, so
        # hasattr skips them.
        latest = self.get_scan_history(tracking_id)[-1]
        if hasattr(shipment, "set_current_status"):
            shipment.set_current_status(latest.get_status())
        return scan

    def get_scan_history(self, tracking_id):
        """Return all scans of one shipment, oldest first.

        Scans are sorted by their real date and time, so the order is right
        even if the clerk recorded them out of order.

        Raises:
            ShipmentNotFoundError: if the tracking id is not in the system.
        """
        self.get_shipment(tracking_id)
        scans = [scan for scan in self._scans
                 if scan.get_tracking_id() == tracking_id]
        # key=ScanEvent.get_datetime tells sorted() to compare scans by the
        # datetime that method returns.
        return sorted(scans, key=ScanEvent.get_datetime)

    def get_scans_for_day(self, day):
        """Return every scan across the network on one day, oldest first.

        Args:
            day: the date as text "YYYY-MM-DD".

        Raises:
            ValueError: if the day is not a valid date.
        """
        try:
            wanted = datetime.strptime(day, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            raise ValueError(
                f"'{day}' is not a valid date, expected YYYY-MM-DD")
        day_scans = [scan for scan in self._scans
                     if scan.get_datetime().date() == wanted]
        return sorted(day_scans, key=ScanEvent.get_datetime)

    def get_current_status(self, tracking_id):
        """Return a shipment's status, taken from its latest scan.

        If it has no scans yet, use its own status if it has one, otherwise
        "received".

        Raises:
            ShipmentNotFoundError: if the tracking id is not in the system.
        """
        history = self.get_scan_history(tracking_id)
        if history:
            return history[-1].get_status()
        shipment = self.get_shipment(tracking_id)
        if hasattr(shipment, "get_current_status"):
            return shipment.get_current_status()
        return "received"

    def get_current_location(self, tracking_id):
        """Return where a shipment was last scanned.

        Raises:
            ShipmentNotFoundError: if the tracking id is not in the system.
        """
        history = self.get_scan_history(tracking_id)
        if history:
            return history[-1].get_location()
        return "not scanned yet"

    def get_transit_time(self, tracking_id):
        """Return the transit time in hours: first scan to delivery scan.

        Raises:
            ShipmentNotFoundError: if the tracking id is not in the system.
            NotDeliveredError: if the shipment has no scans or no delivery
                scan yet, so no honest number can be given.
        """
        history = self.get_scan_history(tracking_id)
        if not history:
            raise NotDeliveredError(f"{tracking_id} has no scans yet")

        delivery_scan = None
        for scan in history:
            if scan.get_status() == "delivered":
                delivery_scan = scan
                break
        if delivery_scan is None:
            raise NotDeliveredError(
                f"{tracking_id} has not been delivered yet, so no transit "
                f"time can be calculated")

        elapsed = delivery_scan.get_datetime() - history[0].get_datetime()
        return elapsed.total_seconds() / 3600

    def check_guarantee_compliance(self):
        """Check every ExpressParcel against its guaranteed delivery time.

        Returns:
            A list of dictionaries, one per express parcel, with keys
            "tracking_id", "guaranteed_hours", "actual_hours" and "met".
            For an undelivered parcel, actual_hours and met are None.
        """
        results = []
        for shipment in self.get_all_shipments():
            if not isinstance(shipment, ExpressParcel):
                continue
            tracking_id = shipment.get_tracking_id()
            guaranteed = shipment.get_guaranteed_hours()
            try:
                actual = self.get_transit_time(tracking_id)
            except NotDeliveredError:
                actual = None
            met = None if actual is None else actual <= guaranteed
            results.append({"tracking_id": tracking_id,
                            "guaranteed_hours": guaranteed,
                            "actual_hours": actual,
                            "met": met})
        return results

        # ------------------------------------------------------------------
    # Billing policy (remote districts and corporate accounts)
    # ------------------------------------------------------------------
    def get_remote_districts(self):
        """Return a copy of the list of remote districts."""
        return list(self._remote_districts)

    def get_corporate_accounts(self):
        """Return a copy of the list of corporate account names."""
        return list(self._corporate_accounts)

    def add_remote_district(self, district):
        """Add a district to the remote list (ignored if already there).

        Raises:
            ValueError: if the name is empty.
        """
        self._add_to_policy_list(self._remote_districts, district,
                                 "District name")

    def add_corporate_account(self, account):
        """Add a sender to the corporate accounts (ignored if already there).

        Raises:
            ValueError: if the name is empty.
        """
        self._add_to_policy_list(self._corporate_accounts, account,
                                 "Account name")

    @staticmethod
    def _add_to_policy_list(policy_list, name, label):
        """Add a name to a policy list unless it is empty or already there."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{label} must be non-empty text")
        name = name.strip()
        if name.lower() not in [item.lower() for item in policy_list]:
            policy_list.append(name)

    # ------------------------------------------------------------------
    # 4.3 Invoicing
    # ------------------------------------------------------------------
    def raise_invoice(self, tracking_id, issue_date):
        """Raise (or re-raise) the invoice for one shipment.

            tracking_id: id of the shipment to bill.
            issue_date: the invoice date as "YYYY-MM-DD".

        Returns:
            The new Invoice.

        Raises:
            ShipmentNotFoundError: if the tracking id is not in the system.
            ValueError: if the date is not valid.
        """
        shipment = self.get_shipment(tracking_id)
        invoice = Invoice.for_shipment(shipment, self._remote_districts,
                                       self._corporate_accounts, issue_date)
        self._invoices[tracking_id] = invoice
        return invoice

    def get_invoice(self, tracking_id):
        """Return the invoice for a shipment. print() it to see the breakdown.

        Raises:
            ShipmentNotFoundError: if the tracking id is not in the system.
            InvoiceNotFoundError: if the shipment has not been invoiced yet.
        """
        self.get_shipment(tracking_id)
        if tracking_id not in self._invoices:
            raise InvoiceNotFoundError(
                f"no invoice has been raised for {tracking_id}, "
                f"raise one first")
        return self._invoices[tracking_id]

    def raise_all_invoices(self, issue_date):
        """Raise an invoice for every shipment in the system in one go.

        Returns:
            A list of the invoices raised, in tracking id order.

        Raises:
            ValueError: if the date is not valid.
        """
        return [self.raise_invoice(shipment.get_tracking_id(), issue_date)
                for shipment in self.get_all_shipments()]

    def get_all_invoices(self):
        """Return every invoice in the system, sorted by tracking id."""
        return [self._invoices[key] for key in sorted(self._invoices)]

        # ------------------------------------------------------------------
    # 4.4 Reporting
    # ------------------------------------------------------------------
    def consignment_register(self):
        """Return the consignment register as readable text.

        One line per shipment: id, service (class name), destination and
        current status.
        """
        shipments = self.get_all_shipments()
        lines = [f"Consignment register ({len(shipments)} shipments)",
                 f"{'ID':<9}{'Service':<16}{'Destination':<14}Status",
                 "-" * 54]
        for shipment in shipments:
            tracking_id = shipment.get_tracking_id()
            lines.append(
                f"{tracking_id:<9}"
                f"{type(shipment).__name__:<16}"
                f"{shipment.get_destination_city():<14}"
                f"{self.get_current_status(tracking_id)}")
        return "\n".join(lines)

    def scan_summary(self):
        """Return the scan summary as readable text.
        """
        lines = ["Scan summary",
                 f"{'ID':<9}{'Scans':>5}  {'Current location':<22}Status",
                 "-" * 54]
        for shipment in self.get_all_shipments():
            tracking_id = shipment.get_tracking_id()
            scan_count = len(self.get_scan_history(tracking_id))
            lines.append(
                f"{tracking_id:<9}{scan_count:>5}  "
                f"{self.get_current_location(tracking_id):<22}"
                f"{self.get_current_status(tracking_id)}")
        return "\n".join(lines)

    def get_revenue_totals(self, month=None):
        """Return the invoice totals, by component, as a dictionary.

        Args:
            month: "YYYY-MM" to include only invoices raised in that month,
                or None to include every invoice.

        Returns:
            A dictionary with the keys invoice_count, transport_charge,
            fuel_levy, remote_surcharge, corporate_discount, subtotal, vat
            and total.

        Raises:
            ValueError: if the month is not in the form YYYY-MM.
        """
        if month is not None:
            try:
                # Re-format so "2026-9" becomes "2026-09" and matches.
                month = datetime.strptime(month, "%Y-%m").strftime("%Y-%m")
            except (ValueError, TypeError):
                raise ValueError(
                    f"'{month}' is not a valid month, expected YYYY-MM")

        chosen = [invoice for invoice in self.get_all_invoices()
                  if month is None or invoice.get_month() == month]
        return {
            "invoice_count": len(chosen),
            "transport_charge": round(
                sum(i.get_transport_charge() for i in chosen), 2),
            "fuel_levy": round(sum(i.get_fuel_levy() for i in chosen), 2),
            "remote_surcharge": round(
                sum(i.get_remote_surcharge() for i in chosen), 2),
            "corporate_discount": round(
                sum(i.get_corporate_discount() for i in chosen), 2),
            "subtotal": round(sum(i.get_subtotal() for i in chosen), 2),
            "vat": round(sum(i.get_vat() for i in chosen), 2),
            "total": round(sum(i.get_total() for i in chosen), 2),
        }

    def revenue_summary(self, month):
        """Return the revenue summary for one month as readable text.

        Args:
            month: the month as "YYYY-MM", e.g. "2026-09".

        Raises:
            ValueError: if the month is not in the form YYYY-MM.
        """
        totals = self.get_revenue_totals(month)
        title = datetime.strptime(month, "%Y-%m").strftime("%B %Y")

        def row(label, amount):
            """Return one aligned line: label left, amount right."""
            return f"{label:<30}{amount:>18,.2f}"

        lines = [
            f"Revenue summary, {title} ({totals['invoice_count']} invoices)",
            row("Transport charge", totals["transport_charge"]),
            row("Fuel levy", totals["fuel_levy"]),
            row("Remote area surcharge", totals["remote_surcharge"]),
            row("Corporate discount", 0 - totals["corporate_discount"]),
            "-" * 48,
            row("Subtotal", totals["subtotal"]),
            row("VAT", totals["vat"]),
            row("Grand total", totals["total"]),
        ]
        return "\n".join(lines)

    def guarantee_compliance_report(self):
        """Return the express parcel guarantee report as readable text.

        Each parcel is MET (delivered inside its guarantee), LATE (delivered
        after it) or PENDING (not delivered yet).
        """
        results = self.check_guarantee_compliance()
        lines = ["Guarantee compliance (express parcels)"]
        if not results:
            lines.append("No express parcels in the system.")
        for result in results:
            start = (f"{result['tracking_id']} guaranteed "
                     f"{result['guaranteed_hours']} h")
            if result["actual_hours"] is None:
                lines.append(f"{start} actual - PENDING")
            else:
                outcome = "MET" if result["met"] else "LATE"
                lines.append(
                    f"{start} actual {result['actual_hours']:.2f} h "
                    f"{outcome}")
        return "\n".join(lines)
        # ------------------------------------------------------------------
    # 4.5 Data persistence
    # ------------------------------------------------------------------
    def to_dict(self):
        """Return the whole state of the system as a JSON-friendly dictionary.

        Contains the policy lists, every shipment, every scan event and every
        invoice. Each record carries its "type" key.
        """
        return {
            "remote_districts": list(self._remote_districts),
            "corporate_accounts": list(self._corporate_accounts),
            "shipments": [s.to_dict() for s in self.get_all_shipments()],
            "scans": [scan.to_dict() for scan in self._scans],
            "invoices": [i.to_dict() for i in self.get_all_invoices()],
        }

    def save(self, filename):
        """Save the entire system to a JSON file.

        The folder is created if it does not exist.

        Raises:
            DataFileError: if the file cannot be written.
        """
        try:
            folder = os.path.dirname(filename)
            if folder:
                os.makedirs(folder, exist_ok=True)
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(self.to_dict(), file, indent=4)
        except OSError as error:
            raise DataFileError(
                f"could not save to '{filename}' ({error}), check that the "
                f"folder is writable and the disk is not full")

    @classmethod
    def load(cls, filename):
        """Build a NEW system from a JSON file written by save().

        The system is only returned if EVERYTHING loaded correctly, so a bad
        file can never leave half-loaded data behind.

        Raises:
            DataFileError: if the file is missing, unreadable, not valid
                JSON, or its contents are incomplete or inconsistent.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise DataFileError(
                f"file '{filename}' was not found, check the file name and "
                f"folder, or save the system first")
        except json.JSONDecodeError as error:
            raise DataFileError(
                f"file '{filename}' is not valid JSON ({error}), restore a "
                f"backup copy or save the system again")
        except OSError as error:
            raise DataFileError(
                f"file '{filename}' could not be read ({error}), check that "
                f"you have permission to open it")

        try:
            mis = cls(data["remote_districts"], data["corporate_accounts"])
            for item in data["shipments"]:
                mis.add_shipment(shipment_from_dict(item))
            for item in data["scans"]:
                scan = ScanEvent.from_dict(item)
                mis.record_scan(scan.get_tracking_id(), scan.get_timestamp(),
                                scan.get_location(), scan.get_status())
            for item in data["invoices"]:
                invoice = Invoice.from_dict(item)
                mis.get_shipment(invoice.get_tracking_id())
                mis._invoices[invoice.get_tracking_id()] = invoice
        except (KeyError, TypeError, ValueError, ShipmentNotFoundError,
                DuplicateTrackingIDError) as error:
            raise DataFileError(
                f"file '{filename}' has unexpected contents "
                f"({type(error).__name__}: {error}), it may be damaged or "
                f"edited by hand, restore a backup copy")
        return mis

    def build_waybill(self, tracking_id):
        """Return the waybill for one shipment as text.

        A waybill shows the shipment details, its scan history and its
        invoice breakdown (or a note that none has been raised yet).

        Raises:
            ShipmentNotFoundError: if the tracking id is not in the system.
        """
        shipment = self.get_shipment(tracking_id)
        lines = [
            f"=== {Shipment.company_name}: Waybill {tracking_id} ===",
            f"Service: {type(shipment).__name__}",
            "",
            "SHIPMENT DETAILS",
            str(shipment),
            "",
            "SCAN HISTORY",
        ]
        history = self.get_scan_history(tracking_id)
        if history:
            lines.extend(f"  {scan}" for scan in history)
        else:
            lines.append("  No scans recorded yet.")
        lines.append("")
        lines.append("INVOICE")
        if tracking_id in self._invoices:
            lines.append(str(self._invoices[tracking_id]))
        else:
            lines.append("  No invoice raised yet.")
        return "\n".join(lines) + "\n"

    def write_waybill(self, tracking_id, folder="waybills"):
        """Write one waybill to folder/TRACKING_ID.txt and return its path.

        Raises:
            ShipmentNotFoundError: if the tracking id is not in the system.
            DataFileError: if the file cannot be written.
        """
        text = self.build_waybill(tracking_id)
        path = os.path.join(folder, f"{tracking_id}.txt")
        try:
            os.makedirs(folder, exist_ok=True)
            with open(path, "w", encoding="utf-8") as file:
                file.write(text)
        except OSError as error:
            raise DataFileError(
                f"could not write waybill '{path}' ({error}), check that "
                f"the folder is writable")
        return path

    def write_all_waybills(self, folder="waybills"):
        """Write one waybill per shipment and return how many were written.

        Raises:
            DataFileError: if a file cannot be written.
        """
        count = 0
        for shipment in self.get_all_shipments():
            self.write_waybill(shipment.get_tracking_id(), folder)
            count += 1
        return count