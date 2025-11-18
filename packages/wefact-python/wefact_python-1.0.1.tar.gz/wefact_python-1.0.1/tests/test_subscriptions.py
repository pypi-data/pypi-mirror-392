import pytest
from wefact import WeFact


@pytest.fixture
def client():
    return WeFact(api_key='your_api_key')


def test_list_subscriptions(client, mocker):
    mock_response = {'subscriptions': []}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.subscriptions.list()
    assert isinstance(response, dict)
    assert 'subscriptions' in response


def test_create_subscription(client, mocker):
    mock_response = {'status': 'success', 'subscription': {'Identifier': 'SUB10000'}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.subscriptions.create(DebtorCode='DB10000', ProductCode='P0001')
    assert response['status'] == 'success'
    assert 'subscription' in response


def test_update_subscription(client, mocker):
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.subscriptions.edit(
        Identifier='SUB10000',
        Description='Updated Subscription',
        PriceExcl=120,
        Periodic='month',
        TerminateAfter=6,
    )
    assert response['status'] == 'success'


def test_show_subscription(client, mocker):
    subscription_id = 'SUB10000'
    mock_response = {'status': 'success', 'subscription': {'Identifier': subscription_id}}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.subscriptions.show(Identifier=subscription_id)
    assert response['status'] == 'success'
    assert response['subscription']['Identifier'] == subscription_id


def test_terminate_subscription(client, mocker):
    mock_response = {'status': 'success'}
    mocker.patch('wefact.request.requests.post', return_value=type('R', (), {
        'status_code': 200,
        'json': staticmethod(lambda: mock_response)
    })())
    response = client.subscriptions.terminate(Identifier='SUB10000')
    assert response['status'] == 'success'