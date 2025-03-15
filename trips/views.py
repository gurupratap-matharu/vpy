from django.views.generic import TemplateView


class SearchResultsView(TemplateView):
    template_name = "trips/search_results.html"


class SeatsView(TemplateView):
    template_name = "trips/seats.html"


class OrderView(TemplateView):
    template_name = "trips/order.html"


class PaymentView(TemplateView):
    template_name = "trips/payment.html"


class PaymentSuccessView(TemplateView):
    template_name = "trips/payment-success.html"
