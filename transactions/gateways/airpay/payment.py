# Importing Python Libraries
import datetime
import logging
from django.conf import settings
from rest_framework import status

# Importing Project Files
import common

db_logger = logging.getLogger("db")

"""
"""


def initiatePayment(params, mid, username, password, apiKey):
    try:
        result = _payment(
            data=params, mid=mid, username=username, password=password, apiKey=apiKey
        )
        return result
    except Exception as exception:
        statusCode = status.HTTP_500_INTERNAL_SERVER_ERROR
        title = "Internal Server Error"
        message = exception.args

        # 500 - Internal Server Error.
        return common.generatingResponse(
            statusCode=statusCode, title=title, message=message
        )


"""
"""


def _payment(data, mid, username, password, apiKey):
    URL = "https://payments.airpay.co.in/pay/index.php"

    data["mid"] = mid
    data["username"] = username
    data["password"] = password
    data["apiKey"] = apiKey

    # process the start the payment.
    payResult = _pay(data=data, url=URL)
    return payResult


"""
"""


def _pay(data, url):
    from .checksum import Checksum

    chk = Checksum()

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    username = data["username"]
    password = data["password"]
    secret = data["apiKey"]
    allData = (
        data["emailId"]
        + data["firstName"]
        + data["lastName"]
        + data["amount"]
        + data["orderId"]
        + today
    )

    privateKey = chk.encrypt(data=username + ":|:" + password, salt=secret)
    keySha256 = chk.encryptSha256(k=username + "~:~" + password)
    checkSum = chk.calculateChecksumSha256(data=allData, salt=keySha256)
    mer_dom = (
        "aHR0cHM6Ly9wcm9kLm1heC1wYXltZW50cy5jb20="
        if settings.ENV == "production"
        else "aHR0cHM6Ly9zdGFnaW5nLm1heC1wYXltZW50cy5jb20"
    )

    payload = {
        "privatekey": privateKey,
        "mercid": data["mid"],
        "orderid": data["orderId"],
        "buyerEmail": data["emailId"],
        "buyerPhone": data["phoneNumber"],
        "buyerFirstName": data["firstName"],
        "buyerLastName": data["lastName"],
        "amount": data["amount"],
        "currency": data["currencyCode"],
        "isocurrency": data["isoCurrencyCode"],
        "mer_dom": mer_dom,
        "checksum": checkSum,
    }

    # Adding an info log showing that MaxPay is about to generate the AirPay's payment portal.
    db_logger.info(
        "About to generate the AirPay's payment portal.\nPayload: {}.".format(payload)
    )

    html = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
    html += '<html xmlns="http://www.w3.org/1999/xhtml">'
    html += "<head>"
    html += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
    html += "<title>Airpay</title>"
    html += '<script type="text/javascript">'
    html += "function submitForm() {"
    html += "var form = document.forms[0];"
    html += "form.submit();"
    html += " }"
    html += "</script>"
    html += "</head>"
    html += '<body onload="javascript:submitForm()">'
    html += "<center>"
    html += '<table width="500px;">'
    html += "<tr>"
    html += '<td align="center" valign="middle">Do Not Refresh or Press Back <br/> Redirecting to MaxPay</td>'
    html += "</tr>"
    html += "<tr>"
    html += '<td align="center" valign="middle">'
    html += '<form action="' + url + '" method="post">'

    html += chk.outputForm(data=payload)

    html += "</form>"
    html += "</tr>"
    html += "</table>"
    html += "</center>"
    html += "</html>"

    return html
