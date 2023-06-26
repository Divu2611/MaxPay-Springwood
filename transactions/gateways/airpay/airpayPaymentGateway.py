# AirPay class manage all functionalities of AirPay Payment Gateway
class AirPay:
    MERCHANT_ID = str()
    USERNAME = str()
    PASSWORD = str()
    API_KEY = str()

    """
    Class constructor

    Parameters of the function:
    * mid - Merchant Id
    * username - Username
    * password - Password
    * apiKey - API Key
    """

    def __init__(self, mid, username, password, apiKey):
        self.MERCHANT_ID = mid
        self.USERNAME = username
        self.PASSWORD = password
        self.API_KEY = apiKey

    """
    """

    def initiatePaymentAPI(self, params):
        from . import payment

        result = payment.initiatePayment(
            params=params,
            mid=self.MERCHANT_ID,
            username=self.USERNAME,
            password=self.PASSWORD,
            apiKey=self.API_KEY,
        )
        return result
