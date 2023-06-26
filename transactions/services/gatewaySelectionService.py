# Importing Python Libraries.
from rest_framework import status

# Importing Project files.
import common

"""
As on 16th June, 2023 - the business logic is as follows:
* If merchant hosted checkout (payment mode in request) -
    If paymentMode is UPI - selected gateway is Decentro.
    If paymentMode is Card -
        If customer is from Sri Lankda - selected gateway is eZCash (Genie).
        If customer is from Egypt - selected gateway is PayMob.
        If customer is from Russia - selected gateway is YooMoney.
    If paymentMode is Wallet - selected gateway is PayMob.
    If paymentMode is either Easypaisa or JazzCash or the customer is from Pakistan - selected gateway is ItzPay.
* If maxpay hosted checkout (payment mode not in request) -
    If customer is from India - selected gateway is AirPay.
    If customer is from Russia - selected gateway is YooMoney.


selectGateway: selects the appropriate payment gateway based on customer's location and selected payment mode.
Parameters of the function:
* data (type dictionary) - holds all the data posted by the client, required information from the data - paymentMode and countryCode.

Return values of the function:
* gateway (type dictionary) - returns the appropriate gateway based on customer's location and selected payment mode.
"""


def selectGateway(data):
    # Setting a flag value to True.
    gatewayAvailable = True

    if "paymentMode" in data:  # Merchant Hosted.
        if data["paymentMode"] == "UPI":  # Payment Mode is UPI.
            gateway = "Decentro"
        elif data["paymentMode"] == "Card":  # Payment Mode is Card.
            if data["countryCode"] == "144":  # Country is Sri Lanka.
                gateway = "eZCash - Genie"
            elif data["countryCode"] == "818":  # Country is Egypt.
                gateway = "Paymob"
            elif data["countryCode"] == "643":  # Country is Russia.
                gateway = "YooMoney"
            else:
                # No payment gateway available for card payment for rest of countries.
                gatewayAvailable = False
        elif data["paymentMode"] == "Wallet":  # Payment Mode is Wallet.
            gateway = "Paymob"
        elif (
            data["paymentMode"] in ["Easypaisa", "JazzCash"]
            or data["countryCode"] == "586"
        ):  # Payment Mode is either Easypaisa or JazzCash or the country is Pakistan.
            gateway = "ItzPay"
        else:
            # No payment gateway available for rest of payment modes.
            gatewayAvailable = False
    else:
        # MaxPay Hosted.
        if data["countryCode"] == "356":  # Country is India.
            gateway = "AirPay"
        elif data["countryCode"] == "643":  # Country is Russia.
            gateway = "YooMoney"
        else:
            # No payment gateway available for rest of countries.
            gatewayAvailable = False

    if gatewayAvailable:
        statusCode = status.HTTP_302_FOUND
        title = "Gateway Found"
        message = gateway

        # 302 - Found.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )
    else:
        statusCode = status.HTTP_503_SERVICE_UNAVAILABLE
        title = "Gateway Not Found"
        message = "Appropriate payment gateway service for selected location and payment mode is not available"

        # 503 - Service Unavailable.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )
