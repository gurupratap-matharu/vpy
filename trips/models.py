from django.conf import settings
from django.core.management import call_command
from django.db import models
from django.templatetags.static import static
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from base.choices import Departamento
from trips.date import duration_display, next_weekday
from trips.managers import RouteManager, StopManager, TripManager


class Company(models.Model):
    class Kind(models.TextChoices):
        URBAN = "u", _("Urbano")
        SHORT = "m", _("Media Distancia")
        LONG = "l", _("Larga Distancia")

    name = models.CharField(_("name"), max_length=200, unique=True)
    slug = models.SlugField(_("slug"), max_length=200, unique=True)
    kind = models.CharField(_("kind"), max_length=1, choices=Kind, default=Kind.LONG)
    red_code = models.CharField(_("red code"), max_length=200, blank=True)
    pink_code = models.CharField(_("pink code"), max_length=200, blank=True)
    is_active = models.BooleanField(_("is_active"), default=True)

    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        verbose_name = _("company")
        verbose_name_plural = _("companies")

    def __str__(self) -> str:
        return self.name

    def natural_key(self) -> tuple[str]:
        return (self.name,)

    def logo_url(self) -> str:
        return static(f"assets/img/company-logos/logo-{self.slug}.avif")


class Stop(models.Model):
    class Kind(models.IntegerChoices):
        TERMINAL = 1, _("Terminal")
        ROADSIDE = 2, _("Roadside")

    name = models.CharField(_("name"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=200, unique=True)
    code = models.CharField(_("code"), max_length=7, unique=True)
    description = models.CharField(_("description"), max_length=800, blank=True)
    kind = models.PositiveIntegerField(_("kind"), choices=Kind, default=Kind.TERMINAL)
    lat = models.DecimalField(_("latitude"), max_digits=9, decimal_places=6)
    lon = models.DecimalField(_("longitude"), max_digits=9, decimal_places=6)
    address = models.CharField(_("address"), max_length=128, blank=True)
    city = models.CharField(_("city"), max_length=64, blank=True)
    state = models.CharField(_("state"), max_length=5, choices=Departamento)
    is_active = models.BooleanField(_("active"), default=True)

    red_code = models.CharField(_("red code"), max_length=200, blank=True)
    pink_code = models.CharField(_("pink code"), max_length=200, blank=True)

    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = StopManager()

    class Meta:
        verbose_name = _("Stop")
        verbose_name_plural = _("Stops")

    def __str__(self) -> str:
        return self.name

    def natural_key(self) -> str:
        return (self.slug,)


class Route(models.Model):
    class Strategy(models.TextChoices):
        AUTO = "a", _("Auto")
        MANUAL = "m", _("Manual")

    name = models.CharField(_("name"), max_length=200)
    code = models.CharField(_("code"), max_length=7, unique=True)
    origin = models.ForeignKey("Stop", on_delete=models.SET_NULL, blank=True, null=True, related_name="routes_outbound")
    destination = models.ForeignKey(
        "Stop", on_delete=models.SET_NULL, blank=True, null=True, related_name="routes_inbound"
    )

    first_departure = models.TimeField(_("first departure"), blank=True, null=True)
    last_departure = models.TimeField(_("last departure"), blank=True, null=True)

    num_departures = models.PositiveIntegerField(_("num of departures"), blank=True, null=True)
    num_companies = models.PositiveIntegerField(_("num of companies"), blank=True, null=True)

    distance = models.DecimalField(_("distance"), max_digits=6, decimal_places=2, blank=True, null=True)
    co2 = models.DecimalField(_("co2"), max_digits=6, decimal_places=2, blank=True, null=True)

    min_price = models.DecimalField(_("min price"), max_digits=9, decimal_places=2, blank=True, null=True)
    avg_price = models.DecimalField(_("avg price"), max_digits=9, decimal_places=2, blank=True, null=True)

    min_duration = models.DurationField(_("min duration"), blank=True, null=True)
    avg_duration = models.DurationField(_("avg duration"), blank=True, null=True)

    strategy = models.CharField(_("strategy"), max_length=1, choices=Strategy, default=Strategy.AUTO)
    is_active = models.BooleanField(_("active"), default=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = RouteManager()

    class Meta:
        verbose_name = _("Route")
        verbose_name_plural = _("Routes")

    def __str__(self) -> str:
        return self.name

    def natural_key(self) -> str:
        return (self.code,)

    def next_departure(self) -> timezone:
        next_monday = next_weekday(timezone.now(), 0)
        return timezone.localtime(next_monday)

    def get_pink_url(self) -> str:
        origin = self.origin.pink_code
        dest = self.destination.pink_code
        next_monday = next_weekday(timezone.now(), 0)
        departure = next_monday.strftime("%m/%d/%Y")

        return f"{settings.PINK_BASE_URL}/{origin}/{dest}?FIda={departure}&CntPas=1"

    def get_red_url(self) -> str:
        if not self.origin.red_code or not self.destination.red_code:
            return ""

        o_slug, o_code = self.origin.red_code.split(",")
        d_slug, d_code = self.destination.red_code.split(",")
        next_monday = next_weekday(timezone.now(), 0)
        departure = next_monday.strftime("%d-%m-%Y")

        return f"{settings.RED_BASE_URL}/{o_slug}/{d_slug}/{o_code}/{d_code}/{departure}/_/1/0/0"

    def pull(self, strategy="red") -> str:
        out = call_command("pullfreshdata", self.id, strategy=strategy)
        return out

    def get_min_duration_display(self) -> str:
        return duration_display(self.min_duration)

    def get_avg_duration_display(self) -> str:
        return duration_display(self.avg_duration)

    def get_carbon_emissions(self) -> int:
        # rough estimate for long route buses
        if not self.distance:
            return 0
        return round(self.distance / 40)

    def get_maps_directions_url(self) -> str:
        o_lat, o_lon = self.origin.lat, self.origin.lon
        d_lat, d_lon = self.destination.lat, self.destination.lon
        return f"https://www.google.com/maps/dir/?api=1&origin={o_lat},{o_lon}&destination={d_lat},{d_lon}&travelmode=driving"


class Trip(models.Model):
    class Category(models.TextChoices):
        CAMASUITE = "cs", _("Cama Suite")
        CAMAEJECUTIVO = "ce", _("Cama Ejecutivo")
        CAMA = "ca", _("Cama")
        SEMICAMA = "sc", _("Semi cama")
        COMMON = "co", _("Común")

    class Strategy(models.TextChoices):
        AUTO = "a", _("Auto")
        MANUAL = "m", _("Manual")

    route = models.ForeignKey("Route", on_delete=models.CASCADE, related_name="trips")
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="services")

    category = models.CharField(_("category"), choices=Category, default=Category.SEMICAMA)
    departure = models.DateTimeField(_("departure"))
    arrival = models.DateTimeField(_("arrival"))
    duration = models.DurationField(_("duration"), blank=True, null=True)
    price = models.DecimalField(_("price"), max_digits=9, decimal_places=2, blank=True, null=True)
    strategy = models.CharField(_("strategy"), max_length=1, choices=Strategy, default=Strategy.AUTO)

    objects = TripManager()

    class Meta:
        verbose_name = _("Trip")
        verbose_name_plural = _("Trips")

    def get_duration_display(self) -> str:
        return duration_display(self.duration)
