# EasyOTP Python SDK

Python SDK for EasyOTP - Send and verify OTP codes via SMS, Email, and Voice.

## Installation

```bash
pip install easyotp
```

Or install from source:

```bash
pip install .
```

## Quick Start

```python
from easyotp import EasyOTP

client = EasyOTP(api_key="your_api_key_here")

response = client.send(
    channel="sms",
    recipient="+1234567890",
    message="Your verification code is: {code}",
    expires_in=300
)

print(f"Verification ID: {response.verification_id}")
print(f"Expires at: {response.expires_at}")

verify_response = client.verify(
    verification_id=response.verification_id,
    code="123456"
)

if verify_response.verified:
    print("Code verified successfully!")
else:
    print(f"Verification failed: {verify_response.message}")
```

## Usage

### Initialization

```python
from easyotp import EasyOTP

client = EasyOTP(
    api_key="your_api_key_here",
    base_url="https://app.easyotp.dev/api/v1",  # Optional, defaults to production
    timeout=30  # Optional, request timeout in seconds
)
```

### Sending Verification Codes

#### SMS

```python
response = client.send(
    channel="sms",
    recipient="+1234567890",
    message="Your verification code is: {code}",
    expires_in=300
)
```

#### Email

```python
response = client.send(
    channel="email",
    recipient="user@example.com",
    subject="Your Verification Code",
    message="Your verification code is: {code}",
    expires_in=600
)
```

#### Voice

```python
response = client.send(
    channel="voice",
    recipient="+1234567890",
    message="Your verification code is: {code}",
    expires_in=300
)
```

### Verifying Codes

```python
verify_response = client.verify(
    verification_id="11f951d5-32d1-4b49-bdda-7da248e2615c",
    code="123456"
)

if verify_response.verified:
    print("Success!")
else:
    print(f"Failed: {verify_response.message}")
```

### Response Objects

#### SendResponse

```python
response = client.send(channel="sms", recipient="+1234567890")

print(response.success)  # True
print(response.verification_id)  # "11f951d5-32d1-4b49-bdda-7da248e2615c"
print(response.expires_at)  # "2024-01-01T12:05:00.000Z"
print(response.expires_at_datetime)  # datetime object
print(response.request_id)  # "7b4d6022-7260-4568-b6b7-29c366c47bbc"
```

#### VerifyResponse

```python
verify_response = client.verify(verification_id="...", code="123456")

print(verify_response.success)  # True
print(verify_response.verified)  # True or False
print(verify_response.message)  # "Code verified successfully" or error message
print(verify_response.request_id)  # "7b4d6022-7260-4568-b6b7-29c366c47bbc"
```

## Error Handling

The SDK provides specific exception classes for different error scenarios:

```python
from easyotp import (
    EasyOTP,
    AuthenticationError,
    InsufficientCreditsError,
    APIKeyDisabledError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ServerError,
)

client = EasyOTP(api_key="your_api_key")

try:
    response = client.send(channel="sms", recipient="+1234567890")
except AuthenticationError as e:
    print(f"Auth failed: {e.message} (request_id: {e.request_id})")
except InsufficientCreditsError as e:
    print(f"No credits: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except NotFoundError as e:
    print(f"Not found: {e.message}")
except ServerError as e:
    print(f"Server error: {e.message}")
except EasyOTPError as e:
    print(f"Error: {e.message}")
```

## Complete Example

```python
from easyotp import EasyOTP, EasyOTPError

client = EasyOTP(api_key="your_api_key")

try:
    send_response = client.send(
        channel="sms",
        recipient="+1234567890",
        message="Your Acme Corp verification code is: {code}",
        expires_in=300
    )
    
    print(f"Code sent! Verification ID: {send_response.verification_id}")
    
    user_code = input("Enter verification code: ")
    
    verify_response = client.verify(
        verification_id=send_response.verification_id,
        code=user_code
    )
    
    if verify_response.verified:
        print("Verification successful!")
    else:
        print(f"Verification failed: {verify_response.message}")
        
except EasyOTPError as e:
    print(f"Error: {e}")
```

## API Reference

### EasyOTP Class

#### `__init__(api_key: str, base_url: str = None, timeout: int = 30)`

Initialize the EasyOTP client.

- `api_key`: Your EasyOTP API key
- `base_url`: Base URL for the API (defaults to production)
- `timeout`: Request timeout in seconds (default: 30)

#### `send(channel: str, recipient: str, message: str = None, subject: str = None, expires_in: int = None, code: str = None) -> SendResponse`

Send a verification code.

- `channel`: Communication channel (`"sms"`, `"email"`, or `"voice"`)
- `recipient`: Recipient address (phone number for SMS/voice, email for email)
- `message`: Custom message template with `{code}` placeholder (optional)
- `subject`: Email subject line (email channel only, optional)
- `expires_in`: Code expiration time in seconds, 60-3600 (optional, default: 300)
- `code`: Custom verification code, 4-10 digits (optional, auto-generated if not provided)

Returns: `SendResponse` object

#### `verify(verification_id: str, code: str) -> VerifyResponse`

Verify a verification code.

- `verification_id`: Verification ID from the send response
- `code`: Verification code to check

Returns: `VerifyResponse` object

## License

MIT

## Support

For support, email support@easyotp.dev or visit https://docs.easyotp.dev

