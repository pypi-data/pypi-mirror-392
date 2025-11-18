import pytest
from wefact import WeFact


@pytest.fixture
def client():
    return WeFact(api_key="test")


def test_list_interactions(client, mocker):
    mock_response = {"interactions": []}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type(
            "R",
            (),
            {
                "status_code": 200,
                "json": staticmethod(lambda: mock_response),
            },
        )(),
    )
    resp = client.interactions.list()
    assert isinstance(resp, dict)
    assert "interactions" in resp


def test_add_interaction(client, mocker):
    mock_response = {"status": "success", "interaction": {"Identifier": "I1"}}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type(
            "R",
            (),
            {
                "status_code": 200,
                "json": staticmethod(lambda: mock_response),
            },
        )(),
    )
    resp = client.interactions.create(Subject="Test", DebtorCode="DB10000")
    assert resp["status"] == "success"
    assert "interaction" in resp


def test_edit_interaction(client, mocker):
    mock_response = {"status": "success"}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type(
            "R",
            (),
            {
                "status_code": 200,
                "json": staticmethod(lambda: mock_response),
            },
        )(),
    )
    resp = client.interactions.edit(Identifier="I1", Subject="Updated")
    assert resp["status"] == "success"


def test_show_interaction(client, mocker):
    mock_response = {"status": "success", "interaction": {"Identifier": "I1"}}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type(
            "R",
            (),
            {
                "status_code": 200,
                "json": staticmethod(lambda: mock_response),
            },
        )(),
    )
    resp = client.interactions.show(Identifier="I1")
    assert resp["status"] == "success"
    assert resp["interaction"]["Identifier"] == "I1"


def test_attachment_actions(client, mocker):
    mock_response = {"status": "success"}
    mocker.patch(
        "wefact.request.requests.post",
        return_value=type(
            "R",
            (),
            {
                "status_code": 200,
                "json": staticmethod(lambda: mock_response),
            },
        )(),
    )
    assert client.interactions.attachment_add(Identifier="I1", FileName="x.txt")[
        "status"
    ] == "success"
    assert client.interactions.attachment_delete(Identifier="I1", AttachmentGuid="A1")[
        "status"
    ] == "success"
    assert client.interactions.attachment_download(Identifier="I1", AttachmentGuid="A1")[
        "status"
    ] == "success"
