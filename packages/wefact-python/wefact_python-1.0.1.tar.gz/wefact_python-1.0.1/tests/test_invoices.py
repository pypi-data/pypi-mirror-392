# /wefact-python/wefact-python/tests/test_invoices.py

import pytest
from wefact import WeFact

@pytest.fixture
def client():
    return WeFact(api_key='your_api_key')

def test_list_invoices(client, mocker):
    mock_response = {'invoices': []}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.list()
    assert isinstance(response, dict)
    assert 'invoices' in response

def test_create_invoice(client, mocker):
    mock_response = {'status': 'success', 'invoice': {'Identifier': 'INV10000'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.create(
        DebtorCode='DB10000',
        InvoiceLines=[{'Number': 1, 'ProductCode': 'P0001', 'Description': 'Test Product', 'PriceExcl': 100}],
    )
    assert response['status'] == 'success'
    assert 'invoice' in response

def test_show_invoice(client, mocker):
    invoice_id = 'INV10000'
    mock_response = {'status': 'success', 'invoice': {'Identifier': invoice_id}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.show(Identifier=invoice_id)
    assert response['status'] == 'success'
    assert response['invoice']['Identifier'] == invoice_id

def test_update_invoice(client, mocker):
    invoice_id = 'INV10000'
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.edit(
        Identifier=invoice_id,
        InvoiceLines=[{'Number': 1, 'ProductCode': 'P0001', 'Description': 'Updated Product', 'PriceExcl': 150}],
    )
    assert response['status'] == 'success'

def test_delete_invoice(client, mocker):
    invoice_id = 'INV10000'
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.delete(Identifier=invoice_id)
    assert response['status'] == 'success'


def test_invoice_credit(client, mocker):
    """Test creating a credit invoice."""
    mock_response = {'status': 'success', 'invoice': {'Identifier': 'INV10001'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.credit(Identifier='INV10000')
    assert response['status'] == 'success'


def test_invoice_part_payment(client, mocker):
    """Test recording partial payment."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.part_payment(Identifier='INV10000', AmountPaid=50.00)
    assert response['status'] == 'success'


def test_invoice_mark_as_paid(client, mocker):
    """Test marking invoice as paid."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.mark_as_paid(Identifier='INV10000')
    assert response['status'] == 'success'


def test_invoice_mark_as_unpaid(client, mocker):
    """Test marking invoice as unpaid."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.mark_as_unpaid(Identifier='INV10000')
    assert response['status'] == 'success'


def test_invoice_send_by_email(client, mocker):
    """Test sending invoice by email."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.send_by_email(Identifier='INV10000')
    assert response['status'] == 'success'


def test_invoice_send_reminder_by_email(client, mocker):
    """Test sending reminder email."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.send_reminder_by_email(Identifier='INV10000')
    assert response['status'] == 'success'


def test_invoice_send_summation_by_email(client, mocker):
    """Test sending summation email."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.send_summation_by_email(Identifier='INV10000')
    assert response['status'] == 'success'


def test_invoice_download(client, mocker):
    """Test downloading invoice PDF."""
    mock_response = {'status': 'success', 'invoice': {'Base64': 'base64data'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.download(Identifier='INV10000')
    assert response['status'] == 'success'


def test_invoice_block(client, mocker):
    """Test blocking invoice."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.block(Identifier='INV10000')
    assert response['status'] == 'success'


def test_invoice_unblock(client, mocker):
    """Test unblocking invoice."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.unblock(Identifier='INV10000')
    assert response['status'] == 'success'


def test_invoice_schedule(client, mocker):
    """Test scheduling invoice."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.schedule(Identifier='INV10000', ScheduledAt='2025-12-31 20:00:00')
    assert response['status'] == 'success'


def test_invoice_cancel_schedule(client, mocker):
    """Test canceling invoice schedule."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.cancel_schedule(Identifier='INV10000')
    assert response['status'] == 'success'


def test_invoice_payment_process_pause(client, mocker):
    """Test pausing payment process."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.payment_process_pause(Identifier='INV10000')
    assert response['status'] == 'success'


def test_invoice_payment_process_reactivate(client, mocker):
    """Test reactivating payment process."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.payment_process_reactivate(Identifier='INV10000')
    assert response['status'] == 'success'


def test_invoice_sort_lines(client, mocker):
    """Test sorting invoice lines."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.sort_lines(Identifier='INV10000', InvoiceLines=[{'Identifier': 1}])
    assert response['status'] == 'success'


def test_invoice_line_add(client, mocker):
    """Test adding invoice lines."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.invoice_line_add(Identifier='INV10000', InvoiceLines=[{}])
    assert response['status'] == 'success'


def test_invoice_line_delete(client, mocker):
    """Test deleting invoice lines."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.invoice_line_delete(Identifier='INV10000', InvoiceLines=[{'Identifier': 1}])
    assert response['status'] == 'success'


def test_invoice_attachment_add(client, mocker):
    """Test adding attachment to invoice."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.attachment_add(ReferenceIdentifier='INV10000', Filename='test.pdf', Base64='base64data')
    assert response['status'] == 'success'


def test_invoice_attachment_delete(client, mocker):
    """Test deleting attachment from invoice."""
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.attachment_delete(ReferenceIdentifier='INV10000', Filename='test.pdf')
    assert response['status'] == 'success'


def test_invoice_attachment_download(client, mocker):
    """Test downloading attachment from invoice."""
    mock_response = {'status': 'success', 'Base64': 'base64data'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.attachment_download(ReferenceIdentifier='INV10000', Filename='test.pdf')
    assert response['status'] == 'success'
