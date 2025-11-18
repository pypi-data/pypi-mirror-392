# /wefact-python/wefact-python/tests/test_creditors.py

import pytest
from wefact import WeFact

@pytest.fixture
def client():
    return WeFact(api_key='your_api_key')

def test_list_creditors(client, mocker):
    mock_response = {'creditors': [{'Identifier': 1, 'CompanyName': 'Test Company'}]}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.creditors.list()
    assert response['creditors'][0]['CompanyName'] == 'Test Company'

def test_create_creditor(client, mocker):
    mock_response = {'status': 'success', 'company': {'Identifier': 1, 'CompanyName': 'New Company'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.creditors.create(CompanyName='New Company')
    assert response['company']['CompanyName'] == 'New Company'

def test_update_creditor(client, mocker):
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.creditors.edit(Identifier=1, CompanyName='Updated Company')
    assert response['status'] == 'success'

def test_show_creditor(client, mocker):
    mock_response = {'company': {'Identifier': 1, 'CompanyName': 'Test Company'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.creditors.show(Identifier=1)
    assert response['company']['CompanyName'] == 'Test Company'

def test_delete_creditor(client, mocker):
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.creditors.delete(Identifier=1)
    assert response['status'] == 'success'