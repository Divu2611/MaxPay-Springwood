# Importing Python Libraries.
import os
import json
import requests
from dotenv import load_dotenv
from rest_framework import status

# Importing Project Files.
import common

load_dotenv()

"""
"""


def initiatePayment(params, key, env):
    try:
        result = _payment(
            data=params,
            key=key,
            env=env,
        )
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


def _payment(data, key, env):
    # get credentials based on enviroment like (env = 'test' or env = 'prod').
    credentials = _getCredentials(env=env)

    # get the auth token.
    authTokenResult = _getAuthToken(key=key)
    authToken = authTokenResult["token"]

    # process to place the order - get the orderId.
    orderResult = _order(data=data, token=authToken)
    orderId = orderResult["id"]

    if data["paymentMode"] == "Card":
        integrationId = credentials["Card"]

        # process to start the payment - get the payment token.
        payResult = _pay(
            data=data, token=authToken, orderId=orderId, integrationId=integrationId
        )
        payToken = payResult["token"]

        # process to pay using card.
        result = _pay_using_card(token=payToken)
    elif data["paymentMode"] == "Wallet":
        integrationId = credentials["Wallet"]

        # process to start the payment - get the payment token.
        payResult = _pay(
            data=data, token=authToken, orderId=orderId, integrationId=integrationId
        )
        payToken = payResult["token"]

        # process to pay using wallet.
        result = _pay_using_wallet(data=data, token=payToken, env=env)
    return result


"""
"""


def _getCredentials(env):
    credentials = {"Card": None, "Wallet": None, "Kiosk": None}

    if env == "test":
        credentials["Card"] = os.getenv("PAYMOB_CARD_INTEGRATION_ID_STAGING")
        credentials["Wallet"] = os.getenv("PAYMOB_WALLET_INTEGRATION_ID_STAGING")
        credentials["Kiosk"] = os.getenv("PAYMOB_KIOSK_INTEGRATION_ID_STAGING")
    elif env == "prod":
        credentials["Card"] = os.getenv("PAYMOB_CARD_INTEGRATION_ID_PRODUCTION")
        credentials["Wallet"] = os.getenv("PAYMOB_WALLET_INTEGRATION_ID_PRODUCTION")
        credentials["Kiosk"] = os.getenv("PAYMOB_KIOSK_INTEGRATION_ID_PRODUCTION")
    return credentials


"""
"""


def _getAuthToken(key):
    url = "https://accept.paymob.com/api/auth/tokens"

    payload = {
        "api_key": key,
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
    }

    response = requests.post(url=url, json=payload, headers=headers)
    response = json.loads(response.text)

    return response


"""
"""


def _order(data, token):
    url = "https://accept.paymob.com/api/ecommerce/orders"

    payload = {
        "auth_token": token,
        "delivery_needed": "false",  # True - Delivery by paymob's accept's delivery service.
        "amount_cents": data["amount"],  # Amount in cents.
        "merchant_order_id": data["referenceId"],
        "items": [
            {
                "name": data["productInformation"],
                "amount_cents": data["amount"],
                "description": data["purposeMessage"],
            }
        ],
    }

    headers = {"accept": "application/json", "content-type": "application/json"}

    response = requests.post(url=url, json=payload, headers=headers)
    response = json.loads(response.text)

    return response


"""
"""


def _pay(data, token, orderId, integrationId):
    url = "https://accept.paymob.com/api/acceptance/payment_keys"

    payload = {
        "auth_token": token,
        "amount_cents": data["amount"],
        "expiration": 900,  # Set expiration to 900 seconds (15 minutes).
        "order_id": orderId,
        "billing_data": {
            "apartment": "NA",
            "email": data["emailId"],
            "floor": "NA",
            "first_name": data["firstName"],
            "street": "NA",
            "building": "NA",
            "phone_number": data["callingCode"] + data["phoneNumber"],
            "shipping_method": "NA",
            "postal_code": "NA",
            "city": "NA",
            "country": "NA",
            "last_name": data["lastName"],
            "state": "NA",
        },
        "currency": "EGP",
        "integration_id": integrationId,
    }

    headers = {"accept": "application/json", "content-type": "application/json"}

    response = requests.post(url=url, json=payload, headers=headers)
    response = json.loads(response.text)

    return response


"""
"""


def _pay_using_card(token):
    iFrameId = os.getenv("PAYMOB_CARD_IFRAME_ID_STAGING")

    url = "https://accept.paymobsolutions.com/api/acceptance/iframes/{}?payment_token={}".format(
        iFrameId, token
    )

    return url


"""
"""


def _pay_using_wallet(data, token, env):
    url = "https://accept.paymob.com/api/acceptance/payments/pay"

    identifier = data["phoneNumber"] if env == "prod" else "01010101010"
    payload = {
        "source": {"identifier": identifier, "subtype": "WALLET"},
        "payment_token": token,
    }

    headers = {"accept": "application/json", "content-type": "application/json"}

    response = requests.post(url=url, json=payload, headers=headers)
    response = json.loads(response.text)

    return response
