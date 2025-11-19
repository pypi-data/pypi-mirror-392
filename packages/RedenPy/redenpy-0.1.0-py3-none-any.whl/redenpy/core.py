from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN, ROUND_UP, ROUND_HALF_EVEN, ROUND_FLOOR, ROUND_CEILING
import re

class RedenPy:
    
    def __init__(self, digit, rule=None):
        """
        A class to do redenomination of a currency.

        Parameters:
        digit (int): The number of digits that wants to be removed from the back
        rule (dict): The rule for the redenomination. If None, uses default behavior.
                     See redenomination_with_rules() for rule structure.
        """
        self.rule = rule or {}
        self.digit = digit
        
        # Rounding method mapping
        self.rounding_methods = {
            "half_up": ROUND_HALF_UP,
            "half_down": ROUND_DOWN,
            "up": ROUND_UP,
            "down": ROUND_DOWN,
            "half_even": ROUND_HALF_EVEN,
            "ceiling": ROUND_CEILING,
            "floor": ROUND_FLOOR,
            "truncate": ROUND_DOWN
        }

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
                # Both exist → determine which is decimal separator by position
                last_comma_pos = cleaned.rfind(",")
                last_dot_pos = cleaned.rfind(".")
                
                if last_dot_pos > last_comma_pos:
                    # Dot comes last → dot is decimal, comma is thousands
                    # e.g., "1,000,000.75"
                    cleaned = cleaned.replace(",", "")
                else:
                    # Comma comes last → comma is decimal, dot is thousands
                    # e.g., "1.000.000,75"
                    cleaned = cleaned.replace(".", "")
                    cleaned = cleaned.replace(",", ".")
            elif cleaned.count(",") > 0:
                # Only comma exists
                # Check if it's likely a decimal separator (2 digits after last comma)
                parts = cleaned.split(",")
                if len(parts[-1]) <= 2 and len(parts) == 2:
                    # Likely decimal separator: "1000,50"
                    cleaned = cleaned.replace(",", ".")
                else:
                    # Likely thousands separator: "1,000" or "1,000,000"
                    cleaned = cleaned.replace(",", "")
            elif cleaned.count(".") > 0:
                # Only dot exists
                parts = cleaned.split(".")
                # If last part has exactly 1-2 digits, treat as decimal
                # Otherwise treat as thousands separator
                if len(parts[-1]) <= 2 and len(parts) == 2:
                    # Likely decimal: "1000.50"
                    pass  # keep dot as is
                else:
                    # Likely thousands separator: "1.000" or "1.000000"
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

    def redenomination_with_rules(self, money, output_type=str):
        """
        Convert money according to comprehensive redenomination rules.
        
        Args:
            money (str | int | float | Decimal): The amount to convert
            output_type (type): Type to return: str, Decimal, float, int
            
        Returns:
            str | Decimal | float | int: The redenominated value according to rules
            
        Rule Structure Example:
        {
            "digit_removal": 3,  # overrides self.digit if provided
            "rounding": {
                "method": "half_up",  # half_up, half_down, up, down, half_even, ceiling, floor, truncate
                "precision": 2        # decimal places to keep
            },
            "fractional_policy": {
                "always_show": false,       # always show decimals even if .00
                "threshold": null,          # only show decimals if >= threshold (e.g., 0.50)
                "context": "auto"           # "always", "never", "auto" (show if non-zero)
            },
            "rounding_interval": {
                "enabled": false,
                "interval": 5,              # round to nearest 5, 10, 25, 50, 100
                "apply_to": "whole"         # "whole", "fractional", "both"
            },
            "minimum_value": {
                "enabled": false,
                "threshold": 0.01,          # values below this become 0
                "action": "round_to_zero"   # "round_to_zero", "round_to_minimum"
            },
            "formatting": {
                "decimal_separator": ",",   # "," or "."
                "thousand_separator": ".",  # ".", ",", " ", or ""
                "force_decimals": false     # always show decimals
            }
        }
        """
        # Parse money input
        money_decimal = self._parse_money(money)
        
        # Get digit removal (from rule or default)
        digit_removal = self.rule.get("digit_removal", self.digit)
        
        # Apply digit removal
        factor = Decimal(10) ** digit_removal
        money_decimal = money_decimal / factor
        
        # Get rounding configuration
        rounding_config = self.rule.get("rounding", {})
        rounding_method = rounding_config.get("method", "half_up")
        precision = rounding_config.get("precision", 2)
        
        # Apply rounding
        rounding_mode = self.rounding_methods.get(rounding_method, ROUND_HALF_UP)
        quantize_str = f"0.{'0' * precision}" if precision > 0 else "1"
        money_decimal = money_decimal.quantize(Decimal(quantize_str), rounding=rounding_mode)
        
        # Apply minimum value rules
        min_value_config = self.rule.get("minimum_value", {})
        if min_value_config.get("enabled", False):
            threshold = Decimal(str(min_value_config.get("threshold", 0.01)))
            if abs(money_decimal) < threshold:
                action = min_value_config.get("action", "round_to_zero")
                if action == "round_to_zero":
                    money_decimal = Decimal(0)
                elif action == "round_to_minimum":
                    money_decimal = threshold if money_decimal > 0 else -threshold
        
        # Apply rounding interval
        interval_config = self.rule.get("rounding_interval", {})
        if interval_config.get("enabled", False):
            interval = Decimal(str(interval_config.get("interval", 1)))
            apply_to = interval_config.get("apply_to", "whole")
            
            if apply_to == "whole":
                whole = (money_decimal // 1)
                frac = money_decimal - whole
                whole = (whole / interval).quantize(Decimal('1'), rounding=rounding_mode) * interval
                money_decimal = whole + frac
            elif apply_to == "fractional":
                whole = (money_decimal // 1)
                frac = money_decimal - whole
                frac = (frac / (interval / 100)).quantize(Decimal('0.01'), rounding=rounding_mode) * (interval / 100)
                money_decimal = whole + frac
            elif apply_to == "both":
                money_decimal = (money_decimal / interval).quantize(Decimal('0.01'), rounding=rounding_mode) * interval
        
        # Handle output formatting
        if output_type == str:
            return self._format_money_string(money_decimal, precision)
        elif output_type == Decimal:
            return money_decimal
        elif output_type == float:
            return float(money_decimal)
        elif output_type == int:
            return int(money_decimal)
        else:
            raise ValueError("Unsupported output_type. Use str, Decimal, float, or int.")
    
    def _parse_money(self, money):
        # Parse money from various input formats to Decimal
        if isinstance(money, str):
            # Remove all non-digit, non-dot, non-comma characters
            cleaned = re.sub(r"[^\d,\.]", "", money)

            # Handle thousands separators and decimal points
            if cleaned.count(",") > 0 and cleaned.count(".") > 0:
                # Both exist → determine which is decimal separator by position
                last_comma_pos = cleaned.rfind(",")
                last_dot_pos = cleaned.rfind(".")
                
                if last_dot_pos > last_comma_pos:
                    # Dot comes last → dot is decimal, comma is thousands
                    cleaned = cleaned.replace(",", "")
                else:
                    # Comma comes last → comma is decimal, dot is thousands
                    cleaned = cleaned.replace(".", "")
                    cleaned = cleaned.replace(",", ".")
            elif cleaned.count(",") > 0:
                # Only comma exists
                parts = cleaned.split(",")
                if len(parts[-1]) <= 2 and len(parts) == 2:
                    # Likely decimal separator: "1000,50"
                    cleaned = cleaned.replace(",", ".")
                else:
                    # Likely thousands separator: "1,000" or "1,000,000"
                    cleaned = cleaned.replace(",", "")
            elif cleaned.count(".") > 0:
                # Only dot exists
                parts = cleaned.split(".")
                # If last part has exactly 1-2 digits, treat as decimal
                # Otherwise treat as thousands separator
                if len(parts[-1]) <= 2 and len(parts) == 2:
                    # Likely decimal: "1000.50"
                    pass  # keep dot as is
                else:
                    # Likely thousands separator: "1.000" or "1.000000"
                    cleaned = cleaned.replace(".", "")

            try:
                return Decimal(cleaned)
            except Exception:
                raise ValueError(f"Invalid money string: {money}")
        else:
            return Decimal(str(money))
    
    def _format_money_string(self, money_decimal, precision):
        # Format Decimal to string according to formatting rules
        formatting = self.rule.get("formatting", {})
        decimal_sep = formatting.get("decimal_separator", ",")
        thousand_sep = formatting.get("thousand_separator", ".")
        force_decimals = formatting.get("force_decimals", False)
        
        fractional_policy = self.rule.get("fractional_policy", {})
        always_show = fractional_policy.get("always_show", False)
        threshold = fractional_policy.get("threshold", None)
        context = fractional_policy.get("context", "auto")
        
        # Separate whole and fractional parts
        whole = int(money_decimal)
        frac_decimal = abs(money_decimal - whole)
        frac = int((frac_decimal * (10 ** precision)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
        
        # Determine if we should show fractional part
        show_frac = False
        if context == "always" or always_show or force_decimals:
            show_frac = True
        elif context == "never":
            show_frac = False
        elif context == "auto":
            if threshold is not None:
                show_frac = frac_decimal >= Decimal(str(threshold))
            else:
                show_frac = frac > 0
        
        # Format whole number with thousand separators
        whole_str = str(abs(whole))
        if thousand_sep:
            # Add thousand separators
            parts = []
            for i, digit in enumerate(reversed(whole_str)):
                if i > 0 and i % 3 == 0:
                    parts.append(thousand_sep)
                parts.append(digit)
            whole_str = ''.join(reversed(parts))
        
        # Add negative sign if needed
        if money_decimal < 0:
            whole_str = '-' + whole_str
        
        # Build final string
        if show_frac and precision > 0:
            frac_str = str(frac).zfill(precision)
            return f"{whole_str}{decimal_sep}{frac_str}"
        else:
            return whole_str