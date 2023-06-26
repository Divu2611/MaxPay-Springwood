# Importing Python Libraries
import json
import requests
import logging
from rest_framework import status

# Importing Project Files
import common

db_logger = logging.getLogger("db")

"""
"""


def initiatePayment(
    params, clientId, clientSecret, moduleSecret, providerSecret, payeeAccount, env
):
    try:
        result = _payment(
            data=params,
            clientId=clientId,
            clientSecret=clientSecret,
            moduleSecret=moduleSecret,
            providerSecret=providerSecret,
            payeeAccount=payeeAccount,
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


def paymentLink(
    params, clientId, clientSecret, moduleSecret, providerSecret, payeeAccount, env
):
    try:
        result = _link(
            data=params,
            clientId=clientId,
            clientSecret=clientSecret,
            moduleSecret=moduleSecret,
            providerSecret=providerSecret,
            payeeAccount=payeeAccount,
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


def _payment(
    data, clientId, clientSecret, moduleSecret, providerSecret, payeeAccount, env
):
    # get URL based on enviroment like (env = 'test' or env = 'prod').
    URL = _getURL(env=env)

    data["clientId"] = clientId
    data["clientSecret"] = clientSecret
    data["moduleSecret"] = moduleSecret
    data["providerSecret"] = providerSecret
    data["payeeAccount"] = payeeAccount

    # UPI-ID Validation.
    upiValidationResult = _verifyUPI(data=data, url=URL)
    if upiValidationResult != True:
        return upiValidationResult

    # process the start the payment.
    payResult = _pay(data=data, url=URL)
    return payResult


"""
"""


def _link(
    data, clientId, clientSecret, moduleSecret, providerSecret, payeeAccount, env
):
    # get URL based on enviroment like (env = 'test' or env = 'prod').
    URL = _getURL(env=env)

    data["clientId"] = clientId
    data["clientSecret"] = clientSecret
    data["moduleSecret"] = moduleSecret
    data["providerSecret"] = providerSecret
    data["payeeAccount"] = payeeAccount

    # process to generate link.
    generateResult = _generate(data=data, url=URL)
    return generateResult


"""
"""


def _getURL(env):
    urlLink = None

    if env == "test":
        urlLink = "https://in.staging.decentro.tech"
    elif env == "prod":
        urlLink = "https://in.decentro.tech"
    else:
        urlLink = "https://in.staging.decentro.tech"
    return urlLink


"""
"""


def _verifyUPI(data, url):
    payload = {
        "reference_id": data["referenceId"],
        "upi_id": data["upiId"],
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "client_id": data["clientId"],
        "client_secret": data["clientSecret"],
        "module_secret": data["moduleSecret"],
        "provider_secret": data["providerSecret"],
    }

    # Adding an info log showing the UPI-ID of customer which is needed to be verified.
    db_logger.info(
        "UPI-ID to be verified: {}.\nReference ID: {}.".format(
            data["upiId"], payload["reference_id"]
        )
    )

    response = requests.post(
        url + "/v2/payments/vpa/validate", json=payload, headers=headers
    )
    response = json.loads(response.text)

    # Adding a info log showing the response from Decentro's UPI API.
    db_logger.info(
        "Response from Decentro's UPI API: {}.\nReference ID: {}.".format(
            response, payload["reference_id"]
        )
    )

    if response["status"] == "FAILURE":
        # Adding a warning log showing that customer's UPI-ID is invalid.
        db_logger.warning(
            "Invalid UPI-ID: {}.\nReference ID: {}".format(
                data["upiId"], payload["reference_id"]
            )
        )

        if response["responseCode"] == "E00009":
            # UPI-ID validation failed.
            return common.generatingResponse(
                statusCode=status.HTTP_401_UNAUTHORIZED,
                title="Invalid upiId",
                message=response["message"],
            )
        else:
            # Internal Server Error.
            raise Exception

    # Adding a info log showing that customer's UPI-ID is valid.
    db_logger.info(
        "Valid UPI-ID: {}.\nReference ID: {}".format(
            data["upiId"], payload["reference_id"]
        )
    )

    return True


"""
"""


def _pay(data, url):
    payload = {
        "reference_id": data["referenceId"],
        "payer_upi": data["upiId"],
        "payee_account": data["payeeAccount"],
        "amount": float(data["amount"]),
        "purpose_message": data["purposeMessage"],
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "client_id": data["clientId"],
        "client_secret": data["clientSecret"],
        "module_secret": data["moduleSecret"],
        "provider_secret": data["providerSecret"],
    }

    # Adding an info log showing that MaxPay is about to make the POST request to Decentro's payment API.
    db_logger.info(
        "About to make the POST request to Decentro's payment API.\nPayload: {}.".format(
            payload
        )
    )

    response = requests.post(
        url + "/v2/payments/collection", json=payload, headers=headers
    )
    response = json.loads(response.text)

    # Adding a info log showing the response from Decentro's payment API.
    db_logger.info(
        "Response from Decentro's Payment API: {}.\nReference ID: {}".format(
            response, payload["reference_id"]
        )
    )

    if response["status"] == "FAILURE":
        # Adding a warning log showing that payment API failed.
        db_logger.warning(
            "Unable to process the transaction.\nPossible reason for error: {}.\nReference ID: {}".format(
                response, payload["reference_id"]
            )
        )

        # Internal Server Error.
        raise Exception

    # Adding a info log showing that payment API succedded.
    db_logger.info(
        "Transacion processed successfully.\nResponse : {}.\nReference ID: {}".format(
            response, payload["reference_id"]
        )
    )

    return response


"""
"""


def _generate(data, url):
    payload = {
        "reference_id": data["referenceId"],
        "payee_account": data["payeeAccount"],
        "amount": float(data["amount"]),
        "purpose_message": data["purposeMessage"],
        "generate_qr": 1,  # This will generate the QR code.
        "generate_uri": 1,  # This will generate a seperate link for famous PSP apps like GPay, PhonePe and PayTM.
        "expiry_time": 15,  # Link will expire after 15 minutes.
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "client_id": data["clientId"],
        "client_secret": data["clientSecret"],
        "module_secret": data["moduleSecret"],
        "provider_secret": data["providerSecret"],
    }

    # Adding an info log showing that MaxPay is about to make the POST request to Decentro's intent API.
    db_logger.info(
        "About to make the POST request to Decentro's intent API.\nPayload: {}.".format(
            payload
        )
    )

    response = requests.post(
        url + "/v2/payments/upi/link", json=payload, headers=headers
    )
    response = json.loads(response.text)

    # Adding a info log showing the response from Decentro's intent API.
    db_logger.info(
        "Response from Decentro's Intent API: {}.\nReference ID: {}.".format(
            response, payload["reference_id"]
        )
    )

    if response["status"] == "FAILURE":
        # Adding a warning log showing that intent API failed.
        db_logger.warning(
            "Unable to generate the intent flow link.\nPossible reason for error: {}.\nReference ID: {}".format(
                response, payload["reference_id"]
            )
        )

        # Internal Server Error.
        raise Exception

    # Adding a info log showing that intent API succedded.
    db_logger.info(
        "Intent flow link generated successfully.\nResponse : {}.\nReference ID: {}".format(
            response, payload["reference_id"]
        )
    )

    return response
