from typing import ClassVar

from django.contrib import admin, messages
from django.core.management import call_command
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils import timezone
from django.utils.html import format_html, format_html_join

from trips.models import Company, Route, Stop, Trip


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin[Company]):
    list_display = ("id", "name", "trips", "red_code", "pink_code", "last_updated", "active")
    list_display_links = ("id", "name")
    list_filter = ("is_active", "updated")
    list_per_page = 30
    prepopulated_fields: ClassVar = {"slug": ("name",)}
    search_fields = ("id", "name")
    ordering = ("name",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Company]:
        qs = super().get_queryset(request)
        qs = qs.annotate(num_trips=Count("services", distinct=True))
        return qs

    @admin.display(ordering="updated")
    def last_updated(self, obj: Company) -> str:
        return obj.updated.strftime("%d %b %Y %H:%M")

    def trips(self, obj: Company) -> int:
        return obj.num_trips

    def active(self, obj: Company) -> bool:
        return obj.is_active

    active.boolean = True


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin[Stop]):
    list_display = ("id", "name", "code", "state", "kind", "red_code", "pink_code", "is_active")
    list_display_links = ("id", "name")
    list_per_page = 30
    prepopulated_fields: ClassVar = {"slug": ("name",)}
    list_filter = ("kind", "state", "is_active")
    search_fields = ("id", "name", "code")
    _basic_fields = (
        ("name", "slug", "code"),
        ("description", "kind"),
    )
    _geo_fields = (("lat", "lon"), ("address", "city", "state"))
    _extra_fields = (("red_code", "pink_code"), "is_active")
    fieldsets = (
        ("Basic Information", {"fields": _basic_fields}),
        ("Geo", {"fields": _geo_fields}),
        ("Extra", {"fields": _extra_fields}),
    )


class TripInlineAdmin(admin.TabularInline):
    model = Trip
    extra = 0


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin[Route]):
    list_display = (
        "id",
        "name",
        "trips",
        "operators",
        "distance",
        "min_fare",
        "min_time",
        "last_updated",
        "red",
        "pink",
        "map",
        "active",
        "strategy",
        "pull_preference",
    )
    list_display_links = ("id", "name")
    list_filter = ("updated", "strategy", "is_active")
    list_per_page = 30
    list_select_related = ("origin", "destination")
    autocomplete_fields = ("origin", "destination")
    search_fields = ("id", "code", "origin__name", "destination__name")
    inlines = (TripInlineAdmin,)
    actions = (
        "pull",
        "pull_red",
        "pull_pink",
        "create_route_page",
    )

    _basic_fields = (("name", "code", "origin", "destination"),)
    _extra_fields = (("distance", "co2", "strategy", "pull_preference", "is_active"),)
    _price_duration_fields = (("min_price", "avg_price", "min_duration", "avg_duration"),)
    _departure_fields = (("num_departures", "num_companies", "first_departure", "last_departure"),)

    fieldsets = (
        ("Basic Information", {"fields": _basic_fields}),
        ("Extra", {"fields": _extra_fields}),
        ("Price & Duration", {"fields": _price_duration_fields}),
        ("Departures", {"fields": _departure_fields}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Route]:
        qs = super().get_queryset(request)
        qs = qs.annotate(num_trips=Count("trips", distinct=True))
        return qs

    def trips(self, obj: Route) -> int:
        return obj.num_trips

    def operators(self, obj: Route) -> int:
        return obj.num_companies or 0

    def min_fare(self, obj: Route) -> str:
        return f"{obj.min_price:,.0f}" if obj.min_price else "?"

    @admin.display(ordering="min_duration")
    def min_time(self, obj: Trip) -> str:
        # converts 5:20:00 -> 5:20
        return str(obj.min_duration)[:-3] if obj.min_duration else "?"

    @admin.display(ordering="updated")
    def last_updated(self, obj: Route) -> str:
        return obj.updated.strftime("%d-%m-%g %H:%M:%S")

    def pink(self, obj: Route) -> str:
        url = obj.get_pink_url()
        return format_html("<a href='{}' target='_blank' rel='noreferrer'>View</a>", url)

    def red(self, obj: Route) -> str:
        url = obj.get_red_url()
        return format_html("<a href='{}' target='_blank' rel='noreferrer'>View</a>", url)

    def map(self, obj: Route) -> str:
        url = obj.get_maps_directions_url()
        return format_html("<a href='{}' target='_blank', rel='noreferrer'>See</a>", url)

    def active(self, obj: Route) -> bool:
        return obj.is_active

    active.boolean = True

    @admin.action(description="Pull selected routes via Red")
    def pull_red(self, request: HttpRequest, qs: QuerySet[Route]) -> None:
        ids = [obj.id for obj in qs]
        out = call_command("pull_red", ids)
        self.message_user(request, f"{out} {len(qs)} routes updated.", messages.SUCCESS)

    @admin.action(description="Pull selected routes via Pink")
    def pull_pink(self, request: HttpRequest, qs: QuerySet[Route]) -> None:
        ids = [obj.id for obj in qs]
        out = call_command("pull_pink", ids)
        self.message_user(request, f"{out} {len(qs)} routes updated.", messages.SUCCESS)

    @admin.action(description="Pull selected routes via Preference")
    def pull(self, request: HttpRequest, qs: QuerySet[Route]) -> None:
        red_qs = qs.filter(pull_preference=Route.PullPreference.RED)
        pink_qs = qs.filter(pull_preference=Route.PullPreference.PINK)
        if red_qs.exists():
            self.pull_red(request, red_qs)
        if pink_qs.exists():
            self.pull_pink(request, pink_qs)

    @admin.action(description="Create Route Pages")
    def create_route_page(self, request: HttpRequest, qs: QuerySet[Route]) -> None:
        ids = [obj.id for obj in qs]
        out = call_command("createroutepage", ids)
        self.message_user(request, f"{out}", messages.SUCCESS)


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("id", "route", "company", "departs", "arrives", "runtime", "price", "strategy")
    list_per_page = 30
    list_select_related = ("route", "company")
    list_filter = ("strategy", "updated")
    search_fields = ("route__name", "company__name", "route__origin__name", "route__destination__name")
    _basic_fields = (("route", "company", "strategy"),)
    _times_fields = (("departure", "arrival", "duration"),)
    _price_category_fields = (("category_a", "price_a", "category_b", "price_b"),)
    fieldsets = (
        ("Basic Information", {"fields": _basic_fields}),
        ("Times", {"fields": _times_fields}),
        ("Price & Category", {"fields": _price_category_fields}),
    )

    @admin.display(ordering="departure")
    def departs(self, obj: Trip) -> str:
        departure = timezone.localtime(obj.departure)
        return departure.strftime("%d %b %H:%M")

    @admin.display(ordering="arrival")
    def arrives(self, obj: Trip) -> str:
        arrival = timezone.localtime(obj.arrival)
        return arrival.strftime("%d %b %H:%M")

    @admin.display(ordering="duration")
    def runtime(self, obj: Trip) -> str:
        # converts 5:20:00 -> 5:20
        return str(obj.duration)[:-3]

    def price(self, obj: Trip) -> int:
        prices = [(obj.category_a, obj.price_a), (obj.category_b, obj.price_b)]
        prices = [(obj.Category(x[0]).label, int(x[1])) for x in prices if x[0] and x[1]]
        return format_html_join("\n", "<span>{} {}</span><br>", (prices))
