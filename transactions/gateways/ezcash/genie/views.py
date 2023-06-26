# Importing Python Libraries
import os
from dotenv import load_dotenv

# Importing Project Files.
from .genieIPG import Genie

load_dotenv()

# Reading Environment Variables.
API_KEY = os.getenv("eZCASH_GENIE_API_KEY")
REDIRECT_URL = (
    os.getenv("eZCASH_REDIRECT_URL_PRODUCTION")
    if os.getenv("ENV") == "production"
    else os.getenv("eZCASH_REDIRECT_URL_STAGING")
)
ENV = "prod" if os.getenv("ENV") == "production" else "test"

genie = Genie(apiKey=API_KEY, redirectURL=REDIRECT_URL, env=ENV)


def initiateTransactionGenie(data):
    transactionDetails = {
        "referenceId": data["referenceId"],
        "amount": data["amount"],
    }

    # initiating the transaction.
    finalResult = genie.initiatePaymentAPI(params=transactionDetails)
    return finalResult
