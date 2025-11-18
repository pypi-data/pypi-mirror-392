"""Utility functions for WeFact API."""

import base64
from datetime import datetime
from pathlib import Path
from typing import Union


def convert_to_base64(file_path: Union[str, Path]) -> str:
    """
    Convert a file to a base64 encoded string.
    
    Args:
        file_path: Path to the file to encode
        
    Returns:
        Base64 encoded string of the file content
        
    Example:
        >>> base64_content = convert_to_base64("invoice.pdf")
        >>> client.invoices.attachment_add(
        ...     ReferenceIdentifier=123,
        ...     Filename="invoice.pdf",
        ...     Base64=base64_content
        ... )
    """
    file_path = Path(file_path)
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def decode_base64_to_file(base64_string: str, output_path: Union[str, Path]) -> None:
    """
    Decode a base64 string and save it to a file.
    
    Args:
        base64_string: Base64 encoded string
        output_path: Path where the decoded file should be saved
        
    Example:
        >>> response = client.invoices.download(Identifier=123)
        >>> decode_base64_to_file(response['Base64'], "invoice.pdf")
    """
    output_path = Path(output_path)
    decoded_content = base64.b64decode(base64_string)
    with open(output_path, 'wb') as f:
        f.write(decoded_content)


def format_date_for_api(date: Union[datetime, str]) -> str:
    """
    Format a date for WeFact API requests.
    
    Args:
        date: datetime object or date string
        
    Returns:
        Date string in format "YYYY-MM-DD"
        
    Example:
        >>> from datetime import datetime, timedelta
        >>> tomorrow = datetime.now() + timedelta(days=1)
        >>> formatted = format_date_for_api(tomorrow)
        >>> client.invoices.mark_as_paid(Identifier=123, PayDate=formatted)
    """
    if isinstance(date, str):
        return date
    return date.strftime("%Y-%m-%d")


def format_datetime_for_api(dt: Union[datetime, str]) -> str:
    """
    Format a datetime for WeFact API requests.
    
    Args:
        dt: datetime object or datetime string
        
    Returns:
        Datetime string in format "YYYY-MM-DD HH:MM:SS"
        
    Example:
        >>> from datetime import datetime, timedelta
        >>> tomorrow = datetime.now() + timedelta(days=1)
        >>> scheduled = format_datetime_for_api(tomorrow)
        >>> client.invoices.schedule(Identifier=123, ScheduledAt=scheduled)
    """
    if isinstance(dt, str):
        return dt
    return dt.strftime("%Y-%m-%d %H:%M:%S")