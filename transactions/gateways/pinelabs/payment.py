# Importing Libraries
import hmac
import json
import requests
import traceback


def initiate_payment(params, mid, access_code, secret_key, env):
    try:
        result = _payment(
            params=params,
            mid=mid,
            access_code=access_code,
            secret_key=secret_key,
            env=env,
        )

        return json.loads(result)
    except Exception as exception:
        traceback.print_exc()
        print("#######Error on payment:initiate_payment#######")
        return {"status": False, "reason": "Exception occured"}


def _payment(params, mid, access_code, secret_key, env):
    postedArray = {}
    URL = _getURL(env)

    # Pushing merchantID, merchant_access_code and merchant_secret_key in the params
    params["merchant_id"] = mid
    params["merchant_access_code"] = access_code
    params["secret_key"] = secret_key

    # remove white space, htmlentities(converts characters to HTML entities), prepared postedArray
    postedArray = _removeSpaceAndPreparePostArray(params)

    # create order and get the token for generated order. token is to be used as query params
    order_detail = _create_order(params=postedArray, url=URL)
    token = order_detail["token"]

    if postedArray["payment_mode"] == "UPI":
        # process to start pay via upi
        response = _pay_via_upi(url=URL, token=token)
    elif postedArray["payment_mode"] == "NB":
        # process to start pay via nb
        response = _pay_via_nb(params=postedArray, url=URL, token=token)
    elif postedArray["payment_mode"] == "Card":
        # process to start pay via card
        response = _pay_via_card(params=postedArray, url=URL, token=token)
    elif postedArray["payment_mode"] == "Wallet":
        # process to start pay via wallet
        response = _pay_via_wallet(params=postedArray, url=URL, token=token)

    return response


"""
*  _removeSpaceAndPreparePostArray method Remove white space, converts characters to HTML entities
*   and prepared the posted array.
*
* param array params - holds request.POST array, merchant_id, merchant_access_key and secret_key.
*
* ##Return values
*
* - return array temp_array - holds the all posted value after removing space.
*
* @param array params - holds request.POST array, merchant_id, merchant_access_key and secret_key.
*
* @return array temp_array - holds the all posted value after removing space.
*
"""


def _removeSpaceAndPreparePostArray(params):
    temp_dictionary = {
        "merchant_id": params["merchant_id"].strip(),
        "merchant_access_code": params["merchant_access_code"].strip(),
        "secret_key": params["secret_key"].strip(),
        "txnid": params["txnid"].strip(),
        "redirectURL": params["redirectURL"].strip(),
        "payment_mode": params["payment_mode"].strip(),
        "amount": params["amount"].strip(),
        "productinfo": params["productinfo"].strip(),
        "firstname": params["firstname"].strip(),
        "calling_code": params["calling_code"].strip(),
        "phone": params["phone"].strip(),
        "email": params["email"].strip(),
        "udf1": params["udf1"].strip(),
        "udf2": params["udf2"].strip(),
        "udf3": params["udf3"].strip(),
        "udf4": params["udf4"].strip(),
        "udf5": params["udf5"].strip(),
        "udf6": params["udf6"].strip(),
        "udf7": params["udf7"].strip(),
        "udf8": params["udf8"].strip(),
        "udf9": params["udf9"].strip(),
        "udf10": params["udf10"].strip(),
        # 'address1' : params['address1'].strip(),
        # 'address2' : params['address2'].strip(),
        # 'city' : params['city'].strip(),
        # 'state' : params['state'].strip(),
        # 'country' : params['country'].strip(),
        # 'zipcode' : params['zipcode'].strip()
    }

    if params["payment_mode"] == "NB":
        pass
    elif params["payment_mode"] == "Card":
        temp_dictionary["card_number"] = params["card_number"].strip()
        temp_dictionary["cvv"] = params["cvv"].strip()
        temp_dictionary["card_holder_name"] = params["card_holder_name"].strip()
        temp_dictionary["card_expiry_year"] = params["card_expiry_year"].strip()
        temp_dictionary["card_expity_month"] = params["card_expity_month"].strip()
        temp_dictionary["is_card_to_be_saved"] = params["is_card_to_be_saved"].strip()
    elif params["payment_mode"] == "Wallet":
        pass

    return temp_dictionary


def _getURL(env):
    url_link = None

    if env == "test":
        url_link = "https://api-staging.pluralonline.com/"
    elif env == "prod":
        url_link = "https://api.pluralonline.com"
    else:
        url_link = "https://api-staging.pluralonline.com/"

    return url_link


def _create_order(params, url):
    order_body = {
        "merchant_data": {
            "merchant_id": params["merchant_id"],
            "merchant_access_code": params["merchant_access_code"],
            "merchant_return_url": params["redirectURL"],
            "merchant_order_id": params["txnid"],
        },
        "payment_info_data": {
            "amount": params["amount"],
            "order_desc": params["productinfo"],
            "currency_code": "INR",
        },
        "customer_data": {
            "country_code": params["calling_code"],
            "mobile_number": params["phone"],
            "email_id": params["email"],
        },
        "billing_address_data": {"first_name": params["firstname"], "country": "India"},
        "shipping_address_data": {
            "first_name": params["firstname"],
            "country": "India",
        },
        "product_info_data": {
            "product_details": [
                {"product_code": params["productinfo"], "product_amount": 200}
            ]
        },
        "additional_info_data": {
            "rfu1": params["udf1"],
            "rfu2": params["udf2"],
            "rfu3": params["udf3"],
            "rfu4": params["udf4"],
            "rfu5": params["udf5"],
            "rfu6": params["udf6"],
            "rfu7": params["udf7"],
            "rfu8": params["udf8"],
            "rfu9": params["udf9"],
            "rfu10": params["udf10"],
        },
    }

    request = encode_order_body(request=json.dumps(order_body))
    header = get_sha_generated(request=request, secure_secret=params["secret_key"])

    payload = {"request": request}
    headers = {"x-verify": header, "content-type": "application/json"}

    response = requests.post(url=url, json=payload, headers=headers)

    return json.loads(response.text)


def encode_order_body(request):
    import base64

    return base64.b64encode(request).decode("utf-8")


def get_sha_generated(request, secure_secret):
    import hashlib

    hex_hash = ""
    converted_hash = bytes.fromhex(secure_secret)

    hash_value = hmac.new(
        converted_hash, request.encode("utf-8"), hashlib.sha256
    ).digest()
    hex_hash = "".join("{:02x}".format(byte) for byte in hash_value)

    return hex_hash


"""
* _pay_via_upi method initiate payment via UPI.
*
* params array params_array - holds all form data required for UPI payment.
* params string url - holds the url based in env(enviroment type env = 'test' or env = 'prod')
*
* param  string upi_id - holds the UPI ID of customer
* param  string is_upi_to_be_saved - holds the decision of customer if he/she wants to save his/her UPI ID
* param  string calling_code - holds the country calling code
* param  string phone - holds the mobile number of customer
* param  string email - holds the Email ID of customer
"""


def _pay_via_upi(url, token):
    payload = {
        "upi_data": {"upi_option": "UPI", "txn_mode": "INTENT"},
        "txn_data": {"payment_mode": "UPI", "navigation_mode": "SEAMLESS"},
    }

    headers = {"checkoutmode": "SEAMLESS", "content-type": "application/json"}

    response = requests.post(
        url=url + "api/v1/upi/process/payment/?token=" + token,
        json=payload,
        headers=headers,
    )

    return response.text


"""
* _pay_via_nb method initiate payment via Net Banking.
*
* params array params_array - holds all form data required for Net Banking payment.
* params string url - holds the url based in env(enviroment type env = 'test' or env = 'prod')
*
* param  string pay_code - holds the unique identifier of the bank
* param  string calling_code - holds the country calling code
* param  string phone - holds the mobile number of customer
* param  string email - holds the Email ID of customer
"""


def _pay_via_nb(params, url, token):
    payload = {
        "netbanking_data": {"pay_code": "NB1006"},
        "customer_data": {
            "country_code": params["calling_code"],
            "mobile_number": params["phone"],
            "email_id": params["email"],
        },
    }

    headers = {"checkoutmode": "SEAMLESS", "content-type": "application/json"}

    response = requests.post(
        url=url + "api/v1/netbanking/process/payment/?token=" + token,
        json=payload,
        headers=headers,
    )

    return response.text


"""
* _pay_via_card method initiate payment via Card.
*
* params array params_array - holds all form data required for Card payment.
* params string url - holds the url based in env(enviroment type env = 'test' or env = 'prod')
*
* param  string card_number - holds the Card number
* param  string cvv - holds the CVV number of the card
* param  string card_holdser_name - holds the name of card holder
* param  string card_expiry_year - holds the expiry year of card
* param  string card_expiry_month - holds the expiry month of card
* param  string is_card_to_be_saved - holds the decision of customer if he/she wants to save his/her Card
* param  string calling_code - holds the country calling code
* param  string phone - holds the mobile number of customer
* param  string email - holds the Email ID of customer
* param  string custome_token - holds the unique identifier of the bank
"""


def _pay_via_card(params, url, token):
    # Creating a customer before initiating the payment. Customer token is used for payment to get initiated.
    customer = _fetch_customer(params=params)
    if "error_code" in customer:
        customer = _create_customer(params=params)

    # Updating param values
    params

    payload = {
        "card_data": {
            "card_number": params["card_number"],
            "cvv": params["cvv"],
            "card_holder_name": params["card_holder_name"],
            "card_expiry_year": params["card_expiry_year"],
            "card_expiry_month": params["card_expiry_month"],
            "is_card_to_be_saved": params["is_card_to_be_saved"],
        },
        "customer_data": {
            "country_code": params["calling_code"],
            "mobile_no": params["phone"],
            "email_id": params["email"],
            "customer_token": customer["customer_token"],
        },
    }

    headers = {"checkoutmode": "SEAMLESS", "content-type": "application/json"}

    response = requests.post(
        url=url + "api/v1/card/process/payment/?token=" + token,
        json=payload,
        headers=headers,
    )

    return response.text


"""
* _pay_via_nb method initiate payment via Wallet.
*
* params array params_array - holds all form data required for Wallet payment.
* params string url - holds the url based in env(enviroment type env = 'test' or env = 'prod')
*
* param  string wallet_code - holds the unique identifier of the wallet
* param  string calling_code - holds the country calling code
* param  string phone - holds the mobile number of customer
* param  string email - holds the Email ID of customer
"""


def _pay_via_wallet(params, url, token):
    payload = {
        "wallet_data": {
            "wallet_code": params["wallet_code"],
            "mobile_number": params["phone"],
        },
        "customer_data": {
            "country_code": params["calling_code"],
            "mobile_number": params["phone"],
            "email_id": params["email"],
        },
    }

    headers = {"checkoutmode": "SEAMLESS", "content-type": "application/json"}

    response = requests.post(
        url=url + "api/v1/wallet/process/payment/?token=" + token,
        json=payload,
        headers=headers,
    )

    return response.text


"""
* _create_customer method creates the new customer.
*
* params array params_array - holds all form data required for Wallet payment.
* params string url - holds the url based in env(enviroment type env = 'test' or env = 'prod')
*
* param  string calling_code - holds the country calling code
* param  string phone - holds the mobile number of customer
* param  string email - holds the Email ID of customer
"""


def _create_customer(params, url):
    payload = {
        "mobile_no": params["phone"],
        "email_id": params["email"],
        "country_code": params["calling_code"],
    }

    headers = {"content-type": "application/json"}

    response = requests.post(
        url=url + "api/v1/customer/create", json=payload, headers=headers
    )

    return json.loads(response.text)


"""
* _fetch_customer method fetches the new customer.
*
* params string mobile_no - holds the mobile number of customer.
* params string calling_code - holds the country calling code.
* params string url - holds the url based in env(enviroment type env = 'test' or env = 'prod').
"""


def _fetch_customer(mobile_no, calling_code, url):
    response = requests.get(
        url=url
        + "api/v1/customer/fetch/mobile_no?country_code="
        + calling_code
        + "&mobile_no="
        + mobile_no
        + "/"
    )
    return json.loads(response)
