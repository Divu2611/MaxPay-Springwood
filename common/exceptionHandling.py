# Importing Python Libraries
from django.shortcuts import render
from rest_framework import status

# Importing Project Files
from . import generatingResponse


def exceptionHandler(func):
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception as exception:
            statusCode = status.HTTP_500_INTERNAL_SERVER_ERROR
            title = "Internal Server Error"
            message = str(exception.args)

            errorResponse = generatingResponse(
                statusCode=statusCode, title=title, message=message
            )

            return render(
                request,
                "serverError.html",
                {"data": errorResponse},
            )

    return wrapper
