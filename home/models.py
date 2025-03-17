from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField

from base.blocks import (
    BaseStreamBlock,
    FAQBlock,
    ImageLinkBlock,
    LinkBlock,
    PromotionsBlock,
)
from base.models import BasePage


class HomePage(BasePage):
    """
    The Home Page is a dynamic page which has different sections that link to other pages
    on the site. Broadly it has the following sections
        - Hero area + search form
        - Featured sections
        - A promotional area
        - Body area
        - CTA section
    """

    page_description = "Use this page to build the home page"

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Homepage image",
    )

    body = StreamField(
        BaseStreamBlock(),
        blank=True,
        use_json_field=True,
    )

    promotions = StreamField(
        [("promotions", PromotionsBlock())],
        verbose_name="Promotions Section",
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    featured_pages = StreamField(
        [("featured", ImageLinkBlock())],
        verbose_name="Popular Destinations Section",
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    faq = StreamField(
        [("faq", FAQBlock())],
        verbose_name="FAQ Section",
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    links = StreamField(
        [("Links", LinkBlock())],
        verbose_name="Links Section",
        blank=True,
        use_json_field=True,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("image"),
        FieldPanel("promotions"),
        FieldPanel("body"),
        FieldPanel("featured_pages"),
        FieldPanel("faq"),
        FieldPanel("links"),
    ]

    class Meta:
        verbose_name = "homepage"
        verbose_name_plural = "homepages"

    def __str__(self):
        return self.title
