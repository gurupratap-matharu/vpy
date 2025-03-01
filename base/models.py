from django.db import models

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    PublishingPanel,
)
from wagtail.fields import StreamField
from wagtail.models import (
    DraftStateMixin,
    LockableMixin,
    Page,
    PreviewableMixin,
    RevisionMixin,
    WorkflowMixin,
)
from wagtail.models.i18n import Locale

from modelcluster.models import ClusterableModel

from .blocks import BaseStreamBlock


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


# @method_decorator(get_cache_control_kwargs(), name="serve")
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

    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
    )

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
