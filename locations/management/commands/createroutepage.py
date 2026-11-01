import random
from argparse import ArgumentParser

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from wagtail.rich_text import RichText

from locations.models import RouteIndexPage, RoutePage
from partners.models import PartnerPage
from trips.models import Route


class Command(BaseCommand):
    help = "Programmatically create a draft version of a Route page from a route data model."

    route = None

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("route_ids", nargs="*", type=int)

    def handle(self, *args, **options) -> str:
        created = 0
        route_ids = options["route_ids"]
        qs = Route.objects.filter(id__in=route_ids)

        for obj in qs:
            try:
                RoutePage.objects.get(code=obj.code)
            except RoutePage.DoesNotExist:
                self.create_page(obj)
                created += 1

        return f"Done. Created {created} pages"

    def create_page(self, obj: Route) -> bool:
        """
        Creates a single RoutePage from the route object nested underthe RouteIndex page tree.
        """

        self.success(f"creating page for {obj}...")
        self.route = obj

        title = self.get_title()
        slug = self.get_slug()
        seo_title = self.get_seo_title()
        search_description = self.get_search_description()
        social_text = self.get_social_text()
        listing_title = self.get_listing_title()
        listing_summary = search_description
        intro = self.get_intro()

        route_index_page = RouteIndexPage.objects.first()
        route_page = RoutePage(
            title=title,
            slug=slug,
            seo_title=seo_title,
            search_description=search_description,
            social_text=social_text,
            listing_title=listing_title,
            listing_summary=listing_summary,
            intro=intro,
            code=self.route.code,
        )

        # this is how stream fields need to be added
        route_page.companies.append(self.get_companies())
        route_page.faq.append(self.get_faq())
        route_page.ratings.append(self.get_ratings())

        route_index_page.add_child(instance=route_page)
        route_page.save()

        print(f"title: {title}")
        print(f"slug: {slug}")
        print(f"seo_title: {seo_title}")
        print(f"search_description: {search_description}")
        print(f"social_text: {social_text}")
        print(f"listing_title: {listing_title}")
        print(f"listing_summary:{listing_summary}")
        print(f"code:{self.route.code}")
        print(f"intro:{intro}")
        print(f"ratings:{self.get_ratings()}")
        print(f"companies:{self.get_companies()}")
        label, data = self.get_faq()
        print(label)
        for x in data["item"]:
            print(x["question"])
            print(x["answer"])
        print("\n")

        return True

    # methods to generate page specific fields
    def get_title(self) -> str:
        return f"{self.route.origin} a {self.route.destination}: horarios y precios"

    def get_slug(self) -> str:
        text = f"{self.route.origin} a {self.route.destination}"
        return slugify(text)

    def get_seo_title(self) -> str:
        return f"{self.route.origin} → {self.route.destination}: horarios y precios | Ventanita"

    def get_search_description(self) -> str:
        origin, dest = self.route.origin, self.route.destination

        templates = [
            (
                f"Conocé cómo viajar en bus de {origin} a {dest} en Paraguay. "
                f"Informate sobre la ruta, los horarios y los detalles de tu viaje con Ventanita."
            ),
            (
                f"¿Viajás de {origin} a {dest}? Descubrí información sobre el recorrido en micro, "
                f"consultá detalles de la ruta y planificá tu próximo viaje con Ventanita."
            ),
            (
                f"Encontrá toda la información para tu viaje en micro desde {origin} a {dest}. "
                f"Horarios, terminales y tips para planificar tu próxima escapada con Ventanita."
            ),
        ]
        return random.choice(templates)

    def get_social_text(self) -> str:
        return self.get_seo_title()

    def get_listing_title(self) -> str:
        return self.get_seo_title()

    def get_listing_summary(self) -> str:
        return self.get_search_description()

    def get_intro(self) -> str:
        origin, dest = self.route.origin, self.route.destination
        num_departures = self.route.num_departures
        num_companies = self.route.num_companies
        min_duration = self.route.get_min_duration_display()

        desc = f"Hay {num_departures} salidas con {num_companies} empresas de bus desde {origin} a {dest} con una duración mínima de {min_duration}."
        return desc

    def get_ratings(self) -> tuple[str, dict]:
        values = range(6)
        data = {
            "five": random.choice(values),
            "four": random.choice(values),
            "three": random.choice(values),
            "two": 0,
            "one": 0,
        }
        return ("Ratings", data)

    def get_faq(self) -> tuple[str, dict]:
        origin, dest = self.route.origin, self.route.destination
        low_d = self.route.get_min_duration_display()
        avg_d = self.route.get_avg_duration_display()
        distance = self.route.distance or 0
        min_price = int(self.route.min_price)
        avg_price = int(self.route.avg_price)
        companies = ", ".join({t.company.name for t in self.route.trips.all()})

        data = {
            "title": f"Preguntas frecuentes sobre la ruta {origin} a {dest}",
            "item": [
                # Price Q&A
                {
                    "question": f"¿Cuál es el precio estimado del pasaje en micro de {origin} a {dest}?",
                    "answer": RichText(
                        f"<p>El costo estimado oscila entre los Gs. {min_price} y Gs. {avg_price} por tramo. Los precios varían según la empresa y el tipo de coche (Común, Semi-Cama o Ejecutivo).</p>"
                    ),
                },
                # Duration Q&A
                {
                    "question": f"¿Cuánto dura el viaje en bus de {origin} a {dest}?",
                    "answer": RichText(
                        f"<p>El viaje en micro suele tardar entre {low_d} y {avg_d}. La duración exacta depende del tipo de servicio (si es directo o si realiza paradas en el camino) y del estado del tráfico en los accesos.</p>"
                    ),
                },
                # Empresas
                {
                    "question": f"¿Qué empresas de transporte operan en la ruta {origin} - {dest}?",
                    "answer": RichText(
                        f"<p>Las principales empresas que cubren este trayecto son {companies} entre otras.</p>"
                    ),
                },
                # First & last departure Q&A
                {
                    "question": f"¿Cuándo es la primera y la última salida de bus entre {origin} y {dest}?",
                    "answer": RichText(
                        f"<p>La primera salida de {origin} a {dest} sale a las {self.route.first_departure:%I:%M %p} y la última salida es a las {self.route.last_departure:%I:%M %p}</p>"
                    ),
                },
                # Distance Q&A
                {
                    "question": f"¿Cuántos kilómetros hay de {origin} a {dest}?",
                    "answer": RichText(
                        f"<p>La distancia por carretera entre {origin} y {dest} es de aproximadamente {distance} kilómetros, aunque puede variar según el recorrido y los puntos de salida y llegada.</p>"
                    ),
                },
                # Generic Q&A
                {
                    "question": "¿Qué diferencia hay entre los servicios Común, Semi-Cama y Ejecutivo?",
                    "answer": RichText(
                        "<p>El servicio común realiza más paradas en el trayecto. Los servicios Semi-Cama y Ejecutivo ofrecen asientos más reclinables, aire acondicionado, pantallas y, en algunos casos, refrigerios a bordo, siendo ideales para viajar de noche.</p>"
                    ),
                },
                # Generic Q&A
                {
                    "question": "¿Es necesario comprar los pasajes con anticipación?",
                    "answer": RichText(
                        "<p>Aunque hay mucha frecuencia, te recomendamos asegurar tu lugar con días de antelación si planeás viajar durante el verano, fines de semana largos, Semana Santa o fiestas de fin de año, ya que la demanda aumenta considerablemente.</p>"
                    ),
                },
                # Generic Q&A
                {
                    "question": "¿Qué documentación necesito para viajar en bus por Paraguay?",
                    "answer": RichText(
                        "<p>Solo necesitás presentar tu Cédula de Identidad civil vigente al momento de abordar. Si viajás con menores de edad, recordá llevar también el Certificado de Nacimiento o la autorización correspondiente si no viaja con ambos padres.</p>"
                    ),
                },
            ],
        }
        return ("faq", data)

    def get_companies(self) -> tuple[str, dict]:
        origin = self.route.origin
        dest = self.route.destination
        companies = list({t.company for t in self.route.trips.all()})

        items = []
        for c in companies:
            try:
                page = PartnerPage.objects.get(slug=c.slug)
            except PartnerPage.DoesNotExist:
                self.danger(f"cant find page for {c.slug}")
            items.append({"title": c.name, "page": page})

        data = {
            "heading_text": f"Empresas que opera de {origin} a {dest}",
            "item": items,
        }
        return ("Links", data)

    def success(self, msg: str) -> str:
        self.stdout.write(self.style.SUCCESS(msg))

    def danger(self, msg: str) -> str:
        self.stdout.write(self.style.ERROR(msg))
