# GovESB Python Package

A comprehensive Python library for integrating with GovESB (Government Enterprise Service Bus), providing secure communication, data encryption, signature verification, and seamless API interactions.

## Features

- 🔐 **Cryptographic Support**: RSA and ECC (Elliptic Curve Cryptography) for secure data transmission
- 📝 **Data Format Support**: JSON and XML data formats
- 🔑 **Token Management**: Automatic OAuth2 token acquisition and management
- ✅ **Signature Verification**: Built-in signature verification for received data
- 📤 **Request Signing**: Automatic request signing before sending to GovESB
- 🔄 **Push/Pull Modes**: Support for both PUSH and PULL connection modes
- 🛡️ **Security**: Industry-standard cryptographic algorithms (SHA256withRSA, ECDSA)

## Installation

Install the package from PyPI:

```bash
pip install govesb
```

Or install from source:

```bash
git clone https://github.com/LarryMatrix/govesb.git
cd govesb
pip install .
```

## Requirements

- Python 3.7 or higher
- cryptography >= 44.0.0
- requests >= 2.32.0
- xmltodict >= 0.14.0

## Data Structure Format

GovESB uses a standardized data structure for both sending and receiving data. All messages follow this format:

```json
{
  "data": {
    "apiCode": "string",
    "esbBody": {
      "ephemeralKey": "base64-encoded-public-key",
      "iv": "initialization-vector",
      "encryptedData": "base64-encoded-encrypted-data"
    }
  },
  "signature": "base64-encoded-signature"
}
```

**Fields:**
- `data.apiCode`: The API code identifying the specific GovESB endpoint
- `data.esbBody`: Contains the encrypted payload
  - `ephemeralKey`: Ephemeral public key used for ECIES encryption (base64-encoded PEM format)
  - `iv`: Initialization vector for AES encryption
  - `encryptedData`: The actual encrypted data (base64-encoded)
- `signature`: ECDSA signature of the entire `data` object (base64-encoded)

The library handles signature verification automatically. If you need to decrypt the `esbBody.encryptedData`, you'll need to implement ECIES decryption using the `ephemeralKey`, `iv`, and your private key.

## Quick Start

### Receiving Data from GovESB

When your system receives data from GovESB, you need to verify the signature and extract the payload. The received data structure contains encrypted data:

```python
import json
import requests
from govesb import DataFormatEnum, ESBHelper

# Configuration
destination_url = "https://your-destination.com/api/endpoint"
destination_username = "system-username"
destination_password = "password"
govesb_public_key = "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"

# Received data from GovESB (with signature and encrypted esbBody)
sample_data = '''
{
  "data": {
    "apiCode": "YOUR_API_CODE",
    "esbBody": {
      "ephemeralKey": "BASE64_ENCODED_EPHEMERAL_PUBLIC_KEY",
      "iv": "INITIALIZATION_VECTOR",
      "encryptedData": "BASE64_ENCODED_ENCRYPTED_DATA"
    }
  },
  "signature": "BASE64_ENCODED_SIGNATURE"
}
'''

# Verify signature and extract data
response_data = ESBHelper.verify_and_extract_data(
    received_data=sample_data,
    format=DataFormatEnum.JSON,
    public_key=govesb_public_key
)

# Check if verification was successful
if response_data.has_data:
    # Parse the verified data to access apiCode and encrypted esbBody
    verified_json = json.loads(response_data.verified_data)
    api_code = verified_json.get('data', {}).get('apiCode')
    esb_body = verified_json.get('data', {}).get('esbBody')
    
    print("API Code:", api_code)
    print("Encrypted ESB Body:", esb_body)
    
    # Note: If esbBody contains encrypted data, you'll need to decrypt it
    # using your private key and the ephemeralKey, iv, and encryptedData fields
    # The decryption process depends on your specific implementation
    
    # Process the verified data
    response = requests.post(
        url=destination_url,
        json=verified_json,
        auth=(destination_username, destination_password)
    )
    print("Response:", response.text)
else:
    print("Signature Verification Failed:", response_data.message)
```

### Sending Data to GovESB

To send data to GovESB, you need to authenticate, sign the request, and send it. The data will be encrypted and signed before sending:

```python
from govesb import DataFormatEnum, ESBHelper

# Configuration
client_id = "your_client_id"
client_secret = "your_client_secret"
api_code = "your_api_code"
signing_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
esb_token_url = "https://esb.example.com/oauth/token"
esb_request_url = "https://esb.example.com/api/request"

# Prepare your data
sample_data = {
    "userId": 1,
    "id": 1,
    "title": "Sample Title",
    "body": "Sample Body"
}

# Send request to GovESB
# The library will automatically:
# 1. Get OAuth2 access token
# 2. Encrypt and sign the data
# 3. Format it with apiCode and encrypted esbBody structure
# 4. Send to GovESB
encrypted_response = ESBHelper.esb_request(
    client_id=client_id,
    client_secret=client_secret,
    api_code=api_code,
    esb_body=sample_data,
    format=DataFormatEnum.JSON,
    key=signing_key,
    esb_token_url=esb_token_url,
    esb_request_url=esb_request_url
)

print('Response from GovESB:', encrypted_response)
```

**Note**: The response from GovESB will have the same structure as the received data format shown above, with `data.apiCode`, `data.esbBody` (containing `ephemeralKey`, `iv`, `encryptedData`), and `signature`.

### Creating a Response for GovESB

When you need to send a response back to GovESB:

```python
from govesb import DataFormatEnum, ESBHelper

system_private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"

# Your response data
response_body = '{"status": "success", "message": "Data processed"}'

# Create signed response
signed_response = ESBHelper.create_response(
    esb_body=response_body,
    format=DataFormatEnum.JSON,
    key=system_private_key,
    is_success=True,
    message="Operation completed successfully"
)

print('Signed response:', signed_response)
```

## Advanced Usage

### Getting OAuth2 Access Token

The `get_esb_access_token` method retrieves an OAuth2 access token that is used in the Authorization header when sending requests to GovESB:

```python
from govesb import GovESBTokenService

# Configuration
client_id = "your_client_id"
client_secret = "your_client_secret"
token_url = "https://esb.example.com/oauth/token"

# Get access token
token_response = GovESBTokenService.get_esb_access_token(
    client_id=client_id,
    client_secret=client_secret,
    token_uri=token_url
)

if token_response.success:
    access_token = token_response.access_token
    print(f"Access token: {access_token}")
    print(f"Token type: {token_response.token_type}")
    print(f"Expires in: {token_response.expires_in} seconds")
    
    # Use the token in Authorization header
    # Authorization: Bearer {access_token}
else:
    print(f"Failed to get token: {token_response.message}")
```

### Creating Signed Requests Manually

You can create signed requests manually using `create_signed_request`. This is useful when you already have an access token:

```python
from govesb import DataFormatEnum, ESBHelper, ModeOfConnection
import requests

# Configuration
api_code = "YOUR_API_CODE"
access_token = "your_access_token"  # Obtained from get_esb_access_token
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
esb_request_url = "https://esb.example.com/api/request"

# Prepare your data
request_body = '{"userId": 1, "action": "get_data"}'

# Create signed request
signed_request = ESBHelper.create_signed_request(
    api_code=api_code,
    access_token=access_token,
    body=request_body,
    format=DataFormatEnum.JSON,
    key=private_key,
    mode=ModeOfConnection.PULL  # or ModeOfConnection.PUSH
)

# Send the signed request
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

response = requests.post(
    esb_request_url,
    headers=headers,
    data=signed_request.encode("utf-8")
)

print("Response:", response.text)
```

### Signing and Verifying Data

#### Using RSA for Signing and Verification

```python
from govesb import RSAHelper
import json

# Load your keys (you can also generate them)
private_key_pem = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
public_key_pem = "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"

# Load keys from PEM strings
private_key = RSAHelper.load_private_key_from_str(private_key_pem)
public_key = RSAHelper.load_public_key_from_str(public_key_pem)

# Data to sign
data_to_sign = '{"userId": 1, "action": "get_data"}'

# Sign the data
signature = RSAHelper.sign(
    data=data_to_sign,
    private_key=private_key,
    algorithm="SHA256"  # Options: SHA1, SHA256, SHA384, SHA512
)

print(f"Signature: {signature}")

# Verify the signature
is_valid = RSAHelper.verify(
    data=data_to_sign,
    signature=signature,
    public_key=public_key,
    algorithm="SHA256"
)

if is_valid:
    print("Signature verification successful!")
else:
    print("Signature verification failed!")
```

#### Using ECC for Signing and Verification

```python
from govesb import ECC

# Private key in PEM format
private_key_pem = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
public_key_pem = "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"

# Data to sign
payload = '{"userId": 1, "action": "get_data"}'

# Sign the payload
signature = ECC.sign_payload(
    payload=payload,
    private_key_str=private_key_pem
)

print(f"ECC Signature: {signature}")

# Verify the signature
is_valid = ECC.verify_payload(
    data=payload,
    signature_str=signature,
    public_key_str=public_key_pem
)

if is_valid:
    print("ECC signature verification successful!")
else:
    print("ECC signature verification failed!")
```

### Verifying and Extracting Data (Detailed)

The `verify_and_extract_data` method verifies the signature and extracts the payload from received GovESB data:

```python
from govesb import DataFormatEnum, ESBHelper
import json

# Configuration
public_key = "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"

# Received data from GovESB
received_data = '''
{
  "data": {
    "apiCode": "YOUR_API_CODE",
    "esbBody": {
      "ephemeralKey": "BASE64_ENCODED_EPHEMERAL_PUBLIC_KEY",
      "iv": "INITIALIZATION_VECTOR",
      "encryptedData": "BASE64_ENCODED_ENCRYPTED_DATA"
    }
  },
  "signature": "BASE64_ENCODED_SIGNATURE"
}
'''

# Verify signature and extract data
response_data = ESBHelper.verify_and_extract_data(
    received_data=received_data,
    format=DataFormatEnum.JSON,
    public_key=public_key
)

# Check verification result
if response_data.has_data:
    # Parse the verified data
    verified_json = json.loads(response_data.verified_data)
    
    # Extract components
    api_code = verified_json.get('data', {}).get('apiCode')
    esb_body = verified_json.get('data', {}).get('esbBody')
    
    print(f"API Code: {api_code}")
    print(f"ESB Body: {esb_body}")
    
    # Access encrypted components
    ephemeral_key = esb_body.get('ephemeralKey')
    iv = esb_body.get('iv')
    encrypted_data = esb_body.get('encryptedData')
    
    print(f"Ephemeral Key: {ephemeral_key}")
    print(f"IV: {iv}")
    print(f"Encrypted Data: {encrypted_data}")
    
    # Process the verified data...
else:
    print(f"Verification failed: {response_data.message}")
```

### Creating Responses (Detailed)

The `create_response` method creates a signed response to send back to GovESB:

```python
from govesb import DataFormatEnum, ESBHelper
import json

# Configuration
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"

# Prepare response data
response_data = {
    "status": "success",
    "result": "Data processed",
    "timestamp": "2024-01-01T00:00:00Z"
}

# Convert to JSON string
response_body = json.dumps(response_data)

# Create signed response
signed_response = ESBHelper.create_response(
    esb_body=response_body,
    format=DataFormatEnum.JSON,
    key=private_key,
    is_success=True,
    message="Operation completed successfully"
)

print("Signed Response:")
print(signed_response)

# The response structure will be:
# {
#   "data": {
#     "status": "success",
#     "result": "Data processed",
#     "timestamp": "2024-01-01T00:00:00Z"
#   },
#   "signature": "BASE64_ENCODED_SIGNATURE"
# }
```

### Complete Workflow with Manual Steps

Here's a complete example showing all the steps manually:

```python
from govesb import (
    DataFormatEnum, ESBHelper, GovESBTokenService, 
    ModeOfConnection, ECC
)
import requests
import json

# Configuration
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
API_CODE = "your_api_code"
PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
ESB_TOKEN_URL = "https://esb.example.com/oauth/token"
ESB_REQUEST_URL = "https://esb.example.com/api/request"

# Step 1: Get OAuth2 access token
print("Step 1: Getting access token...")
token_response = GovESBTokenService.get_esb_access_token(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    token_uri=ESB_TOKEN_URL
)

if not token_response.success:
    print(f"Failed to get token: {token_response.message}")
    exit(1)

access_token = token_response.access_token
print(f"✓ Access token obtained: {access_token[:20]}...")

# Step 2: Prepare request data
print("\nStep 2: Preparing request data...")
request_data = {
    "userId": 1,
    "action": "get_data",
    "parameters": {"id": 123}
}
request_body = json.dumps(request_data)
print(f"✓ Request body prepared")

# Step 3: Create signed request
print("\nStep 3: Creating signed request...")
signed_request = ESBHelper.create_signed_request(
    api_code=API_CODE,
    access_token=access_token,
    body=request_body,
    format=DataFormatEnum.JSON,
    key=PRIVATE_KEY,
    mode=ModeOfConnection.PULL
)
print(f"✓ Signed request created")

# Step 4: Send request to GovESB
print("\nStep 4: Sending request to GovESB...")
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

response = requests.post(
    ESB_REQUEST_URL,
    headers=headers,
    data=signed_request.encode("utf-8")
)

print(f"✓ Response received: {response.status_code}")

# Step 5: Verify response signature
print("\nStep 5: Verifying response signature...")
response_data = ESBHelper.verify_and_extract_data(
    received_data=response.text,
    format=DataFormatEnum.JSON,
    public_key=PUBLIC_KEY
)

if response_data.has_data:
    print("✓ Signature verified successfully")
    verified_json = json.loads(response_data.verified_data)
    print(f"✓ Verified data: {json.dumps(verified_json, indent=2)}")
else:
    print(f"✗ Signature verification failed: {response_data.message}")

# Step 6: Create response back to GovESB
print("\nStep 6: Creating response...")
response_body = json.dumps({"status": "processed", "result": "success"})
signed_response = ESBHelper.create_response(
    esb_body=response_body,
    format=DataFormatEnum.JSON,
    key=PRIVATE_KEY,
    is_success=True,
    message="Data processed successfully"
)
print(f"✓ Signed response created")
```

## API Reference

### Enums

#### `DataFormatEnum`
Supported data formats:
- `DataFormatEnum.JSON` - JSON format
- `DataFormatEnum.XML` - XML format

#### `ModeOfConnection`
Connection modes:
- `ModeOfConnection.PUSH` - Push mode
- `ModeOfConnection.PULL` - Pull mode

### Main Classes

#### `ESBHelper`

Main helper class for GovESB operations.

**Methods:**

- `esb_request(client_id, client_secret, api_code, esb_body, format, key, esb_token_url, esb_request_url)`  
  Sends a signed request to GovESB. Automatically handles token acquisition.
  
  **Parameters:**
  - `client_id` (str): OAuth2 client ID
  - `client_secret` (str): OAuth2 client secret
  - `api_code` (str): API code for the request
  - `esb_body` (dict/str): Request body data
  - `format` (DataFormatEnum): Data format (JSON or XML)
  - `key` (str): Private key for signing (PEM format)
  - `esb_token_url` (str): OAuth2 token endpoint URL
  - `esb_request_url` (str): GovESB request endpoint URL
  
  **Returns:** Response text from GovESB

- `verify_and_extract_data(received_data, format, public_key)`  
  Verifies the signature of received data and extracts the payload.
  
  **Parameters:**
  - `received_data` (str): Received data with signature
  - `format` (DataFormatEnum): Data format (JSON or XML)
  - `public_key` (str): Public key for verification (PEM format)
  
  **Returns:** `ResponseData` object with `has_data` (bool), `verified_data` (str), and `message` (str)

- `create_response(esb_body, format, key, is_success, message)`  
  Creates a signed response for GovESB.
  
  **Parameters:**
  - `esb_body` (str): Response body data
  - `format` (DataFormatEnum): Data format (JSON or XML)
  - `key` (str): Private key for signing (PEM format)
  - `is_success` (bool): Whether the operation was successful
  - `message` (str): Response message
  
  **Returns:** Signed response string

- `create_signed_request(api_code, access_token, body, format, key, mode)`  
  Creates a signed request payload.
  
  **Parameters:**
  - `api_code` (str): API code
  - `access_token` (str): OAuth2 access token
  - `body` (str): Request body
  - `format` (DataFormatEnum): Data format
  - `key` (str): Private key for signing
  - `mode` (ModeOfConnection): Connection mode (default: PULL)
  
  **Returns:** Signed request string

#### `RSAHelper`

Helper class for RSA cryptographic operations.

**Methods:**
- `generate_key_pair()` - Generate RSA key pair
- `encrypt(plain_text, public_key)` - Encrypt data with RSA
- `decrypt(cipher_text, private_key)` - Decrypt RSA encrypted data
- `sign(data, private_key, algorithm)` - Sign data with RSA
- `verify(data, signature, public_key, algorithm)` - Verify RSA signature

#### `ECC`

Helper class for Elliptic Curve Cryptography operations.

**Methods:**
- `sign_payload(payload, private_key_str)` - Sign payload with ECC
- `verify_payload(data, signature_str, public_key_str)` - Verify ECC signature

#### `GovESBTokenService`

Service for managing OAuth2 tokens.

**Methods:**
- `get_esb_access_token(client_id, client_secret, token_uri)` - Get OAuth2 access token

**Returns:** `TokenResponse` object with `success` (bool), `access_token` (str), and `message` (str)

#### `CryptoConfig`

Configuration class for cryptographic settings.

**Methods:**
- `get_ega_private_key()` - Get private key from `GOVESB_PRIVATE_KEY` environment variable
- `get_client_public_key()` - Get public key from `GOVESB_PUBLIC_KEY` environment variable
- `get_algorithm()` - Get configured algorithm (default: "SHA256withRSA")

## Configuration

### Environment Variables

You can configure keys using environment variables:

```bash
export GOVESB_PRIVATE_KEY="/path/to/private_key.pem"
export GOVESB_PUBLIC_KEY="/path/to/public_key.pem"
```

Then use `CryptoConfig` to access them:

```python
from govesb import CryptoConfig

config = CryptoConfig()
private_key = config.get_ega_private_key()
public_key = config.get_client_public_key()
```

## Data Models

### `ResponseData`
Response object returned by `verify_and_extract_data`:
- `has_data` (bool): Whether verification was successful
- `verified_data` (str): Extracted and verified data
- `message` (str): Status message

### `TokenResponse`
Token response object:
- `success` (bool): Whether token acquisition was successful
- `access_token` (str): OAuth2 access token
- `message` (str): Status message

### `CryptoData`
Cryptographic data container:
- `data`: The data payload
- `signature`: The signature

## Error Handling

The library includes comprehensive error handling:

```python
from govesb import ESBHelper, DataFormatEnum

try:
    response_data = ESBHelper.verify_and_extract_data(
        received_data=data,
        format=DataFormatEnum.JSON,
        public_key=public_key
    )
    
    if not response_data.has_data:
        print(f"Verification failed: {response_data.message}")
    else:
        # Process verified data
        process_data(response_data.verified_data)
        
except Exception as e:
    print(f"Error occurred: {e}")
```

## Examples

### Complete Workflow Example

```python
from govesb import DataFormatEnum, ESBHelper, ModeOfConnection
import requests

# Configuration
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
API_CODE = "your_api_code"
PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
ESB_TOKEN_URL = "https://esb.example.com/oauth/token"
ESB_REQUEST_URL = "https://esb.example.com/api/request"

# 1. Send request to GovESB
request_data = {
    "action": "get_data",
    "parameters": {"id": 123}
}

response = ESBHelper.esb_request(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    api_code=API_CODE,
    esb_body=request_data,
    format=DataFormatEnum.JSON,
    key=PRIVATE_KEY,
    esb_token_url=ESB_TOKEN_URL,
    esb_request_url=ESB_REQUEST_URL
)

print("GovESB Response:", response)

# 2. Process received data (if applicable)
# Assuming you receive data from GovESB webhook
# The received data structure will be:
# {
#   "data": {
#     "apiCode": "...",
#     "esbBody": {
#       "ephemeralKey": "...",
#       "iv": "...",
#       "encryptedData": "..."
#     }
#   },
#   "signature": "..."
# }
received_data = response  # In real scenario, this comes from webhook

verified = ESBHelper.verify_and_extract_data(
    received_data=received_data,
    format=DataFormatEnum.JSON,
    public_key=PUBLIC_KEY
)

if verified.has_data:
    # Parse the verified data to access apiCode and encrypted esbBody
    import json
    verified_json = json.loads(verified.verified_data)
    api_code = verified_json.get('data', {}).get('apiCode')
    esb_body = verified_json.get('data', {}).get('esbBody')
    
    print("API Code:", api_code)
    print("Encrypted ESB Body:", esb_body)
    
    # Note: Decrypt esbBody.encryptedData using esbBody.ephemeralKey, esbBody.iv,
    # and your private key if needed for your use case
    
    # Send response back
    response_body = '{"status": "processed", "result": "success"}'
    signed_response = ESBHelper.create_response(
        esb_body=response_body,
        format=DataFormatEnum.JSON,
        key=PRIVATE_KEY,
        is_success=True,
        message="Data processed successfully"
    )
    print("Signed response:", signed_response)
```

## Security Best Practices

1. **Key Management**: Never hardcode private keys. Use environment variables or secure key management systems.
2. **HTTPS**: Always use HTTPS when communicating with GovESB endpoints.
3. **Key Storage**: Store private keys securely and restrict file permissions.
4. **Token Expiration**: Handle token expiration and refresh tokens appropriately.
5. **Input Validation**: Always validate and sanitize data before processing.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please visit:
- GitHub Issues: https://github.com/LarryMatrix/govesb/issues
- Repository: https://github.com/LarryMatrix/govesb

## Author

**Lawrance Massanja**
- Email: massanjal4@gmail.com
- GitHub: [@LarryMatrix](https://github.com/LarryMatrix)

## Changelog

### Version 2.1.0
- Initial release with v2 API
- Support for RSA and ECC cryptography
- JSON and XML format support
- OAuth2 token management
- Signature verification and request signing

---

**Note**: This package is designed specifically for integration with GovESB systems. Ensure you have proper credentials and API access before using this library.
