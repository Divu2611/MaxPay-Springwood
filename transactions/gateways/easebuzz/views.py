# Importing Libraries
import os
import time
import json
from dotenv import load_dotenv

from .easebuzz_payment_gateway import Easebuzz

load_dotenv()


# Initiating the transaction using PayU payment gateway
def initiate_transaction_easebuzz(request):
    MERCHANT_KEY = os.getenv("EASEBUZZ_MERCHANT_KEY")
    SALT = os.getenv("EASEBUZZ_MERCHANT_SALT")
    ENV = "test"

    surl = os.getenv("EASEBUZZ_SURL")
    furl = os.getenv("EASEBUZZ_FURL")

    easebuzz = Easebuzz(MERCHANT_KEY, SALT, ENV)

    transaction_details = {
        "txnid": request.session.get("Reference ID"),
        "firstname": request.session.get("First Name"),
        "phone": request.session.get("Phone Number"),
        "email": request.session.get("Email ID"),
        "amount": request.session.get("Amount"),
        "productinfo": request.session.get("Product Information"),
        "surl": surl,
        "furl": furl,
        "show_payment_mode": request.session.get("PG"),
        # 'city': 'Test',
        # 'zipcode': '123123',
        # 'address2': 'Test',
        # 'state': 'Test',
        # 'address1': 'Test',
        # 'country': 'Test',
        "udf1": request.session.get("UDF1"),
        "udf2": request.session.get("UDF2"),
        "udf3": request.session.get("UDF3"),
        "udf4": request.session.get("UDF4"),
        "udf5": request.session.get("UDF5"),
    }

    # Creating request and recording response
    final_response = easebuzz.initiatePaymentAPI(transaction_details)
    result = json.loads(final_response)
    return result
