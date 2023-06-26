# Importing Python Libraries
import os
import time
import json
import logging
import requests
from dotenv import load_dotenv
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view

# Importing Project Files
import common
from .common.pgAuthentication import pgAuthenticator
from .services.requestService import createRequest
import payment_response.services.dbService as dbService

load_dotenv()
db_logger = logging.getLogger("db")

"""
"""


@csrf_exempt
@common.exceptionHandler
@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def getDecentroResponseAPI(request):
    if request.method != "POST":
        methodResult = common.methodChecker(method=request.method)
        return JsonResponse(methodResult, status=methodResult["statusCode"])

    startTime = time.time()

    # verifying the payment gateway accessing the API.
    authResult = pgAuthenticator(request=request)

    try:
        if "statusCode" in authResult and authResult["statusCode"] in [400, 401]:
            """
            Below is the reason -
            * 401 - Unauthorised: If the Auth-Key in the request header is invalid.
            """

            endTime = time.time() - startTime
            # Analyzing the efficiency of the API.
            apiEfficiency = settings.DECENTRO_CALLBACK_RESPONSE_TIME
            apiEfficiency.observe(endTime)

            return JsonResponse(authResult, status=authResult["statusCode"])
    except:
        # In case of success, authResult contains the payment gateway details (name, auth_key).
        paymentGateway = authResult

    data = request.data.copy()

    if len(data) != 0:
        data["paymentGateway"] = paymentGateway.name
        getResponseAPI(data=data)

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    apiEfficiency = settings.DECENTRO_CALLBACK_RESPONSE_TIME
    apiEfficiency.observe(endTime)

    response = {"response_code": "CB_S00000"}
    return JsonResponse(response)


"""
"""


@csrf_exempt
@common.exceptionHandler
@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def getAirPayResponseAPI(request):
    if request.method != "POST":
        methodResult = common.methodChecker(method=request.method)
        return JsonResponse(methodResult, status=methodResult["statusCode"])

    startTime = time.time()

    data = request.data.copy()

    data["paymentGateway"] = "AirPay"
    data["TRANSACTIONID"] = data["TRANSACTIONID"][:3] + "_" + data["TRANSACTIONID"][3:]

    requestData = getResponseAPI(data=data)

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    apiEfficiency = settings.AIRPAY_CALLBACK_RESPONSE_TIME
    apiEfficiency.observe(endTime)

    return render(
        request,
        "loading.html",
        {"data": requestData},
    )


"""
"""


@csrf_exempt
@common.exceptionHandler
@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def getItzPayResponseAPI(request):
    if request.method != "GET":
        methodResult = common.methodChecker(method=request.method)
        return JsonResponse(methodResult, status=methodResult["statusCode"])

    startTime = time.time()

    # Getting the query parameters.
    data = dict()
    data["paymentGateway"] = "ItzPay"
    data["Status"] = request.GET.get("Status")
    data["Amount"] = request.GET.get("Amount")
    data["CustomerTransactionId"] = request.GET.get("CustomerTransactionId")
    data["OrderId"] = request.GET.get("OrderId")
    data["PaymentType"] = request.GET.get("PaymentType")
    data["Checksum"] = request.GET.get("Checksum")
    data["ChannelId"] = request.GET.get("ChannelId")

    requestData = getResponseAPI(data=data)

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    apiEfficiency = settings.ITZPAY_CALLBACK_RESPONSE_TIME
    apiEfficiency.observe(endTime)

    # response = {"status": "success"}
    # return JsonResponse(response, status=status.HTTP_200_OK)
    return render(
        request,
        "loading.html",
        {"data": requestData},
    )


"""
"""


@csrf_exempt
@common.exceptionHandler
@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def getPaymobResponseAPI(request):
    requestMethod = request.method

    if requestMethod not in ["POST", "GET"]:
        methodResult = common.methodChecker(method=requestMethod)
        return JsonResponse(methodResult, status=methodResult["statusCode"])

    if requestMethod == "POST":
        data = request.data.copy()

        # Filtering the request and storing only the data required to send to client.
        filteredData = dict()
        filteredData["transactionStatus"] = (
            "success" if data["obj"]["success"] else "failure"
        )
        filteredData["transactionTime"] = data["obj"]["updated_at"]
        filteredData["errorReason"] = data["obj"]["data"]["message"]
        filteredData["errorMessage"] = data["obj"]["data"]["message"]
        filteredData["productInformation"] = data["obj"]["order"]["items"][0]["name"]
        filteredData["netAmountDebit"] = data["obj"]["data"]["amount"]
        filteredData["referenceId"] = data["obj"]["order"]["merchant_order_id"]
        filteredData["paymentGateway"] = "Paymob"

        getResponseAPI(data=filteredData)

        response = {"status": "success"}
        return JsonResponse(response, status=status.HTTP_200_OK)

    if requestMethod == "GET":
        referenceID = request.GET.get("merchant_order_id")
        requestData = dbService.getTransactionResponse(referenceId=referenceID)

        return render(
            request,
            "loading.html",
            {"data": requestData},
        )


"""
"""


@csrf_exempt
@common.exceptionHandler
@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def getGenieResponseAPI(request):
    if request.method != "GET":
        methodResult = common.methodChecker(method=request.method)
        return JsonResponse(methodResult, status=methodResult["statusCode"])

    # Setting the baseURL on the basis of environment.
    baseURL = (
        "https://api.geniebiz.lk"
        if os.getenv("ENV") == "production"
        else "https://api.uat.geniebiz.lk"
    )

    # Retriving the transactionId from the request parameter.
    transactionId = request.GET.get("transactionId")
    # Setting the getTransaction API.
    getTransactionAPI = "{}/public/transactions/{}".format(baseURL, transactionId)

    headers = {
        "Accept": "application/json",
        "Authorization": os.getenv("eZCASH_GENIE_API_KEY"),
    }

    # Making a GET request to getTransaction API to get the details of the transaction.
    response = requests.get(url=getTransactionAPI, headers=headers)
    response = json.loads(response.text)

    data = response
    data["state"] = "success"
    data["paymentGateway"] = "eZCash - Genie"

    requestData = getResponseAPI(data=response)

    return render(
        request,
        "loading.html",
        {"data": requestData},
    )


"""
"""


def getResponseAPI(data):
    # data from the payment gateway has the complete transaction details.

    # request, which is need to be sent to client, is generated and DB is updated with complete transaction details.
    requestData = createRequest(data=data, paymentGateway=data["paymentGateway"])

    if requestData["checkoutFlow"] == "Merchant Hosted":
        requests.post(url=requestData["redirectURL"], json=requestData)

    # Adding a info log showing that transaction details are successfully sent to client's redirect URL.
    db_logger.info(
        "Resquest is sent to {}.\nThe resquest {}".format(
            requestData["redirectURL"], requestData
        )
    )

    return requestData

    # TODO: Uncomment for demo
    # if requestData["transactionStatus"].lower() == "success":
    #     discount = (
    #         0 if requestData["discount"] == "N.A." else float(requestData["discount"])
    #     )
    #     amountDebit = float(requestData["netAmountDebit"])
    #     sgst = amountDebit * 0.09
    #     cgst = amountDebit * 0.09
    #     totalTax = cgst + sgst
    #     productPrice = round(amountDebit - totalTax, 2)

    #     return render(
    #         request,
    #         "success.html",
    #         {
    #             "data": requestData,
    #             "productPrice": productPrice,
    #             "discount": discount,
    #             "amountDebit": amountDebit,
    #             "sgst": sgst,
    #             "cgst": cgst,
    #             "totalTax": totalTax,
    #         },
    #     )
    # else:
    #     return render(
    #         request,
    #         "failure.html",
    #         {"data": requestData},
    #     )


@api_view(["POST"])
def final_redirect(request):
    # TODO: Uncomment for demo
    # return render(request, "demo.html")

    return {"statusCode": 200, "message": "Data recieved successfully"}
