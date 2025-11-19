"""
Tests for utility functions
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from mailsafepro.utils import validate_email_format, validate_file_path
from mailsafepro.exceptions import ValidationError


class TestValidateEmailFormat:
    """Test email format validation"""

    def test_valid_emails(self):
        """Test valid email formats"""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.co.uk",
            "user_name@example-domain.com",
            "123@example.com",
            "a@b.co",
        ]

        for email in valid_emails:
            # Should not raise exception
            validate_email_format(email)

    def test_invalid_emails(self):
        """Test invalid email formats"""
        invalid_emails = [
            ("invalid", "Email must contain '@' symbol"),
            ("@example.com", "Invalid email format"),
            ("user@", "Invalid email format"),
            ("user @example.com", "Invalid email format"),
            ("", "Email must be a non-empty string"),
            ("user@@example.com", "Invalid email format"),
        ]

        for email, expected_msg in invalid_emails:
            with pytest.raises(ValidationError, match=expected_msg):
                validate_email_format(email)

    def test_none_email(self):
        """Test None as email"""
        with pytest.raises(ValidationError, match="Email must be a non-empty string"):
            validate_email_format(None)


class TestValidateFilePath:
    """Test file path validation"""

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.stat")
    def test_valid_txt_file(self, mock_stat, mock_is_file, mock_exists):
        """Test valid TXT file"""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_stat.return_value = Mock(st_size=1024)  # 1KB

        result = validate_file_path("emails.txt")
        assert result.name == "emails.txt"

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.stat")
    def test_valid_csv_file(self, mock_stat, mock_is_file, mock_exists):
        """Test valid CSV file"""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_stat.return_value = Mock(st_size=1024)  # 1KB

        result = validate_file_path("data.csv")
        assert result.name == "data.csv"

    @patch("pathlib.Path.exists")
    def test_file_not_found(self, mock_exists):
        """Test file doesn't exist"""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError, match="File not found"):
            validate_file_path("nonexistent.txt")

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    def test_invalid_file_extension(self, mock_is_file, mock_exists):
        """Test invalid file extension"""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        with pytest.raises(ValidationError, match="Unsupported file format"):
            validate_file_path("file.pdf")

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.stat")
    def test_file_too_large(self, mock_stat, mock_is_file, mock_exists):
        """Test file exceeds size limit"""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_stat.return_value = Mock(st_size=10 * 1024 * 1024)  # 10MB

        with pytest.raises(ValidationError, match="File too large"):
            validate_file_path("huge.csv")

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    def test_path_is_directory(self, mock_is_file, mock_exists):
        """Test path is directory not file"""
        mock_exists.return_value = True
        mock_is_file.return_value = False

        with pytest.raises(ValidationError, match="Path is not a file"):
            validate_file_path("/some/directory")
