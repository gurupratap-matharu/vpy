import logging

from wagtail.models import PageManager


logger = logging.getLogger(__name__)


class PartnerPageManager(PageManager):
    def get_queryset(self):
        logger.info("PartnerPageManager: get_queryset called...")
        qs = super().get_queryset()
        qs = qs.select_related("locale")
        return qs
