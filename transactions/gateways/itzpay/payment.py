# Importing Python Libraries.
import json
import requests
from rest_framework import status

# Importing Project Files.
import common

"""
"""


def initiatePayment(params, clientId, clientSecret, secretKey, env):
    try:
        response = _payment(
            data=params,
            clientId=clientId,
            clientSecret=clientSecret,
            secretKey=secretKey,
            env=env,
        )
        return response
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


def _payment(data, clientId, clientSecret, secretKey, env):
    data["clientId"] = clientId
    data["clientSecret"] = clientSecret
    data["secretKey"] = secretKey

    # get the access token.
    accessToken = _getAccessToken(data=data, env=env)
    accessToken = json.loads(accessToken.text)["access_token"]

    # process the start the payment.
    payResult = _pay(data=data, accessToken=accessToken, env=env)
    return payResult


"""
"""


def _getAccessToken(data, env):
    # get URL for access token, based on enviroment like (env = 'test' or env = 'prod').
    url = _getURL(env=env, task="auth")

    payload = {
        "grant_type": "client_credentials",
        "client_id": data["clientId"],
        "client_secret": data["clientSecret"],
    }

    headers = {"content-type": "application/x-www-form-urlencoded"}

    response = requests.post(url=url + "/connect/token", data=payload, headers=headers)

    return response


"""
"""


def _pay(data, accessToken, env):
    # get URL for payment, based on enviroment like (env = 'test' or env = 'prod').
    url = _getURL(env=env, task="api")

    paymentMode = data["paymentMode"]
    if paymentMode == "Easypaisa":
        channelId = 8  # channelId will be 8, if paymentMode is 'Easypaisa'.
    elif paymentMode == "JazzCash":
        channelId = 10  # channelId will be 10, if paymentMode is 'JazzCash'.

    payload = {
        "customerTransactionId": data["referenceId"],
        "clientId": data["clientId"],
        "categoryId": 2,
        "channelId": channelId,
        "item": data["productInformation"],
        "amount": int(float(data["amount"])),  # Amount is in PKR.
        "msisdn": data["phoneNumber"],
        "cnic": data["cnic"],  # Unique Identification number for a citizen of Pakistan.
        "email": data["emailId"],
    }

    headers = {"Authorization": "Bearer " + accessToken}

    response = requests.post(
        url=url + "/gateway/payin/purchase/ewallet", json=payload, headers=headers
    )
    response = json.loads(response.text)

    if response["status"] == "failed":
        # Transaction failed.
        return common.generatingResponse(
            statusCode=status.HTTP_400_BAD_REQUEST,
            title="Failed",
            message=response["message"],
        )

    return response


"""
"""


def _getURL(env, task):
    urlLink = None

    if env == "test":
        urlLink = "https://sandbox-{}.swichnow.com".format(task)
    elif env == "prod":
        urlLink = "https://{}.swichnow.com".format(task)
    else:
        urlLink = "https://sandbox-{}.swichnow.com".format(task)
    return urlLink
