from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal


Channel = Literal["sms", "email", "voice"]


@dataclass
class SendRequest:
    channel: Channel
    recipient: str
    message: Optional[str] = None
    subject: Optional[str] = None
    expires_in: Optional[int] = None
    code: Optional[str] = None

    def to_dict(self) -> dict:
        data = {
            "channel": self.channel,
            "recipient": self.recipient,
        }
        if self.message is not None:
            data["message"] = self.message
        if self.subject is not None:
            data["subject"] = self.subject
        if self.expires_in is not None:
            data["expires_in"] = self.expires_in
        if self.code is not None:
            data["code"] = self.code
        return data


@dataclass
class SendResponse:
    success: bool
    verification_id: str
    expires_at: str
    request_id: str

    @property
    def expires_at_datetime(self) -> datetime:
        return datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))

    @classmethod
    def from_dict(cls, data: dict) -> "SendResponse":
        return cls(
            success=data["success"],
            verification_id=data["verification_id"],
            expires_at=data["expires_at"],
            request_id=data["request_id"],
        )


@dataclass
class VerifyRequest:
    verification_id: str
    code: str

    def to_dict(self) -> dict:
        return {
            "verification_id": self.verification_id,
            "code": self.code,
        }


@dataclass
class VerifyResponse:
    success: bool
    verified: bool
    message: str
    request_id: str

    @classmethod
    def from_dict(cls, data: dict) -> "VerifyResponse":
        return cls(
            success=data["success"],
            verified=data["verified"],
            message=data.get("message", ""),
            request_id=data["request_id"],
        )

