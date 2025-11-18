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

## 🤝 Contributing
Contributions are welcome! Please feel free to open an issue or submit a pull request.

## ⚖️ License
This project is licensed under the MIT License - see the LICENSE file for details.