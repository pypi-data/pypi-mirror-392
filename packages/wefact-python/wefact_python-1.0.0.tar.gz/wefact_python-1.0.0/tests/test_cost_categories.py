# /wefact-python/wefact-python/tests/test_cost_categories.py

import pytest
from wefact import WeFact

@pytest.fixture
def client():
    return WeFact(api_key='your_api_key')

def test_list_cost_categories(client, mocker):
    mock_response = {'costcategories': []}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.cost_categories.list()
    assert isinstance(response, dict)
    assert 'costcategories' in response

def test_create_cost_category(client, mocker):
    mock_response = {'status': 'success', 'category': {'Identifier': 'CC1', 'Title': 'New Cost Category'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.cost_categories.create(Title='New Cost Category')
    assert response['status'] == 'success'
    assert response['category']['Title'] == 'New Cost Category'

def test_update_cost_category(client, mocker):
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.cost_categories.edit(Identifier='existing_category_id', Title='Updated Cost Category')
    assert response['status'] == 'success'

def test_show_cost_category(client, mocker):
    mock_response = {'status': 'success', 'category': {'Identifier': 'existing_category_id', 'Title': 'Title'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.cost_categories.show(Identifier='existing_category_id')
    assert 'category' in response

def test_delete_cost_category(client, mocker):
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.cost_categories.delete(Identifier='existing_category_id')
    assert response['status'] == 'success'