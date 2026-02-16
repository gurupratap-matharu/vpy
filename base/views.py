from django.conf import settings
from django.http import FileResponse, HttpRequest
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from wagtail.models.sites import Site


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> FileResponse:
    """
    You might wonder why you need a separate view, rather than relying on Django’s staticfiles app.
    The reason is that staticfiles only serves files from within the STATIC_URL prefix, like static/.

    Thus staticfiles can only serve /static/favicon.ico,
    whilst the favicon needs to be served at exactly /favicon.ico (without a <link>).

    Say if the project is accessed at an endpoint that returns a simple JSON and doesn't use the
    base.html file then the favicon won't show up.

    This endpoint acts as a fall back to supply the necessary icon at /favicon.ico
    """

    file = (settings.BASE_DIR / "staticfiles" / "assets" / "icons" / "favicon.ico").open("rb")
    return FileResponse(file, headers={"Content-Type": "image/x-icon"})


class RobotsView(TemplateView):
    """
    Render a robots.txt with sitemap urls
    """

    content_type = "text/plain"
    template_name = "robots.txt"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = context["view"].request
        context["wagtail_site"] = Site.find_for_request(request)
        return context


class IndexNow(TemplateView):
    template_name = "indexnow_key.txt"
    content_type = "text/plain"
    extra_context = {"key": settings.INDEXNOW_KEY}
