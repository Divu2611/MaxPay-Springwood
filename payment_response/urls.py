from django.urls import path
from . import views

urlpatterns = [
    path("decentro/payment_response/", views.getDecentroResponseAPI),
    path("airpay/payment_response/", views.getAirPayResponseAPI),
    path("itzpay/payment_response/", views.getItzPayResponseAPI),
    path("paymob/payment_response/", views.getPaymobResponseAPI),
    path("ezcash-genie/payment_response/", views.getGenieResponseAPI),
    path("client-demo-page/transaction-completed/", views.final_redirect),
]
