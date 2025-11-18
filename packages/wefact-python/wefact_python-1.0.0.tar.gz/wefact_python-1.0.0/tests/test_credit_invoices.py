# tests/test_credit_invoices.py

import pytest
from wefact import WeFact

def test_list_credit_invoices(mocker):
    client = WeFact(api_key='your_api_key')
    mock_response = {'creditinvoices': [
        {'Identifier': 1, 'InvoiceCode': 'CI10001'},
        {'Identifier': 2, 'InvoiceCode': 'CI10002'}
    ]}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.list()
    assert response['creditinvoices'] == mock_response['creditinvoices']

def test_create_credit_invoice(mocker):
    client = WeFact(api_key='your_api_key')
    mock_response = {'status': 'success', 'credit_invoice': {'Identifier': 1, 'InvoiceCode': 'CI10001'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.credit(Identifier=1)
    assert response['status'] == 'success'
    assert response['credit_invoice']['InvoiceCode'] == 'CI10001'

def test_update_credit_invoice(mocker):
    client = WeFact(api_key='your_api_key')
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.edit(Identifier=1, Comment='Updated comment')
    assert response['status'] == 'success'

def test_show_credit_invoice(mocker):
    client = WeFact(api_key='your_api_key')
    mock_response = {'status': 'success', 'credit_invoice': {'Identifier': 1, 'InvoiceCode': 'CI10001'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.show(Identifier=1)
    assert response['credit_invoice']['InvoiceCode'] == 'CI10001'

def test_delete_credit_invoice(mocker):
    client = WeFact(api_key='your_api_key')
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.invoices.delete(Identifier=1)
    assert response['status'] == 'success'

def test_create_credit_invoice_error(mocker):
    client = WeFact(api_key='your_api_key')
    mock_response = {'status': 'error', 'errors': ['Invalid data']}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    import pytest
    from wefact.exceptions import ValidationError

    with pytest.raises(ValidationError) as exc:
        client.invoices.credit(Identifier='')
    assert 'Invalid data' in str(exc.value)