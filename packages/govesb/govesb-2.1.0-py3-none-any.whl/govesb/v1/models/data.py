from dataclasses import dataclass, field
from typing import Generic, Optional, TypeVar, Any
from ..models.enums import DataFormatEnum


# @dataclass
# class TokenResponse:
#     success: bool
#     access_token: Optional[str] = None
#     token_type: Optional[str] = None
#     expires_in: Optional[int] = None
#
#     def set_success(self, value: bool):
#         self.success = value

T = TypeVar('T')

@dataclass
class TokenResponse:
    success: Optional[bool] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
    scope: Optional[str] = None

    def __str__(self):
        return (
            f"{{access_token='{self.access_token}', token_type='{self.token_type}', "
            f"expires_in={self.expires_in}, scope='{self.scope}'}}"
        )

@dataclass
class CryptoData(Generic[T]):
    data: Optional[T] = None
    signature: Optional[str] = None

    def __str__(self):
        return f"CryptoData(data={self.data}, signature={self.signature})"

@dataclass
class ESBParameterDto:
    esb_token_uri: Optional[str] = None
    api_code: Optional[str] = None
    push_code: Optional[str] = None
    esb_request_uri: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    key: Optional[str] = None
    format: Optional[DataFormatEnum] = None

@dataclass
class ESBRequest:
    api_code: Optional[str] = None
    push_code: Optional[str] = None
    user_id: Optional[str] = None
    authorization: Optional[str] = None
    signature: Optional[str] = None
    esb_body: Optional[Any] = None
    request_id: Optional[str] = None


@dataclass
class ESBResponse:
    signature: Optional[str] = None
    esb_body: Optional[Any] = None
    request_id: Optional[str] = None
    success: Optional[bool] = None
    message: Optional[str] = None


@dataclass
class RequestData:
    verified: Optional[bool] = None
    esb_body: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class ResponseData:
    verified_data: Optional[str] = None
    has_data: bool = False
    message: Optional[str] = None





