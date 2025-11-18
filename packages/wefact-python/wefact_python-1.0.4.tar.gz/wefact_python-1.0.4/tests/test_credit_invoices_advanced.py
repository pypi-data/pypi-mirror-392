"""Additional tests for CreditInvoice advanced methods."""

import pytest


def test_credit_invoice_part_payment(api_client, mocker):
    """Test part payment for credit invoice."""
    mock_response = {
        "controller": "creditinvoice",
        "action": "part_payment",
        "status": "success",
        "creditinvoice": {
            "Identifier": "123",
            "AmountPaid": "50.00",
        }
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    
    result = api_client.credit_invoices.part_payment(Identifier=123, AmountPaid=50.00)
    
    assert result == mock_response


def test_credit_invoice_mark_as_paid(api_client, mocker):
    """Test marking credit invoice as paid."""
    mock_response = {
        "controller": "creditinvoice",
        "action": "mark_as_paid",
        "status": "success",
        "creditinvoice": {
            "Identifier": "123",
            "Status": "paid",
        }
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    
    result = api_client.credit_invoices.mark_as_paid(Identifier=123, PayDate="2025-01-15")
    
    assert result == mock_response


def test_credit_invoice_line_add(api_client, mocker):
    """Test adding lines to credit invoice."""
    mock_response = {
        "controller": "creditinvoice",
        "action": "credit_invoice_line_add",
        "status": "success",
        "creditinvoice": {
            "Identifier": "123",
        }
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    
    lines = [{"Description": "Service", "PriceExcl": 100.00}]
    result = api_client.credit_invoices.credit_invoice_line_add(Identifier=123, CreditInvoiceLines=lines)
    
    assert result == mock_response


def test_credit_invoice_line_delete(api_client, mocker):
    """Test deleting lines from credit invoice."""
    mock_response = {
        "controller": "creditinvoice",
        "action": "credit_invoice_line_delete",
        "status": "success",
        "creditinvoice": {
            "Identifier": "123",
        }
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    
    lines = [{"Identifier": 456}]
    result = api_client.credit_invoices.credit_invoice_line_delete(Identifier=123, CreditInvoiceLines=lines)
    
    assert result == mock_response


def test_credit_invoice_attachment_add(api_client, mocker):
    """Test adding attachment to credit invoice."""
    mock_response = {
        "controller": "creditinvoice",
        "action": "attachment_add",
        "status": "success"
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    
    result = api_client.credit_invoices.attachment_add(
        ReferenceIdentifier=123,
        Filename="receipt.pdf",
        Base64="base64content"
    )
    
    assert result == mock_response


def test_credit_invoice_attachment_delete(api_client, mocker):
    """Test deleting attachment from credit invoice."""
    mock_response = {
        "controller": "creditinvoice",
        "action": "attachment_delete",
        "status": "success"
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    
    result = api_client.credit_invoices.attachment_delete(
        ReferenceIdentifier=123,
        Filename="receipt.pdf"
    )
    
    assert result == mock_response


def test_credit_invoice_attachment_download(api_client, mocker):
    """Test downloading attachment from credit invoice."""
    mock_response = {
        "controller": "creditinvoice",
        "action": "attachment_download",
        "status": "success",
        "Base64": "base64content"
    }
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    
    result = api_client.credit_invoices.attachment_download(
        ReferenceIdentifier=123,
        Filename="receipt.pdf"
    )
    
    assert result == mock_response
