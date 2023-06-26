# Importing Python Libraries.
import json
import requests
from rest_framework import status

# Importing Project Files.
import common

"""
"""


def initiatePayment(params, apiKey, redirectURL, env):
    try:
        result = _payment(
            data=params,
            apiKey=apiKey,
            redirectURL=redirectURL,
            env=env,
        )
        return result
    except:
        statusCode = status.HTTP_500_INTERNAL_SERVER_ERROR
        title = "Internal Server Error"
        message = "Internal Server Error. Please try again after sometime. If the problem persists, please drop a mail to tech@max-payments.com."

        # 500 - Internal Server Error.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )


"""
"""


def _payment(data, apiKey, redirectURL, env):
    # get URL based on enviroment like (env = 'test' or env = 'prod').
    URL = _getURL(env=env)

    data["apiKey"] = apiKey
    data["redirectURL"] = redirectURL

    # process the start the payment.
    payResult = _pay(data=data, url=URL)
    return payResult


"""
"""


def _getURL(env):
    urlLink = None

    if env == "test":
        urlLink = "https://api.uat.geniebiz.lk"
    elif env == "prod":
        urlLink = "https://api.geniebiz.lk"
    else:
        urlLink = "https://api.uat.geniebiz.lk"

    return urlLink


"""
"""


def _pay(data, url):
    payload = {
        "amount": int(float(data["amount"])),
        "currency": "LKR",
        "redirectUrl": data["redirectURL"],
        "customerReference": data["referenceId"],
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": data["apiKey"],
    }

    response = requests.post(
        url + "/public/v2/transactions", json=payload, headers=headers
    )
    response = json.loads(response.text)

    return response
