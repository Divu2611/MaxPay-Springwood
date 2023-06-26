"""
generatingResponse - Generating desired JSON response
Response contains 1.) Status Code 2.) Description 3.) Sub Description
"""


def generatingResponse(statusCode, title, message):
    statusCode = statusCode
    title = title
    message = message

    jsonResponse = {
        "statusCode": statusCode,
        "title": title,
        "message": message,
    }

    return jsonResponse
