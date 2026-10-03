import logging

from wagtail.models import PageManager


logger = logging.getLogger(__name__)


class PartnerPageManager(PageManager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related("locale")
        return qs
