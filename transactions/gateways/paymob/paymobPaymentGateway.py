# Paymob class manage all functionalities of Paymob Payment Gateway
class Paymob:
    API_KEY = str()
    ENV = str()

    """
    Class constructor

    Parameters of the function:
    * key - API KEY
    * env - Environment ('test' or 'prod')
    """

    def __init__(self, key, env):
        self.API_KEY = key
        self.ENV = env

    """
    """

    def initiatePaymentAPI(self, params):
        from . import payment

        result = payment.initiatePayment(params=params, key=self.API_KEY, env=self.ENV)
        return result
