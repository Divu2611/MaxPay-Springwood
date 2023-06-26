# YooMoney class manage all functionalities of YooMoney Payment Gateway.
class YooMoney:
    SHOP_ID = str()
    SECRET_KEY = str()
    ENV = str()

    """
    Class Constructor

    Parameters of the function:
    * id - Shop Id
    * secretKey - Secret Key
    * env - Environment ('test' or 'prod')
    """

    def __init__(self, id, secretKey, env):
        self.SHOP_ID = id
        self.SECRET_KEY = secretKey
        self.ENV = env

    """
    """

    def initiatePaymentAPI(self, params):
        from . import payment

        result = payment.initiatePayment(
            params=params,
            shopId=self.SHOP_ID,
            secretKey=self.SECRET_KEY,
            env=self.ENV,
        )

        return result
