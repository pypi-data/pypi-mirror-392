from enum import Enum

class FragmentMethod(Enum):
  INIT_BUY_STARS = 'initBuyStarsRequest'
  GET_BUY_STARS_LINK = 'getBuyStarsLink'
  SEARCH_STARS_RECIPIENT = 'searchStarsRecipient'
  
  INIT_GIFT_PREMIUM = 'initGiftPremiumRequest'
  GET_GIFT_PREMIUM_LINK = 'getGiftPremiumLink'
  SEARCH_PREMIUM_RECIPIENT = 'searchPremiumGiftRecipient'
  
  INIT_ADS_TOPUP = 'initAdsTopupRequest'
  GET_ADS_TOPUP_LINK = 'getAdsTopupLink'
  SEARCH_ADS_RECIPIENT = 'searchAdsTopupRecipient'