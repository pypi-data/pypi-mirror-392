"""
FTPS-specific exceptions

Custom exceptions for FTPS operations providing detailed error information.
"""


class FTPSError(Exception):
    """Base exception for FTPS operations"""
    pass


class FTPSConnectionError(FTPSError):
    """FTPS connection failed"""
    pass


class FTPSAuthenticationError(FTPSError):
    """FTPS authentication failed"""
    pass


class FTPSCertificateError(FTPSError):
    """FTPS certificate validation failed"""
    pass


class FTPSTransferError(FTPSError):
    """FTPS file transfer failed"""
    pass