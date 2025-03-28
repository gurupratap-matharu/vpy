import logging

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class FeedbackForm(forms.Form):
    placeholder = _(
        "Mandanos sus comentarios y/o reporta un inconveniente. Queremos mejorar la plataforma para vos. Gracias"
    )
    subject = _("Mensaje")
    email = forms.EmailField(
        required=True,
        min_length=10,
        widget=forms.TextInput(
            attrs={"placeholder": _("Email"), "class": "form-control"}
        ),
    )
    message = forms.CharField(
        min_length=20,
        max_length=1000,
        required=True,
        widget=forms.Textarea(
            attrs={
                "cols": 80,
                "rows": 5,
                "placeholder": placeholder,
                "class": "form-control",
            }
        ),
    )

    def send_mail(self):
        from_email = self.cleaned_data["email"]
        message = "Email: {email}\n\n{message}".format(**self.cleaned_data)

        logger.info("sending feedback...")
        send_mail(
            subject=self.subject,
            message=message,
            from_email=from_email,
            recipient_list=[settings.DEFAULT_TO_EMAIL],
            fail_silently=False,
        )


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        min_length=3,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": _("Nombre"), "class": "form-control"}
        ),
    )
    email = forms.EmailField(
        required=True,
        min_length=10,
        widget=forms.TextInput(
            attrs={"placeholder": _("Email"), "class": "form-control"}
        ),
    )
    subject = forms.CharField(
        max_length=100,
        min_length=3,
        widget=forms.TextInput(
            attrs={"placeholder": _("Asunto"), "class": "form-control"}
        ),
    )
    message = forms.CharField(
        min_length=20,
        max_length=600,
        required=True,
        widget=forms.Textarea(
            attrs={
                "cols": 80,
                "rows": 4,
                "placeholder": _("Mensaje"),
                "class": "form-control",
            }
        ),
    )

    def send_mail(self):
        subject = self.cleaned_data["subject"]
        from_email = self.cleaned_data["email"]
        message = "From: {name}\nEmail: {email}\n\n{message}".format(
            **self.cleaned_data
        )

        logger.info("sending contact form email...")
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[settings.DEFAULT_TO_EMAIL],
            fail_silently=False,
        )
