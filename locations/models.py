import json
import logging
from datetime import time

from django import forms
from django.apps import apps
from django.core.validators import RegexValidator
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, PageChooserPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import StreamField
from wagtail.models import Orderable, PageManager
from wagtail.search import index

from modelcluster.fields import ParentalKey, ParentalManyToManyField

from base.blocks import (
    BaseStreamBlock,
    FAQBlock,
    ImageLinkBlock,
    LinkBlock,
    NavTabBlock,
    NavTabLinksBlock,
    RatingsBlock,
)
from base.choices import Country, Departamento, Weekday
from base.forms import PageFeedbackForm, SuggestionForm
from base.models import BasePage
from base.validators import validate_lat_lng, validate_phone


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

    body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True, collapsed=True)

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
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
    body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True, collapsed=True)
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
        max_num=1,
        collapsed=True,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("intro", classname="collapsed"),
        FieldPanel("image", classname="collapsed"),
        FieldPanel("body", classname="collapsed"),
        FieldPanel("faq", classname="collapsed"),
        FieldPanel("links", classname="collapsed"),
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


class StationPageManager(PageManager):
    def get_queryset(self):
        qs = super().get_queryset().select_related("locale")
        return qs


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
    lat_long = models.CharField(
        max_length=36,
        blank=True,
        help_text="Comma separated lat/long. (Ex. 64.144367, -21.939182) \
                   Right click Google Maps and select 'What's Here'",
        validators=[validate_lat_lng],
    )
    address = models.TextField(_("Address"))
    phone = models.CharField(_("Phone"), max_length=20, blank=True, validators=[validate_phone])
    province = models.CharField(_("Province"), max_length=20, choices=Departamento, blank=True)
    departamento = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="terminales",
    )
    country = models.CharField(_("Country"), max_length=20, choices=Country, blank=True)
    services = ParentalManyToManyField("locations.Service", blank=True)
    directions = StreamField(BaseStreamBlock(), verbose_name="Directions (Como llegar?)", blank=True, collapsed=True)
    body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True, collapsed=True)

    info = StreamField(
        [("Info", NavTabBlock())],
        verbose_name="Info Section",
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
    ratings = StreamField(
        [("Ratings", RatingsBlock())],
        verbose_name="Ratings",
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
        MultiFieldPanel(
            [
                FieldPanel("phone"),
                FieldPanel("address"),
                FieldPanel("lat_long"),
                FieldPanel("province"),
                FieldPanel("departamento"),
                FieldPanel("country"),
                FieldPanel("services", widget=forms.CheckboxSelectMultiple),
                InlinePanel(
                    "opening_hours",
                    label="Opening Hours",
                    classname="collapsed",
                    max_num=7,
                ),
                PageChooserPanel("departamento"),
            ],
            heading="Basic Info",
            classname="collapsed",
        ),
        FieldPanel("info", classname="collapsed"),
        FieldPanel("directions", classname="collapsed"),
        FieldPanel("body", classname="collapsed"),
        FieldPanel("faq", classname="collapsed"),
        FieldPanel("links", classname="collapsed"),
        FieldPanel("companies", classname="collapsed"),
        FieldPanel("ratings", classname="collapsed"),
        MultiFieldPanel(
            [
                FieldPanel("image"),
                InlinePanel("gallery_images", label="Gallery images"),
            ],
            heading="Media",
            classname="collapsed",
        ),
    ]

    objects = StationPageManager()

    class Meta:
        verbose_name = "Station Page"
        verbose_name_plural = "Station Pages"

    def __str__(self):
        return self.title

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        lat, long = self.lat_long.split(",")
        options = {
            "lat": lat,
            "long": long,
            "title": self.title,
            "text": self.intro,
            "url": self.get_full_url(),
        }
        context["options"] = options
        context["today"] = timezone.now().weekday()
        context["page_feedback_form"] = self.get_page_feedback_form()
        context["suggestion_form"] = self.get_suggestion_form()
        return context

    def get_page_feedback_form(self):
        # prepopulate the hidden url field with page url
        initial = {"url": self.url}
        form = PageFeedbackForm(initial=initial)
        return form

    def get_suggestion_form(self):
        initial = {"url": self.url}
        form = SuggestionForm(initial=initial)
        return form

    def get_google_maps_directions_url(self):
        return f"https://www.google.com/maps/dir/?api=1&destination={self.lat_long}"

    def ld_entity(self):
        page_schema = json.dumps(
            {
                "@context": "http://schema.org",
                "@graph": [
                    self._get_breadcrumb_schema(),
                    self._get_image_schema(),
                    self._get_station_schema(),
                    self._get_organisation_schema(),
                    self._get_faq_schema(),
                ],
            },
            ensure_ascii=False,
        )
        return mark_safe(page_schema)

    def _get_station_schema(self):
        return {
            "@type": "BusStation",
            "@id": f"{self.full_url}#busstation",
            "name": self.title,
            "description": self.search_description,
            "url": self.full_url,
            "telephone": self.phone,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": self.address,
                #  "addressLocality": "{{ page.city }}",
                #  "addressRegion": "{{ page.department }}",
                # "postalCode": "{{ page.postal_code }}",
                "addressCountry": "PY",
            },
            "geo": self._get_geo_schema(),
            "openingHoursSpecification": "Mo-Su",
            "image": self._get_image_schema(),
            # Can't seem to pass ratings in google rich test results
            # "aggregateRating": self._get_ratings_schema(),
            "amenityFeature": self._get_services_schema(),
        }

    def _get_image_schema(self):
        image = self.image or self.social_image
        image_url = image.file.url if image else ""
        image_title = getattr(image, "title", "")
        image_description = getattr(image, "description", "")

        image_schema = {
            "@context": "https://schema.org",
            "@type": "ImageObject",
            "contentUrl": f"https://ventanita.com.py{image_url}",
            "url": f"https://ventanita.com.py{image_url}",
            "license": "https://ventanita.com.py/condiciones-generales/",
            "acquireLicensePage": "https://ventanita.com.py/contact/",
            "creditText": image_title,
            "creator": {"@type": "Person", "name": "Ventanita"},
            "copyrightNotice": "Ventanita",
            "contentLocation": self.title,
            "description": image_description,
            "name": image_title,
        }

        return image_schema

    def _get_geo_schema(self):
        lat, long = self.lat_long.split(",")
        return {"@type": "GeoCoordinates", "latitude": lat, "longitude": long}

    def _get_ratings_schema(self):
        if self.ratings:
            obj = self.ratings[0].value
            rating_value = str(obj.get_score())
            rating_count = str(obj.get_total_ratings())
        else:
            rating_value = rating_count = 0

        return {
            "@type": "AggregateRating",
            "ratingValue": rating_value,
            "ratingCount": rating_count,
            "bestRating": "5",
            "worstRating": "1",
        }

    def _get_services_schema(self):
        return [
            {"@type": "LocationFeatureSpecification", "name": service.name, "value": True}
            for service in self.services.all()
        ]

    def _get_breadcrumb_schema(self):
        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Inicio",
                    "item": "https://ventanita.com.py/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Terminales de Ómnibus",
                    "item": "https://ventanita.com.py/terminales-de-omnibus/",
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


class StationPageGalleryImage(Orderable):
    page = ParentalKey("locations.StationPage", on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey("wagtailimages.Image", on_delete=models.CASCADE, related_name="+")
    caption = models.CharField(_("caption"), max_length=250, blank=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = "stationpagegallery"
        verbose_name_plural = "stationpagegallery"


def default_open_time():
    return time(hour=8)


def default_close_time():
    return time(hour=22)


class OpeningHour(Orderable):
    page = ParentalKey("locations.StationPage", on_delete=models.CASCADE, related_name="opening_hours")
    weekday = models.PositiveIntegerField(_("weekday"), choices=Weekday)
    open_time = models.TimeField(_("start"), default=default_open_time)
    close_time = models.TimeField(_("end"), default=default_close_time)
    closed = models.BooleanField(_("closed"), default=False)
    panels = [
        FieldRowPanel(
            [
                FieldPanel("weekday"),
                FieldPanel("open_time"),
                FieldPanel("close_time"),
                FieldPanel("closed"),
            ]
        )
    ]

    class Meta:
        verbose_name = "openinghour"
        verbose_name_plural = "openinghours"

    def __str__(self):
        return f"{self.get_weekday_display()} {self.open_time}:{self.close_time}"


class Service(models.Model):
    """
    A service (amenity) that a station or terminal provides.
    Typically represented in a badge with an icon and optional text for visual purposes
    eg: Washrooms, Cafeteria, Waiting Room, Lockers, etc
    """

    name = models.CharField(_("name"), max_length=255)
    icon = models.CharField(_("icon"), max_length=20, help_text="Only name of the icon")

    panels = [
        FieldPanel("name"),
        FieldPanel("icon"),
    ]

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.name


class RouteIndexPage(BasePage):
    """
    A Page model that creates an index page for all Routes (a listview)
    """

    page_description = "Use this page to show a list of routes"

    intro = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
    body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True, collapsed=True)

    faq = StreamField(
        [("faq", FAQBlock())],
        verbose_name="FAQ Section",
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

    destinos = StreamField(
        [("Links", LinkBlock())],
        verbose_name="City Page Links",
        blank=True,
        max_num=1,
        collapsed=True,
    )
    routes = StreamField(
        [("Links", NavTabLinksBlock())],
        verbose_name="Links Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("intro", classname="collapsed"),
        FieldPanel("image", classname="collapsed"),
        FieldPanel("body", classname="collapsed"),
        FieldPanel("faq", classname="collapsed"),
        FieldPanel("companies", classname="collapsed"),
        FieldPanel("destinos", classname="collapsed"),
        FieldPanel("routes", classname="collapsed"),
    ]

    class Meta:
        verbose_name = "Route Index Page"
        verbose_name_plural = "Route Index Pages"

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
                    "name": "Rutas",
                    "item": self.full_url,
                },
            ],
        }

        return breadcrumb_schema


class RoutePage(BasePage):
    page_description = "Use this to create a A -> B route page"

    code = models.CharField(_("route code"), max_length=20, blank=True)
    intro = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
    province = models.CharField(_("Province"), max_length=20, choices=Departamento, blank=True)
    country = models.CharField(_("Country"), max_length=20, choices=Country, default=Country.PARAGUAY, blank=True)
    body = StreamField(BaseStreamBlock(search_index=False), verbose_name="Page body", blank=True, collapsed=True)
    companies = StreamField(
        [("Links", LinkBlock(search_index=False))],
        verbose_name="Companies Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )
    terminals = StreamField(
        [("Terminals", NavTabLinksBlock(search_index=False))],
        verbose_name="Terminals nearby origin and destination",
        blank=True,
        max_num=1,
        collapsed=True,
    )
    faq = StreamField(
        [("faq", FAQBlock(search_index=False))],
        blank=True,
        max_num=1,
        collapsed=True,
    )
    featured_routes = StreamField(
        [("featured", ImageLinkBlock(search_index=False))],
        verbose_name="Popular Destinations Section",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    links = StreamField(
        [("Routes", NavTabLinksBlock(search_index=False))],
        verbose_name="Outbound Inbound routes",
        blank=True,
        max_num=1,
        collapsed=True,
    )
    ratings = StreamField(
        [("Ratings", RatingsBlock(search_index=False))],
        verbose_name="Ratings",
        blank=True,
        max_num=1,
        collapsed=True,
    )

    content_panels = BasePage.content_panels + [
        FieldRowPanel(
            [
                FieldPanel("code"),
                FieldPanel("province"),
                FieldPanel("country"),
            ],
            classname="collapsed",
        ),
        FieldPanel("intro", classname="collapsed"),
        FieldPanel("body", classname="collapsed"),
        FieldPanel("companies", classname="collapsed"),
        FieldPanel("terminals", classname="collapsed"),
        FieldPanel("faq", classname="collapsed"),
        FieldPanel("featured_routes", classname="collapsed"),
        FieldPanel("links", classname="collapsed"),
        FieldPanel("ratings", classname="collapsed"),
        FieldPanel("image", classname="collapsed"),
    ]

    class Meta:
        verbose_name = "Route Page"
        verbose_name_plural = "Route Pages"

    def __str__(self) -> str:
        return self.title

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        context["page_feedback_form"] = self.get_page_feedback_form()
        context["suggestion_form"] = self.get_suggestion_form()
        context["route"], context["trips"] = self.get_route_trips()
        return context

    def get_page_feedback_form(self):
        # prepopulate the hidden url field with page url
        initial = {"url": self.url}
        form = PageFeedbackForm(initial=initial)
        return form

    def get_suggestion_form(self):
        initial = {"url": self.url}
        form = SuggestionForm(initial=initial)
        return form

    def get_route_trips(self):
        Route = apps.get_model("trips.Route")
        qs = Route.objects.all()
        self.route = get_object_or_404(qs, code=self.code)
        self.trips = self.route.trips.all()
        return self.route, self.trips

    def ld_entity(self):
        page_schema = json.dumps(
            {
                "@context": "http://schema.org",
                "@graph": [
                    self._get_web_page_schema(),
                    self._get_breadcrumb_schema(),
                    self._get_bus_trip_schema(),
                    self._get_faq_schema(),
                ],
            },
            ensure_ascii=False,
        )
        return mark_safe(page_schema)

    def _get_web_page_schema(self) -> dict:
        return {
            "@type": "WebPage",
            "@id": f"{self.full_url}#webpage",
            "url": f"{self.full_url}",
            "name": f"{self.title}",
            "description": f"{self.search_description}",
            "inLanguage": "es-PY",
            "mainEntity": {
                "@id": f"{self.full_url}#departures",
                "url": f"{self.full_url}",
            },
        }

    def _get_breadcrumb_schema(self):
        breadcrumb_schema = {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": "https://ventanita.com.py/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Rutas",
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

    def _get_bus_trip_schema(self):
        if not self.route or not self.trips:
            self.get_route_trips()

        schema = {
            "@type": "ItemList",
            "@id": f"{self.full_url}#departures",
            "name": f"Horarios y Precios de Micros de {self.route.origin} a {self.route.destination}",
            "description": (
                f"Listado de servicios, horarios y tarifas de empresas de micros "
                f"para el trayecto {self.route.origin} a {self.route.destination}."
            ),
            "itemListElement": [self._get_trip_item(pos, trip) for pos, trip in enumerate(self.trips, 1)],
        }

        return schema

    def _get_trip_item(self, pos, trip) -> dict:
        """
        See https://schema.org/BusTrip
        """
        origin = self.route.origin
        dest = self.route.destination
        company = trip.company
        dep = timezone.localtime(trip.departure).time()
        arr = timezone.localtime(trip.arrival).time()
        # Generate unique trip id based on company and departure time
        trip_id = f"trip-{company.slug}-{dep.hour}{dep.minute}"

        trip_item = {
            "@type": "ListItem",
            "position": pos,
            "item": {
                "@type": "BusTrip",
                "@id": f"{self.full_url}#{trip_id}",
                "url": f"{self.full_url}",
                "name": f"Bus de {origin} a {dest} - {company}",
                "busName": f"{company}",
                "departureTime": f"{dep}",
                "arrivalTime": f"{arr}",
                "provider": {
                    "@type": "Organization",
                    "name": f"{company.name}",
                    # provide both id & url to cross link entities
                    "@id": f"https://ventanita.com.py/empresas/{company.slug}/#organization",
                    "url": f"https://ventanita.com.py/empresas/{company.slug}/",
                },
                "departureBusStop": {
                    "@type": "BusStation",
                    "name": f"Terminal de Ómnibus {origin}",
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": f"{origin.address}",
                        "addressCountry": "PY",
                    },
                },
                "arrivalBusStop": {
                    "@type": "BusStation",
                    "name": f"Terminal de Ómnibus de {dest}",
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": f"{dest.address}",
                        "addressCountry": "PY",
                    },
                },
                "offers": {
                    "@type": "Offer",
                    "price": f"{int(trip.price)}",
                    "priceCurrency": "PYG",
                    "category": f"{trip.get_category_display()}",
                    "description": f"Pasaje en categoría {trip.get_category_display()}",
                    "seller": {
                        "@type": "Organization",
                        "name": f"{company.name}",
                        "url": f"https://ventanita.com.py/empresas/{company.slug}/",
                    },
                },
            },
        }
        return trip_item
