from django.urls import path

from .views import (
    CompanyLandingView,
    ContactPageView,
    ExploreView,
    FeedbackPageView,
)


app_name = "pages"

urlpatterns = [
    path("contact/", ContactPageView.as_view(), name="contact"),
    path("feedback/", FeedbackPageView.as_view(), name="feedback"),
    path("para-empresas/", CompanyLandingView.as_view(), name="company-landing"),
    path("explore/", ExploreView.as_view(), name="explore"),
]
