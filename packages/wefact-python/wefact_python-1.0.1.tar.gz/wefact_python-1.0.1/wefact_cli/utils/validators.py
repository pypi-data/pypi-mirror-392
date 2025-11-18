"""Validation utilities for API responses and inputs"""

from typing import Any, Dict, Optional
import re


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format
    
    Args:
        api_key: The API key to validate
    
    Returns:
        True if valid format, False otherwise
    """
    # WeFact API keys appear to be 32-character hexadecimal strings
    if not api_key:
        return False
    
    # Check if it's a reasonable length (at least 20 chars)
    if len(api_key) < 20:
        return False
    
    # Check if it contains only valid characters (alphanumeric)
    if not re.match(r'^[a-fA-F0-9]+$', api_key):
        return False
    
    return True


def is_success_response(response: Dict[str, Any]) -> bool:
    """
    Check if API response indicates success
    
    Args:
        response: API response dictionary
    
    Returns:
        True if response indicates success
    """
    # Check for error status
    if response.get("status") == "error":
        return False
    
    # Check for error key
    if "error" in response and response["error"]:
        return False
    
    # Check for errors array
    if "errors" in response and response["errors"]:
        return False
    
    # If response has data, consider it successful
    # WeFact API typically returns controller name as key
    common_keys = [
        "invoice", "invoices",
        "debtor", "debtors", 
        "product", "products",
        "creditor", "creditors",
        "group", "groups",
        "subscription", "subscriptions",
        "pricequote", "pricequotes",
        "interaction", "interactions",
        "task", "tasks",
        "transaction", "transactions",
        "costcategory", "costcategories",
        "settings"
    ]
    
    for key in common_keys:
        if key in response:
            return True
    
    # If status is explicitly success
    if response.get("status") == "success":
        return True
    
    # Default to True if no error indicators
    return True


def validate_response(response: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate API response and extract error message if any
    
    Args:
        response: API response dictionary
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(response, dict):
        return False, "Response is not a dictionary"
    
    # Check for explicit error status
    if response.get("status") == "error":
        error_msg = response.get("error", "Unknown error")
        return False, error_msg
    
    # Check for error key
    if "error" in response and response["error"]:
        return False, str(response["error"])
    
    # Check for errors array
    if "errors" in response and response["errors"]:
        errors = response["errors"]
        if isinstance(errors, list) and len(errors) > 0:
            return False, str(errors[0])
        return False, str(errors)
    
    return True, None


def validate_identifier(identifier: str) -> bool:
    """
    Validate an identifier/code format
    
    Args:
        identifier: Identifier to validate
    
    Returns:
        True if valid format
    """
    if not identifier or not isinstance(identifier, str):
        return False
    
    # Should be non-empty after stripping
    return len(identifier.strip()) > 0


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid email format
    """
    if not email:
        return False
    
    # Basic email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_price(price: Any) -> bool:
    """
    Validate price value
    
    Args:
        price: Price to validate
    
    Returns:
        True if valid price
    """
    try:
        price_float = float(price)
        return price_float >= 0
    except (ValueError, TypeError):
        return False
