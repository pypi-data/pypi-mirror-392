"""
Unit tests for SecureFTPSClient

Tests the core FTPS client functionality with mock servers and certificates.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from cad_ftps_client import SecureFTPSClient, SecureFTPSSessionFactory
from cad_ftps_client.exceptions import (
    FTPSConnectionError,
    FTPSAuthenticationError, 
    FTPSCertificateError,
)


class TestSecureFTPSSessionFactory:
    """Test SecureFTPSSessionFactory"""

    def test_factory_initialization_with_valid_certs(self, mock_certificates, mock_ssl_context):
        """Factory should initialize with valid certificates"""
        factory = SecureFTPSSessionFactory(
            cert_file=mock_certificates["client-cert"],
            key_file=mock_certificates["client-key"],
            ca_file=mock_certificates["ca-cert"]
        )
        
        assert factory.cert_file == mock_certificates["client-cert"]
        assert factory.key_file == mock_certificates["client-key"] 
        assert factory.ca_file == mock_certificates["ca-cert"]
        assert factory.context is not None

    def test_ssl_context_configuration(self, mock_certificates, mock_ssl_context):
        """SSL context should be configured with security settings"""
        factory = SecureFTPSSessionFactory(
            cert_file=mock_certificates["client-cert"],
            key_file=mock_certificates["client-key"],
            ca_file=mock_certificates["ca-cert"]
        )
        
        # Verify SSL context configuration calls
        mock_ssl_context.load_verify_locations.assert_called_once()
        mock_ssl_context.load_cert_chain.assert_called_once()
        assert mock_ssl_context.check_hostname is True


class TestSecureFTPSClient:
    """Test SecureFTPSClient"""

    def test_client_initialization_with_valid_certs(self, ftps_client_with_mock_ssl):
        """Client should initialize successfully with valid certificates"""
        client = ftps_client_with_mock_ssl
        assert client.host == "test.ftps.server"
        assert client.port == 990
        assert client.session_factory is not None

    def test_client_initialization_with_missing_cert(self, tmp_path):
        """Client should raise FTPSCertificateError for missing certificates"""
        # Create only some certificates
        cert_file = tmp_path / "client-cert.pem"
        cert_file.write_text("cert content")
        
        with pytest.raises(FTPSCertificateError, match="Certificate key missing"):
            SecureFTPSClient(
                host="test.server",
                port=990,
                cert_file=str(cert_file),
                key_file="/nonexistent/key.pem",  # Missing key file
                ca_file="/nonexistent/ca.pem"    # Missing CA file
            )

    @patch('cad_ftps_client.client.ftputil.FTPHost')
    def test_successful_connection(self, mock_ftphost, ftps_client_with_mock_ssl):
        """Successful connection should return context manager"""
        mock_host = Mock()
        mock_ftphost.return_value = mock_host
        
        result = ftps_client_with_mock_ssl.connect("testuser", "testpass")
        
        assert result is ftps_client_with_mock_ssl
        mock_ftphost.assert_called_once_with(
            "test.ftps.server",
            "testuser", 
            "testpass",
            port=990,
            session_factory=ftps_client_with_mock_ssl.session_factory
        )

    @patch('cad_ftps_client.client.ftputil.FTPHost')
    def test_context_manager_usage(self, mock_ftphost, ftps_client_with_mock_ssl):
        """Context manager should provide host and cleanup properly"""
        mock_host = Mock()
        mock_ftphost.return_value = mock_host
        
        with ftps_client_with_mock_ssl.connect("testuser", "testpass") as host:
            assert host is mock_host
        
        # Verify cleanup was called
        mock_host.close.assert_called_once()

    @patch('cad_ftps_client.client.ftputil.FTPHost')
    def test_connection_error_handling(self, mock_ftphost, ftps_client_with_mock_ssl):
        """Connection errors should be properly handled and re-raised"""
        mock_ftphost.side_effect = Exception("Network error")
        
        with pytest.raises(FTPSConnectionError, match="Failed to connect"):
            ftps_client_with_mock_ssl.connect("testuser", "testpass")

    def test_context_manager_cleanup_on_exception(self, ftps_client_with_mock_ssl):
        """Context manager should cleanup even if exceptions occur"""
        with patch('cad_ftps_client.client.ftputil.FTPHost') as mock_ftphost:
            mock_host = Mock()
            mock_ftphost.return_value = mock_host
            
            try:
                with ftps_client_with_mock_ssl.connect("testuser", "testpass") as host:
                    raise ValueError("Test exception")
            except ValueError:
                pass
            
            # Verify cleanup was still called
            mock_host.close.assert_called_once()


class TestIntegrationScenarios:
    """Integration-style tests with more realistic scenarios"""
    
    @patch.dict(os.environ, {"FTPS_TIMEOUT": "60"})
    @patch('cad_ftps_client.client.socket.socket')
    @patch('cad_ftps_client.client.ssl.create_default_context')
    def test_session_factory_with_timeout_configuration(self, mock_ssl_context, mock_socket, mock_certificates):
        """Session factory should respect timeout configuration"""
        mock_context = Mock()
        mock_ssl_context.return_value = mock_context
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        
        factory = SecureFTPSSessionFactory(
            cert_file=mock_certificates["client-cert"],
            key_file=mock_certificates["client-key"],
            ca_file=mock_certificates["ca-cert"]
        )
        
        # This would trigger the session creation logic
        try:
            factory("test.host", "user", "pass", 990)
        except Exception:
            pass  # We expect this to fail in test, but want to check timeout was set
        
        # Verify timeout was configured from environment
        mock_sock.settimeout.assert_called_with(60)

    def test_error_propagation_chain(self, ftps_client_with_mock_ssl):
        """Test that errors propagate correctly through the call stack"""
        with patch('cad_ftps_client.client.ftputil.FTPHost') as mock_ftphost:
            # Simulate an authentication error from deep in the stack
            mock_ftphost.side_effect = FTPSAuthenticationError("530 Login incorrect")
            
            with pytest.raises(FTPSAuthenticationError, match="530 Login incorrect"):
                ftps_client_with_mock_ssl.connect("baduser", "badpass")