"""
CAD FTPS Client

Secure FTPS client with mutual SSL authentication for CAD medical institutions.
Provides professional FTPS client functionality using ftputil for high-level operations
and custom session factory for implicit FTPS with client certificates.
"""

from .client import SecureFTPSClient, SecureFTPSSessionFactory
from .exceptions import (
    FTPSError,
    FTPSConnectionError,
    FTPSAuthenticationError,
    FTPSCertificateError,
    FTPSTransferError,
)

__version__ = "1.0.0"
__author__ = "Neil Anteur"
__email__ = "neil.anteur@gmail.com"

__all__ = [
    "SecureFTPSClient",
    "SecureFTPSSessionFactory", 
    "FTPSError",
    "FTPSConnectionError",
    "FTPSAuthenticationError",
    "FTPSCertificateError",
    "FTPSTransferError",
]