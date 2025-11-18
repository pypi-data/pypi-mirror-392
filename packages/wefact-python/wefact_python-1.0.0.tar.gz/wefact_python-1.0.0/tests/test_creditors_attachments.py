import pytest
from wefact import WeFact


@pytest.fixture
def client():
    return WeFact(api_key="test")


def test_creditor_attachments(client, mocker):
    mock_response = {"status": "success"}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type("R", (), {"status_code": 200, "json": staticmethod(lambda: mock_response)})(),
    )
    assert client.creditors.attachment_add(Identifier="CR1", FileName="x.txt", FileData="<base64>")["status"] == "success"
    assert client.creditors.attachment_delete(Identifier="CR1", AttachmentGuid="A1")["status"] == "success"
    assert client.creditors.attachment_download(Identifier="CR1", AttachmentGuid="A1")["status"] == "success"
