from django.urls import path

from .views import (
    OrderView,
    PaymentSuccessView,
    PaymentView,
    SearchResultsView,
    SeatsView,
)


app_name = "trips"

urlpatterns = [
    path("results/", SearchResultsView.as_view(), name="search-results"),
    path("seats/", SeatsView.as_view(), name="seats"),
    path("order/", OrderView.as_view(), name="order"),
    path("payment/", PaymentView.as_view(), name="payment"),
    path("success/", PaymentSuccessView.as_view(), name="payment-success"),
]
