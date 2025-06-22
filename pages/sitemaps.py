from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    protocol = "https"
    changefreq = "daily"

    def items(self):
        return [
            "contact",
            "feedback",
            "company-landing",
            "explore",
        ]

    def location(self, item):
        return reverse(f"pages:{item}")
