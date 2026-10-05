"""
billing.py - Invoicing for the SwiftLink Logistics MIS.

AndrewIDs: oabdulaz

This module contains the Invoice class. An Invoice records what a customer
owes for ONE shipment and breaks the amount into components (transport,
fuel levy, remote surcharge, corporate discount, subtotal, VAT, total) so the
customer can see how the total was reached.

All billing and tax rates are defined as constants at the top of the Invoice
class. 
"""

from datetime import datetime


class Invoice:
    """
    The invoice stores only the shipment's tracking id, never the shipment
    object itself. The transport charge is NOT recalculated here: it is
    taken from the shipment's own calculate_cost() method.
    """

    #Billing and tax rules 
    FUEL_LEVY_RATE = 0.06           # 6% of the transport charge
    REMOTE_SURCHARGE = 8000         # flat RWF amount for remote districts
    CORPORATE_DISCOUNT_RATE = 0.10  # 10% of the transport charge
    VAT_RATE = 0.18                 # 18% of the subtotal (after discount)

    # Format of the invoice date text, e.g. "2026-09-14".
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, tracking_id, transport_charge, is_remote,
                 is_corporate, issue_date):
        """Create an invoice and work out every component.

        Args:
            tracking_id: id of the shipment being billed.
            transport_charge: the shipment's cost from calculate_cost().
            is_remote: True if the destination is a remote district.
            is_corporate: True if the sender is a corporate account.
            issue_date: date the invoice was raised, "YYYY-MM-DD".

        Raises:
            ValueError: if the date is not in the form YYYY-MM-DD or the
                transport charge is negative.
        """
        # Check the date by trying to parse it.
        try:
            datetime.strptime(issue_date, self.DATE_FORMAT)
        except (ValueError, TypeError):
            raise ValueError(
                f"'{issue_date}' is not a valid date, expected YYYY-MM-DD")

        if transport_charge < 0:
            raise ValueError("Transport charge cannot be negative")

        self._tracking_id = tracking_id
        self._issue_date = issue_date
        self._is_remote = bool(is_remote)
        self._is_corporate = bool(is_corporate)

        # Work out each component. Money is rounded to 2 decimal places.
        self._transport_charge = round(transport_charge, 2)
        self._fuel_levy = round(
            self._transport_charge * self.FUEL_LEVY_RATE, 2)
        self._remote_surcharge = (
            float(self.REMOTE_SURCHARGE) if self._is_remote else 0.0)
        self._corporate_discount = (
            round(self._transport_charge * self.CORPORATE_DISCOUNT_RATE, 2)
            if self._is_corporate else 0.0)
        self._subtotal = round(
            self._transport_charge + self._fuel_levy
            + self._remote_surcharge - self._corporate_discount, 2)
        self._vat = round(self._subtotal * self.VAT_RATE, 2)
        self._total = round(self._subtotal + self._vat, 2)

    @classmethod
    def for_shipment(cls, shipment, remote_districts, corporate_accounts,
                     issue_date):
        """Build an invoice for a shipment object.

        This is the method the LogisticsMIS calls. It works for ANY kind of
        shipment: shipment.calculate_cost() runs the correct
        pricing for that shipment's own class.

        Args:
            shipment: any Shipment, TrackedShipment, ExpressParcel,
                FragileParcel or BulkFreight object.
            remote_districts: list of remote district names (policy).
            corporate_accounts: list of corporate sender names (policy).
            issue_date: "YYYY-MM-DD".

        Returns:
            A new Invoice.
        """
        remote = [name.lower() for name in remote_districts]
        corporate = [name.lower() for name in corporate_accounts]
        is_remote = shipment.get_destination_city().lower() in remote
        is_corporate = shipment.get_sender_name().lower() in corporate
        return cls(shipment.get_tracking_id(), shipment.calculate_cost(),
                   is_remote, is_corporate, issue_date)

    #getters 
    def get_tracking_id(self):
        """Return the id of the shipment this invoice is for."""
        return self._tracking_id

    def get_issue_date(self):
        """Return the invoice date as text "YYYY-MM-DD"."""
        return self._issue_date

    def get_month(self):
        """Return the invoice month as "YYYY-MM", used for monthly reports."""
        return self._issue_date[:7]

    def get_transport_charge(self):
        """Return the transport charge in RWF."""
        return self._transport_charge

    def get_fuel_levy(self):
        """Return the fuel levy in RWF."""
        return self._fuel_levy

    def get_remote_surcharge(self):
        """Return the remote area surcharge in RWF (0 if not remote)."""
        return self._remote_surcharge

    def get_corporate_discount(self):
        """Return the corporate discount in RWF (0 if not corporate)."""
        return self._corporate_discount

    def get_subtotal(self):
        """Return the subtotal before VAT in RWF."""
        return self._subtotal

    def get_vat(self):
        """Return the VAT amount in RWF."""
        return self._vat

    def get_total(self):
        """Return the total payable in RWF."""
        return self._total

    #display and saving
    @staticmethod
    def _row(label, amount):
        """Return one aligned invoice line: label on the left, amount right."""
        return f"{label:<30}{amount:>18,.2f}"

    def __str__(self):
        """Return the invoice broken down by component, ready to print."""
        divider = "-" * 48
        lines = [
            f"Invoice {self._tracking_id}",
            self._row("Transport charge", self._transport_charge),
            self._row(f"Fuel levy ({self.FUEL_LEVY_RATE:.0%})",
                      self._fuel_levy),
            self._row("Remote area surcharge", self._remote_surcharge),
            # 0 - discount keeps a zero discount as 0.00 (not -0.00).
            self._row(f"Corporate discount "
                      f"({self.CORPORATE_DISCOUNT_RATE:.0%})",
                      0 - self._corporate_discount),
            divider,
            self._row("Subtotal", self._subtotal),
            self._row(f"VAT ({self.VAT_RATE:.0%})", self._vat),
            self._row("Total payable", self._total),
        ]
        return "\n".join(lines)

    def to_dict(self):
        """Return the invoice as a dictionary that can be saved to JSON."""
        return {
            "type": "Invoice",
            "tracking_id": self._tracking_id,
            "issue_date": self._issue_date,
            "transport_charge": self._transport_charge,
            "is_remote": self._is_remote,
            "is_corporate": self._is_corporate,
            "fuel_levy": self._fuel_levy,
            "remote_surcharge": self._remote_surcharge,
            "corporate_discount": self._corporate_discount,
            "subtotal": self._subtotal,
            "vat": self._vat,
            "total": self._total,
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild an invoice from a to_dict() dictionary.

        The saved amounts are restored exactly as they were, so an invoice
        raised last month keeps its original figures even if a rate in the
        class is changed later.

        Raises:
            KeyError: a required field is missing from the dictionary.
            ValueError: the date or amount in the dictionary is invalid.
        """
        invoice = cls(data["tracking_id"], data["transport_charge"],
                      data["is_remote"], data["is_corporate"],
                      data["issue_date"])
        invoice._fuel_levy = data["fuel_levy"]
        invoice._remote_surcharge = data["remote_surcharge"]
        invoice._corporate_discount = data["corporate_discount"]
        invoice._subtotal = data["subtotal"]
        invoice._vat = data["vat"]
        invoice._total = data["total"]
        return invoice