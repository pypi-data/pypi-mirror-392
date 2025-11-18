"""Tests for exception handling."""

import pytest
from wefact.exceptions import (
    WeFactAPIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    ServerError,
    ClientError,
    from_response,
    raise_for_response,
    raise_for_wefact_payload,
)


class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, status_code, json_data=None, text=None, reason=None, headers=None):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text or ""
        self.reason = reason
        self.headers = headers or {}
    
    def json(self):
        if self._json_data is None:
            raise ValueError("No JSON data")
        return self._json_data


class TestWeFactAPIError:
    """Test WeFactAPIError base exception."""
    
    def test_basic_error(self):
        """Test basic error creation."""
        error = WeFactAPIError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.status is None
        assert error.code is None
    
    def test_error_with_status(self):
        """Test error with HTTP status code."""
        error = WeFactAPIError("Test error", status=404)
        assert "404" in str(error)
        assert error.status == 404
    
    def test_error_with_code(self):
        """Test error with API error code."""
        error = WeFactAPIError("Test error", code="ERR001")
        assert "ERR001" in str(error)
        assert error.code == "ERR001"
    
    def test_error_with_request_id(self):
        """Test error with request ID."""
        error = WeFactAPIError("Test error", request_id="abc-123")
        assert "request_id=abc-123" in str(error)
        assert error.request_id == "abc-123"
    
    def test_error_with_details(self):
        """Test error with additional details."""
        details = {"field": "invalid value"}
        error = WeFactAPIError("Test error", details=details)
        assert error.details == details


class TestExceptionSubclasses:
    """Test exception subclasses."""
    
    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Unauthorized", status=401)
        assert isinstance(error, WeFactAPIError)
        assert error.status == 401
    
    def test_not_found_error(self):
        """Test NotFoundError."""
        error = NotFoundError("Resource not found", status=404)
        assert isinstance(error, WeFactAPIError)
        assert error.status == 404
    
    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid data", status=422)
        assert isinstance(error, WeFactAPIError)
        assert error.status == 422
    
    def test_server_error(self):
        """Test ServerError."""
        error = ServerError("Internal error", status=500)
        assert isinstance(error, WeFactAPIError)
        assert error.status == 500
    
    def test_client_error(self):
        """Test ClientError."""
        error = ClientError("Bad request", status=400)
        assert isinstance(error, WeFactAPIError)
        assert error.status == 400


class TestFromResponse:
    """Test from_response function."""
    
    def test_from_response_401(self):
        """Test creating exception from 401 response."""
        response = MockResponse(401, {"message": "Unauthorized"})
        error = from_response(response)
        assert isinstance(error, AuthenticationError)
        assert error.status == 401
    
    def test_from_response_403(self):
        """Test creating exception from 403 response."""
        response = MockResponse(403, {"message": "Forbidden"})
        error = from_response(response)
        assert isinstance(error, AuthenticationError)
        assert error.status == 403
    
    def test_from_response_404(self):
        """Test creating exception from 404 response."""
        response = MockResponse(404, {"message": "Not found"})
        error = from_response(response)
        assert isinstance(error, NotFoundError)
        assert error.status == 404
    
    def test_from_response_400(self):
        """Test creating exception from 400 response."""
        response = MockResponse(400, {"message": "Bad request"})
        error = from_response(response)
        assert isinstance(error, ValidationError)
        assert error.status == 400
    
    def test_from_response_422(self):
        """Test creating exception from 422 response."""
        response = MockResponse(422, {"message": "Validation failed"})
        error = from_response(response)
        assert isinstance(error, ValidationError)
        assert error.status == 422
    
    def test_from_response_500(self):
        """Test creating exception from 500 response."""
        response = MockResponse(500, {"message": "Server error"})
        error = from_response(response)
        assert isinstance(error, ServerError)
        assert error.status == 500
    
    def test_from_response_with_errors_array(self):
        """Test creating exception from response with errors array."""
        response = MockResponse(400, {"errors": ["Error 1", "Error 2"]})
        error = from_response(response)
        assert "Error 1; Error 2" in error.message
    
    def test_from_response_with_error_code(self):
        """Test creating exception from response with error code."""
        response = MockResponse(400, {"code": "ERR001", "message": "Error"})
        error = from_response(response)
        assert error.code == "ERR001"
    
    def test_from_response_with_text_body(self):
        """Test creating exception from response with text body."""
        response = MockResponse(500, text="Server error occurred")
        error = from_response(response)
        assert "Server error occurred" in error.message
    
    def test_from_response_with_request_id_header(self):
        """Test creating exception from response with request ID header."""
        response = MockResponse(500, {"message": "Error"}, headers={"X-Request-Id": "req-123"})
        error = from_response(response)
        assert error.request_id == "req-123"


class TestRaiseForResponse:
    """Test raise_for_response function."""
    
    def test_raise_for_response_success(self):
        """Test that 2xx responses don't raise."""
        response = MockResponse(200, {"status": "success"})
        # Should not raise
        raise_for_response(response)
    
    def test_raise_for_response_201(self):
        """Test that 201 responses don't raise."""
        response = MockResponse(201, {"status": "created"})
        # Should not raise
        raise_for_response(response)
    
    def test_raise_for_response_400(self):
        """Test that 400 response raises."""
        response = MockResponse(400, {"message": "Bad request"})
        with pytest.raises(ValidationError):
            raise_for_response(response)
    
    def test_raise_for_response_500(self):
        """Test that 500 response raises."""
        response = MockResponse(500, {"message": "Server error"})
        with pytest.raises(ServerError):
            raise_for_response(response)


class TestRaiseForWeFactPayload:
    """Test raise_for_wefact_payload function."""
    
    def test_raise_for_wefact_payload_success(self):
        """Test that success status doesn't raise."""
        response = MockResponse(200, {"status": "success", "data": {}})
        # Should not raise
        raise_for_wefact_payload(response)
    
    def test_raise_for_wefact_payload_error(self):
        """Test that error status raises."""
        response = MockResponse(200, {"status": "error", "errors": ["Validation failed"]})
        with pytest.raises(ValidationError) as exc_info:
            raise_for_wefact_payload(response)
        assert "Validation failed" in str(exc_info.value)
    
    def test_raise_for_wefact_payload_error_with_message(self):
        """Test error payload with message field."""
        response = MockResponse(200, {"status": "error", "message": "Custom error"})
        with pytest.raises(ValidationError) as exc_info:
            raise_for_wefact_payload(response)
        assert "Custom error" in str(exc_info.value)
    
    def test_raise_for_wefact_payload_server_error(self):
        """Test that 500 status creates ServerError."""
        response = MockResponse(500, {"status": "error", "message": "Internal error"})
        with pytest.raises(ServerError):
            raise_for_wefact_payload(response)
    
    def test_raise_for_wefact_payload_auth_error(self):
        """Test that 401 status creates AuthenticationError."""
        response = MockResponse(401, {"status": "error", "message": "Unauthorized"})
        with pytest.raises(AuthenticationError):
            raise_for_wefact_payload(response)
    
    def test_raise_for_wefact_payload_not_found(self):
        """Test that 404 status creates NotFoundError."""
        response = MockResponse(404, {"status": "error", "message": "Not found"})
        with pytest.raises(NotFoundError):
            raise_for_wefact_payload(response)
    
    def test_raise_for_wefact_payload_non_json(self):
        """Test handling non-JSON response."""
        response = MockResponse(400, text="Bad request")
        with pytest.raises(WeFactAPIError):
            raise_for_wefact_payload(response)
    
    def test_raise_for_wefact_payload_with_data_param(self):
        """Test passing data directly instead of response.json()."""
        response = MockResponse(200)
        data = {"status": "error", "message": "Custom error"}
        with pytest.raises(ValidationError) as exc_info:
            raise_for_wefact_payload(response, data)
        assert "Custom error" in str(exc_info.value)
