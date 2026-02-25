from django.db import models
from django.utils.translation import gettext_lazy as _


class Weekday(models.IntegerChoices):
    MONDAY = 0, _("Monday")
    TUESDAY = 1, _("Tuesday")
    WEDNESDAY = 2, _("Wednesday")
    THURSDAY = 3, _("Thursday")
    FRIDAY = 4, _("Friday")
    SATURDAY = 5, _("Saturday")
    SUNDAY = 6, _("Sunday")


class Departamento(models.TextChoices):
    ALTOPARAGUAY = "APY", "Alto Paraguay"
    ALTOPARANA = "ALP", "Alto Paraná"
    ASUNCION = "ASU", "Asunción"
    AMAMBAY = "AMB", "Amambay"
    BOQUERON = "BOQ", "Boquerón"
    CAAGUAZU = "CGZ", "Caaguazú"
    CAAZAPA = "CZP", "Caazapá"
    CANINDEYU = "CAN", "Canindeyú"
    CENTRAL = "CNT", "Central"
    CONCEPCION = "CON", "Concepción"
    CORDILLERA = "COR", "Cordillera"
    GUAIRA = "GUA", "Guairá"
    ITAPUA = "ITA", "Itapuá"
    MISIONES = "MIS", "Misiones"
    NEEMBUCU = "NIM", "Ñeembucú"
    PARAGUARI = "PAR", "Paraguarí"
    PRESIDENTEHAYES = "PRH", "Presidente Hayes"
    SANPEDRO = "SPD", "San Pedro"
