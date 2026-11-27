import random
from argparse import ArgumentParser

from django.core.management.base import BaseCommand
from django.utils.html import format_html_join
from django.utils.text import slugify

from wagtail.rich_text import RichText

from base.templatetags.base_extras import gs_format
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

        route_index_page = RouteIndexPage.objects.first()
        route_page = RoutePage(
            title=title,
            slug=slug,
            seo_title=seo_title,
            search_description=search_description,
            social_text=social_text,
            listing_title=listing_title,
            listing_summary=listing_summary,
            code=self.route.code,
        )

        # this is how stream fields need to be added
        route_page.companies.append(self.get_companies())
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
        print(f"companies:{self.get_companies()}")

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
                f"¿Viajás de {origin} a {dest}? Descubrí la guía completa sobre los horarios, precios, "
                f"y la ruta. Planificá tu próximo viaje con Ventanita."
            ),
            (
                f"Encontrá toda la información para tu viaje de {origin} a {dest}. "
                f"Horarios, terminales y tips para planificar tu próximo viaje con Ventanita."
            ),
            (
                f"Consultá los horarios, precios estimados y empresas de colectivos para viajar de {origin} a {dest}. "
                f"¡Planificá tu viaje con Ventanita!"
            ),
            (
                f"Compará las salidas de colectivos de {origin} a {dest}. Encontrá precios mínimos, empresas, "
                f"frecuencias y el viaje más rápido en Ventanita."
            ),
        ]
        return random.choice(templates)

    def get_social_text(self) -> str:
        return self.get_seo_title()

    def get_listing_title(self) -> str:
        return self.get_seo_title()

    def get_listing_summary(self) -> str:
        return self.get_search_description()

    def get_faq(self) -> tuple[str, dict]:
        # TODO: Deprecated. We are using FAQ from html template
        # based on progress remove all faq methods
        origin, dest = self.route.origin, self.route.destination

        data = {
            "title": f"Preguntas frecuentes sobre el viaje de {origin} a {dest}",
            "item": [
                self.get_price_faq(),
                self.get_duration_faq(),
                self.get_departure_faq(),
                self.get_companies_faq(),
                self.get_distance_faq(),
                *self.get_generic_faq(),
            ],
        }
        return ("faq", data)

    def get_price_faq(self) -> dict:
        origin, dest = self.route.origin, self.route.destination
        min_price = gs_format(self.route.min_price)
        avg_price = gs_format(self.route.avg_price)

        if min_price == avg_price:
            prefix = f"<p>En promedio, el pasaje en colectivo está unos <b>Gs. {avg_price}</b>.</p>"
        else:
            prefix = (
                f"<p>En promedio, el pasaje en colectivo está unos <b>Gs. {avg_price}</b>,"
                f" pero podés conseguir lo más barato desde <b>Gs. {min_price}</b>.</p>"
            )
        suffix = (
            "<p>Acordate que el precio final depende de la empresa que elijas y el "
            "tipo de coche (Común, Semi-Cama o Ejecutivo).</p><p>Un consejo: los precios suelen subir en fechas "
            "clave (como Semana Santa o fin de año), así que mejor organizate con tiempo.</p>"
        )
        data = {
            "question": f"¿Cuánto sale el pasaje de {origin} a {dest}?",
            "answer": RichText(prefix + suffix),
        }
        return data

    def get_duration_faq(self) -> dict:
        origin, dest = self.route.origin, self.route.destination
        min_d = self.route.get_min_duration_display()
        avg_d = self.route.get_avg_duration_display()
        distance = int(self.route.distance) or 0

        if min_d == avg_d:
            prefix = f"<p>El viaje suele durar más o menos <b>{min_d}</b>.</p> "
        else:
            prefix = f"<p>El viaje suele durar más o menos entre <b>{min_d}</b> y <b>{avg_d}</b>.</p> "

        suffix = (
            "<p>Eso sí, tené en cuenta que el viaje se puede alargar un poco dependiendo del tráfico para salir de la ciudad, "
            "cómo estén las rutas o si el colectivo es de los que paran mucho en el camino a alzar pasajeros.</p>"
            f"<p>Para que sepas la distancia por carretera entre <b>{origin}</b> y <b>{dest}</b> es de aproximadamente <b>{distance}</b> kilómetros.</p>"
        )

        data = {"question": f"¿Cuánto tiempo lleva el viaje de {origin} a {dest}?", "answer": RichText(prefix + suffix)}
        return data

    def get_departure_faq(self) -> dict:
        origin = self.route.origin
        dest = self.route.destination
        first_dep, last_dep = self.route.first_departure, self.route.last_departure

        if first_dep == last_dep:
            # only one trip exists
            answer = (
                f"<p>La única salida de <b>{origin}</b> a <b>{dest}</b> sale a las <b>{first_dep:%H:%M} horas.</b></p>"
            )
        else:
            answer = (
                f"<p>La primera salida de <b>{origin}</b> a <b>{dest}</b> sale a las <b>{first_dep:%H:%M} horas</b> "
                f"y la última salida es a las <b>{last_dep:%H:%M} horas.</b></p>"
            )

        data = {
            "question": f"¿Cuándo es la primera y la última salida de bus entre {origin} y {dest}?",
            "answer": RichText(answer),
        }
        return data

    def get_companies_faq(self) -> dict:
        origin = self.route.origin
        dest = self.route.destination
        companies = {t.company for t in self.route.trips.all()}
        companies_html = format_html_join(
            ", ",
            "<a href='/empresas-de-bus/{}/'>{}</a>",
            ((c.slug, c.name) for c in companies),
        )

        data = {
            "question": f"¿Qué empresas de transporte operan en la ruta {origin} a {dest}?",
            "answer": RichText(
                f"<p>Las principales <a href='/empresas-de-bus/'>empresas de bus</a> que te llevan en esta ruta son {companies_html} entre otras.</p>"
                f"<p>En <a href='/'>Ventanita</a> podés mirar bien los horarios de cada una para elegir la opción que mejor te guste.</p>"
            ),
        }
        return data

    def get_distance_faq(self) -> dict:
        origin = self.route.origin
        dest = self.route.destination
        min_d = self.route.get_min_duration_display()
        avg_d = self.route.get_avg_duration_display()
        distance = int(self.route.distance) or 0

        prefix = (
            f"<p>La distancia por carretera entre <b>{origin}</b> y <b>{dest}</b> es de aproximadamente <b>{distance}</b> kilómetros, "
            f"aunque puede variar según el recorrido y los puntos de salida y llegada.</p>"
        )
        if min_d == avg_d:
            suffix = f"<p>Para que sepas el viaje suele durar más o menos <b>{min_d}</b>.</p> "
        else:
            suffix = f"<p>Para que sepas el viaje suele durar más o menos entre <b>{min_d}</b> y <b>{avg_d}</b>.</p> "

        data = {
            "question": f"¿Cuántos kilómetros hay de {origin} a {dest}?",
            "answer": RichText(prefix + suffix),
        }
        return data

    def get_generic_faq(self) -> dict:
        data = [
            # Seat categories
            {
                "question": "¿Qué diferencia hay entre los servicios Común, Semi-Cama y Ejecutivo?",
                "answer": RichText(
                    "<p>El servicio común realiza más paradas en el trayecto. Los servicios Semi-Cama y Ejecutivo "
                    "ofrecen asientos más reclinables, aire acondicionado, pantallas y, en algunos casos, refrigerios "
                    "a bordo, siendo ideales para viajar de noche.</p>"
                ),
            },
            # Generic Advice
            {
                "question": "¿Es necesario comprar los pasajes con anticipación?",
                "answer": RichText(
                    "<p>Aunque hay mucha frecuencia, te recomendamos asegurar tu lugar con días de antelación "
                    "si planeás viajar durante el verano, fines de semana largos, Semana Santa o "
                    "fiestas de fin de año, ya que la demanda aumenta considerablemente.</p>"
                ),
            },
            # Generic Documentation
            {
                "question": "¿Qué documentación necesito para viajar en bus por Paraguay?",
                "answer": RichText(
                    "<p>Solo necesitás presentar tu <b>Cédula de Identidad</b> civil vigente al momento de abordar. "
                    "Si viajás con <b>menores</b> de edad, recordá llevar también el <b>Certificado de Nacimiento</b> o "
                    "la <i>autorización correspondiente</i> si no viaja con ambos padres.</p>"
                ),
            },
            # Generic Equipaje
            {
                "question": "¿Cuánto equipaje puedo llevar en el bus?",
                "answer": RichText(
                    "<p>Técnicamente podés subir con un bolso de mano chico (de hasta 40x40x25 cm) y llevar en la bodega "
                    "una maleta grande (máximo 80x80x30 cm). En total, tu equipaje no debe pasar los <b>15 kilos</b>.</p>"
                    "<p>Si te excedés en el peso o el tamaño, la empresa te puede cobrar una tasa extra basada en sus precios de encomiendas.</p>"
                    "<p>Pero en realidad no todas las empresas aplican estas reglas de forma estricta según las observaciones de los pasajeros.</p>"
                ),
            },
        ]
        return data

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
