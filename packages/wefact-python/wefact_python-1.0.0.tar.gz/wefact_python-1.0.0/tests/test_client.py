# tests/test_client.py

import pytest
from wefact import WeFact
from wefact.resources import InvoiceResource

@pytest.fixture
def client():
    return WeFact(api_key='your-api-key')

def test_client_initialization(client):
    assert isinstance(client.invoices, InvoiceResource)