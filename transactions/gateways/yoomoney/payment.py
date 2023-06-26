# Importing Python Libraries.
import uuid
from rest_framework import status

# Importing Project Files.
import common

# Importing YooMoney Libraries.
from yookassa import Configuration, Payment
from yookassa.domain.models.currency import Currency

"""
"""


def initiatePayment(params, shopId, secretKey, env):
    try:
        result = _payment(data=params, shopId=shopId, secretKey=secretKey, env=env)
        return result
    except Exception as exception:
        statusCode = status.HTTP_500_INTERNAL_SERVER_ERROR
        title = "Internal Server Error"
        message = "Internal Server Error. Please try again after sometime. If the problem persists, please drop a mail to tech@max-payments.com."

        # 500 - Internal Server Error.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )


"""
"""


def _payment(data, shopId, secretKey, env):
    data["shopId"] = shopId
    data["secretKey"] = secretKey

    # process the start the payment.
    payResult = _pay(data=data)
    return payResult


"""
"""


def _pay(data):
    # Authentication.
    Configuration.account_id = data["shopId"]
    Configuration.secret_key = data["secretKey"]

    # Generating the idempotenceKey.
    idempotenceKey = str(uuid.uuid4())

    # Creating the payment object for payment request.
    paymentObject = {
        "amount": {
            "value": data["amount"],
            "currency": Currency.RUB,
        },
        "confirmation": {
            "type": "redirect",
            "return_url": data["redirectURL"],
        },
        "description": data["purposeMessage"],
    }
    if data["paymentMode"]: # Adding a new field of payment method in payment object if paymentMode is present in the request to MaxPay.
        paymentObject["payment_method_data"] = {"type": "bank_card"}

    # Creating the payment request.
    payment = Payment.create(
        paymentObject,
        idempotenceKey,
    )

    # Returning the response payment object.
    return payment
