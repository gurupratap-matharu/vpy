import json

from django.db import models
from django.utils.html import mark_safe

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
        collapsed=True,
    )

    promotions = StreamField(
        [("promotions", PromotionsBlock())],
        verbose_name="Promotions Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    featured_pages = StreamField(
        [("featured", ImageLinkBlock())],
        verbose_name="Popular Destinations Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    faq = StreamField(
        [("faq", FAQBlock())],
        verbose_name="FAQ Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    links = StreamField(
        [("Links", LinkBlock())],
        verbose_name="Links Section",
        blank=True,
        collapsed=True,
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

    def ld_entity(self):

        page_schema = json.dumps(
            {
                "@context": "http://schema.org",
                "@graph": [
                    self._get_image_schema(),
                    self._get_article_schema(),
                    self._get_faq_schema(),
                    self._get_organisation_schema(),
                ],
            },
            ensure_ascii=False,
        )
        return mark_safe(page_schema)
