"""
Test configuration and fixtures for cad-ftps-client tests
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile


@pytest.fixture
def mock_certificates(tmp_path):
    """Create temporary certificate files for testing"""
    cert_files = {}
    
    for cert_type in ["client-cert", "client-key", "ca-cert"]:
        cert_file = tmp_path / f"{cert_type}.pem"
        # Write valid-looking certificate content to avoid SSL validation issues in tests
        if cert_type == "ca-cert":
            cert_content = """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKoK/heBjcOuMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAkZSMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMjQxMTEzMDAwMDAwWhcNMjUxMTEzMDAwMDAwWjBF
MQswCQYDVQQGEwJGUjETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEAv4WhZH9HT7cMKiEYfWEBrkVWNDECHQhaDNL6Dw4yJ8TqYIRDH0sRF0o
-----END CERTIFICATE-----"""
        elif cert_type == "client-cert":
            cert_content = """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKoK/heBjcOuMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAkZSMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMjQxMTEzMDAwMDAwWhcNMjUxMTEzMDAwMDAwWjBF
MQswCQYDVQQGEwJGUjETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEAv4WhZH9HT7cMKiEYfWEBrkVWNDECHQhaDNL6Dw4yJ8TqYIRDH0sRF0o
-----END CERTIFICATE-----"""
        else:  # client-key
            cert_content = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC/haFkf0dPtwwq
IRh9YQGuRVY0MQIdCFoM0voPDjInxOpghEMfSxEXSj29J1FTVw5S4TpMGXVHD2l8
0mwhVJ/DQP2NV3B4VWQy4J7KcfY+ztlpN4D7rKuOJEXwvhHvQI5x7cEaL1Mq2X8e
RrQI5x7cEaL1Mq2X8eRrQI5x7cEaL1Mq2X8eRrQI5x7cEaL1Mq2X8eRrQI5x7cEa
-----END PRIVATE KEY-----"""
        
        cert_file.write_text(cert_content)
        cert_files[cert_type] = str(cert_file)
    
    return cert_files


@pytest.fixture 
def mock_ssl_context():
    """Mock SSL context to avoid certificate validation in tests"""
    with patch('cad_ftps_client.client.ssl.create_default_context') as mock_context:
        mock_ctx = Mock()
        mock_context.return_value = mock_ctx
        yield mock_ctx


@pytest.fixture
def ftps_client_with_mock_ssl(mock_certificates, mock_ssl_context):
    """Create FTPS client with mocked SSL context"""
    from cad_ftps_client import SecureFTPSClient
    
    return SecureFTPSClient(
        host="test.ftps.server",
        port=990,
        cert_file=mock_certificates["client-cert"],
        key_file=mock_certificates["client-key"],
        ca_file=mock_certificates["ca-cert"]
    )