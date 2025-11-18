import pytest
from wefact import WeFact


@pytest.fixture
def client():
    return WeFact(api_key='your_api_key')


def test_list_groups(client, mocker):
    mock_response = {'groups': [{'Identifier': 1, 'GroupName': 'Test Group'}]}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.groups.list()
    assert isinstance(response, dict)
    assert 'groups' in response


def test_create_group(client, mocker):
    mock_response = {'status': 'success', 'group': {'Identifier': 'G1', 'GroupName': 'Test Group'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.groups.create(Type='debtor', GroupName='Test Group')
    assert response['status'] == 'success'
    assert response['group']['GroupName'] == 'Test Group'


def test_update_group(client, mocker):
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.groups.edit(Identifier='group_id', GroupName='Updated Group Name')
    assert response['status'] == 'success'


def test_show_group(client, mocker):
    mock_response = {'status': 'success', 'group': {'Identifier': 'group_id', 'GroupName': 'Group'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.groups.show(Identifier='group_id')
    assert response['status'] == 'success'
    assert 'GroupName' in response['group']


def test_delete_group(client, mocker):
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.groups.delete(Identifier='group_id')
    assert response['status'] == 'success'