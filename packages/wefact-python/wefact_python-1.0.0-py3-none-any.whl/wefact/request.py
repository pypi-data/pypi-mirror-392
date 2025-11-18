from __future__ import annotations

import requests
from typing import Any, Dict, List
from urllib.parse import urlencode

from .exceptions import (
    ClientError,
    ServerError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    raise_for_response,
    raise_for_wefact_payload,
)


def flatten_params(params: Dict[str, Any], parent_key: str = '') -> List[tuple]:
    """
    Flatten nested dictionaries and lists for form-encoded POST data.
    
    This mimics PHP's form encoding behavior where nested arrays are encoded as:
    InvoiceLines[0][Number]=1&InvoiceLines[0][ProductCode]=P0001
    
    Args:
        params: Dictionary that may contain nested dicts/lists
        parent_key: Used for recursion to build the key path
        
    Returns:
        List of (key, value) tuples suitable for urlencode with doseq=True
    """
    from enum import Enum
    
    def to_string(val):
        """Convert value to string, handling enums properly."""
        if isinstance(val, Enum):
            return val.value
        return str(val)
    
    items = []
    
    for key, value in params.items():
        new_key = f"{parent_key}[{key}]" if parent_key else key
        
        if isinstance(value, dict):
            # Recursively flatten nested dictionaries
            items.extend(flatten_params(value, new_key))
        elif isinstance(value, (list, tuple)):
            # Handle lists/arrays
            for idx, item in enumerate(value):
                if isinstance(item, dict):
                    # List of dicts: InvoiceLines[0][Number]=1
                    items.extend(flatten_params(item, f"{new_key}[{idx}]"))
                else:
                    # Simple list: Tags[0]=tag1, Tags[1]=tag2
                    items.append((f"{new_key}[{idx}]", to_string(item)))
        else:
            # Simple scalar value
            items.append((new_key, to_string(value)))
    
    return items

class RequestMixin:
    api_key: str
    api_url: str

    def _validate_params(self, params: Dict[str, Any]) -> None:
        """Validate and normalize common parameters."""
        # Auto-convert integer Identifier values to strings (common and acceptable)
        identifier_keys = ['Identifier', 'ReferenceIdentifier', 'ContactIdentifier']
        for key in identifier_keys:
            if key in params and isinstance(params[key], int):
                params[key] = str(params[key])

    def _send_request(self, controller: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate parameters before sending
        self._validate_params(params)
        
        payload = {
            'api_key': self.api_key,
            'controller': controller,
            'action': action,
            **params,
        }
        
        # Flatten nested structures for proper form encoding
        # (e.g., InvoiceLines[0][Number]=1&InvoiceLines[0][ProductCode]=P0001)
        flattened = flatten_params(payload)
        encoded_data = urlencode(flattened)
        
        try:
            response = requests.post(
                self.api_url, 
                data=encoded_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
        except requests.RequestException as e:
            # Network/transport error
            raise ClientError(str(e)) from e

        # Raise on HTTP-level errors
        if not (200 <= int(getattr(response, 'status_code', 0)) < 300):
            raise_for_response(response)

        # Parse JSON
        try:
            data = response.json()
        except ValueError as e:
            raise ValidationError('Invalid JSON response') from e

        # Align with WeFact: status=='error' indicates an application-level error
        raise_for_wefact_payload(response, data)
        return data
