from .utils.extract_photo_src import extract_photo_src
from .errors import FragmentAPIError, AdsOperationError, WalletBalanceInsufficient
from .methods import FragmentMethod
from .models import (
  ApiResult,
  InitPurchaseResponseData,
  TransactionMessage,
  Transaction,
  SearchRecipientResponseData
)

class FragmentAdsAPI:
  def __init__(self, client: "FragmentClient") -> None:
    self._client = client
    self._wallet = self._client._ctx.wallet
  
  def init_ads_topup_request(self, recipient_id, amount) -> ApiResult[InitPurchaseResponseData]:
    try:
      data, error = self._client.send_fragment_request(
        method=FragmentMethod.INIT_ADS_TOPUP,
        body={ 'recipient': recipient_id, 'amount': amount }
      )
      
      if error:
        return ApiResult.fail(f"Failed to initialize Ads topup: {error}")
      
      return ApiResult.ok(
        data=InitPurchaseResponseData(
          req_id=str(data['req_id']),
          amount=str(data['amount'])
        )
      )
    except FragmentAPIError as error:
      raise AdsOperationError(f"Failed to initialize Ads topup: {error}")
  
  def get_ads_topup_link(self, account, req_id) -> ApiResult[Transaction]:
    try:
      data, error = self._client.send_fragment_request(
        method=FragmentMethod.GET_ADS_TOPUP_LINK,
        body={
          'account': account,
          'transaction': '1',
          'id': req_id,
          'show_sender': '0'
        }
      )
      
      if error:
        return ApiResult.fail(f"Failed to obtain Ads topup link: {error}")
      
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
      raise AdsOperationError(f"Failed to obtain Ads topup link: {error}")
  
  def search_ads_topup_recipient(self, recipient_username) -> ApiResult[SearchRecipientResponseData]:
    try:
      data, error = self._client.send_fragment_request(
        method=FragmentMethod.SEARCH_ADS_RECIPIENT,
        body={ 'query': recipient_username }
      )
      
      if error:
        return ApiResult.fail(f"Failed to obtain Ads topup recipient: {error}")
      
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
      raise AdsOperationError(f'Failed to obtain Ads topup recipient: {error}')
  
  def create_premium_transaction(self, recipient_id, amount, wallet_account) -> ApiResult[Transaction]:
    try:
      init_data = self.init_ads_topup_request(recipient_id=recipient_id, amount=amount)
      
      if init_data.error:
        return ApiResult.fail(init_data.error)
      
      topup_transaction = self.get_ads_topup_link(
        account=wallet_account,
        req_id=init_data.data.req_id
      )
      
      if topup_transaction.error:
        return ApiResult.fail(topup_transaction.error)
      
      return ApiResult.ok(data=topup_transaction.data)
    except AdsOperationError:
      raise
  
  async def topup_ads(self, username, amount) -> ApiResult[str]:
    try:
      recipient = self.search_ads_topup_recipient(recipient_username=username)
      if recipient.error:
        return ApiResult.fail(error=recipient.error)
      wallet_account = self._wallet.get_wallet_data()
      transaction = self.create_premium_transaction(
        recipient_id=recipient.data.recipient_id,
        amount=amount,
        wallet_account=wallet_account
      )
      
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
    except AdsOperationError:
      raise