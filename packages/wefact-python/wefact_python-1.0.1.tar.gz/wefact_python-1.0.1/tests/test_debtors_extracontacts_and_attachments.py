import pytest
from wefact import WeFact


@pytest.fixture
def client():
    return WeFact(api_key="test")


def test_debtor_extra_client_contacts(client, mocker):
    mock_response = {"status": "success"}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type("R", (), {"status_code": 200, "json": staticmethod(lambda: mock_response)})(),
    )
    assert client.debtors.extra_client_contact_add(Identifier="DB1", Name="Jane")["status"] == "success"
    assert client.debtors.extra_client_contact_edit(Identifier="DB1", ContactIdentifier="C1", Name="Janet")["status"] == "success"
    assert client.debtors.extra_client_contact_delete(Identifier="DB1", ContactIdentifier="C1")["status"] == "success"


def test_debtor_attachments(client, mocker):
    mock_response = {"status": "success"}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type("R", (), {"status_code": 200, "json": staticmethod(lambda: mock_response)})(),
    )
    assert client.debtors.attachment_add(Identifier="DB1", FileName="doc.pdf", FileData="<base64>")["status"] == "success"
    assert client.debtors.attachment_delete(Identifier="DB1", AttachmentGuid="A1")["status"] == "success"
    assert client.debtors.attachment_download(Identifier="DB1", AttachmentGuid="A1")["status"] == "success"
