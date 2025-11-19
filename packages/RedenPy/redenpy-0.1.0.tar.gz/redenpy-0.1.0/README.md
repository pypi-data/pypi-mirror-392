# RedenPy

<!-- [![PyPI version](https://badge.fury.io/py/redenpy.svg)](https://badge.fury.io/py/redenpy) -->
<!-- [![Build Status](https://img.shields.io/travis/com/YOUR_USERNAME/redenpy.svg)](https://travis-ci.com/YOUR_USERNAME/redenpy) -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple, robust Python utility for currency redenomination.

`RedenPy` is designed to parse various money formats—including strings with currency symbols and different decimal/thousand separators—and apply a redenomination by a specified number of digits (e.g., converting 1,000,000 to 1,000).

---

## ✨ Features

* **Handles Multiple Input Types:** Accepts `int`, `float`, `Decimal`, and `str` inputs.
* **Robust String Parsing:** Automatically cleans currency symbols (`$`, `Rp`, `€`, etc.) and non-numeric characters.
* **International Format Support:** Intelligently parses both US-style (`1,000.00`) and EU-style (`1.000,00`) number formats.
* **Flexible Output:** Returns the redenominated value as a `str`, `int`, `float`, or `Decimal`.
* **Accurate Calculations:** Uses the `Decimal` type internally for all calculations to avoid floating-point errors.

---

## 📦 Installation

Install `RedenPy` directly from PyPI:

```bash
pip install redenpy
```

---
## 🚀 Quick Start
```python
from redenpy.core import RedenPy

# 1. Initialize the redenominator
# We want to remove 3 digits (e.g., 1,000 -> 1)
rd = RedenPy(digit=3, rule=None) # 'rule' is reserved for future rounding logic

# 2. Perform redenomination on various inputs

# --- Example 1: Handling International String Formats ---
val_str_us = "$ 1,575,505.75" # Dot as decimal
val_str_eu = "€ 1.575.505,75" # Comma as decimal

# Returns a 'Decimal' object
new_val_us = rd.redenomination(val_str_us, output_type=Decimal)
new_val_eu = rd.redenomination(val_str_eu, output_type=Decimal)

print(f"'{val_str_us}' -> {new_val_us}")
# Output: '$ 1,575,505.75' -> 1575.51

print(f"'{val_str_eu}' -> {new_val_eu}")
# Output: '€ 1.575.505,75' -> 1575.51

# --- Example 2: Controlling Output Type ---
old_val = 1575800

# Get a formatted string with fractions
val_str = rd.redenomination(old_val, fractional=True, output_type=str)
print(f"{old_val} -> '{val_str}' (as string)")
# Output: 1575800 -> '1575,80' (as string)

# Get an integer (truncates the decimal)
val_int = rd.redenomination(old_val, output_type=int)
print(f"{old_val} -> {val_int} (as integer)")
# Output: 1575800 -> 1575 (as integer)

# Get a float
val_float = rd.redenomination(old_val, output_type=float)
print(f"{old_val} -> {val_float} (as float)")
# Output: 1575800 -> 1575.8 (as float)
```

---
## 📖 API Reference

```python
RedenPy(digit, rule)
```
Initializes the redenomination class.
- digit (int): The number of digits to remove (e.g., 3 for 1,000 -> 1). This is equivalent to dividing by $10^{digit}$.
- rule (any): A parameter intended for future, more complex rounding rules (e.g., specific central bank regulations). Note: This parameter is not currently used in the logic. All calculations default to ROUND_HALF_UP to 2 decimal places.

```python
redenomination(money, fractional=False, output_type=str)
```
Performs the redenomination on a given money value.

- money (str | int | float | Decimal): The amount to convert.
- fractional (bool): This parameter only affects the output_type=str.
    - True: Returns the value with a fractional part, separated by a comma (e.g., "1575,51").
    - False: Returns only the whole number part (e.g., "1575").

- output_type (type): The desired return type for the converted value.
    - str: Returns a formatted string. Behavior is controlled by fractional.
    - Decimal: Returns the redenominated value as a Decimal object, rounded to 2 decimal places.
    - float: Returns the redenominated value as a float.
    - int: Returns the redenominated value as an int (note: this truncates any decimal part after rounding, e.g., 1575.51 becomes 1575).

```python
redenomination_with_rules(money, output_type=str)
```
accepts a comprehensive rule dictionary that allows full customization of the redenomination process. Below are all possible rules that can be configured.

## Complete Rule Reference

### 1. `digit_removal` (Integer)

Overrides the default digit removal specified in the constructor.

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `digit_removal` | `int` | Number of digits to remove from the right | `3` removes 3 zeros (1,000,000 → 1,000) |

**Example:**
```python
rule = {"digit_removal": 6}
# 1,000,000 → 1 (removes 6 digits)
```

---

### 2. `rounding` (Object)

Controls how numbers are rounded during redenomination.

| Property | Type | Options | Default | Description |
|----------|------|---------|---------|-------------|
| `method` | `string` | `"half_up"`, `"half_down"`, `"up"`, `"down"`, `"half_even"`, `"ceiling"`, `"floor"`, `"truncate"` | `"half_up"` | Rounding method to apply |
| `precision` | `int` | `0`, `1`, `2`, `3`, etc. | `2` | Number of decimal places to keep |

**Rounding Methods Explained:**
- `"half_up"`: Round 0.5 up (1.5 → 2, -1.5 → -2)
- `"half_down"`: Round 0.5 down (1.5 → 1, -1.5 → -1)
- `"up"`: Always round away from zero (1.1 → 2, -1.1 → -2)
- `"down"`: Always round toward zero (1.9 → 1, -1.9 → -1)
- `"half_even"`: Banker's rounding - round to nearest even (1.5 → 2, 2.5 → 2)
- `"ceiling"`: Always round up (1.1 → 2, -1.1 → -1)
- `"floor"`: Always round down (1.9 → 1, -1.9 → -2)
- `"truncate"`: Remove decimal part (1.9 → 1, -1.9 → -1)

**Example:**
```python
rule = {
    "rounding": {
        "method": "down",
        "precision": 0
    }
}
# 1,234.56 → 1,234 (no decimals, always round down)
```

---

### 3. `fractional_policy` (Object)

Controls when and how fractional/decimal parts are displayed.

| Property | Type | Options | Default | Description |
|----------|------|---------|---------|-------------|
| `always_show` | `bool` | `true`, `false` | `false` | Always display decimals even if .00 |
| `threshold` | `float` or `null` | Any decimal value | `null` | Only show decimals if fractional part ≥ threshold |
| `context` | `string` | `"always"`, `"never"`, `"auto"` | `"auto"` | When to show decimal part |

**Context Options:**
- `"always"`: Always show decimals (1 → 1.00)
- `"never"`: Never show decimals (1.75 → 1)
- `"auto"`: Show decimals only if non-zero (1.00 → 1, 1.50 → 1.50)

**Example:**
```python
rule = {
    "fractional_policy": {
        "always_show": false,
        "threshold": 0.50,
        "context": "auto"
    }
}
# 1.20 → 1 (below threshold)
# 1.60 → 1.60 (above threshold)
```

---

### 4. `rounding_interval` (Object)

Round to specific intervals (useful for cash transactions where smallest denomination is 5 or 10 cents).

| Property | Type | Options | Default | Description |
|----------|------|---------|---------|-------------|
| `enabled` | `bool` | `true`, `false` | `false` | Enable interval rounding |
| `interval` | `int` | `5`, `10`, `25`, `50`, `100`, etc. | `1` | Round to nearest interval |
| `apply_to` | `string` | `"whole"`, `"fractional"`, `"both"` | `"whole"` | What part to apply rounding to |

**Apply To Options:**
- `"whole"`: Round the whole number part (123.45 with interval 10 → 120.45)
- `"fractional"`: Round the fractional part (123.47 with interval 5 → 123.45)
- `"both"`: Round the entire number (123.47 with interval 5 → 125)

**Example:**
```python
rule = {
    "rounding_interval": {
        "enabled": True,
        "interval": 5,
        "apply_to": "fractional"
    }
}
# 1.23 → 1.25 (rounded to nearest 0.05)
# 1.27 → 1.25
```

---

### 5. `minimum_value` (Object)

Handle very small values that should be eliminated or rounded to minimum denomination.

| Property | Type | Options | Default | Description |
|----------|------|---------|---------|-------------|
| `enabled` | `bool` | `true`, `false` | `false` | Enable minimum value handling |
| `threshold` | `float` | Any decimal value | `0.01` | Minimum acceptable value |
| `action` | `string` | `"round_to_zero"`, `"round_to_minimum"` | `"round_to_zero"` | What to do with sub-threshold values |

**Action Options:**
- `"round_to_zero"`: Values below threshold become 0
- `"round_to_minimum"`: Values below threshold become the threshold value

**Example:**
```python
rule = {
    "minimum_value": {
        "enabled": True,
        "threshold": 0.10,
        "action": "round_to_zero"
    }
}
# 0.05 → 0 (below minimum)
# 0.15 → 0.15 (above minimum)
```

---

### 6. `formatting` (Object)

Controls the string output format (thousand separators, decimal separators).

| Property | Type | Options | Default | Description |
|----------|------|---------|---------|-------------|
| `decimal_separator` | `string` | `","`, `"."` | `","` | Character to separate decimals |
| `thousand_separator` | `string` | `"."`, `","`, `" "`, `""` | `"."` | Character to separate thousands |
| `force_decimals` | `bool` | `true`, `false` | `false` | Always show decimal separator |

**Example:**
```python
rule = {
    "formatting": {
        "decimal_separator": ".",
        "thousand_separator": ",",
        "force_decimals": True
    }
}
# 1234567.5 → 1,234,567.50 (US format)

rule = {
    "formatting": {
        "decimal_separator": ",",
        "thousand_separator": ".",
        "force_decimals": True
    }
}
# 1234567.5 → 1.234.567,50 (European format)
```

---

## Complete Rule Example

```python
rule = {
    "digit_removal": 3,
    "rounding": {
        "method": "half_up",
        "precision": 2
    },
    "fractional_policy": {
        "always_show": False,
        "threshold": None,
        "context": "auto"
    },
    "rounding_interval": {
        "enabled": False,
        "interval": 5,
        "apply_to": "fractional"
    },
    "minimum_value": {
        "enabled": False,
        "threshold": 0.01,
        "action": "round_to_zero"
    },
    "formatting": {
        "decimal_separator": ",",
        "thousand_separator": ".",
        "force_decimals": False
    }
}

r = RedenPy(digit=3, rule=rule)
result = r.redenomination_with_rules("$ 1,234,567.89")
print(result)  # 1.234,57
```

---

## Real-World Country Examples

### 🇮🇩 Indonesia 1965 (Removed 3 zeros)
```python
rule = {
    "digit_removal": 3,
    "rounding": {"method": "half_up", "precision": 2},
    "fractional_policy": {"context": "auto"},
    "formatting": {
        "decimal_separator": ",",
        "thousand_separator": "."
    }
}
```

### 🇹🇷 Turkey 2005 (Removed 6 zeros, cash rounding)
```python
rule = {
    "digit_removal": 6,
    "rounding": {"method": "half_up", "precision": 2},
    "rounding_interval": {
        "enabled": True,
        "interval": 5,
        "apply_to": "fractional"
    },
    "fractional_policy": {"context": "always"}
}
```

### 🇧🇷 Brazil 1994 (No decimals, eliminate small values)
```python
rule = {
    "digit_removal": 3,
    "rounding": {"method": "down", "precision": 0},
    "fractional_policy": {"context": "never"},
    "minimum_value": {
        "enabled": True,
        "threshold": 1,
        "action": "round_to_zero"
    }
}
```

### 🇿🇼 Zimbabwe 2009 (Removed 12 zeros)
```python
rule = {
    "digit_removal": 12,
    "rounding": {"method": "half_up", "precision": 2},
    "fractional_policy": {"context": "auto"}
}
```


## 🤝 Contributing
Contributions are welcome! Please feel free to open an issue or submit a pull request.

## ⚖️ License
This project is licensed under the MIT License - see the LICENSE file for details.