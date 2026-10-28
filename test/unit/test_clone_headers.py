"""Regression coverage for explicit custom-header overrides when cloning."""

import pytest
import requests

from dropbox import Dropbox, DropboxTeam
from dropbox.dropbox_client import USER_AUTH


@pytest.mark.parametrize("client_class", [Dropbox, DropboxTeam])
@pytest.mark.parametrize("override", [None, {}, {"X-New": "new-value"}])
def test_clone_respects_explicit_headers(client_class, override, mocker):
    original_headers = {"X-Original": "original-value"}
    with requests.Session() as session:
        response = requests.Response()
        response.status_code = 200
        response.headers["content-type"] = "application/json"
        response._content = b"{}"
        post = mocker.patch.object(session, "post", return_value=response)
        client = client_class("test-token", session=session, headers=original_headers)
        cloned = client.clone(headers=override)
        cloned.request_json_string("api", "test/route", "rpc", "{}", USER_AUTH, None)

    expected = original_headers if override is None else override
    sent_headers = post.call_args.kwargs["headers"]
    assert {key: value for key, value in sent_headers.items() if key.startswith("X-")} == expected
    assert original_headers == {"X-Original": "original-value"}
    assert client._headers == original_headers
