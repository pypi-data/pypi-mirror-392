import pytest
from wefact import WeFact


@pytest.fixture
def client():
    return WeFact(api_key="test")


def test_transaction_match_ignore(client, mocker):
    mock_response = {"status": "success"}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type("R", (), {"status_code": 200, "json": staticmethod(lambda: mock_response)})(),
    )
    assert client.transactions.match(Identifier="TR1")["status"] == "success"
    assert client.transactions.ignore(Identifier="TR1")["status"] == "success"
