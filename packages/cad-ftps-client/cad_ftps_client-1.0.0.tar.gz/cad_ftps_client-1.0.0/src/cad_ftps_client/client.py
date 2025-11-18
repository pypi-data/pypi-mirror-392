"""
Secure FTPS client with mutual SSL authentication

Provides professional FTPS client functionality using ftputil for high-level operations
and custom session factory for implicit FTPS with client certificates.

Usage:
    client = SecureFTPSClient("localhost", 990, cert_file, key_file, ca_file)
    with client.connect("username", "password") as host:
        host.upload("local.txt", "remote.txt")
        files = host.listdir(".")
"""

import ftplib
import logging
import os
import socket
import ssl
from ftplib import FTP_TLS
from pathlib import Path
from typing import Optional

import ftputil
import ftputil.session

from .exceptions import (
    FTPSAuthenticationError,
    FTPSCertificateError,
    FTPSConnectionError,
)

logger = logging.getLogger(__name__)


class SecureFTPSSessionFactory:
    """Factory for creating FTPS sessions with client certificates"""

    def __init__(self, cert_file: str, key_file: str, ca_file: str):
        """
        Initialize session factory with certificate files
        
        Args:
            cert_file: Path to client certificate
            key_file: Path to client private key  
            ca_file: Path to CA certificate
        """
        self.cert_file = cert_file
        self.key_file = key_file
        self.ca_file = ca_file
        self.context = self._create_ssl_context()

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with client certificates"""
        logger.debug("Configuring SSL context...")

        # Strict SSL context
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

        # Load certificates
        context.load_verify_locations(cafile=self.ca_file)
        context.load_cert_chain(certfile=self.cert_file, keyfile=self.key_file)

        # Security configuration
        context.check_hostname = True
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        context.maximum_version = ssl.TLSVersion.TLSv1_3

        # ECDH curve configuration
        context.set_ecdh_curve("X25519")
        context.set_ecdh_curve("prime256v1")
        context.set_ecdh_curve("secp384r1")

        context.verify_flags = ssl.VERIFY_X509_STRICT | ssl.VERIFY_X509_TRUSTED_FIRST

        return context

    def __call__(self, host: str, user: str, password: str, port: int = 990):
        """Create implicit FTPS session (called by ftputil)"""
        logger.debug(f"Creating FTPS session for {user}@{host}:{port}")

        try:
            # Manual SSL connection for implicit FTPS
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Configurable timeout
            timeout = int(os.getenv("FTPS_TIMEOUT", "30"))
            sock.settimeout(timeout)
            sock.connect((host, port))

            # Immediate SSL wrapper
            ssl_sock = self.context.wrap_socket(sock, server_hostname=host)

            # Create FTP_TLS client with SSL socket
            ftps = FTP_TLS()
            ftps.sock = ssl_sock
            ftps.file = ssl_sock.makefile("r", encoding="utf-8")

            # Required attributes for ftputil
            ftps.af = socket.AF_INET
            ftps.host = host
            ftps.port = port
            ftps.context = self.context

            # Read greeting and authenticate
            greeting = ftps.getresp()
            logger.debug(f"Server: {greeting}")

            ftps.login(user, password)
            ftps.prot_p()  # Data protection

            logger.debug("FTPS session established")
            return ftps

        except ssl.SSLError as e:
            logger.error(f"SSL/Certificate error: {e}")
            raise FTPSCertificateError(f"SSL certificate validation failed: {e}")
        except (OSError, ConnectionError) as e:
            logger.error(f"Network connection error: {e}")
            raise FTPSConnectionError(f"Failed to connect to FTPS server: {e}")
        except socket.timeout as e:
            logger.error(f"FTPS/Timeout error: {e}")
            raise FTPSConnectionError(f"Socket timeout or FTP error: {e}")
        except ftplib.all_errors as e:
            logger.error(f"FTPS/Timeout error: {e}")
            raise FTPSConnectionError(f"Socket timeout or FTP error: {e}")
        except Exception as e:
            # Check if it's authentication related
            if "530" in str(e) or "login" in str(e).lower():
                logger.error(f"Authentication error: {e}")
                raise FTPSAuthenticationError(f"FTPS authentication failed: {e}")
            else:
                logger.error(f"Session creation error: {e}")
                raise FTPSConnectionError(f"FTPS session creation failed: {e}")


class SecureFTPSClient:
    """Professional FTPS client with simple API"""

    def __init__(self, host: str, port: int, cert_file: str, key_file: str, ca_file: str):
        """
        Initialize secure FTPS client

        Args:
            host: FTPS server hostname
            port: FTPS port (990 for implicit)
            cert_file: Path to client certificate
            key_file: Path to client private key
            ca_file: Path to CA certificate
        """
        self.host = host
        self.port = port

        # Verify certificates exist
        for cert_type, path in [
            ("cert", cert_file),
            ("key", key_file),
            ("ca", ca_file),
        ]:
            if not Path(path).exists():
                raise FTPSCertificateError(f"Certificate {cert_type} missing: {path}")

        # Create session factory
        self.session_factory = SecureFTPSSessionFactory(cert_file, key_file, ca_file)
        self._host: Optional[ftputil.FTPHost] = None

        logger.info(f"FTPS client configured for {host}:{port}")

    def connect(self, username: str, password: str):
        """
        Connect to FTPS server with context manager

        Args:
            username: FTP username
            password: FTP password

        Returns:
            SecureFTPSClient: Self for context manager pattern

        Usage:
            with client.connect("user", "pass") as host:
                host.upload("local.txt", "remote.txt")
        """
        logger.info(f"Connecting to {username}@{self.host}:{self.port}")

        try:
            # ftputil with our session factory
            self._host = ftputil.FTPHost(
                self.host,
                username,
                password,
                port=self.port,
                session_factory=self.session_factory,
            )
            return self  # Return self for context manager pattern
        except (FTPSConnectionError, FTPSCertificateError, FTPSAuthenticationError):
            # Re-raise specific FTPS exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise FTPSConnectionError(f"Failed to connect to FTPS server: {e}")

    def __enter__(self):
        """Enter context manager"""
        logger.debug("Enter FTPS context manager")
        return self._host

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager - always close the session cleanly"""
        logger.debug("Exit FTPS context manager - cleaning up resources")
        if self._host is not None:
            try:
                self._host.close()
            except Exception as e:
                logger.debug(f"Error during close(): {e}")
            finally:
                self._host = None