from django.conf import settings
from django.core.management.base import BaseCommand

import requests
from bs4 import BeautifulSoup


class Command(BaseCommand):
    """
    Command that submits all the urls of our sitemap to index now via post request.
    """

    SITEMAP_URL = f"{settings.BASE_URI}/sitemap.xml"
    INDEXNOW_URL = "https://api.indexnow.org/IndexNow"

    def handle(self, *args, **kwargs):
        self.stdout.write("fetching sitemap...")

        try:
            r = requests.get(self.SITEMAP_URL, timeout=10)
            r.raise_for_status()

        except requests.exceptions.RequestException as err:
            msg = f"Error fetching sitemap:{err}"
            self.stdout.write(msg)
            return

        soup = BeautifulSoup(r.content, "xml")
        urls = [loc.text for loc in soup.find_all("loc")]

        self.stdout.write(f"Found {len(urls)} URLs in the sitemap.")
        self.submit_urls(urls=urls)
        self.stdout.write("All Done.")

    def submit_urls(self, urls):
        payload = {
            "host": settings.BASE_URI,
            "key": settings.INDEXNOW_KEY,
            "keyLocation": f"{settings.BASE_URI}/{settings.INDEXNOW_KEY}.txt",
            "urlList": urls,
        }

        headers = {
            "Content-type": "application/json",
            "charset": "utf-8",
            "Host": "api.indexnow.org",
        }

        try:
            r = requests.post(url=self.INDEXNOW_URL, headers=headers, json=payload, timeout=10)
            r.raise_for_status()

        except requests.exceptions.RequestException as e:
            msg = f"Error submitting to IndexNow:{e}"
            self.stderr.write(msg)

        else:
            self.stdout.write(f"Successfully submitted {len(urls)} URLs to IndexNow.")
            self.stdout.write(f"Response: {r.status_code} - {r.text}")
