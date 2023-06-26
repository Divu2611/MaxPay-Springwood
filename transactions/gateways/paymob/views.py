# Import Python Libraries
import os
from dotenv import load_dotenv

# Importing Project Files
from .paymobPaymentGateway import Paymob

load_dotenv()

# Reading environment credentials
API_KEY = os.getenv("PAYMOB_API_KEY")

env = "test" if os.getenv("ENV") == "staging" else "prod"
paymob = Paymob(key=API_KEY, env="test")

"""
"""


def initiateTransactionPayMob(data):
    transactionDetails = {
        "referenceId": data["referenceId"],
        "firstName": data["firstName"],
        "lastName": data["lastName"],
        "callingCode": data["callingCode"],
        "phoneNumber": data["phoneNumber"],
        "emailId": data["emailId"],
        "amount": data["amount"],
        "productInformation": data["productInformation"],
        "purposeMessage": "Paymentfor{}".format(data["productInformation"]),
        "paymentMode": data["paymentMode"],
    }

    # initiating the transaction.
    finalResult = paymob.initiatePaymentAPI(params=transactionDetails)
    return finalResult
