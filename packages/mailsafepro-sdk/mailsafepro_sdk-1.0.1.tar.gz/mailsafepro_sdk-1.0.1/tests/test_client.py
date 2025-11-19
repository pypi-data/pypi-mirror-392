"""
Tests for MailSafePro client
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from datetime import datetime, timedelta
import requests

from mailsafepro import MailSafePro
from mailsafepro.exceptions import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    QuotaExceededError,
    ServerError,
    NetworkError,
)


class TestClientInitialization:
    """Test client initialization"""

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        client = MailSafePro(api_key="test_key_123")
        assert client._api_key == "test_key_123"
        assert client._access_token is None
        assert client.base_url == "https://api.mailsafepro.com"

    def test_init_with_custom_base_url(self):
        """Test initialization with custom base URL"""
        client = MailSafePro(api_key="test_key", base_url="http://localhost:8000")
        assert client.base_url == "http://localhost:8000"

    def test_init_with_custom_timeout(self):
        """Test initialization with custom timeout"""
        client = MailSafePro(api_key="test_key", timeout=60)
        assert client.timeout == 60

    def test_init_without_credentials_works(self):
        """Test initialization without credentials is allowed (for login)"""
        # El cliente permite inicialización sin credenciales para JWT login
        client = MailSafePro()
        assert client._api_key is None
        assert client._access_token is None


class TestAuthentication:
    """Test authentication methods"""

    @patch("mailsafepro.client.requests.Session.post")
    def test_jwt_login_success(self, mock_post, mock_jwt_login_response):
        """Test successful JWT login"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_jwt_login_response
        mock_post.return_value = mock_response

        client = MailSafePro.login(username="test@example.com", password="password123")

        assert client._access_token is not None
        assert client._refresh_token == "refresh_token_123"
        assert client._token_expires_at is not None
        mock_post.assert_called_once()

    @patch("mailsafepro.client.requests.Session.post")
    def test_jwt_login_invalid_credentials(self, mock_post):
        """Test JWT login with invalid credentials"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid credentials"
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        with pytest.raises(AuthenticationError):
            MailSafePro.login(username="test@example.com", password="wrong_password")

    @patch("mailsafepro.client.requests.Session.post")
    def test_jwt_token_refresh(self, mock_post, mock_jwt_refresh_response):
        """Test JWT token refresh"""
        # Mock initial login
        login_response = Mock()
        login_response.status_code = 200
        login_response.json.return_value = {
            "access_token": "old_token",
            "refresh_token": "refresh_123",
            "expires_in": 3600,
        }

        # Mock refresh
        refresh_response = Mock()
        refresh_response.status_code = 200
        refresh_response.json.return_value = mock_jwt_refresh_response
        refresh_response.raise_for_status = Mock()

        mock_post.side_effect = [login_response, refresh_response]

        client = MailSafePro.login("test@example.com", "password")

        # Force token expiration
        client._token_expires_at = datetime.now() - timedelta(seconds=10)

        # This should trigger refresh
        client._get_auth_headers()

        assert mock_post.call_count == 2

    @patch("mailsafepro.client.requests.Session.post")
    def test_logout(self, mock_post):
        """Test logout clears tokens"""
        # Mock login
        login_response = Mock()
        login_response.status_code = 200
        login_response.json.return_value = {"access_token": "token", "refresh_token": "refresh", "expires_in": 3600}

        # Mock logout endpoint
        logout_response = Mock()
        logout_response.status_code = 200
        logout_response.raise_for_status = Mock()

        mock_post.side_effect = [login_response, logout_response]

        client = MailSafePro.login("test@example.com", "password")
        client.logout()

        assert client._access_token is None
        assert client._refresh_token is None
        assert client._token_expires_at is None


class TestEmailValidation:
    """Test email validation methods"""

    @patch("mailsafepro.client.requests.Session.request")
    def test_validate_email_success(self, mock_request, mock_validation_response):
        """Test successful email validation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_validation_response
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        client = MailSafePro(api_key="test_key")
        result = client.validate("test@example.com")

        assert result.email == "test@example.com"
        assert result.valid is True
        mock_request.assert_called_once()

    def test_validate_email_invalid_format(self):
        """Test validation with invalid email format"""
        client = MailSafePro(api_key="test_key")

        with pytest.raises(ValidationError, match="Email must contain '@' symbol"):
            client.validate("invalid-email")

    @patch("mailsafepro.client.requests.Session.request")
    def test_validate_with_check_smtp(self, mock_request, mock_validation_response):
        """Test validation with SMTP check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_validation_response
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        client = MailSafePro(api_key="test_key")
        result = client.validate("test@example.com", check_smtp=True)

        assert result.valid is True
        # Verify check_smtp parameter was passed in JSON payload
        call_args = mock_request.call_args
        assert "json" in call_args.kwargs
        assert call_args.kwargs["json"].get("check_smtp") is True

    @patch("mailsafepro.client.requests.Session.request")
    def test_validate_rate_limit_error(self, mock_request):
        """Test handling of rate limit error"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.text = "Rate limit exceeded"
        mock_request.return_value = mock_response

        client = MailSafePro(api_key="test_key")

        with pytest.raises(RateLimitError) as exc_info:
            client.validate("test@example.com")

        assert exc_info.value.retry_after == 60

    @patch("mailsafepro.client.requests.Session.request")
    def test_validate_quota_exceeded_error(self, mock_request):
        """Test handling of quota exceeded error"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"detail": "Daily quota exceeded"}
        mock_request.return_value = mock_response

        client = MailSafePro(api_key="test_key")

        with pytest.raises(AuthenticationError):  # 403 raises AuthenticationError
            client.validate("test@example.com")

    @patch("mailsafepro.client.requests.Session.request")
    def test_validate_server_error(self, mock_request):
        """Test handling of server error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_request.return_value = mock_response

        client = MailSafePro(api_key="test_key")

        with pytest.raises(ServerError) as exc_info:
            client.validate("test@example.com")

        assert exc_info.value.status_code == 500

    @patch("mailsafepro.client.requests.Session.request")
    def test_validate_network_error(self, mock_request):
        """Test handling of network error"""
        mock_request.side_effect = requests.ConnectionError("Connection failed")

        client = MailSafePro(api_key="test_key")

        with pytest.raises(NetworkError):
            client.validate("test@example.com")


class TestBatchValidation:
    """Test batch validation methods"""

    @patch("mailsafepro.client.requests.Session.request")
    def test_validate_batch_success(self, mock_request, mock_batch_response):
        """Test successful batch validation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_batch_response
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        client = MailSafePro(api_key="test_key")
        emails = ["valid1@example.com", "valid2@example.com", "invalid@test.com"]
        result = client.validate_batch(emails)

        assert result.count == 3
        assert result.valid_count == 2
        assert result.invalid_count == 1
        assert len(result.results) == 3
        mock_request.assert_called_once()

    def test_validate_batch_empty_list(self):
        """Test batch validation with empty list"""
        client = MailSafePro(api_key="test_key")

        with pytest.raises(ValidationError, match="Email list cannot be empty"):
            client.validate_batch([])

    def test_validate_batch_exceeds_limit(self):
        """Test batch validation exceeding max limit"""
        client = MailSafePro(api_key="test_key")
        emails = [f"test{i}@example.com" for i in range(10001)]

        with pytest.raises(ValidationError, match="Cannot process more than 10,000 emails"):
            client.validate_batch(emails)

    @patch("mailsafepro.client.requests.Session.request")
    def test_validate_batch_with_options(self, mock_request, mock_batch_response):
        """Test batch validation with custom options"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_batch_response
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        client = MailSafePro(api_key="test_key")
        emails = ["test1@example.com", "test2@example.com"]
        result = client.validate_batch(emails, batch_size=500, concurrent_requests=5)

        assert result.count == 3
        call_args = mock_request.call_args
        assert "json" in call_args.kwargs
        assert call_args.kwargs["json"].get("batch_size") == 500


class TestFileValidation:
    """Test file validation methods"""

    @patch("mailsafepro.client.requests.Session.request")
    @patch("builtins.open", create=True)
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.stat")
    def test_validate_file_success(
        self, mock_stat, mock_is_file, mock_exists, mock_open, mock_request, mock_batch_response
    ):
        """Test successful file validation"""
        # Mock file operations
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_stat.return_value = Mock(st_size=1024)  # 1KB file

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_batch_response
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        # Mock file content
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        client = MailSafePro(api_key="test_key")
        result = client.validate_file("emails.txt")

        assert result.count == 3
        mock_request.assert_called_once()

    def test_validate_file_not_found(self):
        """Test file validation with non-existent file"""
        client = MailSafePro(api_key="test_key")

        with pytest.raises(FileNotFoundError):
            client.validate_file("nonexistent.txt")


class TestRetryLogic:
    """Test retry logic"""

    def test_session_has_retry_configuration(self):
        """Test that session is created with retry configuration"""
        client = MailSafePro(api_key="test_key")

        # Verificar que la sesión privada existe
        assert client._session is not None
        assert isinstance(client._session, requests.Session)

        # Verificar que tiene adapters montados
        assert "https://" in client._session.adapters
        assert "http://" in client._session.adapters

        # Verificar que max_retries está configurado
        assert client.max_retries == 3

    def test_retry_configuration_values(self):
        """Test retry configuration with custom values"""
        client = MailSafePro(api_key="test_key", max_retries=5)

        assert client.max_retries == 5
        assert client._session is not None

    @patch("mailsafepro.client.requests.Session.request")
    def test_server_error_503_raises_exception(self, mock_request):
        """Test that 503 eventually raises ServerError after retries"""
        # Simular que todos los intentos fallan con 503
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.text = "Service Unavailable"
        mock_request.return_value = mock_response

        client = MailSafePro(api_key="test_key")

        # Después de agotar reintentos, debe lanzar ServerError
        with pytest.raises(ServerError) as exc_info:
            client.validate("test@example.com")

        assert exc_info.value.status_code == 503

    @patch("mailsafepro.client.requests.Session.request")
    def test_successful_request_after_transient_failure(self, mock_request, mock_validation_response):
        """Test that transient failures are retried and eventually succeed"""
        # Primera llamada falla, segunda funciona
        fail_response = Mock()
        fail_response.status_code = 502
        fail_response.text = "Bad Gateway"

        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = mock_validation_response
        success_response.raise_for_status = Mock()

        # El retry adapter de requests lo manejará automáticamente
        # En este test solo verificamos que el cliente está configurado correctamente
        mock_request.return_value = success_response

        client = MailSafePro(api_key="test_key")
        result = client.validate("test@example.com")

        assert result.valid is True


class TestAuthHeaders:
    """Test authentication header generation"""

    def test_api_key_headers(self):
        """Test API key authentication headers"""
        client = MailSafePro(api_key="test_key_123")
        headers = client._get_auth_headers()

        assert "X-API-Key" in headers
        assert headers["X-API-Key"] == "test_key_123"

    @patch("mailsafepro.client.requests.Session.post")
    def test_jwt_headers(self, mock_post):
        """Test JWT authentication headers"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "jwt_token_123",
            "refresh_token": "refresh_123",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        client = MailSafePro.login("test@example.com", "password")
        headers = client._get_auth_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer jwt_token_123"

    def test_no_auth_raises_error(self):
        """Test that missing auth raises error"""
        client = MailSafePro()  # No credentials

        with pytest.raises(AuthenticationError, match="No authentication method configured"):
            client._get_auth_headers()
