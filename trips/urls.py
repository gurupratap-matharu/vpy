from django.urls import path

from .views import OrderView, SearchResultsView, SeatsView

app_name = "trips"

urlpatterns = [
    path("results/", SearchResultsView.as_view(), name="search-results"),
    path("seats/", SeatsView.as_view(), name="seats"),
    path("order/", OrderView.as_view(), name="order"),
]
