from django.urls import path

from .views import (
    place_order,
    capture_payment_details
)

urlpatterns = [
    path('create/', place_order),
    path('payment/capture/', capture_payment_details)
]
