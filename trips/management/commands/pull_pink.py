import random
import time
from argparse import ArgumentParser
from collections import OrderedDict
from datetime import datetime, timedelta as td
from statistics import median
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


session = requests.Session()


class Command(BaseCommand):
    help = "Pull fresh data for routes from the outside world"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("route_ids", nargs="*", type=int)
        parser.add_argument("--limit", default="10", type=int)

    def handle(self, *args, **options) -> str:
        self.route_ids = options["route_ids"]
        limit = options["limit"]

        start = timer()
        qs = Route.objects.filter(is_active=True)

        if self.route_ids:
            qs = qs.filter(id__in=self.route_ids)

        qs = qs.select_related("origin", "destination").order_by("updated")
        qs = qs[:limit]

        self.success("using pink strategy...")
        self.success(f"limiting to only {limit} routes...")
        items = qs.count()

        for i, obj in enumerate(qs, start=1):
            self.pull_pink(obj)
            is_last_cycle = i == items
            if not is_last_cycle:
                self.wait()

        end = timer()
        out = f"Took {(end - start):.2f} seconds."
        self.success(out)
        return f"Done. {out}"

    def pull_pink(self, obj: Route) -> bool:
        soup = self.fetch(obj)
        results = soup.find(class_="info")
        if not results:
            # no search results
            return False

        # Parse all trips first
        services = soup.find(id="servicios").find_all(id="divData")
        raw_trips = [self.parse_trip(obj, tag) for tag in services]
        trips = self.merge_trips(raw_trips)

        # calculate route stats from merged trips
        num_companies = len({t.get("company") for t in trips})
        first_departure = min(t.get("departure") for t in trips).time()
        last_departure = max(t.get("departure") for t in trips).time()
        num_departures = len(trips)

        price_tuples = [(t.get("price_a"), t.get("price_b")) for t in trips]
        prices = [x for tup in price_tuples for x in tup if x is not None]

        min_price = min(prices)
        avg_price = int(median(prices))  # we actually calculate the median

        min_duration = min(t.get("duration") for t in trips)
        avg_duration = median(t.get("duration") for t in trips)  # again median

        self.stdout.write(f"min price:{min_price} avg price:{avg_price}")
        self.stdout.write(f"first departure:{first_departure} last departure:{last_departure}")
        self.stdout.write(f"avg duration:{avg_duration} min duration:{min_duration}")
        self.stdout.write(f"num departures:{num_departures} num companies:{num_companies}")

        obj.min_price = min_price
        obj.avg_price = avg_price
        obj.first_departure = first_departure
        obj.last_departure = last_departure
        obj.num_departures = num_departures
        obj.avg_duration = avg_duration
        obj.min_duration = min_duration
        obj.num_companies = num_companies
        obj.save()

        with transaction.atomic():
            # Remove all previous trips
            obj.trips.filter(strategy=Trip.Strategy.AUTO).delete()

            # Create trips
            for trip in trips:
                Trip.objects.get_or_create(route=obj, **trip)

        return True

    def fetch(self, obj: Route) -> BeautifulSoup:
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

        return BeautifulSoup(r.text, "html.parser")

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
            "duration": arrival - departure,
            "category": self.clean_pink_category(tag),
            "price": self.clean_pink_price(tag),
        }

        return trip

    def merge_trips(self, trips: list) -> list[dict]:
        # combine all categories and prices for the same trip
        # trip is same is (company, departure, arrival) is same

        d = OrderedDict()
        for t in trips:
            key = (t["company"], t["departure"], t["arrival"])
            value = (t["category"], t["price"])
            s = d.setdefault(key, set())  # returns the set
            s.add(value)

        # now unpack the ordered dict and created merged trips
        # with keys - price_a, category_a, so on...
        merged = []
        for k, v in d.items():
            # v is the set here
            # for ex:  {(Trip.Category.CAMA, '130000'), (Trip.Category.SEMICAMA, '120000')}
            if len(v) > 1:
                category_a, price_a = v.pop()
                category_b, price_b = v.pop()
            else:
                category_a, price_a = v.pop()
                category_b, price_b = None, None

            trip = {
                "company": k[0],
                "departure": k[1],
                "arrival": k[2],
                "duration": k[2] - k[1],
                "category_a": category_a,
                "price_a": price_a,
            }

            if category_b and price_b:
                trip["category_b"] = category_b
                trip["price_b"] = price_b

            merged.append(trip)

        return merged

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

    def clean_pink_price(self, tag: Tag) -> int:
        # Gs 170.000 -> 170000
        value = tag.find(class_="valor").get_text().lstrip("Gs ").replace(".", "")
        return int(value)

    def wait(self) -> None:
        # don't wait if manually updating single route via admin
        if len(self.route_ids) == 1:
            return

        secs = random.choice([2, 3, 4, 5])
        self.error(f"waiting {secs} secs...")
        time.sleep(secs)

    def success(self, msg: str) -> str:
        self.stdout.write(self.style.SUCCESS(msg))

    def error(self, msg: str) -> str:
        self.stdout.write(self.style.ERROR(msg))
