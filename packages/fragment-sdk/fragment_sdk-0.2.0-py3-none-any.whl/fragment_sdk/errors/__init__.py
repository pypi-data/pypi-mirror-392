class FragmentClientError(Exception):
  """Base class for Client errors"""

class FragmentDataSetupError(FragmentClientError):
  """Error raised when there's a problem with setting up Fragment client data:
  (api_hash, ton_rate, etc).
  """

class FragmentAPIError(FragmentClientError):
  """Error raised when Fragment does not send the expected response."""
  def __init__(self, message, response):
    msg = f"{message}\nThe server responded with: {response}"
    self.response = response
    super(FragmentAPIError, self).__init__(msg)

class FragmentInitError(FragmentClientError):
  """Raised when a required parameter is missing or invalid."""

class StarsOperationError(FragmentClientError):
  """Errors in Stars operations"""

class PremiumOperationError(FragmentClientError):
  """Errors in Telegram Premium operations"""

class AdsOperationError(FragmentClientError):
  """Errors in Telegram Ads operations"""

class WalletError(FragmentClientError):
  """Raised when there's a problem with wallet."""

class WalletVersionError(WalletError):
  """Raised when wrong wallet version specified"""

class WalletBalanceInsufficient(WalletError):
  """Raised when wallet balance insufficient"""