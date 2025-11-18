# tests/test_debtors.py

import pytest
from wefact import WeFact

@pytest.fixture
def client():
    return WeFact(api_key='your_api_key')

def test_list_debtors(client, mocker):
    mock_response = {'debtors': [{'Identifier': 1, 'CompanyName': 'Test Company'}]}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.debtors.list()
    assert response['debtors'][0]['CompanyName'] == 'Test Company'

def test_create_debtor(client, mocker):
    mock_response = {'status': 'success', 'debtor': {'Identifier': 1, 'CompanyName': 'New Company'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.debtors.create(CompanyName='New Company')
    assert response['debtor']['CompanyName'] == 'New Company'

def test_update_debtor(client, mocker):
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.debtors.edit(Identifier=1, CompanyName='Updated Company')
    assert response['status'] == 'success'

def test_show_debtor(client, mocker):
    mock_response = {'debtor': {'Identifier': 1, 'CompanyName': 'Test Company'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.debtors.show(Identifier=1)
    assert response['debtor']['CompanyName'] == 'Test Company'

def test_delete_debtor(client):
    import pytest
    from wefact.exceptions import ClientError

    with pytest.raises(ClientError):
        client.debtors.delete(Identifier=1)