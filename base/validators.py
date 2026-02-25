from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


validate_phone = RegexValidator(
    regex=r"^\+?1?\d{9,17}$",
    message=_("Phone number must be entered in the format: '+595 981 123 456'. Up to 17 digits allowed."),
)
