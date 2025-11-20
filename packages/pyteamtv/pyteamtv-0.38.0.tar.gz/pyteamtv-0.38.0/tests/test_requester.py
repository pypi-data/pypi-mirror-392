import pytest
import requests


def test_http_error_includes_request_and_response_details(requests_mock, requester):
    """Test that HTTP errors include request body and response content"""
    requests_mock.post(
        "https://fake-url/endpoint", status_code=400, text="Invalid request data"
    )

    request_body = {"field": "value"}

    with pytest.raises(requests.HTTPError) as exc_info:
        requester.request("POST", "/endpoint", input_=request_body)

    error_message = str(exc_info.value)
    assert "400" in error_message
    assert "POST" in error_message
    assert "https://fake-url/endpoint" in error_message
    assert str(request_body) in error_message
    assert "Invalid request data" in error_message
