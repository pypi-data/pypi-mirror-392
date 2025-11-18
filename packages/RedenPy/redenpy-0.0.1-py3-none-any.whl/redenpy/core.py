from decimal import Decimal, ROUND_HALF_UP
import re

class RedenPy:
    
    def __init__(self, digit, rule):
        """
        A class to do redenomination of a currency.

        Parameters:
        digit (int): The number of digits that wants to be removed from the back
        rule (json): The rule for the redenomination, round up, round down, etc. Check the docs for details
        """
        self.rule = rule
        self.digit = digit

    def redenomination(self, money, fractional=False, output_type=str):
        """
        Convert money according to redenomination rules.

        Args:
            money (str | int | float | Decimal): The amount to convert. Can include symbols, e.g. "$ 1000", "1000 USD"
            fractional (bool): Whether to include fractional part
            output_type (type): Type to return: str, Decimal, float, int
        Returns:
            str | Decimal | float | int: The redenominated value in the requested type
        """
        # Convert input to Decimal
        if isinstance(money, str):
            # Remove all non-digit, non-dot, non-comma characters
            cleaned = re.sub(r"[^\d,\.]", "", money)

            # Handle thousands separators and decimal points
            if cleaned.count(",") > 0 and cleaned.count(".") > 0:
                # Both exist -> determine which is decimal separator by position
                last_comma_pos = cleaned.rfind(",")
                last_dot_pos = cleaned.rfind(".")
                
                if last_dot_pos > last_comma_pos:
                    # Dot comes last -> dot is decimal, comma is thousands
                    # e.g., "1,000,000.75"
                    cleaned = cleaned.replace(",", "")
                else:
                    # Comma comes last -> comma is decimal, dot is thousands
                    # e.g., "1.000.000,75"
                    cleaned = cleaned.replace(".", "")
                    cleaned = cleaned.replace(",", ".")
            elif cleaned.count(",") > 0:                
                parts = cleaned.split(",")
                if len(parts[-1]) <= 2 and len(parts) == 2:
                    cleaned = cleaned.replace(",", ".")
                else:
                    cleaned = cleaned.replace(",", "")
            elif cleaned.count(".") > 0:
                parts = cleaned.split(".")
                if len(parts[-1]) <= 2 and len(parts) == 2:
                    pass 
                else:
                    cleaned = cleaned.replace(".", "")

            try:
                money = Decimal(cleaned)
            except Exception:
                raise ValueError(f"Invalid money string: {money}")

        else:
            money = Decimal(money)

        # Apply redenomination: remove digits from back
        factor = Decimal(10) ** self.digit
        money = (money / factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Separate whole and fractional parts
        whole = int(money)
        frac = int((money - whole) * 100)

        # Format as string
        result_str = f"{whole},{frac:02d}" if fractional else f"{whole}"

        # Convert to requested output type
        if output_type == str:
            return result_str
        elif output_type == Decimal:
            return money
        elif output_type == float:
            return float(money)
        elif output_type == int:
            return int(money)
        else:
            raise ValueError("Unsupported output_type. Use str, Decimal, float, or int.")