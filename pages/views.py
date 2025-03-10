from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from .forms import ContactForm, FeedbackForm


class ContactPageView(SuccessMessageMixin, FormView):
    template_name = "pages/contact.html"
    form_class = ContactForm
    success_url = "/"
    success_message: str = _("Message sent successfully.")

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)


class FeedbackPageView(SuccessMessageMixin, FormView):
    template_name = "pages/feedback.html"
    form_class = FeedbackForm
    success_url = "/"
    success_message: str = _("Thank you for your feedback 💗")

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)


class CompanyLandingView(TemplateView):
    template_name = "pages/company_landing.html"


class StyleGuideView(TemplateView):
    template_name = "pages/styleguide.html"


class ExploreView(TemplateView):
    template_name = "pages/explore.html"
