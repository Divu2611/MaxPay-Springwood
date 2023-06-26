# Importing Python Libraries
import time
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view

# Importing Project Files
import common
from .common.clientAuthentication import clientAuthenticator
from .services.uniqueTransactionService import verifyUniqueTransaction
from .services.transactionDetailsService import getTransactionDetails
import transactions.services.dbService as dbService
from .gateways.views import pgBalancer


"""
Transaction Initiation - 
Client will request MaxPay to initiate the transaction in either of the two checkout flow -
1.) Merchant Hosted
2.) MaxPay Hosted
Visit the link to refer <https://wiki.springwoodlabs.co/s/796bf2f6-474d-4124-ab8f-a23bb367d1b3>.

The transaction process is then transfered to load balancer - which acts like an API gateway and balances the traffic between all payment gateways onboarded.
Load Balancer then selects the payment gateway depending on checkout flow requested by the client.

Selected payment gateway then initiates the transaction process on basis of request received and returns the desired response, which in turn then shown to client.


initiateTransactionAPI - REST API that initiates the transaction.

Parameters of the function:
* request (type HTTPRequest) - holds all the request details by the client, required for transaction initiation.

Return values of the function:
returns the JsonResponse based on the request received
* Returns 405 - Method Not Allowed error if POST request is not received.
* Returns 400 - Bad Request error if atleast a single mandatory parameter is missing from the request.
* Returns 401 - Unauthorized error if false accountId / hash is provided in the request.
* Returns 500 - Internal Server error if there is an fault in the business logic.

If none of the above error response is returned - 
* Returns the response based on load balancer.
"""


@csrf_exempt
@common.exceptionHandler
@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def initiateTransactionAPI(request):
    if request.method != "POST":
        methodResult = common.methodChecker(method=request.method)
        return JsonResponse(methodResult, status=methodResult["statusCode"])

    # Analyzing the frequency of requests made on the API.
    counter = settings.INITIATE_TRANSACTION_COUNTER
    counter.inc()

    startTime = time.time()

    data = request.data

    # protecting the API by verifiying the client.
    authResult = clientAuthenticator(data=data)
    try:
        if "statusCode" in authResult and authResult["statusCode"] in [400, 401]:
            """
            Client authentication failed:
            One of the possible reasons -
            * 400 - Bad Request: Mandatory parameters might be missing or violates the data type rule.
            * 401 - Unauthorized: Incorrect accountId provided in the request parameter or if there is hash mismatch.
            """

            endTime = time.time() - startTime
            # Analyzing the efficiency of the API.
            apiEfficiency = settings.INITITATE_TRANSACTION_RESPONSE_TIME
            apiEfficiency.observe(endTime)

            return JsonResponse(authResult, status=authResult["statusCode"])
    except:
        # In case of success, authResult contains the account details (account_id, account_secret_key).
        account = authResult

    # verifying if the transactionId against the given accountId already exists.
    uniqueTransactionResult = verifyUniqueTransaction(data=data, account=account)
    if "statusCode" in uniqueTransactionResult and uniqueTransactionResult[
        "statusCode"
    ] in [400, 409, 500]:
        """
        uniqueTransaction response failed:
        One of the possible reasons -
        * 400 - Bad Request: Mandatory parameters might be missing or violates the data type rule.
        * 409 - Conflict: transactionId for given accountId already exists.
        * 500 - Internal Server Error: If there is internal database failure.
        """

        endTime = time.time() - startTime
        # Analyzing the efficiency of the API
        apiEfficiency = settings.INITITATE_TRANSACTION_RESPONSE_TIME
        apiEfficiency.observe(endTime)

        return JsonResponse(
            uniqueTransactionResult,
            status=uniqueTransactionResult["statusCode"],
        )

    # In case of success, uniqueTransaction Result contains the postedData.
    data = uniqueTransactionResult

    # PGbalancer automatically balance the traffic among PGs and then recording the response.
    pgResult = pgBalancer(data=data)

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API.
    apiEfficiency = settings.INITITATE_TRANSACTION_RESPONSE_TIME
    apiEfficiency.observe(endTime)

    return JsonResponse(pgResult, status=pgResult["statusCode"])

    # TODO: Uncomment only for demo
    # return redirect(pgResult["url"])


"""
getTransactionAPI - REST API that returns the transaction details.

Parameters of the function:
* request (type HTTPRequest) - holds all the request details by the client, required for transaction details.

Return values of the function:
returns the JsonResponse based on the request received
* Returns 400 - Bad Request error if atleast a single mandatory parameter is missing from the request.
* Returns 401 - Unauthorized error if false accountId / hash is provided in the request.
* Returns 404 - Not Found error if the transaction details asked is not present in the MaxPay database.

If none of the above error response is returned -
returns the either of the below success response
* Returns 200 - OK response and complete transaction details.
* Returns 206 - Partial Content response if transaction is not completed but initiated.
"""


@csrf_exempt
@common.exceptionHandler
@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def getTransactionAPI(request):
    if request.method != "POST":
        methodResult = common.methodChecker(method=request.method)
        return JsonResponse(methodResult, status=methodResult["statusCode"])

    # Analyzing the frequency of requests made on the API
    counter = settings.TRANSACTION_DETAILS_COUNTER
    counter.inc()

    startTime = time.time()

    data = request.data

    # protecting the API by verifiying the client.
    authResult = clientAuthenticator(data=data)
    try:
        if "statusCode" in authResult and authResult["statusCode"] in [400, 401]:
            """
            Client authentication failed:
            One of the possible reasons -
            * 400 - Bad Request: Mandatory parameters might be missing or violates the data type rule.
            * 401 - Unauthorized: Incorrect accountId provided in the request parameter or if there is hash mismatch.
            """

            endTime = time.time() - startTime
            # Analyzing the efficiency of the API
            apiEfficiency = settings.TRANSACTION_DETAILS_RESPONSE_TIME
            apiEfficiency.observe(endTime)

            return JsonResponse(authResult, status=authResult["statusCode"])
    except:
        pass

    transactionDetailsResult = getTransactionDetails(data=data)

    endTime = time.time() - startTime
    # Analyzing the efficiency of the API
    apiEfficiency = settings.TRANSACTION_DETAILS_RESPONSE_TIME
    apiEfficiency.observe(endTime)

    return JsonResponse(
        transactionDetailsResult, status=transactionDetailsResult["statusCode"]
    )


"""
showPaymentPage - REST API that redirects to a URL for MaxPay hosted checkout
For MaxPay hosted checkout client will recieve a url which when redirected to contains the MaxPay generated payment portal.
"""


@csrf_exempt
@common.exceptionHandler
@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def showPaymentPage(request, referenceId):
    if request.method != "GET":
        methodResult = common.methodChecker(method=request.method)
        return JsonResponse(methodResult, status=methodResult["statusCode"])

    # Analyzing the frequency of requests made on the API
    counter = settings.PAYMENT_PAGE_COUNTER
    counter.inc()

    startTime = time.time()

    try:
        pgResponse = dbService.getPGResponse(referenceId=referenceId)

        if pgResponse.html_response:
            # selected payment gateway responded with an html page
            htmlResponse = pgResponse.response

            endTime = time.time() - startTime
            # Analyzing the efficiency of the API
            apiEfficiency = settings.PAYMENT_PAGE_RESPONSE_TIME
            apiEfficiency.observe(endTime)

            return HttpResponse(htmlResponse)
        else:
            # selectde payment gateway responded with a URL
            urlResponse = pgResponse.response

            endTime = time.time() - startTime
            # Analyzing the efficiency of the API
            apiEfficiency = settings.PAYMENT_PAGE_RESPONSE_TIME
            apiEfficiency.observe(endTime)

            return redirect(urlResponse)
    except Exception as exception:
        statusCode = status.HTTP_500_INTERNAL_SERVER_ERROR
        title = "Internal Server Error"
        message = exception.args

        return JsonResponse(
            common.generatingResponse(
                statusCode=statusCode, title=title, message=message
            )
        )


@api_view()
def testing_form1(request):
    return render(request, "form1.html")


@api_view()
def testing_form2(request):
    return render(request, "form2.html")


@api_view()
def testing_form3(request):
    return render(request, "form3.html")


@api_view()
def testing_formMax(request):
    return render(request, "formMax.html")
