import logging

from django.contrib import messages
from django.db import models
from django.forms import widgets
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    PublishingPanel,
)
from wagtail.contrib.forms.models import (
    FORM_FIELD_CHOICES,
    AbstractEmailForm,
    AbstractFormField,
)
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import (
    DraftStateMixin,
    LockableMixin,
    Page,
    PreviewableMixin,
    RevisionMixin,
    WorkflowMixin,
)
from wagtail.models.i18n import Locale

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from base.cache import get_default_cache_control_decorator
from base.schemas import organisation_schema

from .blocks import BaseStreamBlock


logger = logging.getLogger(__name__)


class Person(
    WorkflowMixin,
    DraftStateMixin,
    LockableMixin,
    RevisionMixin,
    PreviewableMixin,
    ClusterableModel,
):
    """
    A model to store Person objects.

    It is registered using the `register_snippet` as a function in wagtail_hooks.py

    `Person` uses the `ClusterableModel`, which allows the relationship with another
    model to be stored locally to the 'parent' model (e.g. a PageModel) until the parent
    is explicitly saved. This allows the editor to use the 'Preview' button, to preview
    the content without saving the relationship to the database first.

    Read more at https://github.com/wagtail/django-modelcluster
    We use this to add authors to blog articles.
    """

    first_name = models.CharField("First name", max_length=254)
    last_name = models.CharField("Last name", max_length=254)
    job_title = models.CharField("Job title", max_length=254)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("first_name"),
                        FieldPanel("last_name"),
                    ]
                )
            ],
            "Name",
        ),
        FieldPanel("job_title"),
        FieldPanel("image"),
        PublishingPanel(),
    ]

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def thumb_image(self):
        """
        Generate a square html tag for this person if he/she has an image uploaded.

        Ex: '<img alt="kal-visuals-square" height="50" width="50"
                src="/media/images/kal-visuals-square.2e16d0ba.fill-50x50.jpg">'
        """

        return self.image.get_rendition("fill-50x50").img_tag() if self.image else ""


class SocialFields(models.Model):
    """
    Used to store an image and title which can be used when a page is shared on social networks.
    """

    social_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Choose an image you wish to display when this page appears on social media",
    )
    social_text = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel("social_image"),
                FieldPanel("social_text"),
            ],
            "Social networks",
        )
    ]


class ListingFields(models.Model):
    """
    Abstract class to add listing field (the one that appears on search results) and text to any new content type easily.
    """

    listing_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Choose an image you wish to be displayed when this page appears on listings",
    )
    listing_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Override the page title when this page appears on listings",
    )
    listing_summary = models.CharField(
        max_length=255,
        blank=True,
        help_text="The text description used when this page appears on listings. It's also used if meta description is absent",
    )

    class Meta:
        abstract = True

    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel("listing_image"),
                FieldPanel("listing_title"),
                FieldPanel("listing_summary"),
            ],
            "Listing information",
        )
    ]


@method_decorator(get_default_cache_control_decorator(), name="serve")
class BasePage(SocialFields, ListingFields, Page):
    """
    An abstract base page which is optimised and can be inherited by any content page in our project.
    """

    show_in_menus_default = True

    appear_in_search_results = models.BooleanField(
        default=True,
        help_text="Make this page indexable by search engines."
        "If unchecked this page will no longer be indexed by search engines.",
    )

    promote_panels = (
        Page.promote_panels
        + SocialFields.promote_panels
        + ListingFields.promote_panels
        + [
            FieldPanel("appear_in_search_results"),
        ]
    )

    class Meta:
        abstract = True

    def canonical_url(self):
        return self.full_url

    def get_default_locale_url(self):
        es = Locale.objects.get(language_code="es")
        page = self.get_translation_or_none(locale=es)
        if page and page.live:
            return page.full_url

    def _get_organisation_schema(self):
        return organisation_schema

    def _get_image_schema(self):
        image = self.listing_image or self.social_image
        image_url = image.file.url if image else ""

        image_schema = {
            "@context": "https://schema.org",
            "@type": "ImageObject",
            "contentUrl": f"https://ventanita.com.py{image_url}",
            "license": "https://ventanita.com.py/condiciones-generales/",
            "acquireLicensePage": "https://ventanita.com.py/contact/",
            "creditText": self.listing_title or self.social_text,
            "creator": {"@type": "Person", "name": "Ventanita"},
            "copyrightNotice": "Ventanita",
        }

        return image_schema

    def _get_article_schema(self):
        image = self.listing_image or self.social_image
        image_url = image.file.url if image else ""
        org = {
            "@type": "Organization",
            "name": "Ventanita",
            "url": "https://ventanita.com.py",
        }

        article_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": self.title,
            "image": [f"https://ventanita.com.py{image_url}"],
            "datePublished": self.first_published_at.isoformat(),
            "dateModified": self.last_published_at.isoformat(),
            "author": [org],
            "publisher": org,
        }

        return article_schema

    def _get_faq_schema(self):
        if not hasattr(self, "faq"):
            return

        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": self._get_faq_entities(),
        }

        return faq_schema

    def _get_faq_entities(self):
        entities = []
        for block in self.faq:
            for item in block.value["item"]:
                question = item.get("question")
                answer_html = item.get("answer")
                answer_text = strip_tags(answer_html.source)

                entity = {
                    "@type": "Question",
                    "name": question.strip(),
                    "acceptedAnswer": {"@type": "Answer", "text": answer_text.strip()},
                }

                entities.append(entity)

        return entities


BasePage._meta.get_field("seo_title").verbose_name = "Title tag"
BasePage._meta.get_field("search_description").verbose_name = "Meta description"


class StandardPage(BasePage):
    """
    A generic content page which we can use for any page that only needs a title, image, introduction and a body field.
    Some examples are typical static pages like - about, terms, privacy, etc.
    """

    page_description = "Use this to build a simple or generic page"

    introduction = models.TextField(help_text="Text to describe the page", blank=True)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px to 3000px.",
    )

    body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True, collapsed=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("image"),
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "standard page"
        verbose_name_plural = "standard pages"

    def __str__(self):
        return self.title


class FormField(AbstractFormField):
    """
    One FormPage can have many FormFields. Here we declare the parentalkey (foreign key)
    for our form.
    """

    field_type = models.CharField(verbose_name="field type", max_length=16, choices=list(FORM_FIELD_CHOICES))
    page = ParentalKey("FormPage", related_name="form_fields", on_delete=models.CASCADE)


class FormPage(AbstractEmailForm):
    page_description = "Use this page to create a simple form"

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(BaseStreamBlock(), collapsed=True, blank=True)
    thank_you_text = RichTextField(blank=True)
    thank_you_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Veer note how we include the FormField obj via an InlinePanel using the
    # related_name value
    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("image"),
        FieldPanel("body"),
        InlinePanel("form_fields", heading="Form fields", label="Field"),
        FieldPanel("thank_you_text"),
        FieldPanel("thank_you_page"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address"),
                        FieldPanel("to_address"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            "Email",
        ),
    ]

    class Meta:
        verbose_name = "formpage"
        verbose_name_plural = "formpages"

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        for name, field in form.fields.items():
            if isinstance(field.widget, widgets.Textarea):
                field.widget.attrs.update({"rows": "5"})

            if isinstance(field.widget, widgets.Select):
                field.widget.attrs.update({"class": "form-select"})

            attrs = field.widget.attrs
            css_classes = attrs.get("class", "").split()
            css_classes.append("form-control")
            attrs.update({"class": " ".join(css_classes)})

        return form

    def process_form_submission(self, form):
        """
        We manually create the form submission to show in the wagtail UI and
        send an email.
        """

        cleaned_data = form.cleaned_data
        submission = self.get_submission_class().objects.create(form_data=cleaned_data, page=self)

        logger.info("submission:%s" % submission)

        # important: if extending AbstractEmailForm, email logic must be re-added here
        if self.to_address:
            self.send_mail(form)

        return submission

    def render_landing_page(self, request, form_submission=None, *args, **kwargs):
        """
        Redirect user to home page after successful submission.
        """

        url = self.thank_you_page.url if self.thank_you_page else "/"
        # if a form_submission instance is available, append the id to URL
        # when previewing landing page, there will not be a form_submission instance
        if form_submission:
            url += "?id=%s" % form_submission.id

        messages.success(request, _("Mensaje enviado exitosamente! 🙌"))
        return redirect(url, permanent=False)
