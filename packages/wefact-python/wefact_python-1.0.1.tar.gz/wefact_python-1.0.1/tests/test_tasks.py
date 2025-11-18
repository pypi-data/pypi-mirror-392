import pytest
from wefact import WeFact


@pytest.fixture
def client():
    return WeFact(api_key="test")


def test_task_change_status(client, mocker):
    mock_response = {"status": "success"}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type("R", (), {"status_code": 200, "json": staticmethod(lambda: mock_response)})(),
    )
    resp = client.tasks.change_status(Identifier="T1", Status="completed")
    assert resp["status"] == "success"


essential_attachment_payload = {
    "Identifier": "T1",
    "FileName": "note.txt",
    "FileData": "<base64>",
}


def test_task_attachments(client, mocker):
    mock_response = {"status": "success"}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type("R", (), {"status_code": 200, "json": staticmethod(lambda: mock_response)})(),
    )
    assert client.tasks.attachment_add(**essential_attachment_payload)["status"] == "success"
    assert client.tasks.attachment_delete(Identifier="T1", AttachmentGuid="A1")["status"] == "success"
    assert client.tasks.attachment_download(Identifier="T1", AttachmentGuid="A1")["status"] == "success"
