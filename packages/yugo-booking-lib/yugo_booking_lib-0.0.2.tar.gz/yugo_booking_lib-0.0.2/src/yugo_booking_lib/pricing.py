from datetime import datetime

class BookingPrice:
    """
    Simple price helper, similar style to the tutorial.
    It only focuses on nights + total price.
    """

    def calculate_nights(self, check_in_str: str, check_out_str: str, fmt: str = "%Y-%m-%d") -> int:
        """
        Given two date strings, return number of nights.
        Example: "2026-01-08" to "2026-01-15" => 7 nights
        """
        check_in = datetime.strptime(check_in_str, fmt).date()
        check_out = datetime.strptime(check_out_str, fmt).date()
        diff = (check_out - check_in).days
        return max(diff, 0)

    def calculate_total_price(
        self,
        nights: int,
        nightly_rate: float,
        tax_rate: float = 0.0,
        fixed_fee: float = 0.0,
    ) -> float: 
        """
        Given nights + nightly_rate, apply optional tax + fixed fee.
        Returns the final total price.
        """
        base = nights * nightly_rate
        tax = base * tax_rate
        total = base + tax + fixed_fee
        return round(total, 2)
