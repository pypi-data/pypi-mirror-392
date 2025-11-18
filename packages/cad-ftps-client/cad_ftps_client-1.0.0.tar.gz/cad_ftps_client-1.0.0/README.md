# CAD FTPS Client

Secure FTPS client with mutual SSL authentication for CAD medical institutions.

## Features

- **Implicit FTPS** (port 990) with mutual SSL authentication
- **TLS 1.3** support with client/server certificates
- **Chunked uploads** with configurable size and progress callbacks
- **Professional error handling** with specialized exceptions
- **High-level API** built on ftputil for ease of use

## Installation

```bash
pip install cad-ftps-client
```

## Quick Start

```python
from cad_ftps_client import SecureFTPSClient

# Initialize client with certificates
client = SecureFTPSClient(
    host="ftps.hospital.fr",
    port=990,
    cert_file="/path/to/client-cert.pem",
    key_file="/path/to/client-key.pem", 
    ca_file="/path/to/ca-cert.pem"
)

# Connect and transfer files
with client.connect("username", "password") as host:
    # Upload files
    host.upload("local_file.txt", "remote_file.txt")
    
    # List directory
    files = host.listdir("/remote/path")
    
    # Download files
    host.download("remote_file.txt", "local_file.txt")
    
    # Create directories
    host.makedirs("/remote/new/path")
```

## Advanced Usage

### Chunked Upload with Progress

```python
def progress_callback(chunk):
    print(f"Uploaded {len(chunk)} bytes")

with client.connect("username", "password") as host:
    # Upload with custom chunk size and progress callback
    host.upload_chunked(
        "large_file.dat", 
        "remote_large_file.dat",
        chunk_size=1024*1024,  # 1MB chunks
        callback=progress_callback
    )
```

### Error Handling

```python
from cad_ftps_client.exceptions import (
    FTPSConnectionError,
    FTPSAuthenticationError,
    FTPSCertificateError,
    FTPSTransferError
)

try:
    with client.connect("username", "password") as host:
        host.upload("file.txt", "remote.txt")
except FTPSConnectionError:
    print("Failed to connect to FTPS server")
except FTPSAuthenticationError:
    print("Invalid credentials")
except FTPSCertificateError:
    print("Certificate validation failed")
except FTPSTransferError:
    print("File transfer failed")
```

## Certificate Requirements

The client requires three certificate files:

- **Client Certificate** (`client-cert.pem`): Your institution's certificate
- **Private Key** (`client-key.pem`): Private key for client certificate  
- **CA Certificate** (`ca-cert.pem`): Certificate Authority to validate server

## Configuration

### Environment Variables

- `FTPS_TIMEOUT`: Connection timeout in seconds (default: 30)
- `FTPS_CHUNK_SIZE`: Upload chunk size in bytes (default: 524288)
- `FTPS_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### TLS Configuration

The client enforces strong security by default:

- **TLS 1.3 only** (configurable)
- **Certificate verification** required
- **Hostname checking** enabled
- **Strong cipher suites** only

## Development

### Setup Development Environment

```bash
git clone https://github.com/neil-atr/cad-ftps-client
cd cad-ftps-client
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

For issues and questions:
- GitHub Issues: https://github.com/neil-atr/cad-ftps-client/issues
- Email: neil.anteur@gmail.com