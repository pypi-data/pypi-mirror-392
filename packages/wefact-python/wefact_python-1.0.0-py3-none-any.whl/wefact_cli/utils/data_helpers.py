"""Helper functions for handling WeFact API data types"""

from typing import Any, Union


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float, handling strings and None.
    
    The WeFact API returns numeric values inconsistently - sometimes as strings,
    sometimes as actual numbers. This helper handles both cases.
    
    Args:
        value: Value to convert (can be str, int, float, or None)
        default: Default value if conversion fails
    
    Returns:
        Float value or default
    
    Examples:
        >>> safe_float("10.50")
        10.5
        >>> safe_float(10.50)
        10.5
        >>> safe_float("invalid", 0.0)
        0.0
        >>> safe_float(None, 0.0)
        0.0
    """
    if value is None:
        return default
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert a value to int, handling strings and None.
    
    Args:
        value: Value to convert (can be str, int, or None)
        default: Default value if conversion fails
    
    Returns:
        Integer value or default
    
    Examples:
        >>> safe_int("5")
        5
        >>> safe_int(5)
        5
        >>> safe_int("invalid", 0)
        0
        >>> safe_int(None, 0)
        0
    """
    if value is None:
        return default
    
    try:
        # Handle floats as strings (e.g., "10.5" -> 10)
        return int(float(value))
    except (ValueError, TypeError):
        return default


def format_currency(value: Any, currency: str = "€", default: str = "0.00") -> str:
    """
    Format a value as currency, safely handling string/numeric values.
    
    Args:
        value: Numeric value (can be str, int, float, or None)
        currency: Currency symbol to prepend
        default: Default display value if conversion fails
    
    Returns:
        Formatted currency string
    
    Examples:
        >>> format_currency("10.50")
        '€10.50'
        >>> format_currency(10.5, "$")
        '$10.50'
        >>> format_currency("invalid")
        '0.00'
    """
    float_value = safe_float(value, None)
    
    if float_value is None:
        return default
    
    return f"{currency}{float_value:.2f}"


def format_percentage(value: Any, default: str = "0.0") -> str:
    """
    Format a value as percentage, safely handling string/numeric values.
    
    Args:
        value: Numeric value (can be str, int, float, or None)
        default: Default display value if conversion fails
    
    Returns:
        Formatted percentage string
    
    Examples:
        >>> format_percentage("21")
        '21.0%'
        >>> format_percentage(21)
        '21.0%'
        >>> format_percentage("invalid")
        '0.0'
    """
    float_value = safe_float(value, None)
    
    if float_value is None:
        return default
    
    return f"{float_value:.1f}%"


def normalize_api_response(data: dict) -> dict:
    """
    Normalize WeFact API response by converting string numbers to appropriate types.
    
    This is useful when you need actual numeric types for calculations or comparisons.
    Note: This modifies the dictionary in-place and returns it.
    
    Args:
        data: API response dictionary
    
    Returns:
        Normalized dictionary with converted types
    
    Examples:
        >>> normalize_api_response({"Amount": "10.50", "Count": "5"})
        {"Amount": 10.5, "Count": 5}
    """
    # Common numeric fields in WeFact API
    float_fields = {
        'AmountExcl', 'AmountIncl', 'AmountPaid', 'AmountOutstanding',
        'PriceExcl', 'PriceIncl', 'TaxPercentage', 'DiscountPercentage',
        'Discount', 'Total', 'Subtotal'
    }
    
    int_fields = {
        'Identifier', 'Debtor', 'Status', 'Sent', 'Reminders', 'Summations',
        'Number', 'Quantity', 'Term', 'Periods'
    }
    
    for key, value in data.items():
        if key in float_fields and isinstance(value, str):
            data[key] = safe_float(value)
        elif key in int_fields and isinstance(value, str):
            data[key] = safe_int(value)
    
    return data


def get_display_name(item: dict, resource_type: str) -> str:
    """
    Get a human-friendly display name for an API item.
    
    Args:
        item: API response item dictionary
        resource_type: Type of resource (debtor, invoice, product, etc.)
    
    Returns:
        Display name string
    
    Examples:
        >>> get_display_name({"CompanyName": "ACME Corp", "DebtorCode": "DB001"}, "debtor")
        'ACME Corp (DB001)'
        >>> get_display_name({"ProductName": "Hosting", "ProductCode": "P001"}, "product")
        'Hosting (P001)'
    """
    if resource_type == 'debtor':
        name = item.get('CompanyName') or f"{item.get('Initials', '')} {item.get('SurName', '')}".strip()
        code = item.get('DebtorCode', '')
        return f"{name} ({code})" if code else name
    
    elif resource_type == 'invoice':
        code = item.get('InvoiceCode', '')
        debtor = item.get('CompanyName') or item.get('Debtor', '')
        amount = format_currency(item.get('AmountIncl'))
        return f"{code} - {debtor} ({amount})"
    
    elif resource_type == 'product':
        name = item.get('ProductName', '')
        code = item.get('ProductCode', '')
        return f"{name} ({code})" if code else name
    
    elif resource_type == 'creditor':
        name = item.get('CompanyName', '')
        code = item.get('CreditorCode', '')
        return f"{name} ({code})" if code else name
    
    else:
        # Generic fallback
        return item.get('Title') or item.get('Name') or item.get('Description') or str(item.get('Identifier', ''))
