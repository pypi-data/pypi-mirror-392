"""Additional tests for Quote advanced methods."""

import pytest


def test_quote_send_by_email(api_client, mocker):
    """Test sending quote by email."""
    mock_response = {
        "controller": "pricequote",
        "action": "send_by_email",
        "status": "success"
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    
    result = api_client.quotes.send_by_email(Identifier=123)
    
    assert result == mock_response


def test_quote_download(api_client, mocker):
    """Test downloading quote PDF."""
    mock_response = {
        "controller": "pricequote",
        "action": "download",
        "status": "success",
        "Base64": "pdfbase64content"
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    
    result = api_client.quotes.download(Identifier=123)
    
    assert result == mock_response


def test_quote_schedule(api_client, mocker):
    """Test scheduling quote send."""
    mock_response = {
        "controller": "pricequote",
        "action": "schedule",
        "status": "success",
        "pricequote": {
            "Identifier": "123",
            "ScheduledAt": "2025-02-01 10:00:00"
        }
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {'status_code': 200, 'json': staticmethod(lambda: mock_response)}))
    
    result = api_client.quotes.schedule(Identifier=123, ScheduledAt="2025-02-01 10:00:00")
    
    
    assert result == mock_response


def test_quote_cancel_schedule(api_client, mocker):
    """Test cancelling scheduled quote send."""
    mock_response = {
        "controller": "pricequote",
        "action": "cancel_schedule",
        "status": "success",
        "pricequote": {
            "Identifier": "123",
            "ScheduledAt": None
        }
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {'status_code': 200, 'json': staticmethod(lambda: mock_response)}))
    
    result = api_client.quotes.cancel_schedule(Identifier=123)
    
    
    assert result == mock_response


def test_quote_accept(api_client, mocker):
    """Test accepting quote."""
    mock_response = {
        "controller": "pricequote",
        "action": "accept",
        "status": "success",
        "pricequote": {
            "Identifier": "123",
            "Status": "accepted"
        }
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {'status_code': 200, 'json': staticmethod(lambda: mock_response)}))
    
    result = api_client.quotes.accept(Identifier=123)
    
    
    assert result == mock_response


def test_quote_decline(api_client, mocker):
    """Test declining quote."""
    mock_response = {
        "controller": "pricequote",
        "action": "decline",
        "status": "success",
        "pricequote": {
            "Identifier": "123",
            "Status": "declined"
        }
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {'status_code': 200, 'json': staticmethod(lambda: mock_response)}))
    
    result = api_client.quotes.decline(Identifier=123)
    
    
    assert result == mock_response


def test_quote_archive(api_client, mocker):
    """Test archiving quote."""
    mock_response = {
        "controller": "pricequote",
        "action": "archive",
        "status": "success",
        "pricequote": {
            "Identifier": "123",
            "Archived": True
        }
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {'status_code': 200, 'json': staticmethod(lambda: mock_response)}))
    
    result = api_client.quotes.archive(Identifier=123)
    
    
    assert result == mock_response


def test_quote_sort_lines(api_client, mocker):
    """Test sorting quote lines."""
    mock_response = {
        "controller": "pricequote",
        "action": "sort_lines",
        "status": "success",
        "pricequote": {
            "Identifier": "123"
        }
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {'status_code': 200, 'json': staticmethod(lambda: mock_response)}))
    
    lines = [{"Identifier": 456}, {"Identifier": 789}]
    result = api_client.quotes.sort_lines(Identifier=123, PriceQuoteLines=lines)
    
    
    assert result == mock_response


def test_quote_line_add(api_client, mocker):
    """Test adding lines to quote."""
    mock_response = {
        "controller": "pricequote",
        "action": "price_quote_line_add",
        "status": "success",
        "pricequote": {
            "Identifier": "123"
        }
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {'status_code': 200, 'json': staticmethod(lambda: mock_response)}))
    
    lines = [{"Description": "Product A", "PriceExcl": 100.00}]
    result = api_client.quotes.price_quote_line_add(Identifier=123, PriceQuoteLines=lines)
    
    
    assert result == mock_response


def test_quote_line_delete(api_client, mocker):
    """Test deleting lines from quote."""
    mock_response = {
        "controller": "pricequote",
        "action": "price_quote_line_delete",
        "status": "success",
        "pricequote": {
            "Identifier": "123"
        }
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {'status_code': 200, 'json': staticmethod(lambda: mock_response)}))
    
    lines = [{"Identifier": 456}]
    result = api_client.quotes.price_quote_line_delete(Identifier=123, PriceQuoteLines=lines)
    
    
    assert result == mock_response


def test_quote_attachment_add(api_client, mocker):
    """Test adding attachment to quote."""
    mock_response = {
        "controller": "pricequote",
        "action": "attachment_add",
        "status": "success"
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {'status_code': 200, 'json': staticmethod(lambda: mock_response)}))
    
    result = api_client.quotes.attachment_add(
        ReferenceIdentifier=123,
        Filename="spec.pdf",
        Base64="base64content"
    )
    
    assert result == mock_response


def test_quote_attachment_delete(api_client, mocker):
    """Test deleting attachment from quote."""
    mock_response = {
        "controller": "pricequote",
        "action": "attachment_delete",
        "status": "success"
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {'status_code': 200, 'json': staticmethod(lambda: mock_response)}))
    
    result = api_client.quotes.attachment_delete(
        ReferenceIdentifier=123,
        Filename="spec.pdf"
    )
    
    assert result == mock_response


def test_quote_attachment_download(api_client, mocker):
    """Test downloading attachment from quote."""
    mock_response = {
        "controller": "pricequote",
        "action": "attachment_download",
        "status": "success",
        "Base64": "base64content"
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {'status_code': 200, 'json': staticmethod(lambda: mock_response)}))
    
    result = api_client.quotes.attachment_download(
        ReferenceIdentifier=123,
        Filename="spec.pdf"
    )
    
    assert result == mock_response
