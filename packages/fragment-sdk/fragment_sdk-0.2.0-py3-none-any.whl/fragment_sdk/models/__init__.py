from dataclasses import dataclass, asdict
from typing import Any, Generic, Optional, TypeVar, List

T = TypeVar("T")

class BaseResponseModel:
  def to_dict(self) -> dict[str, Any]:
    return asdict(self)

@dataclass(slots=True)
class ApiResult(Generic[T]):
  success: bool
  data: Optional[T] = None
  error: Optional[str] = None
  
  @classmethod
  def ok(cls, data: T) -> "ApiResult[T]":
    return cls(success=True, data=data)

  @classmethod
  def fail(cls, error: str) -> "ApiResult[T]":
    return cls(success=False, error=error)

  def __bool__(self) -> bool:
    return self.success

@dataclass
class SearchRecipientResponseData(BaseResponseModel):
  recipient_id: str
  name: str
  photo_url: str | None

@dataclass
class InitPurchaseResponseData(BaseResponseModel):
  req_id: str
  amount: str
  to_bot: Optional[bool] = None

@dataclass
class TransactionMessage(BaseResponseModel):
  address: str
  amount: str
  payload: str

@dataclass
class Transaction(BaseResponseModel):
  validUntil: int
  messages: List[TransactionMessage]