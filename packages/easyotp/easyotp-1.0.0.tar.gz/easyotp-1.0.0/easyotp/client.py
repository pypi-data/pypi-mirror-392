import requests
from typing import Optional
from .models import (
    SendRequest,
    SendResponse,
    VerifyRequest,
    VerifyResponse,
    Channel,
)
from .exceptions import (
    EasyOTPError,
    AuthenticationError,
    InsufficientCreditsError,
    APIKeyDisabledError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ServerError,
)


class EasyOTP:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://app.easyotp.dev/api/v1",
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    def _handle_response(self, response: requests.Response) -> dict:
        status_code = response.status_code
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise ServerError(
                f"Invalid JSON response: {response.text}",
                status_code=status_code,
            )

        request_id = data.get("request_id")

        if status_code == 200:
            return data
        elif status_code == 400:
            raise ValidationError(
                data.get("error", "Validation error"), request_id, status_code
            )
        elif status_code == 401:
            raise AuthenticationError(
                data.get("error", "Authentication failed"), request_id, status_code
            )
        elif status_code == 402:
            raise InsufficientCreditsError(
                data.get("error", "Insufficient credits"), request_id, status_code
            )
        elif status_code == 403:
            raise APIKeyDisabledError(
                data.get("error", "API key disabled"), request_id, status_code
            )
        elif status_code == 404:
            raise NotFoundError(
                data.get("error", "Not found"), request_id, status_code
            )
        elif status_code == 429:
            retry_after = data.get("retry_after")
            raise RateLimitError(
                data.get("error", "Rate limit exceeded"),
                request_id,
                retry_after=retry_after,
            )
        elif status_code >= 500:
            raise ServerError(
                data.get("error", "Server error"), request_id, status_code
            )
        else:
            raise EasyOTPError(
                data.get("error", f"Unexpected error: {status_code}"),
                request_id,
                status_code,
            )

    def send(
        self,
        channel: Channel,
        recipient: str,
        message: Optional[str] = None,
        subject: Optional[str] = None,
        expires_in: Optional[int] = None,
        code: Optional[str] = None,
    ) -> SendResponse:
        request = SendRequest(
            channel=channel,
            recipient=recipient,
            message=message,
            subject=subject,
            expires_in=expires_in,
            code=code,
        )

        url = f"{self.base_url}/send"
        response = self.session.post(
            url, json=request.to_dict(), timeout=self.timeout
        )

        data = self._handle_response(response)
        return SendResponse.from_dict(data)

    def verify(self, verification_id: str, code: str) -> VerifyResponse:
        request = VerifyRequest(verification_id=verification_id, code=code)

        url = f"{self.base_url}/verify"
        response = self.session.post(
            url, json=request.to_dict(), timeout=self.timeout
        )

        data = self._handle_response(response)
        return VerifyResponse.from_dict(data)

