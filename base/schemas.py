from django.conf import settings


organisation_schema = {
    "@type": "Organization",
    "name": f"{settings.SITE_NAME}",
    "url": f"{settings.BASE_URI}",
    "logo": f"{settings.SITE_NAME}/static/assets/img/logos/ventanita.avif",
    "image": f"{settings.SITE_NAME}/static/assets/img/logos/ventanita.avif",
    "description": "Plataforma de viajes en Paraguay",
    "email": f"{settings.SUPPORT_EMAIL}",
    "telephone": f"{settings.SUPPORT_PHONE}",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Av. Dr. Fernando de la Mora",
        "addressLocality": "Asunción",
        "addressCountry": "PY",
        "addressRegion": "Asunción",
        "postalCode": "001424",
    },
    "contactPoint": {
        "@type": "ContactPoint",
        "telephone": f"{settings.SUPPORT_PHONE}",
        "email": f"{settings.SUPPORT_EMAIL}",
    },
    "sameAs": [],
}
