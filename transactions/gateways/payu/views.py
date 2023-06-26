# Importing Libraries
import os
import time
import requests
from dotenv import load_dotenv

import common

load_dotenv()


# Initiating the transaction using PayU payment gateway
def initiate_transaction_payu(request):
    api = os.getenv("PAYU_API")
    key = os.getenv("PAYU_MERCHANT_KEY")
    salt = os.getenv("PAYU_MERCHANT_SALT")

    surl = os.getenv("PAYU_SURL")
    furl = os.getenv("PAYU_FURL")

    request_to_pg = (
        key
        + "|"
        + request.session.get("Reference ID")
        + "|"
        + request.session.get("Amount")
        + "|"
        + request.session.get("Product Information")
        + "|"
        + request.session.get("First Name")
        + "|"
        + request.session.get("Email ID")
        + "|"
        + request.session.get("UDF1")
        + "|"
        + request.session.get("UDF2")
        + "|"
        + request.session.get("UDF3")
        + "|"
        + request.session.get("UDF4")
        + "|"
        + request.session.get("UDF5")
        + "|"
        + request.session.get("UDF6")
        + "|"
        + request.session.get("UDF7")
        + "|"
        + request.session.get("UDF8")
        + "|"
        + request.session.get("UDF9")
        + "|"
        + request.session.get("UDF10")
        + "|"
        + salt
    )
    # Generating hash value (to inititate transaction) of the user data using all the UDFs
    hash = common.generate_hash(request_to_pg)

    # Generating Payload
    payload = (
        "key="
        + key
        + "&txnid="
        + request.session.get("Reference ID")
        + "&amount="
        + request.session.get("Amount")
        + "&firstname="
        + request.session.get("First Name")
        + "&email="
        + request.session.get("Email ID")
        + "&phone="
        + request.session.get("Phone Number")
        + "&productinfo="
        + request.session.get("Product Information")
        + "&pg="
        + request.session.get("PG")
        + "&bankcode="
        + request.session.get("Bank Code")
        + "&ccnum="
        + request.session.get("Card Number")
        + "&ccexpmon="
        + request.session.get("Expiry Month")
        + "&ccexpyr="
        + request.session.get("Expiry Year")
        + "&ccvv="
        + request.session.get("CV")
        + "&surl="
        + surl
        + "&furl="
        + furl
        + "&udf1="
        + request.session.get("UDF1")
        + "&udf2="
        + request.session.get("UDF2")
        + "&udf3="
        + request.session.get("UDF3")
        + "&udf4="
        + request.session.get("UDF4")
        + "&udf5="
        + request.session.get("UDF5")
        + "&udf6="
        + request.session.get("UDF6")
        + "&udf7="
        + request.session.get("UDF7")
        + "&udf8="
        + request.session.get("UDF8")
        + "&udf9="
        + request.session.get("UDF9")
        + "&udf10="
        + request.session.get("UDF10")
        + "&hash="
        + hash
    )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Creating request and recording response
    response = requests.request("POST", api, data=payload, headers=headers)

    return response
