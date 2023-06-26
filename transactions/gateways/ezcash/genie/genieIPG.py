# Genie class manages all functionalities of Genie Payment Gateway.
class Genie:
    API_KEY = str()
    REDIRECT_URL = str()
    ENV = str()

    """
    Class constructor

    Parameters of the function:
    * apiKey - API Key
    * redirectURL - Redirect URL
    * env - Environment ('test' or 'prod')
    """

    def __init__(self, apiKey, redirectURL, env):
        self.API_KEY = apiKey
        self.REDIRECT_URL = redirectURL
        self.ENV = env

    """
    """

    def initiatePaymentAPI(self, params):
        from . import payment

        result = payment.initiatePayment(
            params=params,
            apiKey=self.API_KEY,
            redirectURL=self.REDIRECT_URL,
            env=self.ENV,
        )

        return result
