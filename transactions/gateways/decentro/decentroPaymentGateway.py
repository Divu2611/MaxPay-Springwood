# Decentro class manage all functionalities of Decentro Payment Gateway
class Decentro:
    CLIENT_ID = str()
    CLIENT_SECRET = str()
    MODULE_SECRET = str()
    PROVIDER_SECRET = str()
    MVA_ESCROW = str()
    ENV = str()

    """
    Class Constructor

    Parameters of the function:
    * id - Client Id
    * clientSecret - Client Secret
    * moduleSecret - Module Secret
    * providerSecret - Provider Secret
    * payeeAccount - MVA Escrow
    * env - Environment ('test' or 'prod')
    """

    def __init__(
        self, id, clientSecret, moduleSecret, providerSecret, payeeAccount, env
    ):
        self.CLIENT_ID = id
        self.CLIENT_SECRET = clientSecret
        self.MODULE_SECRET = moduleSecret
        self.PROVIDER_SECRET = providerSecret
        self.MVA_ESCROW = payeeAccount
        self.ENV = env

    """
    """

    def initiatePaymentAPI(self, params):
        from . import payment

        result = payment.initiatePayment(
            params=params,
            clientId=self.CLIENT_ID,
            clientSecret=self.CLIENT_SECRET,
            moduleSecret=self.MODULE_SECRET,
            providerSecret=self.PROVIDER_SECRET,
            payeeAccount=self.MVA_ESCROW,
            env=self.ENV,
        )

        return result

    """
    """

    def generatePaymentLink(self, params):
        from . import payment

        result = payment.paymentLink(
            params=params,
            clientId=self.CLIENT_ID,
            clientSecret=self.CLIENT_SECRET,
            moduleSecret=self.MODULE_SECRET,
            providerSecret=self.PROVIDER_SECRET,
            payeeAccount=self.MVA_ESCROW,
            env=self.ENV,
        )
        return result
