#!/usr/bin/env python3
"""
Basic usage example for CAD FTPS Client

This example demonstrates how to use the CAD FTPS Client for secure file transfers
with mutual SSL authentication.
"""

import logging
import os
from pathlib import Path

from cad_ftps_client import SecureFTPSClient
from cad_ftps_client.exceptions import (
    FTPSConnectionError,
    FTPSAuthenticationError,
    FTPSCertificateError,
    FTPSTransferError,
)


def setup_logging():
    """Configure logging for the example"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def main():
    """Main example function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Configuration
    FTPS_HOST = "ftps.hospital.fr"
    FTPS_PORT = 990
    USERNAME = "your_username"
    PASSWORD = "your_password"
    
    # Certificate paths (adjust to your setup)
    CERT_DIR = Path("./certificates")
    CLIENT_CERT = CERT_DIR / "client-cert.pem"
    CLIENT_KEY = CERT_DIR / "client-key.pem"
    CA_CERT = CERT_DIR / "ca-cert.pem"
    
    logger.info("CAD FTPS Client - Basic Usage Example")
    
    try:
        # Initialize FTPS client
        client = SecureFTPSClient(
            host=FTPS_HOST,
            port=FTPS_PORT,
            cert_file=str(CLIENT_CERT),
            key_file=str(CLIENT_KEY),
            ca_file=str(CA_CERT)
        )
        
        logger.info(f"Connecting to {FTPS_HOST}:{FTPS_PORT}")
        
        # Connect and perform operations
        with client.connect(USERNAME, PASSWORD) as host:
            logger.info("Successfully connected to FTPS server")
            
            # List current directory
            logger.info("Listing root directory:")
            files = host.listdir(".")
            for file in files[:5]:  # Show first 5 files
                logger.info(f"  - {file}")
            
            # Create a test directory
            test_dir = "test_upload"
            if not host.path.exists(test_dir):
                host.makedirs(test_dir)
                logger.info(f"Created directory: {test_dir}")
            
            # Create a test file locally
            local_file = Path("test_file.txt")
            local_file.write_text("Hello from CAD FTPS Client!")
            
            # Upload file
            remote_file = f"{test_dir}/test_file.txt"
            host.upload(str(local_file), remote_file)
            logger.info(f"Uploaded {local_file} to {remote_file}")
            
            # Verify upload
            if host.path.exists(remote_file):
                remote_size = host.path.getsize(remote_file)
                local_size = local_file.stat().st_size
                logger.info(f"Upload verified - Local: {local_size}, Remote: {remote_size}")
            
            # Download file back (with different name)
            download_file = Path("downloaded_test_file.txt")
            host.download(remote_file, str(download_file))
            logger.info(f"Downloaded {remote_file} to {download_file}")
            
            # Clean up local files
            local_file.unlink()
            download_file.unlink()
            logger.info("Cleaned up local test files")
            
        logger.info("FTPS session closed successfully")
        
    except FTPSConnectionError as e:
        logger.error(f"Connection error: {e}")
    except FTPSAuthenticationError as e:
        logger.error(f"Authentication error: {e}")
    except FTPSCertificateError as e:
        logger.error(f"Certificate error: {e}")
    except FTPSTransferError as e:
        logger.error(f"Transfer error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def chunked_upload_example():
    """Example of chunked upload with progress callback"""
    logger = logging.getLogger(__name__)
    
    def progress_callback(chunk):
        """Progress callback for chunked uploads"""
        logger.debug(f"Uploaded chunk of {len(chunk)} bytes")
    
    # Configuration would be same as main()...
    # This is just to show the API usage
    
    """
    client = SecureFTPSClient(host, port, cert_file, key_file, ca_file)
    
    with client.connect(username, password) as host:
        # For large files, you can use chunked upload
        # Note: This requires additional implementation in the client
        # host.upload_chunked(
        #     "large_file.dat",
        #     "remote_large_file.dat", 
        #     chunk_size=1024*1024,  # 1MB chunks
        #     callback=progress_callback
        # )
        pass
    """


if __name__ == "__main__":
    main()