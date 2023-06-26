# Importing Libraries
from django.conf import settings
from django.http import HttpResponse
from prometheus_client import generate_latest


def requestCounter(request):
    data = generate_latest(settings.COUNTER_REGISTORY)

    return HttpResponse(
        data,
        content_type="text/plain",
    )


def apiEfficiency(request):
    data = generate_latest(settings.API_EFFICIENCY_REGISTORY)

    return HttpResponse(
        data,
        content_type="text/plain",
    )


def dbEfficiency(request):
    data = generate_latest(settings.DB_EFFICIENCY_REGISTORY)

    return HttpResponse(
        data,
        content_type="text/plain",
    )


def serviceEfficiency(request):
    data = generate_latest(settings.SERVICE_EFFICIENCY_REGISTORY)

    return HttpResponse(
        data,
        content_type="text/plain",
    )


def gatewayEfficiency(request):
    data = generate_latest(settings.GATEWAY_EFFICIENCY_REGISTORY)

    return HttpResponse(
        data,
        content_type="text/plain",
    )
