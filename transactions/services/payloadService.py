# Imporing Python Libraries
import re
import time
import logging
from django.conf import settings
from rest_framework import status

# Importing Project Files
import common
import transactions.services.dbService as dbService

db_logger = logging.getLogger("db")

"""
payloadCreator: cleans and prepared the posted data. checks the validations on the posted data.

Parameters of the function:
* data (type dictionary) - holds all the data posted by the client, required for transaction to initiate.

Return values of the function:
response, can be one of the following values -
* postedData (type dictionary) - holds the all posted value after removing space which passed all the validations.
* errorResponse with statusCode 400 (type dictionary) - holds the statusCode, title and message of the response. This can occur if mandatory fields are missing or violates the type rule.
"""


def payloadCreator(data):
    startTime = time.time()

    try:
        postedData = dict()
        # Defining a list of mandatory parameters for initiating transaction.
        mandatoryParameters = [
            "firstName",
            "lastName",
            "callingCode",
            "amount",
            "productInformation",
            "countryCode",
            "currencyCode",
            "redirectURL",
        ]

        # remove white space, prepared postedData.
        postedData = _removeSpaceAndPreparePostData(
            params=data, mandatoryParameters=mandatoryParameters
        )

        # verifies if the countryCode and currencyCode are correct.
        locationValidationResult = _locationValidation(
            countryCode=postedData["countryCode"],
            currencyCode=postedData["currencyCode"],
        )
        if locationValidationResult != True:
            return locationValidationResult

        # empty validation.
        emptyValidationResult = _emptyValidation(
            data=postedData, mandatoryParameters=mandatoryParameters
        )
        if emptyValidationResult != True:
            # atleast one mandatory parameter is empty.

            endTime = time.time() - startTime
            # Analyzing the efficiency of the Service
            serviceEfficiency = settings.PAYLOAD_CREATOR_RESPONSE_TIME
            serviceEfficiency.observe(endTime)

            return emptyValidationResult

        # type validation.
        typeValidationResult = _typeValidation(data=postedData)
        if typeValidationResult != True:
            # atleast one mandatory parameter voilates the type rule.

            endTime = time.time() - startTime
            # Analyzing the efficiency of the Service
            serviceEfficiency = settings.PAYLOAD_CREATOR_RESPONSE_TIME
            serviceEfficiency.observe(endTime)

            return typeValidationResult

        endTime = time.time() - startTime
        # Analyzing the efficiency of the Service
        serviceEfficiency = settings.PAYLOAD_CREATOR_RESPONSE_TIME
        serviceEfficiency.observe(endTime)

        return postedData
    except KeyError as missingParameter:
        # The exception might have occured while removing the space and preparing the post data.
        statusCode = status.HTTP_400_BAD_REQUEST
        title = "Parameters are missing"
        message = "{} in the request message sent to MaxPay might be missing. Kindly check your request parameters.".format(
            missingParameter
        )

        endTime = time.time() - startTime
        # Analyzing the efficiency of the Service
        serviceEfficiency = settings.PAYLOAD_CREATOR_RESPONSE_TIME
        serviceEfficiency.observe(endTime)

        # Adding a warning log showing that required parameters are missing.
        db_logger.warning(
            "Parameters required for transaction initiation ({}) are missing".format(
                missingParameter
            )
        )

        # 400 - Bad Request.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )


"""
_removeSpaceAndPreparePostData: removes white space, and prepared the posted data.

Parameters of the function:
* params (type dictionary) - holds all the data posted by the client, required for transaction to initiate.

Return values of the function:
* postedData (type dictionary) - holds the all posted value after removing space.
"""


def _removeSpaceAndPreparePostData(params, mandatoryParameters):
    # removing unnecessary space from mandatory parameters.
    data = {
        "amount": params["amount"],
        "productInformation": params["productInformation"].strip(),
        "countryCode": params["countryCode"],
        "currencyCode": params["currencyCode"],
        "redirectURL": params["redirectURL"].strip(),
    }

    """
    The following parameters are mandatory from MaxPay point of view: firstName, lastName, emailId and phoneNumber with callingCode
    It is possible that the client will not give all of these, however either emailId or phoneNumber with callingCode must be available.
    """
    if "firstName" in params and params["firstName"]:
        data["firstName"] = params["firstName"].strip()
    else:
        data["firstName"] = "NOT PROVIDED"

    if "lastName" in params and params["firstName"]:
        data["lastName"] = params["lastName"].strip()
    else:
        data["lastName"] = "NOT PROVIDED"

    if "phoneNumber" in params:
        data["callingCode"] = params["callingCode"].strip()
        data["phoneNumber"] = params["phoneNumber"].strip()

    if "emailId" in params:
        data["emailId"] = params["emailId"].strip()

    """
    If paymentMode is provided in the request, depicts that payment is Merchant hosted.
    If no paymentMode, depicts that payment is MaxPay hosted.
    """
    if "paymentMode" in params:
        data["paymentMode"] = params["paymentMode"].strip()

        if data["paymentMode"] == "UPI":
            data["upiChoice"] = params["upiChoice"].strip()
            if data["upiChoice"] == "upiId":
                data["upiId"] = params["upiId"].strip()
            elif "upiApp" in params:
                data["upiApp"] = params["upiApp"].strip()
        elif data["paymentMode"] == "NB":
            pass
        elif data["paymentMode"] == "Card":
            pass
        elif data["paymentMode"] == "Wallet":
            pass

    if params["countryCode"] == "586":
        # removing white spaces from cnic field if country is Pakistan.
        data["cnic"] = params["cnic"].strip()

    # storing remaining data as it is.
    for key, value in params.items():
        if key not in mandatoryParameters:
            data[key] = params[key]

    return data


"""
_locationValidation: verifies if the countryCode and currencyCode provided are correct.

Parameters of the function:
* countryCode (type String) - country code provided by the client in the request
* currencyCode (type String) - currency code provided by the client in the request

Return values of the function:
locationValidationResult, can be one of the following values - 
* errorResponse with status code 400 (type dictionary) - holds the statusCode, title and message of the response. This can occur if either or both countryCode or currencyCode are incorrect.
* True (type boolean) - holds True value if both countryCode and currencyCode are correct.
"""


def _locationValidation(countryCode, currencyCode):
    try:
        locationExists = dbService.getLocation(
            countryCode=countryCode, currencyCode=currencyCode
        )

        if not locationExists:
            statusCode = status.HTTP_400_BAD_REQUEST
            title = "Invalid countryCode or currencyCode"
            message = "countryCode or currencyCode in the request message sent to MaxPay might be incorrect. Kindly check your request parameters."

            # 400 - Bad Request.
            return common.generatingResponse(
                statusCode=statusCode, title=title, message=message
            )

        return locationExists
    except:
        raise Exception("Unable to retrieve the location details from the database.")


"""
_emptyValidation: checks empty validation for mandatory parameters.

Parameters of the function:
* data (type dictionary) - holds all the posted value after removing space, required for transaction to initiate.

Return values of the function:
emptyValidationResult, can be one of the following values -
* errorResponse with status code 400 (type dictionary) - holds the statusCode, title and message of the response. This can occur if one/more mandatory parameters is/are missing from the request parameter.
* True (type boolean) - holds True value if all mandatory parameters are present in the request parameter.
"""


def _emptyValidation(data, mandatoryParameters):
    if "paymentMode" in data:
        if data["paymentMode"] == "UPI":
            # Updating the list of mandatory parameters if payment mode is 'UPI'.
            mandatoryParameters.append("upiChoice")
            if data["upiChoice"] == "upiId":
                # Updating the list of mandatory parameters if selected 'UPI' method is UPI Id.
                mandatoryParameters.append("upiId")
        elif data["paymentMode"] == "NB":
            pass
        elif data["paymentMode"] == "Card":
            # As of 9th June 2023, there are no more mandatory parameters if paymentMode is 'Card'.
            pass
        elif data["paymentMode"] == "Wallet":
            # As of 9th June 2023, there are no more mandatory parameters if paymentMode is 'Wallet'.
            pass

    if not (
        data.get("emailId") or (data.get("phoneNumber")) and data.get("callingCode")
    ):
        statusCode = status.HTTP_400_BAD_REQUEST
        title = "Parameters are missing"
        message = "Both emailId and phoneNumber with callingCode in the request sent to MaxPay might be missing. Kindly check your request parameters and provide atleast one of them."

        # Adding a warning log showing that both emailId and phoneNumber with callingCode are missing.
        db_logger.warning("Both emailId and phoneNumber with callingCode are missing")

        # 400 - Bad Request.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )

    # Setting dummy values if the parameters are not present in the request.
    if not data["emailId"]:
        data["emailId"] = "notmentioned@company.com"
    if not data["phoneNumber"]:
        data["callingCode"] = "+0"
        data["phoneNumber"] = "90000000000"

    if data["countryCode"] == '586':
        # Updating the list of mandatoryParameters. If countryCode is 586 i.e. the country is Pakistan, then cnic is the mandatoryParameter.
        mandatoryParameters.append("cnic")

    # Checking if mandatory parameters are present in the request parameter.
    if not all(data.get(param) for param in mandatoryParameters):
        # one or more mandatory parameters is/are missing from the request parameters.
        missingParameters = [
            params
            for params in mandatoryParameters
            if params in data and (not data[params])
        ]

        statusCode = status.HTTP_400_BAD_REQUEST
        title = "Parameters are missing"
        message = (
            " ".join(map(str, missingParameters))
            + " in the request message sent to MaxPay might be missing. Kindly check your request parameters."
        )

        # Adding a warning log showing that required parameters are missing.
        db_logger.warning(
            "Parameters required for transaction initiation ({}) are missing".format(
                map(str, missingParameters)
            )
        )

        # 400 - Bad Request.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )

    # Returning true if all mandatory parameters are present in the request parameter.
    return True


"""
_typeValidation: checks type validation of mandatory parameters.

Parameters of the function:
* data (type dictionary) - holds all the posted value after removing space, required for transaction to initiate.

Return values of the function:
typeValidationResult, can be one of the following values -
* errorResponse with statusCode 400 (type dictionary) - holds the statusCode, title and message of the response. This can occur if one/more mandatory parameters is/are violating the type validation.
* True (type boolean) - holds True value if all mandatory parameters are follows the type validation.
"""


def _typeValidation(data):
    message = str()
    if not (isinstance(data["firstName"], str)):
        message += "firstName must be a string. "

    if not (isinstance(data["lastName"], str)):
        message += "lastName must be a string. "

    if not (isinstance(data["callingCode"], str)):
        message += "callingCode must be a string. "
    elif not re.match(r"^\+\d+$", data["callingCode"]):
        message += "callingCode must be valid. "

    if not (isinstance(data["phoneNumber"], str)):
        message += "phoneNumber must be a string. "

    if not (isinstance(data["emailId"], str)):
        message += "emailID must be a string. "
    # elif not re.match(
    #     r"^([\w\.-]+)@([\w-]+)\.([\w]{2,8})(\.[\w]{2,8})?", data["emailId"]
    # ):
    #     message += "emailID must be valid. "

    # if not re.match(r"^\d+\.\d{2}$", data["amount"]):
    #     message += "amount must be float up to two decimal. "

    if (
        not (isinstance(data["productInformation"], str))
        or len(data["productInformation"]) > 100
    ):
        message += "productInformation must be a string up to 100 character. "

    # if not (isinstance(data["countryCode"], int)):
    #     message += "countryCode must be integer. "

    # if not (isinstance(data["currencyCode"], int)):
    #     message += "currencyCode must be integer. "

    if not (isinstance(data["redirectURL"], str)):
        message += "redirectURL must be a string. "

    if "paymentMode" in data:
        if not (isinstance(data["paymentMode"], str)):
            message += "paymentMode must be a string. "
        elif (
            not re.match("UPI|Card|NB|Wallet", data["paymentMode"])
            and data["countryCode"] != "586"
        ):  # If countryCode is not 586 i.e. country is not Pakistan, then allowed payment modes are 'UPI', 'Card', 'NB' or 'Wallet'.
            message += (
                "paymentMode must be either 'UPI' or 'Card' or 'NB' or 'Wallet'. "
            )
        elif (
            not re.match("Easypaisa|JazzCash", data["paymentMode"])
            and data["countryCode"] == "586"
        ):  # If countryCode is 586 i.e. country is Pakistan, then allowed payment modes are 'Easypaisa' or 'JazzCash'.
            message += "paymentMode must be either 'Easypaisa' or 'JazzCash'. "

        if data["paymentMode"] == "UPI":
            if not (isinstance(data["upiChoice"], str)):
                message += "upiChoice must be a string. "
            elif not re.match(
                "upiApp|upiId", data["upiChoice"]
            ):  # If value of paymentMode parameter is 'UPI' then the value of upiChoice parameter should be either 'upiApp' or 'upiId'.
                message += "upiChoice must be either 'upiApp' or 'upiId'. "
            elif data["upiChoice"] == "upiId":
                if not (isinstance(data["upiId"], str)):
                    message += "upiId must be a string. "
            elif (
                "upiApp" in data
            ):  # If value of upiChoice parameter is 'upiApp' then the value of upiApp parameter should be either 'GPay' or 'PhonePe' or 'PayTM'.
                if not re.match("GPay|PhonePe|PayTM", data["upiApp"]):
                    message += "upiApp must be either 'GPay' or 'PhonePe' or 'PayTM'. "
        elif data["paymentMode"] == "NB":
            pass
        elif data["paymentMode"] == "Card":
            pass
        elif data["paymentMode"] == "Wallet":
            pass

    # Checking if mandatory parameters are following the type validation.
    if len(message) > 0:
        # one or more mandatory parameters is/are violating the type validation.
        statusCode = status.HTTP_400_BAD_REQUEST
        title = "Parameters violates type validation"
        message += "Kindly check your request parameters."

        # Adding a warning log showing that parameters violates the type validation.
        db_logger.warning(
            "Parameters required for transaction initiation are violating the type validation"
        )

        # 400 - Bad Request.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )

    # Returning true if all mandatory parameters are follows the type validation.
    return True
