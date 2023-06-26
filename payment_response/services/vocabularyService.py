"""
A vocabulary for every payment gateway is defined.

The response details that are need to be sent to client doesn't necessarily matches with key-value response from payment gateway
i.e., though key follows the same purpose but its name in response from payment gateway might be different.

paymentGatewayVocabulary: maps the key names in response details that are need to be sent to client with key names in the response from payment gateway.
"""


paymentGatewayVocabulary = {
    "Decentro": {
        "transactionStatus": "transactionStatus",
        "transactionTime": "timestamp",
        "paymentMode": "transferType",
        "errorMessage": "transactionMessage",
        "errorReason": "transactionMessage",
        "netAmountDebit": "transactionAmount",
        "paymentSource": "Decentro",
        "uniqueIdentifier": "referenceId",
    },
    "AirPay": {
        "transactionStatus": "TRANSACTIONPAYMENTSTATUS",
        "transactionTime": "TRANSACTIONTIME",
        "paymentMode": "CHMOD",
        "errorMessage": "MESSAGE",
        "errorReason": "MESSAGE",
        "netAmountDebit": "AMOUNT",
        "paymentSource": "AirPay",
        "uniqueIdentifier": "TRANSACTIONID",
    },
    "ItzPay": {
        "transactionStatus": "Status",
        "paymentMode": "PaymentType",
        "netAmountDebit": "Amount",
        "paymentSource": "ItzPay",
        "uniqueIdentifier": "CustomerTransactionId",
    },
    "Paymob": {
        "transactionStatus": "transactionStatus",
        "transactionTime": "transactionTime",
        "errorReason": "errorReason",
        "errorMessage": "errorMessage",
        "productInformation": "productInformation",
        "netAmountDebit": "netAmountDebit",
        "paymentSource": "Paymob",
        "uniqueIdentifier": "referenceId",
    },
    "eZCash - Genie": {
        "transactionStatus": "state",
        "transactionTime": "updated",
        "netAmountDebit": "amount",
        "uniqueIdentifier": "customerReference",
    }
}
