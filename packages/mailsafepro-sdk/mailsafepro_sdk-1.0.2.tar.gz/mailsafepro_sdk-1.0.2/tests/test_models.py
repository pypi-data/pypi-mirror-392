"""
Tests for data models
"""
import pytest
from datetime import datetime

from mailsafepro.models import (
    ValidationResult,
    BatchResult,
    SMTPInfo,
    DNSInfo,
    DNSRecordSPF,
    DNSRecordDKIM,
    DNSRecordDMARC,
    ProviderAnalysis,
    SecurityInfo,
    SpamTrapCheck,
    RoleEmailInfo,
    BreachInfo,
    SuggestedFixes,
    Metadata,
)


class TestValidationResult:
    """Test ValidationResult model"""

    def test_from_dict_complete(self):
        """Test creating ValidationResult from complete dict"""
        data = {
            "email": "test@example.com",
            "valid": True,
            "detail": "Email is valid",
            "processing_time": 0.15,
            "risk_score": 0.1,
            "quality_score": 0.95,
            "validation_tier": "standard",
            "suggested_action": "accept",
            "status": "deliverable",
            "provider_analysis": {"provider": "Gmail", "reputation": 0.9, "fingerprint": "abc123"},
            "smtp": {"checked": True, "mailbox_exists": True},
            "dns_security": {"spf": {"status": "pass"}, "mx_records": ["mx1.example.com"]},
            "security": {"in_breach": False, "breach_count": 0},
            "metadata": {"timestamp": "2025-11-17T20:00:00Z", "validation_id": "val_123", "cache_used": False},
        }

        result = ValidationResult.from_dict(data)

        assert result.email == "test@example.com"
        assert result.valid is True
        assert result.risk_score == 0.1
        assert result.quality_score == 0.95
        assert result.smtp is not None
        assert result.dns_security is not None
        assert result.provider_analysis is not None

    def test_from_dict_minimal(self):
        """Test creating ValidationResult from minimal dict"""
        data = {
            "email": "test@example.com",
            "valid": False,
            "detail": "Invalid email",
            "processing_time": 0.05,
            "risk_score": 0.8,
            "quality_score": 0.2,
            "validation_tier": "basic",
            "suggested_action": "reject",
            "status": "invalid",
            "provider_analysis": {"provider": "unknown", "reputation": 0.5},
            "smtp": {"checked": False},
        }

        result = ValidationResult.from_dict(data)

        assert result.email == "test@example.com"
        assert result.valid is False
        assert result.smtp.checked is False
        assert result.dns_security is None


class TestBatchResult:
    """Test BatchResult model"""

    def test_from_dict(self):
        """Test creating BatchResult from dict"""
        data = {
            "count": 3,
            "valid_count": 2,
            "invalid_count": 1,
            "processing_time": 0.45,
            "average_time": 0.15,
            "results": [
                {
                    "email": "test1@example.com",
                    "valid": True,
                    "detail": "Valid",
                    "processing_time": 0.15,
                    "risk_score": 0.1,
                    "quality_score": 0.9,
                    "validation_tier": "standard",
                    "suggested_action": "accept",
                    "status": "valid",
                    "provider_analysis": {"provider": "Gmail", "reputation": 0.9},
                    "smtp": {"checked": False},
                },
                {
                    "email": "test2@example.com",
                    "valid": True,
                    "detail": "Valid",
                    "processing_time": 0.15,
                    "risk_score": 0.1,
                    "quality_score": 0.9,
                    "validation_tier": "standard",
                    "suggested_action": "accept",
                    "status": "valid",
                    "provider_analysis": {"provider": "Yahoo", "reputation": 0.85},
                    "smtp": {"checked": False},
                },
                {
                    "email": "invalid@test.com",
                    "valid": False,
                    "detail": "Invalid",
                    "processing_time": 0.05,
                    "risk_score": 0.9,
                    "quality_score": 0.1,
                    "validation_tier": "basic",
                    "suggested_action": "reject",
                    "status": "invalid",
                    "provider_analysis": {"provider": "unknown", "reputation": 0.5},
                    "smtp": {"checked": False},
                },
            ],
        }

        result = BatchResult.from_dict(data)

        assert result.count == 3
        assert result.valid_count == 2
        assert result.invalid_count == 1
        assert len(result.results) == 3
        assert all(isinstance(r, ValidationResult) for r in result.results)


class TestSMTPInfo:
    """Test SMTPInfo model"""

    def test_from_dict(self):
        """Test creating SMTPInfo from dict"""
        data = {
            "checked": True,
            "mailbox_exists": True,
            "mx_server": "mx1.example.com",
            "response_time": 0.5,
            "detail": "Mailbox exists",
        }

        smtp = SMTPInfo.from_dict(data)

        assert smtp.checked is True
        assert smtp.mailbox_exists is True
        assert smtp.mx_server == "mx1.example.com"


class TestDNSInfo:
    """Test DNSInfo model"""

    def test_from_dict_complete(self):
        """Test creating DNSInfo from complete dict"""
        data = {
            "mx_records": ["mx1.example.com", "mx2.example.com"],
            "spf": {"status": "pass", "record": "v=spf1 include:_spf.example.com ~all"},
            "dkim": {"status": "pass", "selector": "default"},
            "dmarc": {"status": "pass", "policy": "quarantine"},
        }

        dns = DNSInfo.from_dict(data)

        assert len(dns.mx_records) == 2
        assert isinstance(dns.spf, DNSRecordSPF)
        assert isinstance(dns.dkim, DNSRecordDKIM)
        assert isinstance(dns.dmarc, DNSRecordDMARC)


class TestProviderAnalysis:
    """Test ProviderAnalysis model"""

    def test_from_dict(self):
        """Test creating ProviderAnalysis from dict"""
        data = {"provider": "Gmail", "reputation": 0.95, "fingerprint": "abc123"}

        provider = ProviderAnalysis.from_dict(data)

        assert provider.provider == "Gmail"
        assert provider.reputation == 0.95
        assert provider.fingerprint == "abc123"


class TestSecurityInfo:
    """Test SecurityInfo model"""

    def test_from_dict(self):
        """Test creating SecurityInfo from dict"""
        data = {"in_breach": True, "breach_count": 2, "risk_level": "high", "recent_breaches": ["Breach 1", "Breach 2"]}

        security = SecurityInfo.from_dict(data)

        assert security.in_breach is True
        assert security.breach_count == 2
        assert security.risk_level == "high"
        assert len(security.recent_breaches) == 2


class TestMetadata:
    """Test Metadata model"""

    def test_from_dict(self):
        """Test creating Metadata from dict"""
        data = {
            "timestamp": "2025-11-17T20:00:00Z",
            "validation_id": "val_123",
            "cache_used": False,
            "client_plan": "PREMIUM",
        }

        metadata = Metadata.from_dict(data)

        assert metadata.timestamp == "2025-11-17T20:00:00Z"
        assert metadata.validation_id == "val_123"
        assert metadata.cache_used is False
        assert metadata.client_plan == "PREMIUM"
