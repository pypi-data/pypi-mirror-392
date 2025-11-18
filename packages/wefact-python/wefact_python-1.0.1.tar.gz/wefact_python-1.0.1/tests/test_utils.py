"""Tests for utility functions."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
from wefact.utils import (
    convert_to_base64,
    decode_base64_to_file,
    format_date_for_api,
    format_datetime_for_api,
)


def test_convert_to_base64(tmp_path):
    """Test converting file to base64."""
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_content = b"Hello, WeFact!"
    test_file.write_bytes(test_content)
    
    # Convert to base64
    result = convert_to_base64(test_file)
    
    # Verify it's a valid base64 string
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Verify we can decode it back
    import base64
    decoded = base64.b64decode(result)
    assert decoded == test_content


def test_decode_base64_to_file(tmp_path):
    """Test decoding base64 to file."""
    import base64
    
    # Create base64 content
    test_content = b"Test PDF content"
    base64_string = base64.b64encode(test_content).decode('utf-8')
    
    # Decode to file
    output_file = tmp_path / "output.pdf"
    decode_base64_to_file(base64_string, output_file)
    
    # Verify file was created and content matches
    assert output_file.exists()
    assert output_file.read_bytes() == test_content


def test_format_date_for_api_with_datetime():
    """Test formatting datetime object to date string."""
    test_date = datetime(2025, 11, 7, 14, 30, 45)
    result = format_date_for_api(test_date)
    
    assert result == "2025-11-07"


def test_format_date_for_api_with_string():
    """Test formatting date string (passthrough)."""
    test_date = "2025-11-07"
    result = format_date_for_api(test_date)
    
    assert result == "2025-11-07"


def test_format_datetime_for_api_with_datetime():
    """Test formatting datetime object to datetime string."""
    test_dt = datetime(2025, 11, 7, 14, 30, 45)
    result = format_datetime_for_api(test_dt)
    
    assert result == "2025-11-07 14:30:45"


def test_format_datetime_for_api_with_string():
    """Test formatting datetime string (passthrough)."""
    test_dt = "2025-11-07 14:30:45"
    result = format_datetime_for_api(test_dt)
    
    assert result == "2025-11-07 14:30:45"


def test_format_date_for_scheduled_invoice():
    """Test real-world use case: scheduling an invoice."""
    tomorrow = datetime.now() + timedelta(days=1)
    scheduled_date = format_datetime_for_api(tomorrow)
    
    # Should be in correct format
    assert len(scheduled_date) == 19  # "YYYY-MM-DD HH:MM:SS"
    assert scheduled_date[10] == " "
    assert scheduled_date[4] == "-"
    assert scheduled_date[7] == "-"

