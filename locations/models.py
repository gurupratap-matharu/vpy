import json
import logging

from django.core.validators import RegexValidator
from django.db import models
from django.utils.html import mark_safe

from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import StreamField
from wagtail.search import index

from base.blocks import BaseStreamBlock, FAQBlock, LinkBlock, NavTabLinksBlock
from base.models import BasePage

logger = logging.getLogger(__name__)


class CityIndexPage(BasePage):
    """
    A Page model that creates an index page (a listview)
    """

    page_description = "Use this page to show a list of cities"

    intro = models.TextField(help_text="Text to describe the page", blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["CityPage"]

    class Meta:
        verbose_name = "City Index Page"
        verbose_name_plural = "City Index Pages"

    def children(self):
        """
        Allow children of this indexpage to be accessible via the indexpage object on
        templates. We can use this to show featured sections of the site and their
        child pages.
        """
        return self.get_children().specific().live()

    def get_context(self, request, *args, **kwargs):
        """
        Overrides the context to list all child items, that are live, by title
        alphabetical order.
        """

        context = super().get_context(request, *args, **kwargs)
        context["cities"] = self.get_children().live().order_by("title")
        return context

    def ld_entity(self):

        page_schema = json.dumps(
            {
                "@context": "http://schema.org",
                "@graph": [
                    self._get_breadcrumb_schema(),
                    self._get_image_schema(),
                    self._get_faq_schema(),
                    self._get_article_schema(),
                    self._get_organisation_schema(),
                ],
            },
            ensure_ascii=False,
        )
        return mark_safe(page_schema)

    def _get_breadcrumb_schema(self):
        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Pasajes de Micro",
                    "item": "https://ventanita.com.py/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Paraguay",
                    "item": self.full_url,
                },
            ],
        }

        return breadcrumb_schema


class CityPage(BasePage):
    """
    Detail page for a specific city or town.
    """

    page_description = "Use this page to create a city"

    intro = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )

    lat_long = models.CharField(
        max_length=36,
        blank=True,
        help_text="Comma separated lat/long. (Ex. 64.144367, -21.939182) \
                   Right click Google Maps and select 'What's Here'",
        validators=[
            RegexValidator(
                regex=r"^(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)$",
                message="Lat Long must be a comma-separated numeric lat and long",
                code="invalid_lat_long",
            ),
        ],
    )

    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, collapsed=True
    )

    faq = StreamField(
        [("faq", FAQBlock())],
        verbose_name="FAQ Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    links = StreamField(
        [("Links", NavTabLinksBlock())],
        verbose_name="Links Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    companies = StreamField(
        [("Links", LinkBlock())],
        verbose_name="Companies Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    search_fields = BasePage.search_fields + [index.SearchField("body")]

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
        FieldPanel("image"),
        FieldPanel("lat_long"),
        FieldPanel("body"),
        FieldPanel("faq"),
        FieldPanel("links"),
        FieldPanel("companies"),
    ]

    parent_page_types = ["locations.CityIndexPage"]

    class Meta:
        verbose_name = "CityPage"
        verbose_name_plural = "CityPages"

    def __str__(self):
        return self.title

    def get_context(self, request, *args, **kwargs):
        """
        Overrides the context to list all child items, that are live, by title
        alphabetical order.
        """

        lat_long = self.lat_long or ","
        lat, long = lat_long.split(",")

        context = super().get_context(request, *args, **kwargs)
        context["lat_long"] = {"lat": lat, "long": long}
        context["stations"] = self.get_children().live().order_by("title")

        return context

    def ld_entity(self):

        page_schema = json.dumps(
            {
                "@context": "http://schema.org",
                "@graph": [
                    self._get_breadcrumb_schema(),
                    self._get_image_schema(),
                    self._get_faq_schema(),
                    self._get_article_schema(),
                    self._get_organisation_schema(),
                ],
            },
            ensure_ascii=False,
        )
        return mark_safe(page_schema)

    def _get_breadcrumb_schema(self):
        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Pasajes de Micro",
                    "item": "https://ventanita.com.py/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Paraguay",
                    "item": self.get_parent().full_url,
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": self.title,
                    "item": self.full_url,
                },
            ],
        }

        return breadcrumb_schema


class StationIndexPage(BasePage):
    """
    A Page model that creates an index page (a listview)
    """

    page_description = "Use this page to show a list of terminals or stations"

    intro = models.TextField(help_text="Text to describe the page", blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["StationPage"]

    class Meta:
        verbose_name = "Station Index Page"
        verbose_name_plural = "Station Index Pages"

    def children(self):
        """
        Allow children of this indexpage to be accessible via the indexpage object on
        templates. We can use this to show featured sections of the site and their
        child pages.
        """
        return self.get_children().specific().live()

    def ld_entity(self):

        page_schema = json.dumps(
            {
                "@context": "http://schema.org",
                "@graph": [
                    self._get_breadcrumb_schema(),
                    self._get_image_schema(),
                    self._get_faq_schema(),
                    self._get_article_schema(),
                    self._get_organisation_schema(),
                ],
            },
            ensure_ascii=False,
        )
        return mark_safe(page_schema)

    def _get_breadcrumb_schema(self):
        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Paraguay",
                    "item": "https://ventanita.com.py/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Terminales De Micro",
                    "item": self.full_url,
                },
            ],
        }

        return breadcrumb_schema


class StationPage(RoutablePageMixin, BasePage):
    """
    A station detail view which represent a stop | terminal | station
    This is a leaf page and the hierarchy is country -> city -> station
    """

    page_description = "Use this to create a station or terminal page"

    intro = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )

    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, collapsed=True
    )
    address = models.TextField()
    lat_long = models.CharField(
        max_length=36,
        blank=True,
        help_text="Comma separated lat/long. (Ex. 64.144367, -21.939182) \
                   Right click Google Maps and select 'What's Here'",
        validators=[
            RegexValidator(
                regex=r"^(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)$",
                message="Lat Long must be a comma-separated numeric lat and long",
                code="invalid_lat_long",
            ),
        ],
    )

    faq = StreamField(
        [("faq", FAQBlock())],
        verbose_name="FAQ Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    links = StreamField(
        [("Links", NavTabLinksBlock())],
        verbose_name="Links Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    companies = StreamField(
        [("Links", LinkBlock())],
        verbose_name="Companies Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("address"),
        index.SearchField("body"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
        FieldPanel("image"),
        FieldPanel("lat_long"),
        FieldPanel("address"),
        FieldPanel("body"),
        FieldPanel("faq"),
        FieldPanel("links"),
        FieldPanel("companies"),
    ]

    class Meta:
        verbose_name = "Station Page"
        verbose_name_plural = "Station Pages"

    def __str__(self):
        return self.title

    def get_context(self, request, *args, **kwargs):

        context = super().get_context(request, *args, **kwargs)

        lat, long = self.lat_long.split(",")
        context["lat_long"] = {"lat": lat, "long": long}

        return context

    def ld_entity(self):

        page_schema = json.dumps(
            {
                "@context": "http://schema.org",
                "@graph": [
                    self._get_breadcrumb_schema(),
                    self._get_image_schema(),
                    self._get_article_schema(),
                    self._get_faq_schema(),
                    self._get_organisation_schema(),
                ],
            },
            ensure_ascii=False,
        )
        return mark_safe(page_schema)

    def _get_breadcrumb_schema(self):
        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Pasajes de Micro",
                    "item": "https://ventanita.com.py/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Paraguay",
                    "item": self.get_parent().get_parent().full_url,
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": self.get_parent().title,
                    "item": self.get_parent().full_url,
                },
                {
                    "@type": "ListItem",
                    "position": 4,
                    "name": self.title,
                    "item": self.full_url,
                },
            ],
        }

        return breadcrumb_schema
