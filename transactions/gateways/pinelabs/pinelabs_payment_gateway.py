# Pinelabs class manages all the functionalities of Pinelabs payment gateway
class Pinelabs:
    MID = str()
    PASSWORD = str()
    SECRET_KEY = str()
    ENV = str()

    """
    *
    * initialised private variable for setup pinelabs payment gateway.
    *
    * @param  string key - holds the merchant key.
    * @param  string salt - holds the merchant salt key.
    * @param  string env - holds the env(enviroment). 
    *
    """

    def __init__(self, mid, password, secret_key, env):
        self.MID = mid
        self.PASSWORD = password
        self.SECRET_KEY = secret_key
        self.ENV = env

    def initiatePaymentAPI(self, params):
        from . import payment

        result = payment.initiate_payment(
            params=params,
            mid=self.MID,
            access_code=self.PASSWORD,
            secret_key=self.SECRET_KEY,
            env=self.ENV,
        )
        return result
