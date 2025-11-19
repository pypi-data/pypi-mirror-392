from typing import Tuple, Optional, Any
from .utils.extract_photo_src import extract_photo_src
from .methods import FragmentMethod
from .errors import StarsOperationError, FragmentAPIError, WalletBalanceInsufficient
from .models import (
  ApiResult,
  SearchRecipientResponseData,
  InitPurchaseResponseData,
  Transaction,
  TransactionMessage,
)

class FragmentStarsAPI:
  def __init__(self, client: "FragmentClient") -> None:
    self._client = client
    self._wallet = self._client._ctx.wallet
  
  def init_buy_stars_request(self, recipient_id, quantity) -> ApiResult[InitPurchaseResponseData]:
    try:
      data, error = self._client.send_fragment_request(
        method=FragmentMethod.INIT_BUY_STARS,
        body={ 'recipient': recipient_id, 'quantity': quantity }
      )
      
      if error:
        return ApiResult.fail(f'Failed to initialize Stars purchase: {error}')
      
      return ApiResult.ok(
        data=InitPurchaseResponseData(
          req_id=data.get("req_id"),
          amount=data.get("amount"),
          to_bot=bool(data.get("to_bot"))
        )
      )
    except FragmentAPIError as error:
      raise StarsOperationError(f"Failed to initialize Stars purchase: {error}")
  
  def get_buy_stars_link(self, account, req_id) -> ApiResult[Transaction]:
    try:
      data, error = self._client.send_fragment_request(
        method=FragmentMethod.GET_BUY_STARS_LINK,
        body={
          'account': account,
          'transaction': '1',
          'id': req_id,
          'show_sender': '0'
        }
      )
      
      if error:
        return ApiResult.fail(f'Failed to obtain Stars purchase link: {error}')
      
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
      raise StarsOperationError(f"Failed to obtain Stars purchase link: {error}")
  
  def search_stars_recipient(self, recipient_username) -> ApiResult[SearchRecipientResponseData]:
    try:
      data, error = self._client.send_fragment_request(
        method=FragmentMethod.SEARCH_STARS_RECIPIENT,
        body={
          'query': recipient_username,
          'quantity': '',
        }
      )
      
      if error:
        return ApiResult.fail(f"Failed to obtain Stars recipient: {error}")
      
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
      raise StarsOperationError(f"Failed to obtain Stars recipient: {error}")
  
  def create_stars_transaction(self, recipient_id, quantity, wallet_account) -> ApiResult[Transaction]:
    try:
      init_data = self.init_buy_stars_request(
        recipient_id=recipient_id,
        quantity=quantity
      )
      
      if init_data.error:
        return ApiResult.fail(init_data.error)
      
      buy_transaction = self.get_buy_stars_link(
        account=wallet_account,
        req_id=init_data.data.req_id
      )
      
      if buy_transaction.error:
        return ApiResult.fail(buy_transaction.error)
      
      return ApiResult.ok(data=buy_transaction.data)
    except StarsOperationError:
      raise
  
  async def buy_stars(self, username: str, quantity: int) -> ApiResult[str]:
    try:
      recipient = self.search_stars_recipient(recipient_username=username)
      if recipient.error:
        return ApiResult.fail(recipient.error)
      wallet_account = self._wallet.get_wallet_data()
      transaction = self.create_stars_transaction(recipient_id=recipient.data.recipient_id, quantity=quantity, wallet_account=wallet_account)
      
      if transaction.error:
        return ApiResult.fail(transaction.error)

      transaction_msg = transaction.data.messages[0]
      tx_hash = await self._wallet.process_transaction(
        destination=transaction_msg.address,
        amount=transaction_msg.amount,
        body=transaction_msg.payload
      )
      
      return ApiResult.ok(data=tx_hash)
    except WalletBalanceInsufficient as error:
      return ApiResult.fail(error=error)
    except StarsOperationError:
      raise