import random
import time
from argparse import ArgumentParser
from datetime import datetime, timedelta as td
from timeit import default_timer as timer

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_time

import requests
from bs4 import BeautifulSoup, Tag

from trips.models import Company, Route, Trip


HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X)"
    "AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257"
    "Safari/9537.53",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}


class Command(BaseCommand):
    help = "Pull fresh data for routes from the outside world"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("route_ids", nargs="*", type=int)
        parser.add_argument("--strategy", default="red", choices=["red", "pink"])
        parser.add_argument("--limit", default="10", type=int)

    def handle(self, *args, **options) -> str:
        route_ids = options["route_ids"]
        strategy = options.get("strategy")
        limit = options["limit"]

        start = timer()
        qs = Route.objects.filter(is_active=True)

        if route_ids:
            qs = qs.filter(id__in=route_ids)

        qs = qs.select_related("origin", "destination").order_by("updated")

        self.success(f"limiting to only {limit} routes...")
        qs = qs[:limit]

        session = requests.Session()

        if strategy == "red":
            self.success("using red strategy...")
            for obj in qs:
                self.success(f"pulling route:{obj}")
                url = obj.get_red_url()

                try:
                    r = session.get(url, headers=HEADERS, timeout=15)
                    r.raise_for_status()
                except requests.exceptions.HTTPError as errh:
                    self.error("Http Error:", errh.response.text)
                except requests.exceptions.ConnectionError as errc:
                    self.error("Error Connecting:", errc.response.text)
                except requests.exceptions.Timeout as errt:
                    self.error("Timeout Error:", errt.response.text)
                except requests.exceptions.RequestException as err:
                    self.error("Oops: Something Else", err.response.text)

                soup = BeautifulSoup(r.text, "html.parser")
                self.pull_red(obj, soup)
                self.wait()

        else:
            self.success("using pink strategy...")
            for obj in qs:
                self.success(f"pulling route:{obj}")
                url = obj.get_pink_url()

                try:
                    r = session.get(url, headers=HEADERS, timeout=15)
                    r.raise_for_status()
                except requests.exceptions.HTTPError as errh:
                    self.error("Http Error:", errh.response.text)
                except requests.exceptions.ConnectionError as errc:
                    self.error("Error Connecting:", errc.response.text)
                except requests.exceptions.Timeout as errt:
                    self.error("Timeout Error:", errt.response.text)
                except requests.exceptions.RequestException as err:
                    self.error("Oops: Something Else", err.response.text)

                soup = BeautifulSoup(r.text, "html.parser")
                self.pull_pink(obj, soup)
                self.wait()

        end = timer()
        out = f"Took {(end - start):.2f} seconds."
        self.success(out)
        return f"Done. {out}"

    # Pink
    def pull_pink(self, obj: Route, soup: BeautifulSoup) -> bool:
        results = soup.find(class_="info")
        if not results:
            # no search results
            return False

        tag = results.find(class_="table")

        min_price = self.clean_price(self.get_value(tag, id="tableCellPasajeMasBarato"))
        avg_price = self.clean_price(self.get_value(tag, id="tableCellPrecioPromedio"))

        first_departure = self.clean_time(self.get_value(tag, id="tableCellHorarioPrimeraSalida"))
        last_departure = self.clean_time(self.get_value(tag, id="tableCellHorarioUltimaSalida"))

        num_departures = int(self.get_value(tag, id="tableCellCantidadSalidas"))
        avg_duration = self.clean_duration(self.get_value(tag, id="tableCellDuracionAprox"))

        # find unique logos
        num_companies = len({t.img.attrs.get("title") for t in soup.find_all(class_="logo")})

        # find min duration
        durations = sorted(x.get_text().strip() for x in soup.find_all(class_="tiempo-viaje"))
        if durations:
            fastest = durations[0]
            h, m = [int(x) for x in fastest.replace("h", "").replace("m", "").split(" ")]
            min_duration = td(hours=h, minutes=m)

        obj.min_price = min_price
        obj.avg_price = avg_price
        obj.first_departure = first_departure
        obj.last_departure = last_departure
        obj.num_departures = num_departures
        obj.avg_duration = avg_duration
        obj.min_duration = min_duration
        obj.num_companies = num_companies
        obj.save()

        self.stdout.write(f"min price:{min_price}")
        self.stdout.write(f"avg price:{avg_price}")
        self.stdout.write(f"first departure:{first_departure}")
        self.stdout.write(f"last departure:{last_departure}")
        self.stdout.write(f"num departures:{num_departures}")
        self.stdout.write(f"avg duration:{avg_duration}")
        self.stdout.write(f"min duration:{min_duration}")
        self.stdout.write(f"num companies:{num_companies}")

        # Extract each trip
        services = soup.find(id="servicios").find_all(id="divData")
        trips = [self.parse_trip(obj, tag) for tag in services]

        with transaction.atomic():
            # Remove all previous trips
            obj.trips.filter(strategy=Trip.Strategy.AUTO).delete()

            # Create trips
            for trip in trips:
                Trip.objects.get_or_create(route=obj, **trip)

        return True

    def parse_trip(self, obj: Route, tag: Tag) -> dict:
        """Extracts pink trip data from a list of services."""

        departure = self.clean_pink_departure(obj, tag)
        arrival = self.clean_pink_arrival(obj, tag)

        if arrival < departure:
            # If arrival < departure it means trip reached the next day
            # increment day by 1
            arrival = arrival + td(days=1)

        trip = {
            "company": self.clean_pink_company(tag),
            "departure": departure,
            "arrival": arrival,
            "duration": self.clean_pink_duration(tag),
            "category": self.clean_pink_category(tag),
            "price": self.clean_pink_price(tag),
        }

        return trip

    def get_value(self, tag, id=None) -> str:
        el = tag.find(id=id)
        return el.parent.next_sibling.next_sibling.get_text().strip()

    def clean_time(self, text: str) -> str:
        # converts '00:00hs.' -> '00:00' for duration field
        return text.rstrip("hs.")

    def clean_duration(self, text: str) -> td:
        # converts '6 horas 4 minutos' to timedelta object
        hours, minutes = text.replace(" horas ", ",").replace(" minutos", "").split(",")
        return td(hours=int(hours), minutes=int(minutes))

    def clean_price(self, text: str) -> str:
        # converts 'Gs154.706' -> '154706'
        return text.lstrip("Gs").replace(".", "")

    def parse_dt(self, obj: Route, time: str) -> datetime:
        # converts '05:15' -> aware datetime
        t = parse_time(time)
        dt = obj.next_departure().replace(
            hour=t.hour,
            minute=t.minute,
            second=t.second,
            microsecond=t.microsecond,
        )
        return dt

    def clean_pink_company(self, tag: Tag) -> Company:
        pink_code = tag.find(id="imgLogoEmpresa").attrs.get("title").lstrip("Viajá por ")
        try:
            c = Company.objects.get(pink_code=pink_code)
        except Company.DoesNotExist:
            self.error(f"Company with pink_code:{pink_code} does not exist!")
            raise
        return c

    def clean_pink_departure(self, obj: Route, tag: Tag) -> datetime:
        txt = tag.find(class_="salida").find(class_="hora").get_text().strip()  # 00:00
        return self.parse_dt(obj, txt)

    def clean_pink_arrival(self, obj: Route, tag: Tag) -> datetime:
        txt = tag.find(class_="llegada").find(class_="hora").get_text().strip()  # 05:15
        return self.parse_dt(obj, txt)

    def clean_pink_duration(self, tag: Tag) -> td:
        # Duration 05h 00m -> timedelta (we can also try parse_duration here)
        txt = tag.find(class_="middle").find(class_="tiempo-viaje").get_text().strip()
        txt = txt.replace("h", "").replace("m", "")
        hours, minutes = map(int, txt.split(" "))
        return td(hours=hours, minutes=minutes)

    def clean_pink_category(self, tag: Tag) -> Trip.Category:
        cat = tag.find(class_="servicio").find("span").get_text().strip().lower()
        map = {
            "ca": Trip.Category.CAMA,
            "cama": Trip.Category.CAMA,
            "diferencial": Trip.Category.SEMICAMA,
            "semicama": Trip.Category.SEMICAMA,
            "comun": Trip.Category.COMMON,
        }
        return map.get(cat, Trip.Category.SEMICAMA)

    def clean_pink_price(self, tag: Tag) -> str:
        # Gs 170.000 -> 170000
        return tag.find(class_="valor").get_text().lstrip("Gs ").replace(".", "")

    # Red
    def pull_red(self, obj: Route, soup: BeautifulSoup) -> bool:
        # Parse all trips first
        cards = soup.find_all(class_="nC-N2W_card")
        trips = [self.parse_card(obj, card) for card in cards]

        if not trips:
            # no search results
            return False

        # Build route metadata from trips - they don't provide
        num_companies = len({t.get("company") for t in trips})

        first_departure = min([t.get("departure") for t in trips]).time()
        last_departure = max([t.get("departure") for t in trips]).time()
        num_departures = len(trips)

        min_price = min(t.get("price") for t in trips)
        avg_price = sum(t.get("price") for t in trips) / num_departures

        min_duration = min(t.get("duration") for t in trips)
        avg_duration = sum([t.get("duration") for t in trips], td()) / num_departures

        self.stdout.write(f"min price:{min_price}")
        self.stdout.write(f"avg price:{avg_price}")
        self.stdout.write(f"first departure:{first_departure}")
        self.stdout.write(f"last departure:{last_departure}")
        self.stdout.write(f"num departures:{num_departures}")
        self.stdout.write(f"avg duration:{avg_duration}")
        self.stdout.write(f"min duration:{min_duration}")
        self.stdout.write(f"num companies:{num_companies}")

        obj.num_companies = num_companies
        obj.first_departure = first_departure
        obj.last_departure = last_departure
        obj.num_departures = num_departures
        obj.min_price = min_price
        obj.avg_price = avg_price
        obj.avg_duration = avg_duration
        obj.min_duration = min_duration
        obj.save()

        with transaction.atomic():
            # Remove all previous Auto trips - revise this later
            obj.trips.filter(strategy=Trip.Strategy.AUTO).delete()

            # Create trips
            for trip in trips:
                t, created = Trip.objects.get_or_create(route=obj, **trip)
                self.stdout.write(f"trip:{t} created:{created}")

        return True

    def parse_card(self, obj: Route, tag: Tag) -> dict:
        """Parse each trip from red search results."""

        departure = self.clean_red_departure(obj, tag)
        arrival = self.clean_red_arrival(obj, tag)

        if arrival < departure:
            # If arrival < departure it means trip reached the next day
            # increment day by 1
            arrival = arrival + td(days=1)

        trip = {
            "company": self.clean_red_company(tag),
            "departure": departure,
            "arrival": arrival,
            "duration": self.clean_red_duration(tag),
            "category": self.clean_red_category(tag),
            "price": self.clean_red_price(tag),
        }
        return trip

    def clean_red_company(self, tag: Tag) -> Company:
        red_code = tag.find(attrs={"data-testid": "service-company"}).attrs.get("alt").strip()
        try:
            c = Company.objects.get(red_code=red_code)
        except Company.DoesNotExist:
            self.error(f"Company with red_code:{red_code} does not exist!")
            raise
        return c

    def clean_red_departure(self, obj: Route, tag: Tag) -> datetime:
        txt = tag.find(attrs={"data-testid": "service-departure-time"}).get_text().strip().rstrip("hs")
        return self.parse_dt(obj, txt)

    def clean_red_arrival(self, obj: Route, tag: Tag) -> datetime:
        txt = tag.find(attrs={"data-testid": "service-arrival-time"}).get_text().strip().rstrip("hs")
        return self.parse_dt(obj, txt)

    def clean_red_duration(self, tag: Tag) -> td:
        """Converts 4h -> td(hours=4), 6h 15m -> td(hours=6, minutes=15)"""

        txt = tag.find(attrs={"data-testid": "service-duration"}).get_text().strip()
        txt = txt.replace("h", "").replace("m", "").split(" ")
        lst = [int(x) for x in txt]
        hours, *mins = lst
        minutes = mins[0] if mins else 0
        return td(hours=hours, minutes=minutes)

    def clean_red_category(self, tag: Tag) -> str:
        row0 = tag.find(attrs={"data-testid": "service-quality-row-0"})
        cat = row0.find(class_="nC-N2W_qualityName").get_text().strip().lower()
        map = {
            "cama suite": Trip.Category.CAMASUITE,
            "cama ejecutivo": Trip.Category.CAMAEJECUTIVO,
            "cama": Trip.Category.CAMA,
            "semicama": Trip.Category.SEMICAMA,
            "comun": Trip.Category.COMMON,
        }
        return map.get(cat, Trip.Category.SEMICAMA)

    def clean_red_price(self, tag: Tag) -> str:
        """Convertes 110.000 -> 11000"""

        txt = tag.find(class_="nC-N2W_bigAmount").get_text().strip()
        txt = txt.replace(".", "")
        return int(txt)

    def wait(self) -> None:
        time.sleep(random.choice([1, 2, 3]))

    def success(self, msg: str) -> str:
        self.stdout.write(self.style.SUCCESS(msg))

    def error(self, msg: str) -> str:
        self.stdout.write(self.style.ERROR(msg))
