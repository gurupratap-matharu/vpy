import logging

from django.test import override_settings
from django.utils import timezone

from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import nested_form_data, streamfield

from base.cache import DUMMY_CACHE
from home.models import HomePage
from locations.models import CityIndexPage, CityPage, StationIndexPage, StationPage

logger = logging.getLogger(__name__)


@override_settings(CACHE=DUMMY_CACHE)
class CityIndexPageTests(WagtailPageTestCase):
    """
    Test suite for the city index page
    """

    template_name = "locations/city_index_page.html"

    @classmethod
    def setUpTestData(cls):
        try:
            default_home = Page.objects.get(title="Welcome to your new Wagtail site!")
            default_home.slug = "home-old"
            default_home.save_revision().publish()
            default_home.save()

        except Page.DoesNotExist:
            pass

        cls.root = Page.objects.get(id=1).specific
        cls.home_page = HomePage(title="Home", slug="home")
        cls.city_index_page = CityIndexPage(title="cities", slug="cities")

        # Set Home Page as child of root
        cls.root.add_child(instance=cls.home_page)

        # Save and publish Home Page
        cls.home_page.save_revision().publish()
        cls.home_page.save()

        # Set default Home Page as root page for Site
        cls.site = Site.objects.get(id=1)
        cls.site.root_page = cls.home_page
        cls.site.save()

        # Add CityIndexPage as child of HomePage
        cls.home_page.add_child(instance=cls.city_index_page)
        cls.city_index_page.first_published_at = timezone.now()
        cls.city_index_page.last_published_at = timezone.now()
        cls.city_index_page.save_revision().publish()
        cls.city_index_page.save()

    def test_get(self):
        response = self.client.get(self.city_index_page.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertNotContains(response, "Hi I should not be on this page")

    def test_default_route(self):
        self.assertPageIsRoutable(self.city_index_page)

    def test_page_is_renderable(self):
        self.assertPageIsRenderable(self.city_index_page)

    def test_page_is_previewable(self):
        self.assertPageIsPreviewable(self.city_index_page)

    def test_editability(self):
        self.assertPageIsEditable(self.city_index_page)

    def test_can_create_city_index_under_home_page(self):
        self.assertCanCreateAt(HomePage, CityIndexPage)

    def test_can_create_city_page_under_cityindexpage(self):
        self.assertCanCreateAt(CityIndexPage, CityPage)

    def test_cannot_create_wrong_children_or_parents_for_city_index_page(self):
        self.assertCanNotCreateAt(CityIndexPage, HomePage)

    def test_city_index_page_subpages(self):
        self.assertAllowedSubpageTypes(CityIndexPage, {CityPage})


@override_settings(CACHE=DUMMY_CACHE)
class CityPageTests(WagtailPageTestCase):
    """
    Test suite for City Page.
    """

    template_name = "locations/city_page.html"

    @classmethod
    def setUpTestData(cls):
        try:
            default_home = Page.objects.get(title="Welcome to your new Wagtail site!")
            default_home.slug = "home-old"
            default_home.save_revision().publish()
            default_home.save()

        except Page.DoesNotExist:
            pass

        cls.root = Page.objects.get(id=1).specific
        cls.home_page = HomePage(title="Home", slug="home")
        cls.city_index_page = CityIndexPage(title="cities", slug="cities")
        cls.city_page = CityPage(title="Buenos Aires", slug="buenos-aires")

        # Set Home Page as child of root
        cls.root.add_child(instance=cls.home_page)

        # Save and publish Home Page
        cls.home_page.save_revision().publish()
        cls.home_page.save()

        # Set default Home Page as root page for Site
        cls.site = Site.objects.get(id=1)
        cls.site.root_page = cls.home_page
        cls.site.save()

        # Add CityIndexPage as child of HomePage
        cls.home_page.add_child(instance=cls.city_index_page)
        cls.city_index_page.save_revision().publish()
        cls.city_index_page.save()

        # Add CityPage as child of CityIndexPage
        cls.city_index_page.add_child(instance=cls.city_page)

        cls.city_page.first_published_at = timezone.now()
        cls.city_page.last_published_at = timezone.now()
        cls.city_page.save_revision().publish()
        cls.city_page.save()

    def _get_post_data(self):
        return nested_form_data(
            {
                "title": "Buenos Aires",
                "body": streamfield([("text", "Lorem ipsum dolor sit amet")]),
                "faq": streamfield([("text", "Lorem ipsum dolor sit amet")]),
                "links": streamfield([("text", "Lorem ipsum dolor sit amet")]),
                "companies": streamfield([("text", "Lorem ipsum dolor sit amet")]),
            }
        )

    def test_get(self):
        response = self.client.get(self.city_page.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertNotContains(response, "Hi I should not be on this page")

    def test_default_route(self):
        self.assertPageIsRoutable(self.city_page)

    def test_page_is_renderable(self):
        self.assertPageIsRenderable(self.city_page)

    def test_page_is_previewable(self):
        post_data = self._get_post_data()
        self.assertPageIsPreviewable(self.city_page, post_data=post_data)

    def test_editability(self):
        post_data = self._get_post_data()
        self.assertPageIsEditable(self.city_page, post_data=post_data)

    def test_can_create_city_page_under_city_index(self):
        self.assertCanCreateAt(CityIndexPage, CityPage)

    def test_can_create_station_page_under_citypage(self):
        self.assertCanCreateAt(CityPage, StationPage)

    def test_cannot_create_wrong_children_or_parents_for_city_page(self):
        self.assertCanNotCreateAt(StationPage, CityPage)


@override_settings(CACHE=DUMMY_CACHE)
class StationIndexPageTests(WagtailPageTestCase):
    """
    Test suite for the station index page
    """

    template_name = "locations/station_index_page.html"

    @classmethod
    def setUpTestData(cls):
        try:
            default_home = Page.objects.get(title="Welcome to your new Wagtail site!")
            default_home.slug = "home-old"
            default_home.save_revision().publish()
            default_home.save()

        except Page.DoesNotExist:
            pass

        cls.root = Page.objects.get(id=1).specific
        cls.home_page = HomePage(title="Home", slug="home")
        cls.station_index_page = StationIndexPage(title="terminales", slug="terminales")

        # Set Home Page as child of root
        cls.root.add_child(instance=cls.home_page)

        # Save and publish Home Page
        cls.home_page.save_revision().publish()
        cls.home_page.save()

        # Set default Home Page as root page for Site
        cls.site = Site.objects.get(id=1)
        cls.site.root_page = cls.home_page
        cls.site.save()

        # Add StationIndexPage as child of HomePage
        cls.home_page.add_child(instance=cls.station_index_page)
        cls.station_index_page.first_published_at = timezone.now()
        cls.station_index_page.last_published_at = timezone.now()
        cls.station_index_page.save_revision().publish()
        cls.station_index_page.save()

    def test_get(self):
        response = self.client.get(self.station_index_page.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertNotContains(response, "Hi I should not be on this page")

    def test_default_route(self):
        self.assertPageIsRoutable(self.station_index_page)

    def test_page_is_renderable(self):
        self.assertPageIsRenderable(self.station_index_page)

    def test_page_is_previewable(self):
        self.assertPageIsPreviewable(self.station_index_page)

    def test_editability(self):
        self.assertPageIsEditable(self.station_index_page)

    def test_can_create_station_index_under_home_page(self):
        self.assertCanCreateAt(HomePage, StationIndexPage)

    def test_can_create_station_page_under_stationindexpage(self):
        self.assertCanCreateAt(StationIndexPage, StationPage)

    def test_cannot_create_wrong_children_or_parents_for_station_index_page(self):
        self.assertCanNotCreateAt(StationIndexPage, HomePage)


@override_settings(CACHE=DUMMY_CACHE)
class StationPageTests(WagtailPageTestCase):
    """
    Test suite for Station Page.
    """

    template_name = "locations/station_page.html"

    @classmethod
    def setUpTestData(cls):
        try:
            default_home = Page.objects.get(title="Welcome to your new Wagtail site!")
            default_home.slug = "home-old"
            default_home.save_revision().publish()

        except Page.DoesNotExist:
            pass

        cls.root = Page.objects.get(id=1).specific
        cls.home_page = HomePage(title="Home", slug="home")
        cls.city_index_page = CityIndexPage(title="cities", slug="cities")
        cls.city_page = CityPage(title="Buenos Aires", slug="buenos-aires")
        cls.station_page = StationPage(
            title="Terminal Omnibus",
            slug="terminal-omnibus",
            address="Av. Gdor. Ricardo Videla Mendoza Argentina",
            lat_long="-32.89481666936962, -68.829083231125",
        )

        # Set Home Page as child of root
        cls.root.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()

        # Set default Home Page as root page for Site
        cls.site = Site.objects.get(id=1)
        cls.site.root_page = cls.home_page
        cls.site.save()

        # Add CityIndexPage as child of HomePage
        cls.home_page.add_child(instance=cls.city_index_page)
        cls.city_index_page.save_revision().publish()

        # Add CityPage as child of CityIndexPage
        cls.city_index_page.add_child(instance=cls.city_page)
        cls.city_page.save_revision().publish()

        # Add StationPage as child of CityPage
        cls.city_page.add_child(instance=cls.station_page)

        cls.station_page.first_published_at = timezone.now()
        cls.station_page.last_published_at = timezone.now()
        cls.station_page.save_revision().publish()

    def _get_post_data(self):
        return nested_form_data(
            {
                "title": "Terminal de Retiro",
                "address": "Buenos Aires Argentina CP 1143",
                "lat_long": "-35.3421, -54.4488",
                "body": streamfield([("text", "Lorem ipsum dolor sit amet")]),
                "faq": streamfield([("text", "Lorem ipsum dolor sit amet")]),
                "links": streamfield([("text", "Lorem ipsum dolor sit amet")]),
                "companies": streamfield([("text", "Lorem ipsum dolor sit amet")]),
            }
        )

    def test_get(self):
        response = self.client.get(self.station_page.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertNotContains(response, "Hi I should not be on this page")

    def test_default_route(self):
        self.assertPageIsRoutable(self.station_page)

    def test_editability(self):
        post_data = self._get_post_data()
        self.assertPageIsEditable(self.station_page, post_data=post_data)

    def test_general_previewability(self):
        post_data = self._get_post_data()
        self.assertPageIsPreviewable(self.station_page, post_data=post_data)

    def test_can_create_station_page_under_city_page(self):
        self.assertCanCreateAt(CityPage, StationPage)

    def test_can_create_city_page_under_stationpage(self):
        self.assertCanNotCreateAt(StationPage, CityPage)

    def test_cannot_create_wrong_children_or_parents_for_station_page(self):
        self.assertCanNotCreateAt(StationPage, CityPage)
