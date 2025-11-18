# /wefact-python/wefact-python/tests/test_products.py

import pytest
from wefact import WeFact

@pytest.fixture
def client():
    return WeFact(api_key='your_api_key')

def test_list_products(client, mocker):
    mock_response = {'products': []}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.products.list()
    assert isinstance(response, dict)
    assert 'products' in response

def test_create_product(client, mocker):
    mock_response = {'status': 'success', 'product': {'Identifier': 'P0001', 'ProductName': 'Test Product'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.products.create(ProductName='Test Product', ProductKeyPhrase='Test Key Phrase', PriceExcl=100)
    assert response['status'] == 'success'
    assert response['product']['ProductName'] == 'Test Product'

def test_update_product(client, mocker):
    mock_response = {'status': 'success', 'product': {'Identifier': 'P0001', 'ProductName': 'Updated Product'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.products.edit(Identifier='P0001', ProductName='Updated Product', ProductKeyPhrase='Updated Key Phrase', PriceExcl=150)
    assert response['status'] == 'success'
    assert response['product']['ProductName'] == 'Updated Product'

def test_show_product(client, mocker):
    mock_response = {'status': 'success', 'product': {'Identifier': 'P0001'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.products.show(Identifier='P0001')
    assert response['status'] == 'success'
    assert response['product']['Identifier'] == 'P0001'

def test_delete_product(client, mocker):
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.products.delete(Identifier='P0001')
    assert response['status'] == 'success'