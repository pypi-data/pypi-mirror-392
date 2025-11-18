import pytest
from wefact import WeFact


@pytest.fixture
def client():
    return WeFact(api_key="test")


def test_list_quotes(client, mocker):
    mock_response = {"pricequotes": []}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type("R", (), {"status_code": 200, "json": staticmethod(lambda: mock_response)})(),
    )
    resp = client.quotes.list()
    assert isinstance(resp, dict)
    assert "pricequotes" in resp


def test_create_quote(client, mocker):
    mock_response = {"status": "success", "pricequote": {"Identifier": "Q0001"}}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type("R", (), {"status_code": 200, "json": staticmethod(lambda: mock_response)})(),
    )
    resp = client.quotes.create(DebtorCode="DB10000", PriceQuoteLines=[{"Description": "Setup", "PriceExcl": 50}])
    assert resp["status"] == "success"
    assert "pricequote" in resp


def test_accept_quote(client, mocker):
    mock_response = {"status": "success"}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type("R", (), {"status_code": 200, "json": staticmethod(lambda: mock_response)})(),
    )
    resp = client.quotes.accept(Identifier="Q0001")
    assert resp["status"] == "success"


def test_quote_attachments(client, mocker):
    mock_response = {"status": "success"}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type("R", (), {"status_code": 200, "json": staticmethod(lambda: mock_response)})(),
    )
    assert client.quotes.attachment_add(Identifier="Q0001", FileName="terms.pdf", FileData="<base64>")["status"] == "success"
    assert client.quotes.attachment_delete(Identifier="Q0001", AttachmentGuid="ATT-1")["status"] == "success"
    assert client.quotes.attachment_download(Identifier="Q0001", AttachmentGuid="ATT-1")["status"] == "success"
