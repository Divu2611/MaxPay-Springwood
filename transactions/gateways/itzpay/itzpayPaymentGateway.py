# ItzPay class manage all functionalities of ItzPay Payment Gateway
class ItzPay:
    CLIENT_ID = str()
    CLIENT_SECRET = str()
    SECRET_KEY = str()
    ENV = str()

    """
    Class constructor

    Parameters of the function:
    * id - Client Id
    * secret - Client Secret Key
    * key - Secret Key (to generate checksum)
    """

    def __init__(self, id, secret, key, env):
        self.CLIENT_ID = id
        self.CLIENT_SECRET = secret
        self.SECRET_KEY = key
        self.ENV = env

    """
    """

    def initiatePaymentAPI(self, params):
        from . import payment

        result = payment.initiatePayment(
            params=params,
            clientId=self.CLIENT_ID,
            clientSecret=self.CLIENT_SECRET,
            secretKey=self.SECRET_KEY,
            env=self.ENV,
        )

        return result
