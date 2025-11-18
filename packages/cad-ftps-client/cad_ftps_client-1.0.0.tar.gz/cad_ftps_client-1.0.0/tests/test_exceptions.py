"""
Unit tests for FTPS exceptions

Tests the exception hierarchy and error handling behavior.
"""

import pytest
from cad_ftps_client.exceptions import (
    FTPSError,
    FTPSConnectionError,
    FTPSAuthenticationError,
    FTPSCertificateError, 
    FTPSTransferError,
)


class TestFTPSExceptions:
    """Test FTPS exception classes"""

    def test_exception_hierarchy(self):
        """All FTPS exceptions should inherit from FTPSError"""
        assert issubclass(FTPSConnectionError, FTPSError)
        assert issubclass(FTPSAuthenticationError, FTPSError) 
        assert issubclass(FTPSCertificateError, FTPSError)
        assert issubclass(FTPSTransferError, FTPSError)

    def test_base_exception_inheritance(self):
        """FTPSError should inherit from Exception"""
        assert issubclass(FTPSError, Exception)

    def test_exception_instantiation_and_messages(self):
        """Exceptions should be instantiable with custom messages"""
        test_message = "Test error message"
        
        exceptions = [
            FTPSError(test_message),
            FTPSConnectionError(test_message),
            FTPSAuthenticationError(test_message),
            FTPSCertificateError(test_message),
            FTPSTransferError(test_message),
        ]
        
        for exc in exceptions:
            assert str(exc) == test_message

    def test_exception_raising_and_catching(self):
        """Exceptions should be properly raisable and catchable"""
        
        # Test specific exception catching
        with pytest.raises(FTPSConnectionError):
            raise FTPSConnectionError("Connection failed")
            
        with pytest.raises(FTPSAuthenticationError):
            raise FTPSAuthenticationError("Auth failed")
            
        with pytest.raises(FTPSCertificateError):
            raise FTPSCertificateError("Cert validation failed")
            
        with pytest.raises(FTPSTransferError):
            raise FTPSTransferError("Transfer failed")

    def test_catch_base_exception(self):
        """Base FTPSError should catch all FTPS-specific exceptions"""
        
        exceptions = [
            FTPSConnectionError("Connection error"),
            FTPSAuthenticationError("Auth error"), 
            FTPSCertificateError("Cert error"),
            FTPSTransferError("Transfer error"),
        ]
        
        for exc in exceptions:
            with pytest.raises(FTPSError):
                raise exc

    def test_catch_generic_exception(self):
        """Generic Exception should catch all FTPS exceptions"""
        
        exceptions = [
            FTPSError("Base error"),
            FTPSConnectionError("Connection error"),
            FTPSAuthenticationError("Auth error"),
            FTPSCertificateError("Cert error"), 
            FTPSTransferError("Transfer error"),
        ]
        
        for exc in exceptions:
            with pytest.raises(Exception):
                raise exc