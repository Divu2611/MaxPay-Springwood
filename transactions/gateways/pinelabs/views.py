# Importing Libraries
import os
from dotenv import load_dotenv

from .pinelabs_payment_gateway import Pinelabs

load_dotenv()


def initiate_transaction_pinelabs(request):
    MERCHANT_ID = os.getenv("PINELABS_MID")
    MERCHANT_ACCESS_KEY = os.getenv("PINELABS_PASSOWRD")
    MERCHANT_SECRET_KEY = os.getenv("PINELABS_SECRET_KEY")

    pinelabs = Pinelabs(
        mid=MERCHANT_ID,
        password=MERCHANT_ACCESS_KEY,
        secret_key=MERCHANT_SECRET_KEY,
        env="test",
    )

    transaction_details = {
        "txnid": request.session.get("Reference ID"),
        "redirectURL": request.session.get("Redirect URL"),
        "payment_mode": request.session.get("Payment Mode"),
        "amount": request.session.get("Amount"),
        "productinfo": request.session.get("Product Information"),
        "firstname": request.session.get("First Name"),
        "calling_code": "+91", # As of now
        "phone": request.session.get("Phone Number"),
        "email": request.session.get("Email ID"),
        "card_number": request.session.get("Card Number"),
        "cvv": request.session.get("CVV"),
        "card_holder_name": request.session.get("Holder Name"),
        "card_expiry_month": request.session.get("Expiry Month"),
        "card_expiry_year": request.session.get("Expiry Year"),
        "is_card_to_be_saved": request.session.get("Is Card to be saved"),
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
        "udf6": request.session.get("UDF6"),
        "udf7": request.session.get("UDF7"),
        "udf8": request.session.get("UDF8"),
        "udf9": request.session.get("UDF9"),
        "udf10": request.session.get("UDF10"),
    }


    response = pinelabs.initiatePaymentAPI(transaction_details)
    return response
