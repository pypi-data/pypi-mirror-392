from .utils.extract_photo_src import extract_photo_src

from .methods import FragmentMethod
from .errors import PremiumOperationError, FragmentAPIError, WalletBalanceInsufficient
from .models import (
  ApiResult,
  SearchRecipientResponseData,
  InitPurchaseResponseData,
  Transaction,
  TransactionMessage
)

class FragmentPremiumAPI:
  def __init__(self, client: "FragmentClient") -> None:
    self._client = client
    self._wallet = self._client._ctx.wallet
  
  def init_gift_premium_request(self, recipient_id, months) -> ApiResult[InitPurchaseResponseData]:
    try:
      data, error = self._client.send_fragment_request(
        method=FragmentMethod.INIT_GIFT_PREMIUM,
        body={ 'recipient': recipient_id, 'months': months }
      )
      
      if error:
        return ApiResult.fail(f"Failed to initialize Premium purchase: {error}")
      
      return ApiResult.ok(
        data=InitPurchaseResponseData(
          req_id=data.get("req_id"),
          amount=data.get("amount")
        )
      )
    except FragmentAPIError as error:
      raise PremiumOperationError(f"Failed to initialize Premium purchase: {error}")
  
  def get_gift_premium_link(self, account, req_id) -> ApiResult[Transaction]:
    try:
      data, error = self._client.send_fragment_request(
        method=FragmentMethod.GET_GIFT_PREMIUM_LINK,
        body={
          'account': account,
          'transaction': '1',
          'id': req_id,
          'show_sender': '0'
        }
      )
      
      if error:
        return ApiResult.fail(f'Failed to obtain Premium purchase link: {error}')
      
      transaction = data.get('transaction')
      transaction_messages = transaction.get('messages')
      messages = [
        TransactionMessage(
          address=item.get('address'),
          amount=item.get('amount'),
          payload=item.get('payload')
        )
        for item in transaction_messages
      ]
      
      return ApiResult.ok(
        data=Transaction(
          validUntil=transaction.get('validUntil'),
          messages=messages
        )
      )
    except FragmentAPIError as error:
      raise PremiumOperationError(f"Failed to obtain Premium purchase link: {error}")
  
  def search_premium_recipient(self, recipient_username) -> ApiResult[SearchRecipientResponseData]:
    try:
      data, error = self._client.send_fragment_request(
        method=FragmentMethod.SEARCH_PREMIUM_RECIPIENT,
        body={
          'query': recipient_username,
          'months': ''
        }
      )
      
      if error:
        return ApiResult.fail(f"Failed to obtain Premium recipient: {error}")
      
      if found := data.get('found'):
        photo = found.get('photo')
        photo_src = extract_photo_src(html_photo=photo)
      
      return ApiResult.ok(
        data=SearchRecipientResponseData(
          recipient_id=found.get('recipient'),
          name=found.get('name'),
          photo_url=photo_src
        )
      )
    except FragmentAPIError as error:
      raise PremiumOperationError(f"Failed to obtain Premium recipient: {error}")
  
  def create_premium_transaction(self, recipient_id, months, wallet_account) -> ApiResult[Transaction]:
    try:
      init_data = self.init_gift_premium_request(recipient_id=recipient_id, months=months)
      
      if init_data.error:
        return ApiResult.fail(init_data.error)
      
      buy_transaction = self.get_gift_premium_link(
        account=wallet_account,
        req_id=init_data.data.req_id
      )
      
      if buy_transaction.error:
        return ApiResult.fail(buy_transaction.error)
      
      return ApiResult.ok(data=buy_transaction.data)
    except PremiumOperationError:
      raise
  
  async def buy_premium(self, username, months = 3) -> ApiResult[str]:
    try:
      recipient = self.search_premium_recipient(recipient_username=username)
      if recipient.error:
        return ApiResult.fail(error=recipient.error)
      wallet_account = self._wallet.get_wallet_data()
      transaction = self.create_premium_transaction(recipient_id=recipient.data.recipient_id, months=months, wallet_account=wallet_account)
      
      if transaction.error:
        return ApiResult.fail(error=transaction.error)
      
      transaction_msg = transaction.data.messages[0]
      tx_hash = await self._wallet.process_transaction(
        destination=transaction_msg.address,
        amount=transaction_msg.amount,
        body=transaction_msg.payload
      )
      
      return ApiResult.ok(data=tx_hash)
    except WalletBalanceInsufficient as error:
      return ApiResult.fail(error=error)
    except PremiumOperationError:
      raise