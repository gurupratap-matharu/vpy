import logging

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Command that submits all the urls of our sitemap to index now via post request.
    """

    BASE_URL = "https://ventanita.com.py"
    SITEMAP_URL = f"{BASE_URL}/sitemap.xml"
    INDEXNOW_URL = "https://api.indexnow.org/IndexNow"

    def handle(self, *args, **kwargs):
        self.stdout.write("fetching sitemap...")

        try:
            response = requests.get(self.SITEMAP_URL, timeout=10)
            response.raise_for_status()

        except requests.exceptions.RequestException as err:
            msg = "Error fetching sitemap:%s" % err

            logger.error(msg)
            self.stderr.write(msg)

            return

        soup = BeautifulSoup(response.content, "xml")
        urls = [loc.text for loc in soup.find_all("loc")]

        self.stdout.write(f"Found {len(urls)} URLs in the sitemap.")
        self.submit_urls(urls=urls)
        self.stdout.write("All Done.")

    def submit_urls(self, urls):
        payload = {
            "host": self.BASE_URL,
            "key": settings.INDEXNOW_KEY,
            "keyLocation": f"{self.BASE_URL}/{settings.INDEXNOW_KEY}.txt",
            "urlList": urls,
        }

        headers = {
            "Content-type": "application/json",
            "charset": "utf-8",
            "Host": "api.indexnow.org",
        }

        try:
            response = requests.post(url=self.INDEXNOW_URL, headers=headers, json=payload, timeout=10)
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            msg = "Error submitting to IndexNow:%s" % e

            logger.error(msg)
            self.stderr.write(msg)

        else:
            self.stdout.write(f"Successfully submitted {len(urls)} URLs to IndexNow.")
            self.stdout.write(f"Response: {response.status_code} - {response.text}")
