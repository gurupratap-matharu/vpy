from django.urls import path

from .views import (
    CompanyLandingView,
    ContactPageView,
    ExploreView,
    FeedbackPageView,
    StyleGuideView,
)


app_name = "pages"

urlpatterns = [
    path("contact/", ContactPageView.as_view(), name="contact"),
    path("feedback/", FeedbackPageView.as_view(), name="feedback"),
    path("para-empresas/", CompanyLandingView.as_view(), name="company-landing"),
    path("styleguide/", StyleGuideView.as_view(), name="styleguide"),
    path("explore/", ExploreView.as_view(), name="explore"),
]
