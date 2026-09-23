from django.urls import path

from .views import ContactPageView, FeedbackPageView


app_name = "pages"

urlpatterns = [
    path("contact/", ContactPageView.as_view(), name="contact"),
    path("feedback/", FeedbackPageView.as_view(), name="feedback"),
]
